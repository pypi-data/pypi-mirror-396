import copy
import inspect
import os
import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional, Union
import torch
import torch.distributed as dist
from packaging import version
from torch import nn
from ..cache_utils import (
    Cache,
    DynamicCache,
    EncoderDecoderCache,
    QuantizedCache,
    StaticCache,
)
from ..dynamic_module_utils import (
    check_python_requirements,
    get_cached_module_file,
    get_class_in_module,
    resolve_trust_remote_code,
)
from ..integrations.deepspeed import is_deepspeed_zero3_enabled
from ..integrations.fsdp import is_fsdp_managed_module
from ..masking_utils import create_masks_for_generate
from ..pytorch_utils import isin_mps_friendly
from ..tokenization_utils import ExtensionsTrie
from ..utils import (
    ModelOutput,
    MEROAIKwargs,
    is_accelerate_available,
    is_hqq_available,
    is_optimum_quanto_available,
    is_torchdynamo_exporting,
    logging,
)
from .candidate_generator import (
    AssistantVocabTranslatorCache,
    AssistedCandidateGenerator,
    AssistedCandidateGeneratorDifferentTokenizers,
    CandidateGenerator,
    EarlyExitCandidateGenerator,
    PromptLookupCandidateGenerator,
    UniversalSpeculativeDecodingGenerator,
    _prepare_attention_mask,
    _prepare_token_type_ids,
)
from .configuration_utils import (
    ALL_STATIC_CACHE_IMPLEMENTATIONS,
    DEPRECATED_STATIC_CACHE_IMPLEMENTATIONS,
    STATIC_CACHE_IMPLEMENTATIONS,
    GenerationConfig,
    GenerationMode,
)
from .continuous_batching import ContinuousMixin
from .logits_process import (
    EncoderNoRepeatNGramLogitsProcessor,
    EncoderRepetitionPenaltyLogitsProcessor,
    EpsilonLogitsWarper,
    EtaLogitsWarper,
    ExponentialDecayLengthPenalty,
    ForcedBOSTokenLogitsProcessor,
    ForcedEOSTokenLogitsProcessor,
    InfNanRemoveLogitsProcessor,
    LogitNormalization,
    LogitsProcessorList,
    MinLengthLogitsProcessor,
    MinNewTokensLengthLogitsProcessor,
    MinPLogitsWarper,
    NoBadWordsLogitsProcessor,
    NoRepeatNGramLogitsProcessor,
    PrefixConstrainedLogitsProcessor,
    RepetitionPenaltyLogitsProcessor,
    SequenceBiasLogitsProcessor,
    SuppressTokensAtBeginLogitsProcessor,
    SuppressTokensLogitsProcessor,
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
    TypicalLogitsWarper,
    UnbatchedClassifierFreeGuidanceLogitsProcessor,
)
from .stopping_criteria import (
    ConfidenceCriteria,
    EosTokenCriteria,
    MaxLengthCriteria,
    MaxTimeCriteria,
    StoppingCriteria,
    StoppingCriteriaList,
    StopStringCriteria,
)
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
    from ..tokenization_utils_base import PreTrainedTokenizerBase
    from .streamers import BaseStreamer
logger = logging.get_logger(__name__)
if is_accelerate_available():
    from accelerate.hooks import AlignDevicesHook, add_hook_to_module
ALL_CACHE_NAMES = [
    "past_key_values",
    "cache_params",
    "state",
    "mems",
    "past_buckets_states",
]
GENERATION_MODES_MAPPING = {
    GenerationMode.SAMPLE: "_sample",
    GenerationMode.GREEDY_SEARCH: "_sample",
    GenerationMode.BEAM_SEARCH: "_beam_search",
    GenerationMode.BEAM_SAMPLE: "_beam_search",
    GenerationMode.ASSISTED_GENERATION: "_assisted_decoding",
    GenerationMode.DOLA_GENERATION: "MEROAI-community/dola",
    GenerationMode.CONTRASTIVE_SEARCH: "MEROAI-community/contrastive-search",
    GenerationMode.GROUP_BEAM_SEARCH: "MEROAI-community/group-beam-search",
    GenerationMode.CONSTRAINED_BEAM_SEARCH: "MEROAI-community/constrained-beam-search",
}
@dataclass
class GenerateDecoderOnlyOutput(ModelOutput):
    sequences: torch.LongTensor
    scores: Optional[tuple[torch.FloatTensor]] = None
    logits: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[tuple[tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Cache] = None
@dataclass
class GenerateEncoderDecoderOutput(ModelOutput):
    sequences: torch.LongTensor
    scores: Optional[tuple[torch.FloatTensor]] = None
    logits: Optional[tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    cross_attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    decoder_hidden_states: Optional[tuple[tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Cache] = None
@dataclass
class GenerateBeamDecoderOnlyOutput(ModelOutput):
    sequences: torch.LongTensor
    sequences_scores: Optional[torch.FloatTensor] = None
    scores: Optional[tuple[torch.FloatTensor]] = None
    logits: Optional[tuple[torch.FloatTensor]] = None
    beam_indices: Optional[torch.LongTensor] = None
    attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    hidden_states: Optional[tuple[tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Cache] = None
@dataclass
class GenerateBeamEncoderDecoderOutput(ModelOutput):
    sequences: torch.LongTensor
    sequences_scores: Optional[torch.FloatTensor] = None
    scores: Optional[tuple[torch.FloatTensor]] = None
    logits: Optional[tuple[torch.FloatTensor]] = None
    beam_indices: Optional[torch.LongTensor] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    cross_attentions: Optional[tuple[tuple[torch.FloatTensor]]] = None
    decoder_hidden_states: Optional[tuple[tuple[torch.FloatTensor]]] = None
    past_key_values: Optional[Cache] = None
GreedySearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
ContrastiveSearchDecoderOnlyOutput = GenerateDecoderOnlyOutput
SampleDecoderOnlyOutput = GenerateDecoderOnlyOutput
ContrastiveSearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
GreedySearchEncoderDecoderOutput = GenerateEncoderDecoderOutput
SampleEncoderDecoderOutput = GenerateEncoderDecoderOutput
BeamSearchDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput
BeamSampleDecoderOnlyOutput = GenerateBeamDecoderOnlyOutput
BeamSearchEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput
BeamSampleEncoderDecoderOutput = GenerateBeamEncoderDecoderOutput
GreedySearchOutput = Union[GreedySearchEncoderDecoderOutput, GreedySearchDecoderOnlyOutput]
SampleOutput = Union[SampleEncoderDecoderOutput, SampleDecoderOnlyOutput]
BeamSearchOutput = Union[BeamSearchEncoderDecoderOutput, BeamSearchDecoderOnlyOutput]
BeamSampleOutput = Union[BeamSampleEncoderDecoderOutput, BeamSampleDecoderOnlyOutput]
ContrastiveSearchOutput = Union[ContrastiveSearchEncoderDecoderOutput, ContrastiveSearchDecoderOnlyOutput]
GenerateNonBeamOutput = Union[GenerateDecoderOnlyOutput, GenerateEncoderDecoderOutput]
GenerateBeamOutput = Union[GenerateBeamDecoderOnlyOutput, GenerateBeamEncoderDecoderOutput]
GenerateOutput = Union[GenerateNonBeamOutput, GenerateBeamOutput]
class GenerationMixin(ContinuousMixin):
    def load_custom_generate(
        self,
        pretrained_model_name_or_path: Optional[Union[str, os.PathLike]] = None,
        trust_remote_code: Optional[bool] = None,
        **kwargs,
    ) -> Callable:
        try:
            module = get_cached_module_file(
                pretrained_model_name_or_path, module_file="custom_generate/generate.py", **kwargs
            )
        except OSError:
            raise OSError(
                f"`{pretrained_model_name_or_path}` does not contain a `custom_generate` subdirectory with a "
                "`generate.py` file, can't load the custom generate function."
            )
        is_local_code = os.path.exists(pretrained_model_name_or_path)
        error_message = (
            f"The repository `{pretrained_model_name_or_path}` contains custom generation code that will override "
            "the default `generate` method."
        )
        resolve_trust_remote_code(
            trust_remote_code,
            pretrained_model_name_or_path,
            has_local_code=is_local_code,
            has_remote_code=not is_local_code,
            error_message=error_message,
        )
        check_python_requirements(
            pretrained_model_name_or_path, requirements_file="custom_generate/requirements.txt", **kwargs
        )
        custom_generate_function = get_class_in_module("generate", module)
        return custom_generate_function
    def _cache_dependant_input_preparation(
        self,
        input_ids: torch.LongTensor,
        inputs_embeds: Optional[torch.FloatTensor],
        cache_position: Optional[torch.LongTensor],
    ) -> tuple[torch.FloatTensor, torch.LongTensor]:
        if is_torchdynamo_exporting():
            return self._cache_dependant_input_preparation_exporting(input_ids, inputs_embeds, cache_position)
        if inputs_embeds is not None and input_ids.shape[1] == 0:
            inputs_embeds = inputs_embeds[:, -cache_position.shape[0] :]
        elif (
            inputs_embeds is not None
            or (cache_position[-1] >= input_ids.shape[1])
        ):
            input_ids = input_ids[:, -cache_position.shape[0] :]
        elif input_ids.shape[1] != cache_position.shape[0]:
            input_ids = input_ids[:, cache_position]
        return inputs_embeds, input_ids
    def _cache_dependant_input_preparation_exporting(
        self,
        input_ids: torch.LongTensor,
        inputs_embeds: Optional[torch.FloatTensor],
        cache_position: Optional[torch.LongTensor],
    ) -> tuple[torch.FloatTensor, torch.LongTensor]:
        if inputs_embeds is None:
            input_ids = input_ids[:, cache_position]
        else:
            def branch_1(inputs_embeds, cache_position):
                return inputs_embeds[:, -cache_position.shape[0] :].clone()
            def branch_2(input_ids, cache_position):
                return input_ids[:, -cache_position.shape[0] :].clone()
            def branch_3(input_ids, cache_position):
                return input_ids[:, cache_position].clone()
            inputs_embeds, input_ids = torch.cond(
                input_ids.shape[1] == 0,
                (
                    lambda input_ids, inputs_embeds, cache_position: (
                        branch_1(inputs_embeds, cache_position),
                        input_ids.clone(),
                    )
                ),
                (
                    lambda input_ids, inputs_embeds, cache_position: (
                        inputs_embeds,
                        torch.cond(
                            cache_position[-1] >= input_ids.shape[1],
                            branch_2,
                            lambda input_ids, cache_position: (
                                torch.cond(
                                    input_ids.shape[1] != cache_position.shape[0],
                                    branch_3,
                                    (lambda input_ids, cache_position: input_ids.clone()),
                                    [input_ids, cache_position],
                                )
                            ),
                            [input_ids, cache_position],
                        ),
                    )
                ),
                [input_ids, inputs_embeds, cache_position],
            )
        return inputs_embeds, input_ids
    def prepare_inputs_for_generation(
        self,
        input_ids: torch.LongTensor,
        past_key_values: Optional[Cache] = None,
        attention_mask: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs,
    ):
        model_inputs = {}
        model_inputs["cache_position"] = cache_position
        if past_key_values is not None:
            model_inputs["past_key_values"] = past_key_values
            inputs_embeds, input_ids = self._cache_dependant_input_preparation(
                input_ids, inputs_embeds, cache_position
            )
        input_ids_key = "decoder_input_ids" if self.config.is_encoder_decoder else "input_ids"
        if not self.config.is_encoder_decoder:
            if inputs_embeds is not None and len(cache_position) == inputs_embeds.shape[1]:
                model_inputs[input_ids_key] = None
                model_inputs["inputs_embeds"] = inputs_embeds
            else:
                model_inputs[input_ids_key] = input_ids.clone(memory_format=torch.contiguous_format)
                model_inputs["inputs_embeds"] = None
        else:
            model_inputs[input_ids_key] = input_ids.clone(memory_format=torch.contiguous_format)
        encoder_attention_mask = attention_mask if self.config.is_encoder_decoder else None
        attention_mask = (
            kwargs.pop("decoder_attention_mask", None) if self.config.is_encoder_decoder else attention_mask
        )
        attention_mask_key = "decoder_attention_mask" if self.config.is_encoder_decoder else "attention_mask"
        position_ids_key = "decoder_position_ids" if self.config.is_encoder_decoder else "position_ids"
        if (
            attention_mask is not None
            and kwargs.get(position_ids_key) is None
            and position_ids_key in set(inspect.signature(self.forward).parameters.keys())
        ):
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            kwargs[position_ids_key] = position_ids
        for model_input_name in ["position_ids", "token_type_ids", "decoder_position_ids"]:
            model_input = kwargs.get(model_input_name)
            if model_input is not None:
                if past_key_values is not None:
                    current_input_length = (
                        model_inputs["inputs_embeds"].shape[1]
                        if model_inputs.get("inputs_embeds") is not None
                        else model_inputs[input_ids_key].shape[1]
                    )
                    model_input = model_input[:, -current_input_length:]
                    model_input = model_input.clone(memory_format=torch.contiguous_format)
                model_inputs[model_input_name] = model_input
        if (
            isinstance(past_key_values, Cache)
            and past_key_values.is_compileable
            and attention_mask is not None
            and attention_mask.ndim == 2
        ):
            if not self.config.is_encoder_decoder and model_inputs["inputs_embeds"] is not None:
                batch_size, sequence_length, _ = model_inputs["inputs_embeds"].shape
            else:
                batch_size, sequence_length = model_inputs[input_ids_key].shape[:2]
            base_model = getattr(self, self.base_model_prefix, self)
            decoder = base_model.get_decoder() if hasattr(base_model, "get_decoder") else None
            causal_mask_creation_function = getattr(
                base_model, "_prepare_4d_causal_attention_mask_with_cache_position", None
            )
            if causal_mask_creation_function is None and decoder is not None:
                causal_mask_creation_function = getattr(
                    decoder, "_prepare_4d_causal_attention_mask_with_cache_position", None
                )
            if causal_mask_creation_function is None:
                token_type_ids = model_inputs.get("token_type_ids")
                position_ids = model_inputs.get(position_ids_key)
                causal_mask_creation_function = getattr(self, "create_masks_for_generate", create_masks_for_generate)
                attention_mask = causal_mask_creation_function(
                    config=self.config,
                    input_embeds=torch.empty((batch_size, sequence_length), dtype=self.dtype),
                    attention_mask=attention_mask,
                    cache_position=cache_position,
                    past_key_values=past_key_values,
                    position_ids=position_ids,
                    token_type_ids=token_type_ids,
                )
            else:
                attention_mask = causal_mask_creation_function(
                    attention_mask,
                    sequence_length=sequence_length,
                    target_length=past_key_values.get_max_cache_shape(),
                    dtype=self.dtype,
                    cache_position=cache_position,
                    batch_size=batch_size,
                    config=self.config,
                    past_key_values=past_key_values,
                )
        if attention_mask is not None:
            model_inputs[attention_mask_key] = attention_mask
        if encoder_attention_mask is not None:
            model_inputs["attention_mask"] = encoder_attention_mask
        for key, value in kwargs.items():
            if key not in model_inputs:
                model_inputs[key] = value
        model_inputs.pop("labels", None)
        return model_inputs
    def _prepare_model_inputs(
        self,
        inputs: Optional[torch.Tensor] = None,
        bos_token_id: Optional[torch.Tensor] = None,
        model_kwargs: Optional[dict[str, torch.Tensor]] = None,
    ) -> tuple[torch.Tensor, Optional[str], dict[str, torch.Tensor]]:
        if (
            self.config.is_encoder_decoder
            and hasattr(self, "encoder")
            and self.encoder.main_input_name != self.main_input_name
        ):
            input_name = self.encoder.main_input_name
        else:
            input_name = self.main_input_name
        model_kwargs = {k: v for k, v in model_kwargs.items() if v is not None or k != input_name}
        inputs_kwarg = model_kwargs.pop(input_name, None)
        if inputs_kwarg is not None and inputs is not None:
            raise ValueError(
                f"`inputs`: {inputs}` were passed alongside {input_name} which is not allowed. "
                f"Make sure to either pass {inputs} or {input_name}=..."
            )
        elif inputs_kwarg is not None:
            inputs = inputs_kwarg
        if input_name == "input_ids" and "inputs_embeds" in model_kwargs:
            if model_kwargs["inputs_embeds"] is None:
                model_kwargs.pop("inputs_embeds")
            elif not self.config.is_encoder_decoder:
                has_inputs_embeds_forwarding = "inputs_embeds" in set(
                    inspect.signature(self.prepare_inputs_for_generation).parameters.keys()
                )
                if not has_inputs_embeds_forwarding:
                    raise ValueError(
                        f"You passed `inputs_embeds` to `.generate()`, but the model class {self.__class__.__name__} "
                        "doesn't have its forwarding implemented. See the GPT2 implementation for an example "
                        "(https://github.com/huggingface/MEROAI/pull/21405), and feel free to open a PR with it!"
                    )
                model_kwargs["input_ids"] = self._maybe_initialize_input_ids_for_generation(
                    inputs, bos_token_id, model_kwargs=model_kwargs
                )
                inputs, input_name = model_kwargs["inputs_embeds"], "inputs_embeds"
            else:
                if inputs is not None:
                    raise ValueError("You passed `inputs_embeds` and `input_ids` to `.generate()`. Please pick one.")
                inputs, input_name = model_kwargs["inputs_embeds"], "inputs_embeds"
        inputs = self._maybe_initialize_input_ids_for_generation(inputs, bos_token_id, model_kwargs)
        return inputs, input_name, model_kwargs
    def _maybe_initialize_input_ids_for_generation(
        self,
        inputs: Optional[torch.Tensor] = None,
        bos_token_id: Optional[torch.Tensor] = None,
        model_kwargs: Optional[dict[str, torch.Tensor]] = None,
    ) -> torch.LongTensor:
        if inputs is not None:
            return inputs
        encoder_outputs = model_kwargs.get("encoder_outputs")
        if self.config.is_encoder_decoder and encoder_outputs is not None:
            shape = encoder_outputs.last_hidden_state.size()[:-1]
            return torch.ones(shape, dtype=torch.long, device=self.device) * -100
        batch_size = 1
        for value in model_kwargs.values():
            if isinstance(value, torch.Tensor):
                batch_size = value.shape[0]
                break
        if "inputs_embeds" in model_kwargs:
            return torch.ones((batch_size, 0), dtype=torch.long, device=self.device)
        if bos_token_id is None:
            raise ValueError("`bos_token_id` has to be defined when no `input_ids` are provided.")
        return torch.ones((batch_size, 1), dtype=torch.long, device=self.device) * bos_token_id
    def _prepare_attention_mask_for_generation(
        self,
        inputs_tensor: torch.Tensor,
        generation_config: GenerationConfig,
        model_kwargs: dict[str, Any],
    ) -> torch.LongTensor:
        pad_token_id = generation_config._pad_token_tensor
        eos_token_id = generation_config._eos_token_tensor
        if "input_ids" in model_kwargs and model_kwargs["input_ids"].shape[1] > 0:
            inputs_tensor = model_kwargs["input_ids"]
        default_attention_mask = torch.ones(inputs_tensor.shape[:2], dtype=torch.long, device=inputs_tensor.device)
        if pad_token_id is None:
            return default_attention_mask
        is_input_ids = len(inputs_tensor.shape) == 2 and inputs_tensor.dtype in [torch.int, torch.long]
        if not is_input_ids:
            return default_attention_mask
        is_pad_token_in_inputs = (pad_token_id is not None) and (
            isin_mps_friendly(elements=inputs_tensor, test_elements=pad_token_id).any()
        )
        is_pad_token_not_equal_to_eos_token_id = (eos_token_id is None) or ~(
            isin_mps_friendly(elements=eos_token_id, test_elements=pad_token_id).any()
        )
        can_infer_attention_mask = is_pad_token_in_inputs * is_pad_token_not_equal_to_eos_token_id
        attention_mask_from_padding = inputs_tensor.ne(pad_token_id).long()
        attention_mask = (
            attention_mask_from_padding * can_infer_attention_mask + default_attention_mask * ~can_infer_attention_mask
        )
        return attention_mask
    def _prepare_encoder_decoder_kwargs_for_generation(
        self,
        inputs_tensor: torch.Tensor,
        model_kwargs,
        model_input_name: Optional[str],
        generation_config: GenerationConfig,
    ) -> dict[str, Any]:
        encoder = self.get_encoder()
        if hasattr(self, "hf_device_map"):
            if hasattr(encoder, "_hf_hook"):
                encoder._hf_hook.io_same_device = True
            else:
                add_hook_to_module(encoder, AlignDevicesHook(io_same_device=True))
        irrelevant_prefix = ["decoder_", "cross_attn", "use_cache"]
        encoder_kwargs = {
            argument: value
            for argument, value in model_kwargs.items()
            if not any(argument.startswith(p) for p in irrelevant_prefix)
        }
        encoder_signature = set(inspect.signature(encoder.forward).parameters)
        encoder_accepts_wildcard = "kwargs" in encoder_signature or "model_kwargs" in encoder_signature
        if not encoder_accepts_wildcard:
            encoder_kwargs = {
                argument: value for argument, value in encoder_kwargs.items() if argument in encoder_signature
            }
        encoder_kwargs["output_attentions"] = generation_config.output_attentions
        encoder_kwargs["output_hidden_states"] = generation_config.output_hidden_states
        model_input_name = model_input_name if model_input_name is not None else self.main_input_name
        encoder_kwargs["return_dict"] = True
        encoder_kwargs[model_input_name] = inputs_tensor
        model_kwargs["encoder_outputs"]: ModelOutput = encoder(**encoder_kwargs)
        return model_kwargs
    def _prepare_decoder_input_ids_for_generation(
        self,
        batch_size: int,
        model_input_name: str,
        model_kwargs: dict[str, torch.Tensor],
        decoder_start_token_id: torch.Tensor,
        device: Optional[torch.device] = None,
    ) -> tuple[torch.LongTensor, dict[str, torch.Tensor]]:
        if model_kwargs is not None and "decoder_input_ids" in model_kwargs:
            decoder_input_ids = model_kwargs.pop("decoder_input_ids")
        elif "input_ids" in model_kwargs and model_input_name != "input_ids":
            decoder_input_ids = model_kwargs.pop("input_ids")
        else:
            decoder_input_ids = None
        if device is None:
            device = self.device
        if decoder_start_token_id.ndim == 1:
            if decoder_start_token_id.shape[0] != batch_size:
                raise ValueError(
                    f"`decoder_start_token_id` expected to have length {batch_size} but got {decoder_start_token_id.shape[0]}"
                )
            decoder_start_token_id = decoder_start_token_id.view(-1, 1)
        else:
            decoder_start_token_id = (
                torch.ones((batch_size, 1), dtype=torch.long, device=device) * decoder_start_token_id
            )
        if decoder_input_ids is None:
            decoder_input_ids = decoder_start_token_id
        elif "donut" in self.__class__.__name__.lower() or (
            self.config.model_type == "vision-encoder-decoder" and "donut" in self.config.encoder.model_type.lower()
        ):
            pass
        elif self.config.model_type == "whisper":
            pass
        elif (decoder_input_ids[:, 0] != decoder_start_token_id[:, 0]).all().item():
            decoder_input_ids = torch.cat([decoder_start_token_id, decoder_input_ids], dim=-1)
            if "decoder_attention_mask" in model_kwargs:
                decoder_attention_mask = model_kwargs["decoder_attention_mask"]
                decoder_attention_mask = torch.cat(
                    (torch.ones_like(decoder_attention_mask)[:, :1], decoder_attention_mask),
                    dim=-1,
                )
                model_kwargs["decoder_attention_mask"] = decoder_attention_mask
        return decoder_input_ids, model_kwargs
    @staticmethod
    def _expand_inputs_for_generation(
        expand_size: int = 1,
        is_encoder_decoder: bool = False,
        input_ids: Optional[torch.LongTensor] = None,
        **model_kwargs,
    ) -> tuple[torch.LongTensor, dict[str, Any]]:
        if expand_size == 1:
            return input_ids, model_kwargs
        def _expand_dict_for_generation(dict_to_expand):
            for key in dict_to_expand:
                if (
                    key != "cache_position"
                    and dict_to_expand[key] is not None
                    and isinstance(dict_to_expand[key], torch.Tensor)
                ):
                    dict_to_expand[key] = dict_to_expand[key].repeat_interleave(expand_size, dim=0)
            return dict_to_expand
        if input_ids is not None:
            input_ids = input_ids.repeat_interleave(expand_size, dim=0)
        model_kwargs = _expand_dict_for_generation(model_kwargs)
        if is_encoder_decoder:
            if model_kwargs.get("encoder_outputs") is None:
                raise ValueError("If `is_encoder_decoder` is True, make sure that `encoder_outputs` is defined.")
            model_kwargs["encoder_outputs"] = _expand_dict_for_generation(model_kwargs["encoder_outputs"])
        return input_ids, model_kwargs
    def _update_model_kwargs_for_generation(
        self,
        outputs: ModelOutput,
        model_kwargs: dict[str, Any],
        is_encoder_decoder: bool = False,
        num_new_tokens: int = 1,
    ) -> dict[str, Any]:
        for possible_cache_name in ALL_CACHE_NAMES:
            if possible_cache_name in outputs:
                if possible_cache_name in ("past_buckets_states", "mems"):
                    cache_name = "past_key_values"
                else:
                    cache_name = possible_cache_name
                model_kwargs[cache_name] = getattr(outputs, possible_cache_name)
                break
        if "token_type_ids" in model_kwargs:
            token_type_ids = model_kwargs["token_type_ids"]
            model_kwargs["token_type_ids"] = torch.cat([token_type_ids, token_type_ids[:, -1].unsqueeze(-1)], dim=-1)
        if not is_encoder_decoder:
            if "attention_mask" in model_kwargs:
                attention_mask = model_kwargs["attention_mask"]
                model_kwargs["attention_mask"] = torch.cat(
                    [attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1
                )
        else:
            if "decoder_attention_mask" in model_kwargs:
                decoder_attention_mask = model_kwargs["decoder_attention_mask"]
                model_kwargs["decoder_attention_mask"] = torch.cat(
                    [decoder_attention_mask, decoder_attention_mask.new_ones((decoder_attention_mask.shape[0], 1))],
                    dim=-1,
                )
        if model_kwargs.get("use_cache", True):
            model_kwargs["cache_position"] = model_kwargs["cache_position"][-1:] + num_new_tokens
        else:
            past_positions = model_kwargs.pop("cache_position")
            new_positions = torch.arange(
                past_positions[-1] + 1, past_positions[-1] + num_new_tokens + 1, dtype=past_positions.dtype
            ).to(past_positions.device)
            model_kwargs["cache_position"] = torch.cat((past_positions, new_positions))
        return model_kwargs
    def _get_candidate_generator(
        self,
        generation_config: GenerationConfig,
        input_ids: torch.LongTensor,
        inputs_tensor: torch.Tensor,
        logits_processor: LogitsProcessorList,
        model_kwargs: dict[str, Any],
        assistant_model: Optional["PreTrainedModel"] = None,
        target_tokenizer: Optional["PreTrainedTokenizerBase"] = None,
        assistant_tokenizer: Optional["PreTrainedTokenizerBase"] = None,
    ) -> CandidateGenerator:
        different_tokenizers = all(v is not None for v in (assistant_model, target_tokenizer, assistant_tokenizer))
        if generation_config.assistant_early_exit is not None:
            candidate_generator = EarlyExitCandidateGenerator(
                input_ids=input_ids,
                assistant_model=self,
                generation_config=generation_config,
                model_kwargs=model_kwargs,
                inputs_tensor=inputs_tensor,
                logits_processor=logits_processor,
            )
        elif generation_config.prompt_lookup_num_tokens is not None:
            candidate_generator = PromptLookupCandidateGenerator(
                eos_token_id=generation_config._eos_token_tensor,
                num_output_tokens=generation_config.prompt_lookup_num_tokens,
                max_matching_ngram_size=generation_config.max_matching_ngram_size or 2,
                max_length=generation_config.max_length,
                logits_processor=logits_processor,
                vocab_size=self.config.get_text_config().vocab_size,
            )
        elif different_tokenizers:
            if generation_config.do_sample is True:
                atm_translator = AssistantVocabTranslatorCache.get_translator(
                    target_tokenizer,
                    assistant_tokenizer,
                    self.config.get_text_config().vocab_size,
                    assistant_model=assistant_model,
                    assistant_prune_lm_head=True,
                )
                assistant_model.generation_config.repetition_penalty = None
                candidate_generator = UniversalSpeculativeDecodingGenerator(
                    input_ids=input_ids,
                    assistant_model=assistant_model,
                    generation_config=generation_config,
                    model_kwargs=model_kwargs,
                    inputs_tensor=inputs_tensor,
                    logits_processor=logits_processor,
                    target_tokenizer=target_tokenizer,
                    assistant_tokenizer=assistant_tokenizer,
                    atm_translator=atm_translator,
                )
            elif generation_config.do_sample is False:
                candidate_generator = AssistedCandidateGeneratorDifferentTokenizers(
                    input_ids=input_ids,
                    assistant_model=assistant_model,
                    generation_config=generation_config,
                    model_kwargs=model_kwargs,
                    inputs_tensor=inputs_tensor,
                    logits_processor=logits_processor,
                    target_tokenizer=target_tokenizer,
                    assistant_tokenizer=assistant_tokenizer,
                )
            else:
                raise ValueError(
                    f"Invalid value for `do_sample`: expected a boolean, got {type(generation_config.do_sample).__name__}"
                )
        else:
            candidate_generator = AssistedCandidateGenerator(
                input_ids=input_ids,
                assistant_model=assistant_model,
                generation_config=generation_config,
                model_kwargs=model_kwargs,
                inputs_tensor=inputs_tensor,
                logits_processor=logits_processor,
            )
        return candidate_generator
    def _get_logits_processor(
        self,
        generation_config: GenerationConfig,
        input_ids_seq_length: Optional[int] = None,
        encoder_input_ids: Optional[torch.LongTensor] = None,
        prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], list[int]]] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        device: Optional[str] = None,
        model_kwargs: Optional[dict[str, Any]] = None,
        negative_prompt_ids: Optional[torch.Tensor] = None,
        negative_prompt_attention_mask: Optional[torch.Tensor] = None,
    ) -> LogitsProcessorList:
        processors = LogitsProcessorList()
        if logits_processor is None:
            logits_processor = []
        if generation_config.guidance_scale is not None and generation_config.guidance_scale != 1:
            processors.append(
                UnbatchedClassifierFreeGuidanceLogitsProcessor(
                    generation_config.guidance_scale,
                    self,
                    unconditional_ids=negative_prompt_ids,
                    unconditional_attention_mask=negative_prompt_attention_mask,
                    use_cache=generation_config.use_cache,
                )
            )
        if generation_config.sequence_bias is not None:
            processors.append(SequenceBiasLogitsProcessor(sequence_bias=generation_config.sequence_bias))
        if (
            generation_config.encoder_repetition_penalty is not None
            and generation_config.encoder_repetition_penalty != 1.0
        ):
            if len(encoder_input_ids.shape) == 2:
                processors.append(
                    EncoderRepetitionPenaltyLogitsProcessor(
                        penalty=generation_config.encoder_repetition_penalty,
                        encoder_input_ids=encoder_input_ids,
                    )
                )
            else:
                warnings.warn(
                    "Passing `encoder_repetition_penalty` requires some form of `input_ids` to be passed to "
                    "`generate`, ignoring the argument.",
                    UserWarning,
                )
        if generation_config.repetition_penalty is not None and generation_config.repetition_penalty != 1.0:
            processors.append(RepetitionPenaltyLogitsProcessor(penalty=generation_config.repetition_penalty))
        if generation_config.no_repeat_ngram_size is not None and generation_config.no_repeat_ngram_size > 0:
            processors.append(NoRepeatNGramLogitsProcessor(generation_config.no_repeat_ngram_size))
        if (
            generation_config.encoder_no_repeat_ngram_size is not None
            and generation_config.encoder_no_repeat_ngram_size > 0
        ):
            if len(encoder_input_ids.shape) == 2:
                processors.append(
                    EncoderNoRepeatNGramLogitsProcessor(
                        generation_config.encoder_no_repeat_ngram_size,
                        encoder_input_ids,
                    )
                )
            else:
                warnings.warn(
                    "Passing `encoder_no_repeat_ngram_size` requires some form of `input_ids` to be passed to "
                    "`generate`, ignoring the argument.",
                    UserWarning,
                )
        if generation_config.bad_words_ids is not None:
            processors.append(
                NoBadWordsLogitsProcessor(
                    generation_config.bad_words_ids,
                    generation_config._eos_token_tensor,
                )
            )
        if (
            generation_config.min_length is not None
            and getattr(generation_config, "_eos_token_tensor", None) is not None
            and generation_config.min_length > 0
        ):
            processors.append(
                MinLengthLogitsProcessor(
                    generation_config.min_length,
                    generation_config._eos_token_tensor,
                    device=device,
                )
            )
        if (
            generation_config.min_new_tokens is not None
            and getattr(generation_config, "_eos_token_tensor", None) is not None
            and generation_config.min_new_tokens > 0
        ):
            processors.append(
                MinNewTokensLengthLogitsProcessor(
                    input_ids_seq_length,
                    generation_config.min_new_tokens,
                    generation_config._eos_token_tensor,
                    device=device,
                )
            )
        if prefix_allowed_tokens_fn is not None:
            processors.append(
                PrefixConstrainedLogitsProcessor(
                    prefix_allowed_tokens_fn,
                    generation_config.num_beams,
                )
            )
        if generation_config.forced_bos_token_id is not None:
            processors.append(
                ForcedBOSTokenLogitsProcessor(
                    generation_config.forced_bos_token_id,
                )
            )
        if generation_config.forced_eos_token_id is not None:
            processors.append(
                ForcedEOSTokenLogitsProcessor(
                    generation_config.max_length,
                    generation_config.forced_eos_token_id,
                    device=device,
                )
            )
        if generation_config.remove_invalid_values is True:
            processors.append(InfNanRemoveLogitsProcessor())
        if generation_config.exponential_decay_length_penalty is not None:
            processors.append(
                ExponentialDecayLengthPenalty(
                    generation_config.exponential_decay_length_penalty,
                    generation_config._eos_token_tensor,
                    input_ids_seq_length,
                )
            )
        if generation_config.suppress_tokens is not None:
            processors.append(
                SuppressTokensLogitsProcessor(
                    generation_config.suppress_tokens,
                    device=device,
                )
            )
        if generation_config.begin_suppress_tokens is not None:
            begin_index = input_ids_seq_length
            begin_index = (
                begin_index
                if (input_ids_seq_length > 1 or generation_config.forced_bos_token_id is None)
                else begin_index + 1
            )
            processors.append(
                SuppressTokensAtBeginLogitsProcessor(
                    generation_config.begin_suppress_tokens,
                    begin_index,
                    device=device,
                )
            )
        processors = self._merge_criteria_processor_list(processors, logits_processor)
        if generation_config.do_sample:
            if generation_config.num_beams > 1:
                if isinstance(generation_config._eos_token_tensor, list):
                    min_tokens_to_keep = len(generation_config._eos_token_tensor) + 1
                elif isinstance(generation_config._eos_token_tensor, torch.Tensor):
                    min_tokens_to_keep = generation_config._eos_token_tensor.shape[0] + 1
                else:
                    min_tokens_to_keep = 2
            else:
                min_tokens_to_keep = 1
            if generation_config.temperature is not None and generation_config.temperature != 1.0:
                processors.append(TemperatureLogitsWarper(generation_config.temperature))
            if generation_config.top_k is not None and generation_config.top_k != 0:
                processors.append(
                    TopKLogitsWarper(top_k=generation_config.top_k, min_tokens_to_keep=min_tokens_to_keep)
                )
            if generation_config.top_p is not None and generation_config.top_p < 1.0:
                processors.append(
                    TopPLogitsWarper(top_p=generation_config.top_p, min_tokens_to_keep=min_tokens_to_keep)
                )
            if generation_config.min_p is not None:
                processors.append(
                    MinPLogitsWarper(min_p=generation_config.min_p, min_tokens_to_keep=min_tokens_to_keep)
                )
            if generation_config.typical_p is not None and generation_config.typical_p < 1.0:
                processors.append(
                    TypicalLogitsWarper(mass=generation_config.typical_p, min_tokens_to_keep=min_tokens_to_keep)
                )
            if generation_config.epsilon_cutoff is not None and 0.0 < generation_config.epsilon_cutoff < 1.0:
                processors.append(
                    EpsilonLogitsWarper(
                        epsilon=generation_config.epsilon_cutoff, min_tokens_to_keep=min_tokens_to_keep
                    )
                )
            if generation_config.eta_cutoff is not None and 0.0 < generation_config.eta_cutoff < 1.0:
                processors.append(
                    EtaLogitsWarper(
                        epsilon=generation_config.eta_cutoff, min_tokens_to_keep=min_tokens_to_keep, device=device
                    )
                )
        if generation_config.watermarking_config is not None:
            processors.append(
                generation_config.watermarking_config.construct_processor(
                    self.config.get_text_config().vocab_size, device
                )
            )
        if generation_config.renormalize_logits is True:
            processors.append(LogitNormalization())
        return processors
    def _get_stopping_criteria(
        self,
        generation_config: GenerationConfig,
        stopping_criteria: Optional[StoppingCriteriaList],
        tokenizer: Optional["PreTrainedTokenizerBase"] = None,
    ) -> StoppingCriteriaList:
        criteria = StoppingCriteriaList()
        if generation_config.max_length is not None:
            max_position_embeddings = getattr(self.config, "max_position_embeddings", None)
            criteria.append(
                MaxLengthCriteria(
                    max_length=generation_config.max_length,
                    max_position_embeddings=max_position_embeddings,
                )
            )
        if generation_config.max_time is not None:
            criteria.append(MaxTimeCriteria(max_time=generation_config.max_time))
        if generation_config.stop_strings is not None:
            if tokenizer is None:
                raise ValueError(
                    "There are one or more stop strings, either in the arguments to `generate` or in the "
                    "model's generation config, but we could not locate a tokenizer. When generating with "
                    "stop strings, you must pass the model's tokenizer to the `tokenizer` argument of `generate`."
                )
            criteria.append(StopStringCriteria(stop_strings=generation_config.stop_strings, tokenizer=tokenizer))
        if generation_config._eos_token_tensor is not None:
            criteria.append(EosTokenCriteria(eos_token_id=generation_config._eos_token_tensor))
        if (
            generation_config.is_assistant
            and generation_config.assistant_confidence_threshold is not None
            and generation_config.assistant_confidence_threshold > 0
        ):
            criteria.append(
                ConfidenceCriteria(assistant_confidence_threshold=generation_config.assistant_confidence_threshold)
            )
        criteria = self._merge_criteria_processor_list(criteria, stopping_criteria)
        return criteria
    def _merge_criteria_processor_list(
        self,
        default_list: Union[LogitsProcessorList, StoppingCriteriaList],
        custom_list: Union[LogitsProcessorList, StoppingCriteriaList],
    ) -> Union[LogitsProcessorList, StoppingCriteriaList]:
        if len(custom_list) == 0:
            return default_list
        final_list = type(default_list)()
        for default in default_list:
            using_custom = False
            for custom in custom_list:
                if type(custom) is type(default):
                    object_type = "stopping criteria" if isinstance(custom, StoppingCriteria) else "logits processor"
                    logger.warning_once(
                        f"A custom {object_type} of type {type(custom)} has been passed to `.generate()`, but it "
                        f"was also created in `.generate()`, given its parameterization. The custom {type(custom)} "
                        f"will take precedence. Please check the docstring of {type(custom)} to see related "
                        "`.generate()` flags."
                    )
                    final_list.append(custom)
                    using_custom = True
                    break
            if not using_custom:
                final_list.append(default)
        for custom in custom_list:
            if custom not in final_list:
                final_list.append(custom)
        return final_list
    def compute_transition_scores(
        self,
        sequences: torch.Tensor,
        scores: tuple[torch.Tensor],
        beam_indices: Optional[torch.Tensor] = None,
        normalize_logits: bool = False,
    ) -> torch.Tensor:
        if beam_indices is None:
            beam_indices = torch.arange(scores[0].shape[0]).view(-1, 1).to(sequences.device)
            beam_indices = beam_indices.expand(-1, len(scores))
        scores = torch.stack(scores).reshape(len(scores), -1).transpose(0, 1)
        if normalize_logits:
            scores = scores.reshape(-1, self.config.get_text_config().vocab_size, scores.shape[-1])
            scores = torch.nn.functional.log_softmax(scores, dim=1)
            scores = scores.reshape(-1, scores.shape[-1])
        beam_indices_mask = beam_indices < 0
        max_beam_length = (1 - beam_indices_mask.long()).sum(-1).max()
        beam_indices = beam_indices.clone()[:, :max_beam_length]
        beam_indices_mask = beam_indices_mask[:, :max_beam_length]
        beam_indices[beam_indices_mask] = 0
        beam_sequence_indices = beam_indices * self.config.get_text_config().vocab_size
        cut_idx = sequences.shape[-1] - max_beam_length
        indices = sequences[:, cut_idx:] + beam_sequence_indices
        transition_scores = scores.gather(0, indices)
        transition_scores[beam_indices_mask] = 0
        return transition_scores
    def _validate_generation_mode(self, generation_mode, generation_config, generation_mode_kwargs):
        if generation_mode == GenerationMode.BEAM_SEARCH and "streamer" in generation_mode_kwargs:
            raise ValueError(
                "`streamer` cannot be used with beam search (yet!). Make sure that `num_beams` is set to 1."
            )
        if generation_mode == GenerationMode.ASSISTED_GENERATION:
            if generation_config.num_return_sequences > 1:
                raise ValueError(
                    "num_return_sequences has to be 1 when doing assisted generate, "
                    f"but is {generation_config.num_return_sequences}."
                )
            if self._is_stateful:
                raise ValueError(
                    f"assisted generation is not supported with stateful models, such as {self.__class__.__name__}"
                )
        if (assistant_model := generation_mode_kwargs.get("assistant_model")) is not None:
            if self.config.is_encoder_decoder and not assistant_model.config.is_encoder_decoder:
                attributes_to_check = ["encoder_attention_heads", "encoder_ffn_dim", "encoder_layers"]
                attributes_to_check = [attr for attr in dir(assistant_model.config) if attr in attributes_to_check]
                are_equal = all(
                    getattr(self.config, attr) == getattr(assistant_model.config, attr) for attr in attributes_to_check
                )
                if not are_equal:
                    raise ValueError(
                        "The main model and the assistant don't have compatible encoder-dependent input shapes. "
                        "Ensure you load the assistant with the correct encoder-decoder class, e.g. `AutoModelForSpeechSeq2Seq` for Whisper."
                    )
            doc_reference = (
                "(see https://huggingface.co/docs/MEROAI/en/generation_strategies#universal-assisted-decoding)"
            )
            if self.config.get_text_config().vocab_size == assistant_model.config.get_text_config().vocab_size:
                if "assistant_tokenizer" in generation_mode_kwargs:
                    raise ValueError(
                        f"`assistant_tokenizer` is not required when the main and assistant models use the same tokenizer. Please omit `assistant_tokenizer` from `generate()` {doc_reference}."
                    )
            else:
                if "tokenizer" not in generation_mode_kwargs or "assistant_tokenizer" not in generation_mode_kwargs:
                    raise ValueError(
                        f"The main and assistant models have different tokenizers. Please provide `tokenizer` and `assistant_tokenizer` to `generate()` {doc_reference}."
                    )
    def _validate_model_kwargs(self, model_kwargs: dict[str, Any]):
        if self.config.is_encoder_decoder:
            for key in ["decoder_input_ids"]:
                model_kwargs.pop(key, None)
        unused_model_args = []
        model_args = set(inspect.signature(self.prepare_inputs_for_generation).parameters)
        if "kwargs" in model_args or "model_kwargs" in model_args:
            model_args |= set(inspect.signature(self.forward).parameters)
        if self.config.is_encoder_decoder:
            base_model = getattr(self, self.base_model_prefix, None)
            encoder = getattr(self, "encoder", None)
            if encoder is None and base_model is not None:
                encoder = getattr(base_model, "encoder", None)
            if encoder is not None:
                encoder_model_args = set(inspect.signature(encoder.forward).parameters)
                model_args |= encoder_model_args
            decoder = getattr(self, "decoder", None)
            if decoder is None and base_model is not None:
                decoder = getattr(base_model, "decoder", None)
            if decoder is not None:
                decoder_model_args = set(inspect.signature(decoder.forward).parameters)
                model_args |= {f"decoder_{x}" for x in decoder_model_args}
        for key, value in model_kwargs.items():
            if value is not None and key not in model_args and key not in MEROAIKwargs.__optional_keys__:
                unused_model_args.append(key)
        if unused_model_args:
            raise ValueError(
                f"The following `model_kwargs` are not used by the model: {unused_model_args} (note: typos in the"
                " generate arguments will also show up in this list)"
            )
    def _validate_generated_length(self, generation_config, input_ids_length, has_default_max_length):
        if has_default_max_length and generation_config.max_new_tokens is None and generation_config.max_length == 20:
            warnings.warn(
                f"Using the model-agnostic default `max_length` (={generation_config.max_length}) to control the "
                "generation length. We recommend setting `max_new_tokens` to control the maximum length of the "
                "generation.",
                UserWarning,
            )
        if input_ids_length >= generation_config.max_length:
            input_ids_string = "decoder_input_ids" if self.config.is_encoder_decoder else "input_ids"
            raise ValueError(
                f"Input length of {input_ids_string} is {input_ids_length}, but `max_length` is set to"
                f" {generation_config.max_length}. This can lead to unexpected behavior. You should consider"
                " increasing `max_length` or, better yet, setting `max_new_tokens`."
            )
        min_length_error_suffix = (
            " Generation will stop at the defined maximum length. You should decrease the minimum length and/or "
            "increase the maximum length."
        )
        if has_default_max_length:
            min_length_error_suffix += (
                f" Note that `max_length` is set to {generation_config.max_length}, its default value."
            )
        if generation_config.min_length is not None and generation_config.min_length > generation_config.max_length:
            warnings.warn(
                f"Unfeasible length constraints: `min_length` ({generation_config.min_length}) is larger than"
                f" the maximum possible length ({generation_config.max_length})." + min_length_error_suffix,
                UserWarning,
            )
        if generation_config.min_new_tokens is not None:
            min_length = generation_config.min_new_tokens + input_ids_length
            if min_length > generation_config.max_length:
                warnings.warn(
                    f"Unfeasible length constraints: `min_new_tokens` ({generation_config.min_new_tokens}), when "
                    f"added to the prompt length ({input_ids_length}), is larger than"
                    f" the maximum possible length ({generation_config.max_length})." + min_length_error_suffix,
                    UserWarning,
                )
    def _prepare_generated_length(
        self,
        generation_config,
        has_default_max_length,
        has_default_min_length,
        model_input_name,
        input_ids_length,
        inputs_tensor,
    ):
        if generation_config.max_new_tokens is not None:
            if not has_default_max_length and generation_config.max_length is not None:
                logger.warning(
                    f"Both `max_new_tokens` (={generation_config.max_new_tokens}) and `max_length`(="
                    f"{generation_config.max_length}) seem to have been set. `max_new_tokens` will take precedence. "
                    "Please refer to the documentation for more information. "
                    "(https://huggingface.co/docs/MEROAI/main/en/main_classes/text_generation)"
                )
            generation_config.max_length = generation_config.max_new_tokens + input_ids_length
        elif (
            model_input_name == "inputs_embeds"
            and input_ids_length != inputs_tensor.shape[1]
            and not self.config.is_encoder_decoder
        ):
            generation_config.max_length -= inputs_tensor.shape[1]
        elif has_default_max_length:
            if generation_config.max_length == GenerationConfig().max_length:
                generation_config.max_length = generation_config.max_length + input_ids_length
                max_position_embeddings = getattr(self.config, "max_position_embeddings", None)
                if max_position_embeddings is not None:
                    generation_config.max_length = min(generation_config.max_length, max_position_embeddings)
        if generation_config.min_new_tokens is not None:
            if not has_default_min_length:
                logger.warning(
                    f"Both `min_new_tokens` (={generation_config.min_new_tokens}) and `min_length`(="
                    f"{generation_config.min_length}) seem to have been set. `min_new_tokens` will take precedence. "
                    "Please refer to the documentation for more information. "
                    "(https://huggingface.co/docs/MEROAI/main/en/main_classes/text_generation)"
                )
            generation_config.min_length = generation_config.min_new_tokens + input_ids_length
        elif (
            model_input_name == "inputs_embeds"
            and input_ids_length != inputs_tensor.shape[1]
            and not self.config.is_encoder_decoder
        ):
            generation_config.min_length = max(generation_config.min_length - inputs_tensor.shape[1], 0)
        return generation_config
    def _prepare_generation_config(
        self,
        generation_config: Optional[GenerationConfig],
        use_model_defaults: Optional[bool] = None,
        **kwargs: Any,
    ) -> tuple[GenerationConfig, dict]:
        using_model_generation_config = False
        if generation_config is None:
            if (
                self.generation_config._from_model_config
                and self.generation_config._original_object_hash == hash(self.generation_config)
                and len(self.config._get_non_default_generation_parameters()) > 0
            ):
                new_generation_config = GenerationConfig.from_model_config(self.config)
                if new_generation_config != self.generation_config:
                    warnings.warn(
                        "You have modified the pretrained model configuration to control generation. This is a"
                        " deprecated strategy to control generation and will be removed in v5."
                        " Please use and modify the model generation configuration (see"
                        " https://huggingface.co/docs/MEROAI/generation_strategies#default-text-generation-configuration )",
                        UserWarning,
                    )
                    self.generation_config = new_generation_config
            generation_config = self.generation_config
            using_model_generation_config = True
            if generation_config.cache_implementation == "hybrid":
                generation_config.cache_implementation = None
        generation_config = copy.deepcopy(generation_config)
        if not using_model_generation_config:
            model_base_version = version.parse(version.parse(self.generation_config.MEROAI_version).base_version)
            if use_model_defaults is True or (
                use_model_defaults is None and model_base_version >= version.parse("4.50.0")
            ):
                modified_values = {}
                global_default_generation_config = GenerationConfig()
                model_generation_config = self.generation_config
                for key, model_gen_config_value in model_generation_config.__dict__.items():
                    if key.startswith("_") or key == "MEROAI_version":
                        continue
                    if key == "cache_implementation" and model_generation_config.cache_implementation == "hybrid":
                        continue
                    global_default_value = getattr(global_default_generation_config, key, None)
                    custom_gen_config_value = getattr(generation_config, key, None)
                    if (
                        custom_gen_config_value == global_default_value
                        and model_gen_config_value != global_default_value
                    ):
                        modified_values[key] = model_gen_config_value
                        setattr(generation_config, key, model_gen_config_value)
                if generation_config.temperature == 0.0:
                    generation_config.do_sample = False
                if use_model_defaults is None and len(modified_values) > 0:
                    logger.warning_once(
                        f"`generation_config` default values have been modified to match model-specific defaults: "
                        f"{modified_values}. If this is not desired, please set these values explicitly."
                    )
            else:
                if generation_config.bos_token_id is None:
                    generation_config.bos_token_id = self.generation_config.bos_token_id
                if generation_config.eos_token_id is None:
                    generation_config.eos_token_id = self.generation_config.eos_token_id
                if generation_config.pad_token_id is None:
                    generation_config.pad_token_id = self.generation_config.pad_token_id
                if generation_config.decoder_start_token_id is None:
                    generation_config.decoder_start_token_id = self.generation_config.decoder_start_token_id
        model_kwargs = generation_config.update(**kwargs)
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        model_kwargs.update({"output_attentions": output_attentions} if output_attentions else {})
        model_kwargs.update({"output_hidden_states": output_hidden_states} if output_hidden_states else {})
        return generation_config, model_kwargs
    def _get_initial_cache_position(self, seq_length, device, model_kwargs):
        if "cache_position" in model_kwargs and model_kwargs["cache_position"] is not None:
            return model_kwargs
        if "inputs_embeds" in model_kwargs and not self.config.is_encoder_decoder:
            cache_position = torch.ones_like(model_kwargs["inputs_embeds"][0, :, 0], dtype=torch.int64).cumsum(0) - 1
        elif "decoder_inputs_embeds" in model_kwargs and self.config.is_encoder_decoder:
            cache_position = (
                torch.ones_like(model_kwargs["decoder_inputs_embeds"][0, :, 0], dtype=torch.int64).cumsum(0) - 1
            )
        else:
            cache_position = torch.ones(seq_length, dtype=torch.int64, device=device).cumsum(0) - 1
        past_length = 0
        if model_kwargs.get("past_key_values") is not None:
            cache = model_kwargs["past_key_values"]
            past_length = 0
            if isinstance(cache, tuple):
                past_length = cache[0][0].shape[2]
            elif hasattr(cache, "get_seq_length"):
                past_length = cache.get_seq_length()
            cache_position = cache_position[past_length:]
        model_kwargs["cache_position"] = cache_position
        return model_kwargs
    def _get_cache(self, cache_implementation: str, batch_size: int, max_cache_len: int, model_kwargs) -> Cache:
        requires_cross_attention_cache = (
            self.config.is_encoder_decoder or model_kwargs.get("encoder_outputs") is not None
        )
        offload_cache = "offloaded" in cache_implementation
        if hasattr(self, "_cache"):
            cache_to_check = self._cache.self_attention_cache if requires_cross_attention_cache else self._cache
        need_new_cache = (
            not hasattr(self, "_cache")
            or cache_to_check.offloading != offload_cache
            or cache_to_check.max_batch_size != batch_size
            or cache_to_check.max_cache_len < max_cache_len
        )
        if requires_cross_attention_cache and hasattr(self, "_cache"):
            need_new_cache = (
                need_new_cache
                or self._cache.cross_attention_cache.max_cache_len != model_kwargs["encoder_outputs"][0].shape[1]
            )
        if need_new_cache:
            self_attention_cache_kwargs = {
                "config": self.config.get_text_config(decoder=True),
                "max_cache_len": max_cache_len,
                "offloading": offload_cache,
            }
            self._cache = StaticCache(**self_attention_cache_kwargs)
            if requires_cross_attention_cache:
                cross_attention_cache_kwargs = {
                    "config": self.config.get_text_config(decoder=True),
                    "max_cache_len": model_kwargs["encoder_outputs"][0].shape[1],
                    "offloading": offload_cache,
                }
                self._cache = EncoderDecoderCache(self._cache, StaticCache(**cross_attention_cache_kwargs))
        else:
            self._cache.reset()
        return self._cache
    @classmethod
    def _supports_default_dynamic_cache(cls) -> bool:
        return not cls._is_stateful and all(
            special_model_name not in cls.__name__.lower()
            for special_model_name in [
                "reformer",
                "minimax",
                "xlnet",
                "lfm2",
                "lfm2-vl",
            ]
        )
    def _prepare_cache_for_generation(
        self,
        generation_config: GenerationConfig,
        model_kwargs: dict,
        generation_mode: GenerationMode,
        batch_size: int,
        max_cache_length: int,
    ) -> bool:
        is_hybrid_cache = any(class_name in self.__class__.__name__.lower() for class_name in ["mamba", "falconh1"])
        cache_name = "past_key_values" if not is_hybrid_cache else "cache_params"
        requires_cross_attention_cache = (
            self.config.is_encoder_decoder or model_kwargs.get("encoder_outputs") is not None
        )
        user_defined_cache = model_kwargs.get(cache_name)
        if user_defined_cache is not None:
            if generation_config.cache_implementation is not None:
                raise ValueError(
                    f"Passing both `cache_implementation` (used to initialize certain caches) and `{cache_name}` (a "
                    "Cache object) is unsupported. Please use only one of the two."
                )
            if isinstance(user_defined_cache, tuple) and self._supports_default_dynamic_cache():
                logger.warning_once(
                    "Passing a tuple of `past_key_values` is deprecated and will be removed in MEROAI v4.58.0. "
                    "You should pass an instance of `Cache` instead."
                )
                model_kwargs[cache_name] = (
                    DynamicCache.from_legacy_cache(user_defined_cache)
                    if not requires_cross_attention_cache
                    else EncoderDecoderCache.from_legacy_cache(user_defined_cache)
                )
            return
        if generation_config.use_cache is False:
            return
        if not self._supports_default_dynamic_cache():
            if generation_config.cache_implementation is not None:
                logger.warning_once(
                    "This model does not support `Cache` instances. `cache_implementation` (set to "
                    f"{generation_config.cache_implementation}) will be ignored.",
                )
            return
        if (
            generation_mode == GenerationMode.ASSISTED_GENERATION
            and generation_config.cache_implementation is not None
        ):
            logger.warning_once(
                "An assistant model is provided, using a dynamic cache instead of a cache of type="
                f"'{generation_config.cache_implementation}'."
            )
            generation_config.cache_implementation = None
        if (
            generation_mode in (GenerationMode.ASSISTED_GENERATION, GenerationMode.CONTRASTIVE_SEARCH)
            or generation_config.cache_implementation == "dynamic_full"
        ):
            dynamic_cache_kwargs = {}
        else:
            dynamic_cache_kwargs = {"config": self.config.get_text_config(decoder=True)}
        if generation_config.cache_implementation is not None:
            if generation_config.cache_implementation in ALL_STATIC_CACHE_IMPLEMENTATIONS:
                if generation_config.cache_implementation in DEPRECATED_STATIC_CACHE_IMPLEMENTATIONS:
                    logger.warning_once(
                        f"Using `cache_implementation='{generation_config.cache_implementation}' is deprecated. "
                        f"Please only use one of {STATIC_CACHE_IMPLEMENTATIONS}, and the layer structure will be "
                        "inferred automatically."
                    )
                model_kwargs[cache_name] = self._get_cache(
                    cache_implementation=generation_config.cache_implementation,
                    batch_size=max(generation_config.num_beams, generation_config.num_return_sequences) * batch_size,
                    max_cache_len=max_cache_length,
                    model_kwargs=model_kwargs,
                )
            elif generation_config.cache_implementation == "quantized":
                if self.config.is_encoder_decoder or not self._supports_default_dynamic_cache():
                    raise ValueError(
                        "This model does not support the quantized cache. If you want your model to support quantized "
                        "cache, please open an issue and tag @zucchini-nlp."
                    )
                cache_config = generation_config.cache_config if generation_config.cache_config is not None else {}
                if "config" not in cache_config:
                    cache_config["config"] = self.config.get_text_config()
                backend = cache_config.pop("backend", "quanto")
                if backend == "quanto" and not is_optimum_quanto_available():
                    raise ImportError(
                        "You need to install optimum-quanto in order to use KV cache quantization with optimum-quanto "
                        "backend. Please install it via  with `pip install optimum-quanto`"
                    )
                elif backend == "HQQ" and not is_hqq_available():
                    raise ImportError(
                        "You need to install `HQQ` in order to use KV cache quantization with HQQ backend. "
                        "Please install it via  with `pip install hqq`"
                    )
                model_kwargs[cache_name] = QuantizedCache(backend=backend, **cache_config)
            elif generation_config.cache_implementation == "offloaded":
                model_kwargs[cache_name] = DynamicCache(**dynamic_cache_kwargs, offloading=True)
            elif "dynamic" in generation_config.cache_implementation:
                model_kwargs[cache_name] = DynamicCache(**dynamic_cache_kwargs)
        else:
            model_kwargs[cache_name] = DynamicCache(**dynamic_cache_kwargs)
        if requires_cross_attention_cache and not isinstance(model_kwargs[cache_name], EncoderDecoderCache):
            model_kwargs[cache_name] = EncoderDecoderCache(
                model_kwargs[cache_name],
                DynamicCache(**dynamic_cache_kwargs),
            )
    def _supports_logits_to_keep(self) -> bool:
        return "logits_to_keep" in set(inspect.signature(self.forward).parameters.keys())
    def _prepare_special_tokens(
        self,
        generation_config: GenerationConfig,
        kwargs_has_attention_mask: Optional[bool] = None,
        device: Optional[Union[torch.device, str]] = None,
    ):
        def _tensor_or_none(token, device=None):
            if token is None:
                return token
            device = device if device is not None else self.device
            if isinstance(token, torch.Tensor):
                return token.to(device)
            return torch.tensor(token, device=device, dtype=torch.long)
        bos_token_tensor = _tensor_or_none(generation_config.bos_token_id, device=device)
        eos_token_tensor = _tensor_or_none(generation_config.eos_token_id, device=device)
        pad_token_tensor = _tensor_or_none(generation_config.pad_token_id, device=device)
        decoder_start_token_tensor = _tensor_or_none(generation_config.decoder_start_token_id, device=device)
        if self.config.is_encoder_decoder:
            decoder_start_token_tensor = (
                decoder_start_token_tensor if decoder_start_token_tensor is not None else bos_token_tensor
            )
        if eos_token_tensor is not None and eos_token_tensor.ndim == 0:
            eos_token_tensor = eos_token_tensor.unsqueeze(0)
        if pad_token_tensor is None and eos_token_tensor is not None:
            if kwargs_has_attention_mask is not None and not kwargs_has_attention_mask:
                logger.warning(
                    "The attention mask and the pad token id were not set. As a consequence, you may observe "
                    "unexpected behavior. Please pass your input's `attention_mask` to obtain reliable results."
                )
            pad_token_tensor = eos_token_tensor[0]
            logger.warning(f"Setting `pad_token_id` to `eos_token_id`:{pad_token_tensor} for open-end generation.")
        if self.config.is_encoder_decoder and decoder_start_token_tensor is None:
            raise ValueError(
                "`decoder_start_token_id` or `bos_token_id` has to be defined for encoder-decoder generation."
            )
        if (
            eos_token_tensor is not None
            and isin_mps_friendly(elements=eos_token_tensor, test_elements=pad_token_tensor).any()
        ):
            if kwargs_has_attention_mask is not None and not kwargs_has_attention_mask:
                logger.warning_once(
                    "The attention mask is not set and cannot be inferred from input because pad token is same as "
                    "eos token. As a consequence, you may observe unexpected behavior. Please pass your input's "
                    "`attention_mask` to obtain reliable results."
                )
        if eos_token_tensor is not None and (
            torch.is_floating_point(eos_token_tensor) or (eos_token_tensor < 0).any()
        ):
            logger.warning(
                f"`eos_token_id` should consist of positive integers, but is {eos_token_tensor}. Your generation "
                "will not stop until the maximum length is reached. Depending on other flags, it may even crash."
            )
        generation_config._bos_token_tensor = bos_token_tensor
        generation_config._eos_token_tensor = eos_token_tensor
        generation_config._pad_token_tensor = pad_token_tensor
        generation_config._decoder_start_token_tensor = decoder_start_token_tensor
    def _valid_auto_compile_criteria(self, model_kwargs: dict[str, Any], generation_config: GenerationConfig) -> bool:
        if generation_config.disable_compile:
            return False
        valid_hardware = self.device.type == "cuda" or bool(
            generation_config.compile_config is not None and generation_config.compile_config._compile_all_devices
        )
        using_compilable_cache = (
            isinstance(model_kwargs.get("past_key_values"), Cache) and model_kwargs["past_key_values"].is_compileable
        )
        can_compile = valid_hardware and using_compilable_cache
        if getattr(self, "hf_quantizer", None) is not None:
            can_compile &= self.hf_quantizer.is_compileable
        if hasattr(self, "hf_device_map"):
            all_model_devices = set(self.hf_device_map.values())
            has_cpu_offload = "cpu" in all_model_devices and len(all_model_devices) > 1
            can_compile &= not has_cpu_offload
            has_disk_offload = "disk" in all_model_devices
            can_compile &= not has_disk_offload
        if generation_config.compile_config is not None and not can_compile:
            logger.warning_once(
                "You have set `compile_config`, but we are unable to meet the criteria for compilation. Compilation "
                "will be skipped."
            )
        return can_compile
    def _get_deprecated_gen_repo(
        self,
        generation_mode: GenerationMode,
        trust_remote_code: bool,
        custom_generate: Optional[str] = None,
    ) -> Optional[str]:
        if custom_generate is not None or "/" not in (repo := GENERATION_MODES_MAPPING[generation_mode]):
            return None
        logger.warning_once(
            f"{generation_mode.name.replace('_', ' ').title()} was moved to a `custom_generate` repo: https://hf.co/{repo}. "
            f"To prevent loss of backward compatibility, add `custom_generate='{repo}'` "
            "to your `generate` call before v4.62.0."
        )
        if not trust_remote_code:
            raise ValueError(
                f"{generation_mode.name.replace('_', ' ').title()} requires `trust_remote_code=True` in your `generate` call, "
                f"since it loads https://hf.co/{repo}."
            )
        return repo
    def _extract_generation_mode_kwargs(
        self,
        custom_generate,
        kwargs,
        synced_gpus,
        assistant_model,
        streamer,
    ) -> dict[str, Any]:
        generation_mode_kwargs = {
            "tokenizer": kwargs.pop("tokenizer", None),
            "assistant_tokenizer": kwargs.pop("assistant_tokenizer", None),
            "assistant_model": assistant_model,
            "streamer": streamer,
        }
        generation_mode_kwargs["synced_gpus"] = (
            (is_deepspeed_zero3_enabled() or is_fsdp_managed_module(self)) and dist.get_world_size() > 1
            if synced_gpus is None
            else synced_gpus
        )
        generation_mode_kwargs = {k: v for k, v in generation_mode_kwargs.items() if v is not None}
        if isinstance(custom_generate, Callable):
            usual_mode_kwargs = inspect.signature(GenerationMixin._sample).parameters.keys()
            custom_generate_kwargs = inspect.signature(custom_generate).parameters.keys()
            new_custom_keys = custom_generate_kwargs - usual_mode_kwargs
            generation_mode_kwargs = {k: kwargs.pop(k) for k in new_custom_keys if k in kwargs}
        return generation_mode_kwargs
    @torch.no_grad()
    def generate(
        self,
        inputs: Optional[torch.Tensor] = None,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], list[int]]] = None,
        synced_gpus: Optional[bool] = None,
        assistant_model: Optional["PreTrainedModel"] = None,
        streamer: Optional["BaseStreamer"] = None,
        negative_prompt_ids: Optional[torch.Tensor] = None,
        negative_prompt_attention_mask: Optional[torch.Tensor] = None,
        use_model_defaults: Optional[bool] = None,
        custom_generate: Optional[Union[str, Callable]] = None,
        **kwargs,
    ) -> Union[GenerateOutput, torch.LongTensor]:
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        if custom_generate is not None and isinstance(custom_generate, str):
            global_keys_to_exclude = {
                "self",
                "kwargs",
                "global_keys_to_exclude",
                "trust_remote_code",
                "custom_generate",
            }
            generate_arguments = {key: value for key, value in locals().items() if key not in global_keys_to_exclude}
            generate_arguments.update(kwargs)
            custom_generate_function = self.load_custom_generate(
                custom_generate, trust_remote_code=trust_remote_code, **kwargs
            )
            return custom_generate_function(model=self, **generate_arguments)
        generation_mode_kwargs = self._extract_generation_mode_kwargs(
            custom_generate,
            kwargs,
            synced_gpus,
            assistant_model,
            streamer,
        )
        generation_config, model_kwargs = self._prepare_generation_config(
            generation_config, use_model_defaults, **kwargs
        )
        generation_mode = generation_config.get_generation_mode(assistant_model)
        if isinstance(custom_generate, Callable):
            decoding_method = custom_generate
        else:
            decoding_method = getattr(type(self), GENERATION_MODES_MAPPING[generation_mode])
        self._validate_model_kwargs(model_kwargs.copy())
        self._validate_generation_mode(generation_mode, generation_config, generation_mode_kwargs)
        if deprecated_mode_repo := self._get_deprecated_gen_repo(generation_mode, trust_remote_code, custom_generate):
            return GenerationMixin.generate(
                self,
                inputs=inputs,
                generation_config=generation_config,
                logits_processor=logits_processor,
                stopping_criteria=stopping_criteria,
                prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
                assistant_model=assistant_model,
                negative_prompt_ids=negative_prompt_ids,
                negative_prompt_attention_mask=negative_prompt_attention_mask,
                use_model_defaults=use_model_defaults,
                custom_generate=deprecated_mode_repo,
                trust_remote_code=trust_remote_code,
                **generation_mode_kwargs,
                **kwargs,
            )
        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
        accepts_attention_mask = "attention_mask" in set(inspect.signature(self.forward).parameters.keys())
        requires_attention_mask = "encoder_outputs" not in model_kwargs
        kwargs_has_attention_mask = model_kwargs.get("attention_mask", None) is not None
        inputs_tensor, model_input_name, model_kwargs = self._prepare_model_inputs(
            inputs, generation_config.bos_token_id, model_kwargs
        )
        if "inputs_tensor" in inspect.signature(decoding_method).parameters.keys():
            generation_mode_kwargs["inputs_tensor"] = inputs_tensor
        batch_size = inputs_tensor.shape[0]
        device = inputs_tensor.device
        self._prepare_special_tokens(generation_config, kwargs_has_attention_mask, device=device)
        if not self.config.is_encoder_decoder:
            if (
                generation_config._pad_token_tensor is not None
                and batch_size > 1
                and len(inputs_tensor.shape) == 2
                and torch.sum(inputs_tensor[:, -1] == generation_config._pad_token_tensor) > 0
            ):
                logger.warning(
                    "A decoder-only architecture is being used, but right-padding was detected! For correct "
                    "generation results, please set `padding_side='left'` when initializing the tokenizer."
                )
        if not self.config.is_encoder_decoder and model_input_name == "inputs_embeds":
            generation_config.use_cache = True
        if not kwargs_has_attention_mask and requires_attention_mask and accepts_attention_mask:
            model_kwargs["attention_mask"] = self._prepare_attention_mask_for_generation(
                inputs_tensor, generation_config, model_kwargs
            )
        elif kwargs_has_attention_mask:
            if model_input_name == "input_ids" and len(model_kwargs["attention_mask"].shape) > 2:
                raise ValueError("`attention_mask` passed to `generate` must be 2D.")
        if self.config.is_encoder_decoder and "encoder_outputs" not in model_kwargs:
            model_kwargs = self._prepare_encoder_decoder_kwargs_for_generation(
                inputs_tensor, model_kwargs, model_input_name, generation_config
            )
        if self.config.is_encoder_decoder:
            input_ids, model_kwargs = self._prepare_decoder_input_ids_for_generation(
                batch_size=batch_size,
                model_input_name=model_input_name,
                model_kwargs=model_kwargs,
                decoder_start_token_id=generation_config._decoder_start_token_tensor,
                device=inputs_tensor.device,
            )
        else:
            input_ids = inputs_tensor if model_input_name == "input_ids" else model_kwargs.pop("input_ids")
        input_ids, model_kwargs = self._expand_inputs_for_generation(
            input_ids=input_ids,
            expand_size=max(generation_config.num_beams, generation_config.num_return_sequences),
            is_encoder_decoder=self.config.is_encoder_decoder,
            **model_kwargs,
        )
        if generation_config.token_healing:
            input_ids = self.heal_tokens(input_ids, generation_mode_kwargs.get("tokenizer"))
        if streamer is not None:
            streamer.put(input_ids.cpu())
        input_ids_length = input_ids.shape[1]
        has_default_max_length = kwargs.get("max_length") is None and generation_config.max_length is not None
        has_default_min_length = kwargs.get("min_length") is None and generation_config.min_length is not None
        generation_config = self._prepare_generated_length(
            generation_config=generation_config,
            has_default_max_length=has_default_max_length,
            has_default_min_length=has_default_min_length,
            model_input_name=model_input_name,
            inputs_tensor=inputs_tensor,
            input_ids_length=input_ids_length,
        )
        if self._supports_logits_to_keep() and "logits_to_keep" not in model_kwargs:
            model_kwargs["logits_to_keep"] = 1
        self._validate_generated_length(generation_config, input_ids_length, has_default_max_length)
        max_cache_length = generation_config.max_length - 1
        if (
            inputs_tensor.shape[1] != input_ids_length
            and model_input_name == "inputs_embeds"
            and not self.config.is_encoder_decoder
        ):
            max_cache_length += inputs_tensor.shape[1]
        self._prepare_cache_for_generation(
            generation_config, model_kwargs, generation_mode, batch_size, max_cache_length
        )
        if self.device.type != input_ids.device.type:
            warnings.warn(
                "You are calling .generate() with the `input_ids` being on a device type different"
                f" than your model's device. `input_ids` is on {input_ids.device.type}, whereas the model"
                f" is on {self.device.type}. You may experience unexpected behaviors or slower generation."
                " Please make sure that you have put `input_ids` to the"
                f" correct device by calling for example input_ids = input_ids.to('{self.device.type}') before"
                " running `.generate()`.",
                UserWarning,
            )
        prepared_logits_processor = self._get_logits_processor(
            generation_config=generation_config,
            input_ids_seq_length=input_ids_length,
            encoder_input_ids=inputs_tensor,
            prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
            logits_processor=logits_processor,
            device=inputs_tensor.device,
            model_kwargs=model_kwargs,
            negative_prompt_ids=negative_prompt_ids,
            negative_prompt_attention_mask=negative_prompt_attention_mask,
        )
        prepared_stopping_criteria = self._get_stopping_criteria(
            generation_config=generation_config,
            stopping_criteria=stopping_criteria,
            tokenizer=generation_mode_kwargs.get("tokenizer"),
        )
        model_kwargs["use_cache"] = generation_config.use_cache
        result = decoding_method(
            self,
            input_ids,
            logits_processor=prepared_logits_processor,
            stopping_criteria=prepared_stopping_criteria,
            generation_config=generation_config,
            **generation_mode_kwargs,
            **model_kwargs,
        )
        if (
            generation_config.return_legacy_cache is True
            and hasattr(result, "past_key_values")
            and getattr(result.past_key_values, "to_legacy_cache") is not None
        ):
            result.past_key_values = result.past_key_values.to_legacy_cache()
        return result
    def _has_unfinished_sequences(self, this_peer_finished: bool, synced_gpus: bool, device: torch.device) -> bool:
        if synced_gpus:
            this_peer_finished_flag = torch.tensor(0.0 if this_peer_finished else 1.0, device=device)
            dist.all_reduce(this_peer_finished_flag, op=dist.ReduceOp.SUM)
            if this_peer_finished_flag.item() == 0.0:
                return False
        elif this_peer_finished:
            return False
        return True
    def heal_tokens(
        self, input_ids: torch.LongTensor, tokenizer: Optional["PreTrainedTokenizerBase"] = None
    ) -> torch.LongTensor:
        if tokenizer is None:
            raise ValueError(
                " When generating with token healing, you must pass the model's tokenizer to the `tokenizer` "
                "argument of `generate`."
            )
        bos_token_id, pad_token_id = tokenizer.bos_token_id, tokenizer.pad_token_id
        vocab_trie = ExtensionsTrie(tokenizer.get_vocab())
        generation_config = GenerationConfig(max_new_tokens=1, pad_token_id=pad_token_id)
        prompts = [p.strip() for p in tokenizer.batch_decode(input_ids, skip_special_tokens=True)]
        input_ids = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
        ).input_ids.to(input_ids.device)
        input_ids = torch.where(input_ids == bos_token_id, pad_token_id, input_ids)
        if input_ids.numel() == 0:
            return input_ids
        tail_ids = input_ids[:, -1].tolist()
        if tokenizer.convert_tokens_to_ids(" ") is not None:
            space_tok = tokenizer.convert_ids_to_tokens(tokenizer.convert_tokens_to_ids(" "))[0]
            tail_toks = (tokenizer.decode(t).replace(" ", space_tok) for t in tail_ids)
        else:
            tail_toks = (tokenizer.decode(t) for t in tail_ids)
        for batch_idx, (tail_id, tail_tok) in enumerate(zip(tail_ids, tail_toks)):
            batch_ids = input_ids[batch_idx]
            if torch.all(batch_ids == pad_token_id).item():
                continue
            seq_bias = {
                (tokenizer.convert_tokens_to_ids(alt_tok),): 10.0 for alt_tok in vocab_trie.extensions(prefix=tail_tok)
            }
            if len(seq_bias) == 1:
                continue
            seq_bias[(tail_id,)] += 1.0
            generation_config.update(sequence_bias=seq_bias)
            trimmed_ids = batch_ids[:-1]
            if trimmed_ids.numel() == 0:
                continue
            if len(batch_ids[batch_ids != pad_token_id]) == 1:
                trimmed_ids[-1] = bos_token_id
            input_ids[batch_idx] = self.generate(trimmed_ids.unsqueeze(0), generation_config=generation_config)
        return input_ids
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
        pad_token_id = generation_config._pad_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        has_eos_stopping_criteria = any(hasattr(criteria, "eos_token_id") for criteria in stopping_criteria)
        do_sample = generation_config.do_sample
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (
                model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None
            )
        batch_size, cur_len = input_ids.shape[:2]
        this_peer_finished = False
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(cur_len, input_ids.device, model_kwargs)
        model_forward = self.__call__
        compile_forward = self._valid_auto_compile_criteria(model_kwargs, generation_config)
        if compile_forward:
            os.environ["TOKENIZERS_PARALLELISM"] = "0"
            if self.config._attn_implementation == "flash_attention_2":
                if generation_config.compile_config is not None and generation_config.compile_config.fullgraph:
                    logger.warning_once(
                        "When using Flash Attention 2 and a static cache, you cannot use the option `CompileConfig(fullgraph=True)` as "
                        "FA2 introduces graph breaks. We overrode the option with `fullgraph=False`."
                    )
                    generation_config.compile_config.fullgraph = False
            model_forward = self.get_compiled_call(generation_config.compile_config)
        if generation_config.prefill_chunk_size is not None:
            model_kwargs = self._prefill_chunking(input_ids, generation_config, **model_kwargs)
            is_prefill = False
        else:
            is_prefill = True
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)
            if is_prefill:
                outputs = self(**model_inputs, return_dict=True)
                is_prefill = False
            else:
                outputs = model_forward(**model_inputs, return_dict=True)
            model_kwargs = self._update_model_kwargs_for_generation(
                outputs,
                model_kwargs,
                is_encoder_decoder=self.config.is_encoder_decoder,
            )
            if synced_gpus and this_peer_finished:
                continue
            next_token_logits = outputs.logits[:, -1, :].to(copy=True, dtype=torch.float32, device=input_ids.device)
            next_token_scores = logits_processor(input_ids, next_token_logits)
            if return_dict_in_generate:
                if output_scores:
                    scores += (next_token_scores,)
                if output_logits:
                    raw_logits += (next_token_logits,)
                if output_attentions:
                    decoder_attentions += (
                        (outputs.decoder_attentions,) if self.config.is_encoder_decoder else (outputs.attentions,)
                    )
                    if self.config.is_encoder_decoder:
                        cross_attentions += (outputs.cross_attentions,)
                if output_hidden_states:
                    decoder_hidden_states += (
                        (outputs.decoder_hidden_states,)
                        if self.config.is_encoder_decoder
                        else (outputs.hidden_states,)
                    )
            if do_sample:
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)
            else:
                next_tokens = torch.argmax(next_token_scores, dim=-1)
            if has_eos_stopping_criteria:
                next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            if streamer is not None:
                streamer.put(next_tokens.cpu())
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
            cur_len += 1
            del outputs
        if streamer is not None:
            streamer.end()
        if return_dict_in_generate:
            if self.config.is_encoder_decoder:
                return GenerateEncoderDecoderOutput(
                    sequences=input_ids,
                    scores=scores,
                    logits=raw_logits,
                    encoder_attentions=encoder_attentions,
                    encoder_hidden_states=encoder_hidden_states,
                    decoder_attentions=decoder_attentions,
                    cross_attentions=cross_attentions,
                    decoder_hidden_states=decoder_hidden_states,
                    past_key_values=model_kwargs.get("past_key_values"),
                )
            else:
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
    @staticmethod
    def _flatten_beam_dim(tensor: torch.Tensor) -> torch.Tensor:
        shape = list(tensor.shape)
        return torch.reshape(tensor, [shape[0] * shape[1]] + shape[2:])
    @staticmethod
    def _unflatten_beam_dim(tensor: torch.Tensor, batch_size: int, num_beams: int) -> torch.Tensor:
        shape = list(tensor.shape)
        return torch.reshape(tensor, [batch_size, num_beams] + shape[1:])
    @staticmethod
    def _gather_beams(tensor: torch.Tensor, beam_indices: torch.Tensor) -> torch.Tensor:
        while len(beam_indices.shape) < len(tensor.shape):
            beam_indices = beam_indices.unsqueeze(-1)
        gathered_tensor = torch.take_along_dim(input=tensor, indices=beam_indices, dim=1)
        return gathered_tensor
    @staticmethod
    def _check_early_stop_heuristic(
        is_early_stop_heuristic_unsatisfied: torch.Tensor,
        running_beam_scores: torch.Tensor,
        beam_scores: torch.Tensor,
        is_sent_finished: torch.Tensor,
        cur_len: int,
        max_length: int,
        decoder_prompt_len: int,
        early_stopping: Union[bool, str],
        length_penalty: float,
    ):
        if early_stopping == "never" and length_penalty > 0.0:
            best_hypothetical_length = max_length - decoder_prompt_len
        else:
            best_hypothetical_length = cur_len - decoder_prompt_len
        best_possible_running_score = running_beam_scores[:, :1] / (best_hypothetical_length**length_penalty)
        worst_finished_score = torch.where(is_sent_finished, torch.min(beam_scores, dim=1, keepdim=True)[0], -1.0e9)
        return is_early_stop_heuristic_unsatisfied & torch.any(
            best_possible_running_score > worst_finished_score, dim=-1, keepdim=True
        )
    @staticmethod
    def _beam_search_has_unfinished_sequences(
        is_early_stop_heuristic_unsatisfied: torch.Tensor,
        is_sent_finished: torch.Tensor,
        next_token_hits_stopping_criteria: torch.Tensor,
        early_stopping: Union[bool, str],
    ):
        improvement_possible = torch.any(is_early_stop_heuristic_unsatisfied)
        exists_open_beam = ~(torch.all(is_sent_finished) & (early_stopping is True))
        valid_continuations = ~torch.all(next_token_hits_stopping_criteria)
        return improvement_possible & exists_open_beam & valid_continuations
    def _get_top_k_continuations(
        self,
        accumulated_log_probs: torch.Tensor,
        running_sequences: torch.Tensor,
        running_beam_indices: torch.Tensor,
        cur_len: int,
        decoder_prompt_len: int,
        do_sample: bool,
        beams_to_keep: int,
        num_beams: int,
        vocab_size: int,
        batch_size: int,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if do_sample:
            topk_indices = torch.multinomial(
                nn.functional.softmax(accumulated_log_probs, dim=-1), num_samples=beams_to_keep
            )
            topk_log_probs = torch.gather(input=accumulated_log_probs, dim=1, index=topk_indices)
        else:
            topk_log_probs, topk_indices = torch.topk(accumulated_log_probs, k=beams_to_keep)
        topk_current_beam_indices = topk_indices // vocab_size
        topk_running_beam_indices = self._gather_beams(running_beam_indices, topk_current_beam_indices)
        topk_running_sequences = self._gather_beams(running_sequences, topk_current_beam_indices)
        topk_ids = topk_indices % vocab_size
        topk_running_sequences[:, :, cur_len] = topk_ids
        batch_offset = torch.arange(batch_size, device=topk_ids.device).view(-1, 1) * num_beams
        batch_modified_indices = topk_current_beam_indices + batch_offset
        topk_running_beam_indices[:, :, cur_len - decoder_prompt_len] = batch_modified_indices
        return topk_log_probs, topk_running_sequences, topk_running_beam_indices
    def _get_running_beams_for_next_iteration(
        self,
        topk_log_probs: torch.Tensor,
        topk_running_sequences: torch.Tensor,
        topk_running_beam_indices: torch.Tensor,
        next_token_hits_stopping_criteria: torch.Tensor,
        num_beams: int,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        topk_running_log_probs = topk_log_probs + next_token_hits_stopping_criteria.to(torch.float32) * -1.0e9
        next_topk_indices = torch.topk(topk_running_log_probs, k=num_beams)[1]
        running_sequences = self._gather_beams(topk_running_sequences, next_topk_indices)
        running_beam_scores = self._gather_beams(topk_running_log_probs, next_topk_indices)
        running_beam_indices = self._gather_beams(topk_running_beam_indices, next_topk_indices)
        return running_sequences, running_beam_scores, running_beam_indices
    def _update_finished_beams(
        self,
        sequences: torch.Tensor,
        topk_running_sequences: torch.Tensor,
        beam_scores: torch.Tensor,
        topk_log_probs: torch.Tensor,
        beam_indices: torch.Tensor,
        topk_running_beam_indices: torch.Tensor,
        is_early_stop_heuristic_unsatisfied: torch.Tensor,
        is_sent_finished: torch.Tensor,
        next_token_hits_stopping_criteria: torch.Tensor,
        top_num_beam_mask: torch.Tensor,
        num_beams: int,
        cur_len: int,
        decoder_prompt_len: int,
        length_penalty: float,
        early_stopping: Union[bool, str],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        did_top_num_beams_just_finished = next_token_hits_stopping_criteria & top_num_beam_mask[None, :]
        topk_log_probs = topk_log_probs / ((cur_len + 1 - decoder_prompt_len) ** length_penalty)
        beams_in_batch_are_full = torch.all(is_sent_finished, axis=-1, keepdims=True) & (early_stopping is True)
        topk_log_probs += beams_in_batch_are_full.to(torch.float32) * -1.0e9
        topk_log_probs += (~is_early_stop_heuristic_unsatisfied).to(torch.float32) * -1.0e9
        topk_log_probs += (~did_top_num_beams_just_finished) * -1.0e9
        merged_sequences = torch.cat((sequences, topk_running_sequences), dim=1)
        merged_scores = torch.cat((beam_scores, topk_log_probs), dim=1)
        merged_beam_indices = torch.cat((beam_indices, topk_running_beam_indices), dim=1)
        merged_is_sent_finished = torch.cat((is_sent_finished, did_top_num_beams_just_finished), dim=1)
        topk_merged_indices = torch.topk(merged_scores, k=num_beams)[1]
        sequences = self._gather_beams(merged_sequences, topk_merged_indices)
        beam_scores = self._gather_beams(merged_scores, topk_merged_indices)
        beam_indices = self._gather_beams(merged_beam_indices, topk_merged_indices)
        is_sent_finished = self._gather_beams(merged_is_sent_finished, topk_merged_indices)
        return sequences, beam_scores, beam_indices, is_sent_finished
    def _beam_search(
        self,
        input_ids: torch.LongTensor,
        logits_processor: LogitsProcessorList,
        stopping_criteria: StoppingCriteriaList,
        generation_config: GenerationConfig,
        synced_gpus: bool = False,
        **model_kwargs,
    ) -> Union[GenerateBeamOutput, torch.LongTensor]:
        pad_token_id = generation_config._pad_token_tensor
        eos_token_id = generation_config._eos_token_tensor
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        do_sample = generation_config.do_sample
        early_stopping = generation_config.early_stopping
        length_penalty = generation_config.length_penalty
        max_length = generation_config.max_length
        num_beams = generation_config.num_beams
        num_return_sequences = generation_config.num_return_sequences
        batch_size_unflattened, cur_len = input_ids.shape[:2]
        batch_size = batch_size_unflattened // num_beams
        if self.__class__.__name__ == "MoshiDepthDecoder":
            vocab_size = self.config.audio_vocab_size
        elif self.__class__.__name__ == "ImageGPTForCausalImageModeling":
            vocab_size = self.get_output_embeddings().out_features
        elif self.__class__.__name__ == "BarkSemanticModel":
            vocab_size = self.config.output_vocab_size
        else:
            vocab_size = self.config.get_text_config().vocab_size
        decoder_prompt_len = cur_len
        this_peer_finished = False
        n_eos_tokens = eos_token_id.shape[0] if eos_token_id is not None else 0
        beams_to_keep = max(2, 1 + n_eos_tokens) * num_beams
        top_num_beam_mask = torch.cat(
            (torch.ones((num_beams), dtype=torch.bool), torch.zeros((beams_to_keep - num_beams), dtype=torch.bool)),
            dim=0,
        ).to(input_ids.device)
        model_kwargs = self._get_initial_cache_position(cur_len, input_ids.device, model_kwargs)
        sequential = generation_config.low_memory
        if sequential:
            raise ValueError(
                "`low_memory=True` is not supported after the beam search refactor. Please check the discussion in "
                "#35802 *after the PR got merged*, and add a comment there if your questions are not yet answered."
            )
        all_scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        beam_indices = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (
                model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None
            )
        output_fill_value = pad_token_id or eos_token_id[0] if eos_token_id is not None else -1
        running_sequences = torch.full(
            (batch_size, num_beams, max_length),
            fill_value=output_fill_value,
            dtype=torch.int64,
            device=input_ids.device,
        )
        running_sequences[:, :, :cur_len] = self._unflatten_beam_dim(input_ids, batch_size, num_beams)
        sequences = running_sequences.detach().clone()
        running_beam_scores = torch.zeros((batch_size, num_beams), dtype=torch.float, device=input_ids.device)
        running_beam_scores[:, 1:] = -1e9
        beam_scores = torch.full((batch_size, num_beams), fill_value=-1e9, dtype=torch.float, device=input_ids.device)
        is_sent_finished = torch.zeros((batch_size, num_beams), dtype=torch.bool, device=input_ids.device)
        is_early_stop_heuristic_unsatisfied = torch.ones((batch_size, 1), dtype=torch.bool, device=input_ids.device)
        next_token_hits_stopping_criteria = torch.zeros(
            (batch_size, num_beams), dtype=torch.bool, device=input_ids.device
        )
        running_beam_indices = torch.full(
            (batch_size, num_beams, max_length - cur_len), fill_value=-1, dtype=torch.int32, device=input_ids.device
        )
        beam_indices = running_beam_indices.detach().clone()
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            flat_running_sequences = self._flatten_beam_dim(running_sequences[:, :, :cur_len])
            model_inputs = self.prepare_inputs_for_generation(flat_running_sequences, **model_kwargs)
            model_outputs = self(**model_inputs, return_dict=True)
            model_kwargs = self._update_model_kwargs_for_generation(
                model_outputs,
                model_kwargs,
                is_encoder_decoder=self.config.is_encoder_decoder,
            )
            if synced_gpus and this_peer_finished:
                continue
            logits = model_outputs.logits[:, -1, :].to(copy=True, dtype=torch.float32, device=input_ids.device)
            log_probs = nn.functional.log_softmax(logits, dim=-1)
            log_probs = logits_processor(flat_running_sequences, log_probs)
            if return_dict_in_generate:
                if output_logits:
                    raw_logits += (logits.clone(),)
                if return_dict_in_generate and output_scores:
                    all_scores += (log_probs.clone(),)
                if output_attentions:
                    decoder_attentions += (
                        (model_outputs.decoder_attentions,)
                        if self.config.is_encoder_decoder
                        else (model_outputs.attentions,)
                    )
                    if self.config.is_encoder_decoder:
                        cross_attentions += (model_outputs.cross_attentions,)
                if output_hidden_states:
                    decoder_hidden_states += (
                        (model_outputs.decoder_hidden_states,)
                        if self.config.is_encoder_decoder
                        else (model_outputs.hidden_states,)
                    )
            del model_outputs
            log_probs = self._unflatten_beam_dim(log_probs, batch_size, num_beams)
            log_probs = log_probs + running_beam_scores[:, :, None]
            log_probs = torch.reshape(log_probs, (batch_size, num_beams * vocab_size))
            topk_log_probs, topk_running_sequences, topk_running_beam_indices = self._get_top_k_continuations(
                accumulated_log_probs=log_probs,
                running_sequences=running_sequences,
                running_beam_indices=running_beam_indices,
                cur_len=cur_len,
                decoder_prompt_len=decoder_prompt_len,
                do_sample=do_sample,
                beams_to_keep=beams_to_keep,
                num_beams=num_beams,
                vocab_size=vocab_size,
                batch_size=batch_size,
            )
            next_token_hits_stopping_criteria = stopping_criteria(
                self._flatten_beam_dim(topk_running_sequences[:, :, : cur_len + 1]),
                all_scores,
            )
            next_token_hits_stopping_criteria = self._unflatten_beam_dim(
                next_token_hits_stopping_criteria, batch_size, beams_to_keep
            )
            running_sequences, running_beam_scores, running_beam_indices = self._get_running_beams_for_next_iteration(
                topk_log_probs=topk_log_probs,
                topk_running_sequences=topk_running_sequences,
                topk_running_beam_indices=topk_running_beam_indices,
                next_token_hits_stopping_criteria=next_token_hits_stopping_criteria,
                num_beams=num_beams,
            )
            sequences, beam_scores, beam_indices, is_sent_finished = self._update_finished_beams(
                sequences=sequences,
                topk_running_sequences=topk_running_sequences,
                beam_scores=beam_scores,
                topk_log_probs=topk_log_probs,
                beam_indices=beam_indices,
                topk_running_beam_indices=topk_running_beam_indices,
                is_early_stop_heuristic_unsatisfied=is_early_stop_heuristic_unsatisfied,
                is_sent_finished=is_sent_finished,
                next_token_hits_stopping_criteria=next_token_hits_stopping_criteria,
                top_num_beam_mask=top_num_beam_mask,
                num_beams=num_beams,
                cur_len=cur_len,
                decoder_prompt_len=decoder_prompt_len,
                length_penalty=length_penalty,
                early_stopping=early_stopping,
            )
            if model_kwargs.get("past_key_values", None) is not None:
                beam_idx = self._flatten_beam_dim(running_beam_indices[..., cur_len - decoder_prompt_len])
                if hasattr(self, "_reorder_cache"):
                    model_kwargs["past_key_values"] = self._reorder_cache(model_kwargs["past_key_values"], beam_idx)
                else:
                    model_kwargs["past_key_values"].reorder_cache(beam_idx)
            cur_len = cur_len + 1
            is_early_stop_heuristic_unsatisfied = self._check_early_stop_heuristic(
                is_early_stop_heuristic_unsatisfied=is_early_stop_heuristic_unsatisfied,
                running_beam_scores=running_beam_scores,
                beam_scores=beam_scores,
                is_sent_finished=is_sent_finished,
                cur_len=cur_len,
                max_length=max_length,
                decoder_prompt_len=decoder_prompt_len,
                early_stopping=early_stopping,
                length_penalty=length_penalty,
            )
            this_peer_finished = not self._beam_search_has_unfinished_sequences(
                is_early_stop_heuristic_unsatisfied,
                is_sent_finished,
                next_token_hits_stopping_criteria,
                early_stopping,
            )
        sequences = self._flatten_beam_dim(sequences[:, :num_return_sequences, :])
        beam_scores = self._flatten_beam_dim(beam_scores[:, :num_return_sequences])
        beam_indices = self._flatten_beam_dim(beam_indices[:, :num_return_sequences, :])
        max_generated_length = ((beam_indices + 1).bool()).sum(dim=1).max()
        output_length = decoder_prompt_len + max_generated_length
        sequences = sequences[:, :output_length]
        beam_indices = beam_indices[:, :max_generated_length]
        if return_dict_in_generate:
            if not output_scores:
                beam_scores = None
            if self.config.is_encoder_decoder:
                return GenerateBeamEncoderDecoderOutput(
                    sequences=sequences,
                    sequences_scores=beam_scores,
                    scores=all_scores,
                    logits=raw_logits,
                    beam_indices=beam_indices,
                    encoder_attentions=encoder_attentions,
                    encoder_hidden_states=encoder_hidden_states,
                    decoder_attentions=decoder_attentions,
                    cross_attentions=cross_attentions,
                    decoder_hidden_states=decoder_hidden_states,
                    past_key_values=model_kwargs.get("past_key_values"),
                )
            else:
                return GenerateBeamDecoderOnlyOutput(
                    sequences=sequences,
                    sequences_scores=beam_scores,
                    scores=all_scores,
                    logits=raw_logits,
                    beam_indices=beam_indices,
                    attentions=decoder_attentions,
                    hidden_states=decoder_hidden_states,
                    past_key_values=model_kwargs.get("past_key_values"),
                )
        else:
            return sequences
    def _assisted_decoding(
        self,
        input_ids: torch.LongTensor,
        logits_processor: LogitsProcessorList,
        stopping_criteria: StoppingCriteriaList,
        generation_config: GenerationConfig,
        synced_gpus: bool = False,
        streamer: Optional["BaseStreamer"] = None,
        inputs_tensor: Optional[torch.FloatTensor] = None,
        assistant_model: Optional["PreTrainedModel"] = None,
        assistant_tokenizer: Optional["PreTrainedTokenizerBase"] = None,
        tokenizer: Optional["PreTrainedTokenizerBase"] = None,
        **model_kwargs,
    ) -> Union[GenerateNonBeamOutput, torch.LongTensor]:
        if not model_kwargs["use_cache"]:
            raise ValueError("assisted generate requires `use_cache=True`")
        if generation_config.cache_implementation in ["static", "hybrid", "sliding_window"] or (
            "past_key_values" in model_kwargs
            and hasattr(model_kwargs["past_key_values"], "layers")
            and any(getattr(l, "is_compileable", False) for l in model_kwargs["past_key_values"].layers)
        ):
            raise ValueError("assisted generate is not supported with Static cache classes`")
        candidate_generator = self._get_candidate_generator(
            generation_config=generation_config,
            input_ids=input_ids,
            inputs_tensor=inputs_tensor,
            assistant_model=assistant_model,
            logits_processor=logits_processor,
            target_tokenizer=tokenizer,
            assistant_tokenizer=assistant_tokenizer,
            model_kwargs=model_kwargs,
        )
        do_sample = generation_config.do_sample
        output_attentions = generation_config.output_attentions
        output_hidden_states = generation_config.output_hidden_states
        output_scores = generation_config.output_scores
        output_logits = generation_config.output_logits
        return_dict_in_generate = generation_config.return_dict_in_generate
        scores = () if (return_dict_in_generate and output_scores) else None
        raw_logits = () if (return_dict_in_generate and output_logits) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            encoder_hidden_states = (
                model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None
            )
        batch_size, cur_len = input_ids.shape[:2]
        if batch_size > 1:
            raise ValueError("assisted generate is only supported for batch_size = 1")
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        model_kwargs = self._get_initial_cache_position(cur_len, input_ids.device, model_kwargs)
        this_peer_finished = False
        is_first_iteration = True
        while self._has_unfinished_sequences(this_peer_finished, synced_gpus, device=input_ids.device):
            cur_len = input_ids.shape[1]
            candidate_input_ids, candidate_logits = candidate_generator.get_candidates(input_ids)
            candidate_input_ids = candidate_input_ids.to(self.device)
            if candidate_logits is not None:
                candidate_logits = candidate_logits.to(self.device)
            candidate_length = candidate_input_ids.shape[1] - input_ids.shape[1]
            is_done_candidate = stopping_criteria(candidate_input_ids, None)
            candidate_kwargs = copy.copy(model_kwargs)
            candidate_kwargs = _prepare_attention_mask(
                candidate_kwargs, candidate_input_ids.shape[1], self.config.is_encoder_decoder
            )
            candidate_kwargs = _prepare_token_type_ids(candidate_kwargs, candidate_input_ids.shape[1])
            if "cache_position" in candidate_kwargs:
                candidate_kwargs["cache_position"] = torch.cat(
                    (
                        candidate_kwargs["cache_position"],
                        torch.arange(cur_len, cur_len + candidate_length, device=input_ids.device, dtype=torch.long),
                    ),
                    dim=0,
                )
            model_inputs = self.prepare_inputs_for_generation(candidate_input_ids, **candidate_kwargs)
            if "logits_to_keep" in model_inputs:
                model_inputs["logits_to_keep"] = candidate_length + 1
            outputs = self(**model_inputs)
            new_logits = outputs.logits[:, -candidate_length - 1 :].to(
                dtype=torch.float32, device=input_ids.device
            )
            next_token_logits = new_logits.clone()
            if len(logits_processor) > 0:
                for i in range(candidate_length + 1):
                    new_logits[:, i, :] = logits_processor(candidate_input_ids[:, : cur_len + i], new_logits[:, i, :])
            if do_sample and candidate_logits is not None:
                valid_tokens, n_matches = _speculative_sampling(
                    candidate_input_ids,
                    candidate_logits,
                    candidate_length,
                    new_logits,
                    is_done_candidate,
                )
            else:
                if do_sample:
                    probs = new_logits.softmax(dim=-1)
                    selected_tokens = torch.multinomial(probs[0, :, :], num_samples=1).squeeze(1)[None, :]
                else:
                    selected_tokens = new_logits.argmax(dim=-1)
                candidate_new_tokens = candidate_input_ids[:, cur_len:]
                n_matches = ((~(candidate_new_tokens == selected_tokens[:, :-1])).cumsum(dim=-1) < 1).sum()
                if is_done_candidate and n_matches == candidate_length:
                    n_matches -= 1
                valid_tokens = selected_tokens[:, : n_matches + 1]
            input_ids = torch.cat((input_ids, valid_tokens), dim=-1)
            if streamer is not None:
                streamer.put(valid_tokens.cpu())
            new_cur_len = input_ids.shape[1]
            outputs.past_key_values.crop(new_cur_len - 1)
            candidate_generator.update_candidate_strategy(input_ids, new_logits, n_matches)
            model_kwargs = self._update_model_kwargs_for_generation(
                outputs,
                model_kwargs,
                is_encoder_decoder=self.config.is_encoder_decoder,
                num_new_tokens=n_matches + 1,
            )
            if synced_gpus and this_peer_finished:
                continue
            if return_dict_in_generate:
                newly_added_length = n_matches + 1
                if output_scores:
                    scores += tuple(new_logits[:, i, :] for i in range(newly_added_length))
                if output_logits:
                    raw_logits += tuple(next_token_logits[:, i, :] for i in range(newly_added_length))
                newly_added_length = new_cur_len if is_first_iteration else newly_added_length
                if output_attentions:
                    if self.config.is_encoder_decoder:
                        cross_attentions = _split_model_outputs(
                            cross_attentions, outputs.cross_attentions, cur_len, newly_added_length
                        )
                        decoder_attentions = _split_model_outputs(
                            decoder_attentions,
                            outputs.decoder_attentions,
                            cur_len,
                            newly_added_length,
                            is_decoder_attention=True,
                        )
                    elif outputs.attentions[0] is not None:
                        decoder_attentions = _split_model_outputs(
                            decoder_attentions,
                            outputs.attentions,
                            cur_len,
                            newly_added_length,
                            is_decoder_attention=True,
                        )
                if output_hidden_states:
                    if self.config.is_encoder_decoder:
                        decoder_hidden_states = _split_model_outputs(
                            decoder_hidden_states, outputs.decoder_hidden_states, cur_len, newly_added_length
                        )
                    else:
                        decoder_hidden_states = _split_model_outputs(
                            decoder_hidden_states, outputs.hidden_states, cur_len, newly_added_length
                        )
            unfinished_sequences = unfinished_sequences & ~stopping_criteria(input_ids, scores)
            this_peer_finished = unfinished_sequences.max() == 0
            is_first_iteration = False
        if streamer is not None:
            streamer.end()
        if (
            hasattr(candidate_generator, "assistant_model")
            and candidate_generator.assistant_model.generation_config.num_assistant_tokens_schedule == "heuristic"
        ):
            candidate_generator.assistant_model.generation_config.num_assistant_tokens = (
                candidate_generator.num_assistant_tokens
            )
        if return_dict_in_generate:
            if self.config.is_encoder_decoder:
                return GenerateEncoderDecoderOutput(
                    sequences=input_ids,
                    scores=scores,
                    logits=raw_logits,
                    encoder_attentions=encoder_attentions,
                    encoder_hidden_states=encoder_hidden_states,
                    decoder_attentions=decoder_attentions,
                    cross_attentions=cross_attentions,
                    decoder_hidden_states=decoder_hidden_states,
                    past_key_values=model_kwargs.get("past_key_values"),
                )
            else:
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
    def _prefill_chunking(self, input_ids: torch.LongTensor, generation_config: GenerationConfig, **model_kwargs):
        torch._dynamo.config.cache_size_limit = 64
        chunk_size = generation_config.prefill_chunk_size
        input_chunks = torch.split(input_ids[:, :-1], chunk_size, dim=-1)
        if "past_key_values" not in model_kwargs:
            raise ValueError("Cannot use prefill chunking without a cache")
        model_forward = self.forward
        compile_forward = self._valid_auto_compile_criteria(model_kwargs, generation_config)
        if compile_forward:
            model_forward = self.get_compiled_call(generation_config.compile_config)
        attention_mask = model_kwargs.pop("attention_mask", None)
        past_length = 0
        for input_chunk in input_chunks:
            current_length = past_length + input_chunk.shape[-1]
            if attention_mask is not None:
                model_kwargs["attention_mask"] = attention_mask[:, :current_length]
            model_kwargs["cache_position"] = torch.arange(
                past_length, current_length, dtype=torch.long, device=input_chunk.device
            )
            model_kwargs["position_ids"] = model_kwargs["cache_position"].unsqueeze(0)
            model_inputs = self.prepare_inputs_for_generation(input_chunk, **model_kwargs)
            outputs = model_forward(**model_inputs, return_dict=True)
            model_kwargs["past_key_values"] = outputs.past_key_values
            past_length = current_length
        model_kwargs["attention_mask"] = attention_mask
        model_kwargs["cache_position"] = model_kwargs["cache_position"][-1:] + 1
        _ = model_kwargs.pop("position_ids", None)
        return model_kwargs
def _speculative_sampling(
    candidate_input_ids,
    candidate_logits,
    candidate_length,
    new_logits,
    is_done_candidate,
):
    new_candidate_input_ids = candidate_input_ids[:, -candidate_length:]
    q = candidate_logits.softmax(dim=-1)
    q_i = q[:, torch.arange(candidate_length), new_candidate_input_ids].squeeze(0, 1)
    p = new_logits.softmax(dim=-1)
    p_i = p[:, torch.arange(candidate_length), new_candidate_input_ids].squeeze(0, 1)
    probability_ratio = p_i / q_i
    r_i = torch.rand_like(probability_ratio)
    is_accepted = r_i <= probability_ratio
    n_matches = ((~is_accepted).cumsum(dim=-1) < 1).sum()
    if is_done_candidate and n_matches == candidate_length:
        n_matches -= 1
        valid_tokens = new_candidate_input_ids[:, : n_matches + 1]
    else:
        gamma = candidate_logits.shape[1]
        p_n_plus_1 = p[:, n_matches, :]
        if n_matches < gamma:
            q_n_plus_1 = q[:, n_matches, :]
            p_prime = torch.clamp((p_n_plus_1 - q_n_plus_1), min=0)
            p_prime.div_(p_prime.sum())
        else:
            p_prime = p_n_plus_1
        t = torch.multinomial(p_prime, num_samples=1).squeeze(1)[None, :]
        if n_matches > 0:
            valid_tokens = torch.cat((new_candidate_input_ids[:, :n_matches], t), dim=-1)
        else:
            valid_tokens = t
    return valid_tokens, n_matches
def _split_model_outputs(outputs, new_outputs, cur_len, added_len, is_decoder_attention=False):
    if len(outputs) == 0:
        new_tuple = ()
        for layer in new_outputs:
            last_dim_size = cur_len if is_decoder_attention else layer.shape[-1]
            new_tuple += (layer[..., :cur_len, :last_dim_size],)
        outputs += (new_tuple,)
        cur_len += 1
        added_len -= cur_len
    for i in range(added_len):
        new_tuple = ()
        for layer in new_outputs:
            last_dim_size = cur_len + i if is_decoder_attention else layer.shape[-1]
            new_tuple += (layer[..., i : i + 1, :last_dim_size],)
        outputs += (new_tuple,)
    return outputs