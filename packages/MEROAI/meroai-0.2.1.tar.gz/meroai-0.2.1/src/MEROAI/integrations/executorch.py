import logging
from typing import Callable, Optional
import torch
from ..cache_utils import (
    DynamicCache,
    DynamicLayer,
    DynamicSlidingWindowLayer,
    EncoderDecoderCache,
    StaticCache,
)
from ..generation.configuration_utils import GenerationConfig
from ..masking_utils import (
    ALL_MASK_ATTENTION_FUNCTIONS,
    _ignore_causal_mask_sdpa,
    _is_torch_greater_or_equal_than_2_5,
    prepare_padding_mask,
)
from ..modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from ..pytorch_utils import (
    is_torch_greater_or_equal,
    is_torch_greater_or_equal_than_2_3,
    is_torch_greater_or_equal_than_2_6,
)
class TorchExportableModuleForVLM:
    def __init__(self, model, max_batch_size: int = 1, max_cache_len: int = 1024):
        self.model = model
        self.max_batch_size = max_batch_size
        self.max_cache_len = max_cache_len
        self.config = model.config
        self.vision_encoder = model.model.vision_model
        self.connector = model.model.connector
        self.text_decoder = model.model.text_model
        self.exported_vision_encoder = None
        self.exported_connector = None
        self.exported_text_decoder = None
    def export_vision_encoder(self):
        self.vision_encoder.eval()
        pixel_values = torch.randn(1, 3, 384, 384, dtype=torch.float32)
        dynamic_shapes = {
            "pixel_values": {
                2: torch.export.Dim.AUTO,
                3: torch.export.Dim.AUTO,
            }
        }
        self.exported_vision_encoder = torch.export.export(
            self.vision_encoder,
            args=(pixel_values,),
            dynamic_shapes=dynamic_shapes,
            strict=False,
        )
        return self.exported_vision_encoder
    def export_connector(self):
        self.connector.eval()
        vision_hidden_size = self.config.vision_config.hidden_size
        image_size = self.config.vision_config.image_size
        patch_size = self.config.vision_config.patch_size
        patches_per_dim = image_size // patch_size
        num_patches = patches_per_dim * patches_per_dim
        image_hidden_states = torch.randn(1, num_patches, vision_hidden_size, dtype=torch.float32)
        dynamic_shapes = {"image_hidden_states": {1: torch.export.Dim.AUTO}}
        self.exported_connector = torch.export.export(
            self.connector,
            args=(image_hidden_states,),
            dynamic_shapes=dynamic_shapes,
            strict=False,
        )
        return self.exported_connector
    def export_text_decoder(self):
        self.exportable_text_decoder = TorchExportableModuleForDecoderOnlyLM(model=self.text_decoder)
        seq_length = 3
        input_ids = torch.zeros((1, seq_length), dtype=torch.long)
        cache_position = torch.arange(seq_length, dtype=torch.long)
        max_seq_length = min(self.max_cache_len, self.config.text_config.max_position_embeddings)
        seq_len_dim = torch.export.Dim("seq_length_dim", max=max_seq_length - 1)
        dynamic_shapes = {
            "input_ids": {1: seq_len_dim},
            "cache_position": {0: seq_len_dim},
        }
        self.exported_text_decoder = self.exportable_text_decoder.export(
            input_ids=input_ids,
            cache_position=cache_position,
            dynamic_shapes=dynamic_shapes,
            strict=False,
        )
        return self.exported_text_decoder
    def export(self, **kwargs):
        self.export_vision_encoder(**kwargs)
        self.export_connector(**kwargs)
        self.export_text_decoder(**kwargs)
        return {
            "vision_encoder": self.exported_vision_encoder,
            "connector": self.exported_connector,
            "text_decoder": self.exported_text_decoder,
        }
    def forward(self, pixel_values, input_ids, cache_position):
        pass
    def generate(
        self, pixel_values=None, input_ids=None, max_new_tokens=50, do_sample=False, temperature=1.0, **kwargs
    ):
        pass
class TorchExportableModuleForDecoderOnlyLM(torch.nn.Module):
    def __init__(
        self,
        model: PreTrainedModel,
        batch_size: Optional[int] = None,
        max_cache_len: Optional[int] = None,
        device: Optional[torch.device] = None,
    ) -> None:
        super().__init__()
        config = model.config.get_text_config()
        if not hasattr(config, "use_cache") or config.use_cache is False:
            raise ValueError("The model must have caching enabled to be performant.")
        if hasattr(config, "layer_types") and getattr(config, "sliding_window", None) is not None:
            self.model = TorchExportableModuleWithHybridCache(model, batch_size, max_cache_len, device)
        else:
            logging.info(
                "Using `StaticCache` for export as `layer_types` is not specified or `sliding_window` is `null` in the config."
            )
            self.model = TorchExportableModuleWithStaticCache(model, batch_size, max_cache_len, device)
        ALL_MASK_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", sdpa_mask_without_vmap)
        ALL_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", ALL_ATTENTION_FUNCTIONS["sdpa"])
        self.model.model.config._attn_implementation = "sdpa_without_vmap"
    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        cache_position: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        return self.model.forward(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            cache_position=cache_position,
        )
    def export(
        self,
        input_ids: Optional[torch.Tensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        cache_position: Optional[torch.Tensor] = None,
        dynamic_shapes: Optional[dict] = None,
        strict: Optional[bool] = None,
    ) -> torch.export.ExportedProgram:
        if not (input_ids is None) ^ (inputs_embeds is None):
            raise ValueError("Need to specify either input_ids or inputs_embeds.")
        if hasattr(self.model, "base_model_prefix"):
            base = getattr(self.model, self.model.base_model_prefix, self.model)
            model_device = base.device
        elif hasattr(self.model, "model"):
            model_device = self.model.model.device
        else:
            model_device = "cpu"
            logging.warning(
                "TorchExportableModuleForDecoderOnlyLM.export Can't infer device from the model. Set to CPU by default."
            )
        if input_ids is not None:
            input_kwargs = {
                "input_ids": input_ids,
                "cache_position": cache_position
                if cache_position is not None
                else torch.arange(input_ids.shape[-1], dtype=torch.long, device=model_device),
            }
        else:
            input_kwargs = {
                "inputs_embeds": inputs_embeds,
                "cache_position": cache_position
                if cache_position is not None
                else torch.arange(inputs_embeds.shape[1], dtype=torch.long, device=model_device),
            }
        exported_program = torch.export.export(
            self.model,
            args=(),
            kwargs=input_kwargs,
            dynamic_shapes=dynamic_shapes,
            strict=strict if strict is not None else True,
        )
        return exported_program
    @staticmethod
    def generate(
        exported_program: torch.export.ExportedProgram,
        tokenizer,
        prompt: str,
        max_new_tokens: int = 20,
        do_sample: bool = False,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 1.0,
        device: str = "cpu",
    ) -> str:
        exported_module = exported_program.module()
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
        generated_ids = input_ids.clone()
        curr_position = 0
        for i in range(input_ids.shape[1]):
            curr_input_ids = input_ids[:, i : i + 1]
            curr_cache_position = torch.tensor([curr_position], dtype=torch.long, device=device)
            _ = exported_module(input_ids=curr_input_ids, cache_position=curr_cache_position)
            curr_position += 1
        for _ in range(max_new_tokens):
            curr_input_ids = generated_ids[:, -1:]
            curr_cache_position = torch.tensor([curr_position], dtype=torch.long, device=device)
            outputs = exported_module(input_ids=curr_input_ids, cache_position=curr_cache_position)
            if do_sample:
                if temperature > 0:
                    logits = outputs / temperature
                else:
                    logits = outputs
                if top_k > 0:
                    indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                    logits[indices_to_remove] = float("-inf")
                if top_p < 1.0:
                    sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                    cumulative_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
                    sorted_indices_to_remove = cumulative_probs > top_p
                    sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                    sorted_indices_to_remove[..., 0] = 0
                    indices_to_remove = sorted_indices_to_remove.scatter(-1, sorted_indices, sorted_indices_to_remove)
                    logits[indices_to_remove] = float("-inf")
                probs = torch.softmax(logits, dim=-1)
                next_token_id = torch.multinomial(probs, num_samples=1)
            else:
                next_token_id = outputs.argmax(dim=-1, keepdim=True)
            if next_token_id.dim() > 2:
                next_token_id = next_token_id.squeeze(-1)
            generated_ids = torch.cat([generated_ids, next_token_id], dim=-1)
            curr_position += 1
            if next_token_id.item() == tokenizer.eos_token_id:
                break
        return tokenizer.decode(generated_ids[0], skip_special_tokens=True)
class TorchExportableModuleWithStaticCache(torch.nn.Module):
    def __init__(
        self,
        model: PreTrainedModel,
        batch_size: Optional[int] = None,
        max_cache_len: Optional[int] = None,
        device: Optional[torch.device] = None,
    ) -> None:
        super().__init__()
        config = model.config.get_text_config()
        generation_config = model.generation_config
        if generation_config is None:
            raise AssertionError(
                "The model must have a generation config to be exported with static caching. "
                "Please set `generation_config` in `model`."
            )
        if not generation_config.use_cache:
            raise AssertionError(
                "The model must have caching enabled to be exported with static caching. "
                "Please set `generation_config.use_cache=True`."
            )
        if generation_config.cache_implementation != "static":
            raise AssertionError(
                "The model must use a 'static' caching implementation to be exported with static caching. "
                "Please set `generation_config.cache_implementation='static'`."
            )
        cache_config = {} if generation_config.cache_config is None else generation_config.cache_config
        if batch_size is None:
            batch_size = cache_config.get("batch_size", None)
            if batch_size is None:
                raise ValueError("batch_size must be provided, either as an argument or in cache_config.")
        if max_cache_len is None:
            max_cache_len = cache_config.get("max_cache_len", None)
            if max_cache_len is None:
                raise ValueError("max_cache_len must be provided, either as an argument or in cache_config.")
        if device is None:
            device = cache_config.get("device", model.device)
        self.model = model
        self.static_cache = StaticCache(max_cache_len=max_cache_len, config=config)
        head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        num_heads = getattr(config, "num_key_value_heads", config.num_attention_heads)
        dtype = self.model.dtype
        self.static_cache.early_initialization(batch_size, num_heads, head_dim, dtype, device)
        for i in range(len(self.static_cache)):
            self.register_buffer(f"key_cache_{i}", self.static_cache.layers[i].keys, persistent=False)
            self.register_buffer(f"value_cache_{i}", self.static_cache.layers[i].values, persistent=False)
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        cache_position: Optional[torch.Tensor] = None,
    ):
        past_key_values = self.static_cache
        outs = self.model(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            cache_position=cache_position,
            attention_mask=None,
            past_key_values=past_key_values,
            use_cache=True,
        )
        if hasattr(outs, "logits"):
            return outs.logits
        else:
            return outs.last_hidden_state
    @staticmethod
    def generate(
        exported_program: torch.export.ExportedProgram,
        prompt_token_ids: torch.Tensor,
        max_new_tokens: int,
    ) -> torch.Tensor:
        device = prompt_token_ids.device
        prompt_token_len = prompt_token_ids.shape[-1]
        max_generation_length = prompt_token_len + max_new_tokens
        for buffer_name, buffer in exported_program.named_buffers():
            if buffer_name.startswith("key_cache"):
                max_cache_len = buffer.shape[2]
                max_generation_length = min(max_generation_length, max_cache_len)
                break
        response_tokens = []
        for input_pos in range(min(max_generation_length, prompt_token_len)):
            result = exported_program.module().forward(
                input_ids=prompt_token_ids[:, input_pos : input_pos + 1],
                cache_position=torch.tensor([input_pos], dtype=torch.long, device=device),
            )
            response_tokens.append(prompt_token_ids[0][input_pos].item())
        current_token = torch.argmax(result[:, -1, :], dim=-1).item()
        response_tokens.append(current_token)
        while len(response_tokens) < max_generation_length:
            result = exported_program.module().forward(
                input_ids=torch.tensor([[current_token]], dtype=torch.long, device=device),
                cache_position=torch.tensor([len(response_tokens)], dtype=torch.long, device=device),
            )
            current_token = torch.argmax(result[:, -1, :], dim=-1).item()
            response_tokens.append(current_token)
        return torch.tensor([response_tokens], dtype=torch.long, device=device)
class TorchExportableModuleWithHybridCache(torch.nn.Module):
    def __init__(
        self,
        model: PreTrainedModel,
        batch_size: Optional[int] = None,
        max_cache_len: Optional[int] = None,
        device: Optional[torch.device] = None,
    ) -> None:
        super().__init__()
        self.model = model
        config = model.config.get_text_config()
        generation_config = model.generation_config
        if generation_config is None:
            raise AssertionError(
                "The model must have a generation config to be exported with static caching. "
                "Please set `generation_config` in `model`."
            )
        if not config.use_cache:
            raise AssertionError("Model must have caching enabled.")
        cache_config = {} if generation_config.cache_config is None else generation_config.cache_config
        if batch_size is None:
            batch_size = cache_config.get("batch_size", None)
            if batch_size is None:
                raise ValueError("batch_size must be provided, either as an argument or in cache_config.")
        if max_cache_len is None:
            max_cache_len = cache_config.get("max_cache_len", None)
            if max_cache_len is None:
                raise ValueError("max_cache_len must be provided, either as an argument or in cache_config.")
        if device is None:
            device = cache_config.get("device", model.device)
        self.cache = StaticCache(config=config, max_cache_len=max_cache_len)
        head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        num_heads = getattr(config, "num_key_value_heads", config.num_attention_heads)
        dtype = self.model.dtype
        self.cache.early_initialization(batch_size, num_heads, head_dim, dtype, device)
        for i in range(len(self.cache)):
            self.register_buffer(f"key_cache_{i}", self.cache.layers[i].keys, persistent=False)
            self.register_buffer(f"value_cache_{i}", self.cache.layers[i].values, persistent=False)
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        cache_position: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        outputs = self.model(
            input_ids=input_ids,
            inputs_embeds=inputs_embeds,
            cache_position=cache_position,
            attention_mask=None,
            past_key_values=self.cache,
            use_cache=True,
        )
        return outputs.logits
def convert_and_export_with_cache(
    model: PreTrainedModel,
    example_input_ids: Optional[torch.Tensor] = None,
    example_cache_position: Optional[torch.Tensor] = None,
    dynamic_shapes: Optional[dict] = None,
    strict: Optional[bool] = None,
):
    if not is_torch_greater_or_equal_than_2_3:
        raise ImportError("torch >= 2.3 is required.")
    import torch.export._trace
    ALL_MASK_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", sdpa_mask_without_vmap)
    ALL_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", ALL_ATTENTION_FUNCTIONS["sdpa"])
    model.config._attn_implementation = "sdpa_without_vmap"
    with torch.no_grad():
        example_input_ids = (
            example_input_ids
            if example_input_ids is not None
            else torch.tensor([[1]], dtype=torch.long, device=model.device)
        )
        example_cache_position = (
            example_cache_position
            if example_cache_position is not None
            else torch.tensor([0], dtype=torch.long, device=model.device)
        )
        if is_torch_greater_or_equal("2.6.0"):
            exported_program = torch.export.export(
                TorchExportableModuleWithStaticCache(model),
                args=(),
                kwargs={"input_ids": example_input_ids, "cache_position": example_cache_position},
                dynamic_shapes=dynamic_shapes,
                strict=strict if strict is not None else True,
            )
        else:
            if dynamic_shapes is not None:
                logging.warning(
                    "Dynamic shapes spec will be ignored by convert_and_export_with_cache for torch < 2.6.0."
                )
            if strict is not None:
                logging.warning("The strict flag will be ignored by convert_and_export_with_cache for torch < 2.6.0.")
            exported_program = torch.export._trace._export(
                TorchExportableModuleWithStaticCache(model),
                args=(),
                kwargs={"input_ids": example_input_ids, "cache_position": example_cache_position},
                pre_dispatch=False,
                strict=True,
            )
        return exported_program
class Seq2SeqLMEncoderExportableModule(torch.nn.Module):
    def __init__(self, encoder_model):
        super().__init__()
        self.encoder = encoder_model
    def forward(self, input_ids):
        return self.encoder(input_ids=input_ids).last_hidden_state
class Seq2SeqLMDecoderExportableModuleWithStaticCache(torch.nn.Module):
    def __init__(self, model, max_static_cache_length, batch_size):
        super().__init__()
        self.decoder = model.get_decoder()
        self.lm_head = model.lm_head
        self.config = model.config
        model_device = next(model.parameters()).device
        self.static_cache = StaticCache(config=self.config, max_cache_len=max_static_cache_length)
        head_dim = getattr(self.config, "head_dim", self.config.hidden_size // self.config.num_attention_heads)
        num_heads = getattr(self.config, "num_key_value_heads", self.config.num_attention_heads)
        self.static_cache.early_initialization(batch_size, num_heads, head_dim, torch.float32, model_device)
        self.cache = EncoderDecoderCache(self.static_cache, DynamicCache(config=self.config))
        register_dynamic_cache_export_support()
        for i in range(len(self.static_cache)):
            self.register_buffer(f"key_cache_{i}", self.static_cache.layers[i].keys, persistent=False)
            self.register_buffer(f"value_cache_{i}", self.static_cache.layers[i].values, persistent=False)
    def forward(self, decoder_input_ids, encoder_hidden_states, cache_position):
        outputs = self.decoder(
            input_ids=decoder_input_ids,
            encoder_hidden_states=encoder_hidden_states,
            past_key_values=self.cache,
            use_cache=True,
            cache_position=cache_position,
        )
        lm_logits = self.lm_head(outputs[0])
        return lm_logits
class Seq2SeqLMExportableModule(torch.nn.Module):
    def __init__(
        self, model, batch_size=1, max_hidden_seq_length=4096, cache_implementation="static", max_cache_length=1024
    ):
        super().__init__()
        self.full_model = model
        self.encoder = model.get_encoder()
        self.config = model.config
        self.max_hidden_seq_length = max_hidden_seq_length
        self.generation_config = GenerationConfig(
            use_cache=True,
            max_length=max_cache_length,
            cache_implementation=cache_implementation,
            cache_config={
                "batch_size": batch_size,
                "max_cache_len": max_cache_length,
            },
        )
        self.exported_encoder = None
        self.exported_decoder = None
    def _export_encoder(self, encoder_input_ids):
        wrapped_encoder = Seq2SeqLMEncoderExportableModule(self.encoder).to(self.full_model.device).eval()
        seq_len_dim = torch.export.Dim("encoder_seq_length", max=self.max_hidden_seq_length)
        with torch.no_grad():
            exported_encoder = torch.export.export(
                wrapped_encoder, (encoder_input_ids,), dynamic_shapes={"input_ids": {1: seq_len_dim}}, strict=True
            )
        return exported_encoder
    def _export_decoder(self, decoder_input_ids, encoder_hidden_states, cache_position):
        target_device = self.full_model.device
        wrapped_decoder = (
            Seq2SeqLMDecoderExportableModuleWithStaticCache(
                model=self.full_model,
                max_static_cache_length=self.generation_config.cache_config.get("max_cache_len"),
                batch_size=self.generation_config.cache_config.get("batch_size"),
            )
            .to(target_device)
            .eval()
        )
        decoder_input_ids = decoder_input_ids.to(target_device)
        encoder_hidden_states = encoder_hidden_states.to(target_device)
        cache_position = cache_position.to(target_device)
        encoder_seq_len_dim = torch.export.Dim("encoder_hidden_seq_length", max=self.max_hidden_seq_length)
        with torch.no_grad():
            exported_decoder = torch.export.export(
                wrapped_decoder,
                (decoder_input_ids, encoder_hidden_states, cache_position),
                dynamic_shapes={
                    "decoder_input_ids": None,
                    "encoder_hidden_states": {1: encoder_seq_len_dim},
                    "cache_position": None,
                },
                strict=True,
            )
        return exported_decoder
    def export(self, encoder_input_ids=None, decoder_input_ids=None, encoder_hidden_states=None, cache_position=None):
        device = self.full_model.device
        example_encoder_input_ids = (
            encoder_input_ids
            if encoder_input_ids is not None
            else torch.ones((1, 10), dtype=torch.long, device=device)
        )
        example_decoder_input_ids = (
            decoder_input_ids
            if decoder_input_ids is not None
            else torch.tensor([[0]], dtype=torch.long, device=device)
        )
        example_cache_position = (
            cache_position if cache_position is not None else torch.tensor([0], dtype=torch.long, device=device)
        )
        example_encoder_hidden_states = (
            encoder_hidden_states
            if encoder_hidden_states is not None
            else torch.zeros(
                (self.generation_config.cache_config.get("batch_size"), 10, self.config.d_model),
                dtype=torch.float32,
                device=device,
            )
        )
        self.exported_encoder = self._export_encoder(example_encoder_input_ids)
        self.exported_decoder = self._export_decoder(
            example_decoder_input_ids, example_encoder_hidden_states, example_cache_position
        )
        return self
    def generate(self, prompt_token_ids, max_new_tokens):
        with torch.no_grad():
            model_device = self.full_model.device
            if prompt_token_ids.device != model_device:
                prompt_token_ids = prompt_token_ids.to(model_device)
            encoder_output = self.exported_encoder.module()(prompt_token_ids)
            decoder_input_ids = torch.tensor([[0]], dtype=torch.long, device=model_device)
            generated_ids = [0]
            for i in range(max_new_tokens - 1):
                logits = self.exported_decoder.module()(
                    decoder_input_ids, encoder_output, torch.tensor([i], dtype=torch.long, device=model_device)
                )
                next_token = torch.argmax(logits[:, -1, :], dim=-1).item()
                generated_ids.append(next_token)
                decoder_input_ids = torch.tensor([[next_token]], dtype=torch.long, device=model_device)
                if next_token == self.config.eos_token_id:
                    break
            return generated_ids
def export_with_dynamic_cache(
    model: PreTrainedModel,
    example_input_ids: Optional[torch.Tensor] = None,
    example_attention_mask: Optional[torch.Tensor] = None,
):
    if not is_torch_greater_or_equal_than_2_3:
        raise ImportError("torch >= 2.3 is required.")
    ALL_MASK_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", sdpa_mask_without_vmap)
    ALL_ATTENTION_FUNCTIONS.register("sdpa_without_vmap", ALL_ATTENTION_FUNCTIONS["sdpa"])
    model.config._attn_implementation = "sdpa_without_vmap"
    register_dynamic_cache_export_support()
    with torch.no_grad():
        exported_program = torch.export.export(
            model,
            (),
            {
                "input_ids": example_input_ids,
                "attention_mask": example_attention_mask,
                "past_key_values": DynamicCache(config=model.config),
                "use_cache": True,
            },
            strict=False,
        )
        return exported_program
def register_dynamic_cache_export_support():
    try:
        torch.utils._pytree.register_pytree_node(
            DynamicCache,
            lambda dynamic_cache: torch.utils._pytree._dict_flatten(_get_cache_dict(dynamic_cache)),
            _unflatten_dynamic_cache,
            serialized_type_name=f"{DynamicCache.__module__}.{DynamicCache.__name__}",
            flatten_with_keys_fn=lambda dynamic_cache: torch.utils._pytree._dict_flatten_with_keys(
                _get_cache_dict(dynamic_cache)
            ),
        )
        torch.fx._pytree.register_pytree_flatten_spec(
            DynamicCache,
            lambda cache, spec: torch.fx._pytree._dict_flatten_spec(_get_cache_dict(cache), spec),
        )
    except ValueError as e:
        if "already registered as pytree node" not in str(e):
            raise
def _get_cache_dict(cache: DynamicCache):
    if any(not isinstance(layer, (DynamicLayer, DynamicSlidingWindowLayer)) for layer in cache.layers):
        raise RuntimeError("This pytree flattening function should only be applied to DynamicCache")
    if not is_torch_greater_or_equal_than_2_6:
        logging.warning("DynamicCache + torch.export is tested on torch 2.6.0+ and may not work on earlier versions.")
    return {
        "key_cache": [layer.keys for layer in cache.layers if layer.keys is not None],
        "value_cache": [layer.values for layer in cache.layers if layer.values is not None],
    }
def _unflatten_dynamic_cache(values, context: torch.utils._pytree.Context):
    dictionary = torch.utils._pytree._dict_unflatten(values, context)
    cache = DynamicCache()
    key_list = dictionary.get("key_cache", [])
    value_list = dictionary.get("value_cache", [])
    for idx in range(max(len(key_list), len(value_list))):
        key = key_list[idx] if idx < len(key_list) else None
        value = value_list[idx] if idx < len(value_list) else None
        cache.update(key, value, idx)
    return cache
def sdpa_mask_without_vmap(
    batch_size: int,
    cache_position: torch.Tensor,
    kv_length: int,
    kv_offset: int = 0,
    mask_function: Optional[Callable] = None,
    attention_mask: Optional[torch.Tensor] = None,
    local_size: Optional[int] = None,
    allow_is_causal_skip: bool = True,
    allow_torch_fix: bool = True,
    **kwargs,
) -> Optional[torch.Tensor]:
    q_length = cache_position.shape[0]
    padding_mask = prepare_padding_mask(attention_mask, kv_length, kv_offset)
    if allow_is_causal_skip and _ignore_causal_mask_sdpa(padding_mask, q_length, kv_length, local_size):
        return None
    kv_arange = torch.arange(kv_length, device=cache_position.device)
    kv_arange += kv_offset
    reshaped_cache_position = cache_position.view(-1, 1)
    sliding_window = getattr(kwargs["config"], "sliding_window", None)
    chunk_size = getattr(kwargs["config"], "attention_chunk_size", None)
    if sliding_window is not None and chunk_size is not None:
        raise ValueError("Cannot use both `sliding_window` and `attention_chunk_size`")
    causal_mask = kv_arange <= reshaped_cache_position
    if sliding_window is not None:
        sliding_mask_overlay = kv_arange > reshaped_cache_position - sliding_window
        causal_mask *= sliding_mask_overlay
    elif chunk_size is not None:
        chunked_mask_overlay = kv_arange // chunk_size == reshaped_cache_position // chunk_size
        causal_mask *= chunked_mask_overlay
    causal_mask = causal_mask[None, None, :, :].expand(batch_size, -1, -1, -1)
    if padding_mask is not None:
        causal_mask = causal_mask * padding_mask[:, None, None, :]
    if not _is_torch_greater_or_equal_than_2_5 and allow_torch_fix:
        causal_mask |= torch.all(~causal_mask, dim=-1, keepdim=True)
    return causal_mask