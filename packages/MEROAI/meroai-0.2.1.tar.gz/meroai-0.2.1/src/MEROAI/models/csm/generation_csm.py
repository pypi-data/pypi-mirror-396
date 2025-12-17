import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional, Union
import torch
import torch.nn as nn
from ...generation import (
    GenerateDecoderOnlyOutput,
    GenerationConfig,
    GenerationMixin,
    GenerationMode,
)
from ...generation.logits_process import LogitsProcessorList
from ...generation.stopping_criteria import MaxLengthCriteria, StoppingCriteriaList
from ...generation.utils import GenerateNonBeamOutput
from ...utils import logging
if TYPE_CHECKING:
    from ...generation.streamers import BaseStreamer
logger = logging.get_logger(__name__)
@dataclass
class CsmGenerateOutput(GenerateDecoderOnlyOutput):
    audio: Optional[list[torch.Tensor]] = None
class CsmGenerationMixin(GenerationMixin):
    def _get_stopping_criteria(
        self,
        *args,
        **kwargs,
    ) -> StoppingCriteriaList:
        criteria = super()._get_stopping_criteria(*args, **kwargs)
        kept_criteria = StoppingCriteriaList()
        for criterion in criteria:
            if not isinstance(criterion, MaxLengthCriteria):
                logger.warning(
                    f"Csm does not support {criterion.__class__.__name__} stopping criteria, it will be ignored."
                )
            else:
                kept_criteria.append(criterion)
        return kept_criteria
    def _prepare_generation_config(
        self, generation_config: Optional[GenerationConfig], use_model_defaults: Optional[bool] = None, **kwargs: Any
    ) -> tuple[GenerationConfig, dict]:
        depth_decoder_kwargs = {
            k[len("depth_decoder_") :]: v for k, v in kwargs.items() if k.startswith("depth_decoder_")
        }
        kwargs = {k: v for k, v in kwargs.items() if not k.startswith("depth_decoder_")}
        generation_config, model_kwargs = super()._prepare_generation_config(
            generation_config, use_model_defaults, **kwargs
        )
        self.depth_decoder.generation_config.update(**depth_decoder_kwargs)
        depth_decoder_min_new_tokens = getattr(self.depth_decoder.generation_config, "min_new_tokens") or (
            self.config.num_codebooks - 1
        )
        depth_decoder_max_new_tokens = getattr(self.depth_decoder.generation_config, "max_new_tokens") or (
            self.config.num_codebooks - 1
        )
        if {depth_decoder_min_new_tokens, depth_decoder_max_new_tokens} != {self.config.num_codebooks - 1}:
            raise ValueError(
                f"depth_decoder_generation_config's min_new_tokens ({depth_decoder_min_new_tokens}) and max_new_tokens ({depth_decoder_max_new_tokens}) must be equal to self.config.num_codebooks - 1 ({self.config.num_codebooks - 1})"
            )
        elif self.depth_decoder.generation_config.return_dict_in_generate:
            logger.warning(
                "depth_decoder_generation_config.return_dict_in_generate is set to True, but this will be ignored as the depth decoder model does not return a dictionary in generate"
            )
            self.depth_decoder.generation_config.return_dict_in_generate = False
        self.depth_decoder.generation_config.min_new_tokens = depth_decoder_min_new_tokens
        self.depth_decoder.generation_config.max_new_tokens = depth_decoder_max_new_tokens
        original_get_generation_mode = generation_config.get_generation_mode
        def patched_get_generation_mode(assistant_model=None):
            generation_mode = original_get_generation_mode(assistant_model)
            if generation_mode not in [GenerationMode.GREEDY_SEARCH, GenerationMode.SAMPLE]:
                raise ValueError(
                    f"Generation mode {generation_mode} is not supported for CSM model. Please set generation parameters to use greedy or sampling generation."
                )
            return generation_mode
        generation_config.get_generation_mode = patched_get_generation_mode
        return generation_config, model_kwargs
    def _sample(
        self,
        input_ids: torch.LongTensor,
        logits_processor: LogitsProcessorList,
        stopping_criteria: StoppingCriteriaList,
        generation_config: GenerationConfig,
        synced_gpus: bool = False,
        streamer: Optional["BaseStreamer"] = None,
        **model_kwargs,
    ) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        pad_token_id = self.config.codebook_pad_token_id
        has_eos_stopping_criteria = generation_config._eos_token_tensor is not None
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        do_sample = generation_config.do_sample
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        batch_size, cur_len = input_ids.shape[:2]
        this_peer_finished = False
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(cur_len, input_ids.device, model_kwargs)
        if input_ids.ndim == 2 and model_kwargs.get("inputs_embeds") is None:
            for criterion in stopping_criteria:
                if isinstance(criterion, MaxLengthCriteria):
                    criterion.max_length -= cur_len
        model_forward = self.__call__
        compile_forward = self._valid_auto_compile_criteria(model_kwargs, generation_config)
        if compile_forward:
            os.environ["TOKENIZERS_PARALLELISM"] = "0"
            model_forward = self.get_compiled_call(generation_config.compile_config)
        is_prefill = True
        while self._has_unfinished_sequences(
            this_peer_finished,
            synced_gpus,
            device=input_ids.device,
        ):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            model_inputs.update({"output_attentions": output_attentions} if output_attentions else {})
            model_inputs.update({"output_hidden_states": True})
            if is_prefill:
                outputs = self(**model_inputs, return_dict=True)
                is_prefill = False
            else:
                outputs = model_forward(**model_inputs, return_dict=True)
            model_kwargs = self._update_model_kwargs_for_generation(
                outputs,
                model_kwargs,
            )
            if synced_gpus and this_peer_finished:
                continue
            next_token_logits = outputs.logits[:, -1, :].clone().float()
            next_token_logits = next_token_logits.to(input_ids.device)
            next_token_scores = logits_processor(input_ids, next_token_logits)
            if return_dict_in_generate:
                if output_scores:
                    scores += (next_token_scores,)
                if output_logits:
                    raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += (outputs.attentions,)
                if output_hidden_states:
                    decoder_hidden_states += (outputs.hidden_states,)
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
            else:
                next_tokens = torch.argmax(next_token_scores, dim=-1)
            first_codebook_ids = next_tokens[:, None]
            depth_decoder_input_ids = nn.functional.pad(first_codebook_ids, (1, 0), value=0)
            backbone_last_hidden_state = outputs.hidden_states[-1][:, -1, :]
            depth_decoder_outputs = self.depth_decoder.generate(
                input_ids=depth_decoder_input_ids, backbone_last_hidden_state=backbone_last_hidden_state.clone()
            )
            codebook_ids = (
                depth_decoder_outputs
                if isinstance(depth_decoder_outputs, torch.Tensor)
                else depth_decoder_outputs.sequences
            )
            codebook_ids = codebook_ids[:, 1:]
            next_tokens = codebook_ids
            if has_eos_stopping_criteria:
                next_tokens = next_tokens * unfinished_sequences.unsqueeze(-1) + pad_token_id * (
                    1 - unfinished_sequences.unsqueeze(-1)
                )
            if input_ids.ndim == 2:
                input_ids = next_tokens[:, None, :]
            else:
                input_ids = torch.cat([input_ids, next_tokens[:, None, :]], dim=1)
            if streamer is not None:
                streamer.put(next_tokens.cpu())
            unfinished_sequences = unfinished_sequences & ~(
                input_ids[:, -1, :-1] == self.config.codebook_eos_token_id
            ).all(-1)
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
            cur_len += 1
            del outputs
            del depth_decoder_outputs
        if streamer is not None:
            streamer.end()
        if return_dict_in_generate:
            return GenerateDecoderOnlyOutput(
                sequences=input_ids,
                scores=scores,
                logits=raw_logits,
                attentions=decoder_attentions,
                hidden_states=decoder_hidden_states,
                past_key_values=model_kwargs.get("past_key_values"),
            )
        else:
            return input_ids
    def generate(
        self,
        input_ids: Optional[torch.Tensor] = None,
        input_values: Optional[torch.Tensor] = None,
        input_values_cutoffs: Optional[torch.Tensor] = None,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        synced_gpus: Optional[bool] = None,
        streamer: Optional["BaseStreamer"] = None,
        output_audio: Optional[bool] = False,
        **kwargs,
    ) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        generate_output = super().generate(
            input_ids=input_ids,
            input_values=input_values,
            input_values_cutoffs=input_values_cutoffs,
            generation_config=generation_config,
            logits_processor=logits_processor,
            stopping_criteria=stopping_criteria,
            synced_gpus=synced_gpus,
            streamer=streamer,
            **kwargs,
        )
        generate_returned_dict = not isinstance(generate_output, torch.Tensor)
        audio = None
        if output_audio:
            generated_audio_codes = generate_output.sequences if generate_returned_dict else generate_output
            audio = []
            with torch.no_grad():
                for audio_codes_batch in generated_audio_codes:
                    eos_idxs = (audio_codes_batch == self.config.codebook_eos_token_id).all(dim=-1).nonzero()
                    if eos_idxs.numel() != 0:
                        cutoff_idx = eos_idxs.min()
                    else:
                        cutoff_idx = audio_codes_batch.shape[0]
                    audio_codes_batch = audio_codes_batch[:cutoff_idx]
                    codec_decode_output = self.codec_model.decode(audio_codes_batch.transpose(0, 1).unsqueeze(0))
                    audio.append(codec_decode_output.audio_values[0, 0])
        if generate_returned_dict:
            return CsmGenerateOutput(audio=audio, **generate_output)
        elif output_audio:
            return audio
        else:
            return generate_output