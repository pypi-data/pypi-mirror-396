from dataclasses import dataclass
from typing import Optional, Union
import torch
from torch import nn
from ...cache_utils import Cache
from ...generation import GenerationMixin
from ...modeling_flash_attention_utils import FlashAttentionKwargs
from ...modeling_outputs import BaseModelOutputWithPast, ModelOutput
from ...modeling_utils import PreTrainedModel
from ...processing_utils import Unpack
from ...utils import MEROAIKwargs, auto_docstring
from ...utils.generic import check_model_inputs
from ..auto import AutoModel
from .configuration_cohere2_vision import Cohere2VisionConfig
class Cohere2VisionMultiModalProjector(nn.Module):
    def __init__(self, config: Cohere2VisionConfig):
        super().__init__()
        self.config = config
        self.downsample_factor = config.downsample_factor
        self.intermediate_size = config.alignment_intermediate_size
        self.linear_1 = nn.Linear(
            config.vision_config.hidden_size * (config.downsample_factor**2), self.intermediate_size, bias=True
        )
        self.act = nn.SiLU()
        self.linear_2 = nn.Linear(self.intermediate_size // 2, config.text_config.hidden_size, bias=True)
    def pixel_shuffle(self, image_features):
        batch_size, seq_length, feature_dim = image_features.shape
        height = width = int(seq_length**0.5)
        image_features = image_features.reshape(image_features.shape[0], width, height, -1)
        channels = image_features.shape[-1]
        image_features = image_features.reshape(
            batch_size, width, int(height / self.downsample_factor), int(channels * self.downsample_factor)
        )
        image_features = image_features.permute(0, 2, 1, 3)
        image_features = image_features.reshape(
            batch_size, int(height / self.downsample_factor), int(width / self.downsample_factor), -1
        )
        image_features = image_features.permute(0, 2, 1, 3)
        return image_features
    def forward(self, image_features):
        image_features = self.pixel_shuffle(image_features)
        hidden_states = self.linear_1(image_features)
        x, gate = hidden_states.chunk(2, dim=-1)
        hidden_states = self.act(gate) * x
        hidden_states = self.linear_2(hidden_states)
        return hidden_states
@dataclass
@auto_docstring(
)
class Cohere2VisionModelOutputWithPast(BaseModelOutputWithPast):
    image_hidden_states: Optional[torch.FloatTensor] = None
@dataclass
@auto_docstring(
)
class Cohere2VisionCausalLMOutputWithPast(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[torch.FloatTensor]] = None
    image_hidden_states: Optional[torch.FloatTensor] = None
@auto_docstring
class Cohere2VisionPreTrainedModel(PreTrainedModel):
    config: Cohere2VisionConfig
    base_model_prefix = ""
    supports_gradient_checkpointing = True
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn = True
    _supports_sdpa = True
    _can_compile_fullgraph = False
    _supports_flex_attn = True
    _supports_attention_backend = True
    _can_record_outputs = {
        "hidden_states": "DecoderLayer",
        "attentions": "Attention",
    }
@auto_docstring(
)
class Cohere2VisionModel(Cohere2VisionPreTrainedModel):
    _checkpoint_conversion_mapping = {}
    def __init__(self, config: Cohere2VisionConfig):
        super().__init__(config)
        self.vision_tower = AutoModel.from_config(config.vision_config)
        self.multi_modal_projector = Cohere2VisionMultiModalProjector(config)
        self.language_model = AutoModel.from_config(config.text_config)
        self.post_init()
    def get_input_embeddings(self):
        return self.language_model.get_input_embeddings()
    def set_input_embeddings(self, value):
        self.language_model.set_input_embeddings(value)
    def set_decoder(self, decoder):
        self.language_model = decoder
    def get_decoder(self):
        return self.language_model
    def get_image_features(self, pixel_values: torch.FloatTensor):
        image_features = self.vision_tower(pixel_values, output_hidden_states=True)
        selected_image_feature = image_features.last_hidden_state
        image_features = self.multi_modal_projector(selected_image_feature)
        return image_features
    def get_placeholder_mask(
        self, input_ids: torch.LongTensor, inputs_embeds: torch.FloatTensor, image_features: torch.FloatTensor
    ):
        if input_ids is None:
            special_image_mask = inputs_embeds == self.get_input_embeddings()(
                torch.tensor(self.config.image_token_id, dtype=torch.long, device=inputs_embeds.device)
            )
            special_image_mask = special_image_mask.all(-1)
        else:
            special_image_mask = input_ids == self.config.image_token_id
        n_image_tokens = special_image_mask.sum()
        special_image_mask = special_image_mask.unsqueeze(-1).expand_as(inputs_embeds).to(inputs_embeds.device)
        n_image_features = image_features.shape[0] * image_features.shape[1]
        if inputs_embeds[special_image_mask].numel() != image_features.numel():
            raise ValueError(
                f"Image features and image tokens do not match: tokens: {n_image_tokens}, features {n_image_features}"
            )
        return special_image_mask
    @check_model_inputs()
    @auto_docstring
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[FlashAttentionKwargs],
    ) -> Union[tuple, Cohere2VisionModelOutputWithPast]:
        if (input_ids is None) ^ (inputs_embeds is not None):
            raise ValueError("You must specify exactly one of input_ids or inputs_embeds")
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
        if pixel_values is not None:
            image_features = self.get_image_features(pixel_values)
            image_features = image_features.to(inputs_embeds.device, inputs_embeds.dtype)
            special_image_mask = self.get_placeholder_mask(
                input_ids, inputs_embeds=inputs_embeds, image_features=image_features
            )
            inputs_embeds = inputs_embeds.masked_scatter(special_image_mask, image_features)
        outputs = self.language_model(
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        return Cohere2VisionModelOutputWithPast(
            last_hidden_state=outputs.last_hidden_state,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            image_hidden_states=image_features if pixel_values is not None else None,
        )
@auto_docstring(
)
class Cohere2VisionForConditionalGeneration(Cohere2VisionPreTrainedModel, GenerationMixin):
    _checkpoint_conversion_mapping = {}
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config: Cohere2VisionConfig):
        super().__init__(config)
        self.model = Cohere2VisionModel(config)
        self.lm_head = nn.Linear(config.text_config.hidden_size, config.text_config.vocab_size, bias=False)
        self.post_init()
    def get_input_embeddings(self):
        return self.model.get_input_embeddings()
    def set_input_embeddings(self, value):
        self.model.set_input_embeddings(value)
    def get_output_embeddings(self) -> nn.Module:
        return self.lm_head
    def set_decoder(self, decoder):
        self.model.set_decoder(decoder)
    def get_decoder(self):
        return self.model.get_decoder()
    def get_image_features(self, pixel_values: torch.FloatTensor):
        return self.model.get_image_features(pixel_values=pixel_values)
    @property
    def language_model(self):
        return self.model.language_model
    @property
    def vision_tower(self):
        return self.model.vision_tower
    @property
    def multi_modal_projector(self):
        return self.model.multi_modal_projector
    @check_model_inputs()
    @auto_docstring
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        logits_to_keep: Union[int, torch.Tensor] = 0,
        image_sizes: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> Union[tuple, Cohere2VisionCausalLMOutputWithPast]:
        outputs = self.model(
            input_ids=input_ids,
            pixel_values=pixel_values,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            image_sizes=image_sizes,
            **kwargs,
        )
        hidden_states = outputs[0]
        slice_indices = slice(-logits_to_keep, None) if isinstance(logits_to_keep, int) else logits_to_keep
        logits = self.lm_head(hidden_states[:, slice_indices, :])
        loss = None
        if labels is not None:
            loss = self.loss_function(
                logits=logits, labels=labels, vocab_size=self.config.text_config.vocab_size, **kwargs
            )
        return Cohere2VisionCausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            image_hidden_states=outputs.image_hidden_states,
        )
    def prepare_inputs_for_generation(
        self,
        input_ids,
        past_key_values=None,
        inputs_embeds=None,
        pixel_values=None,
        attention_mask=None,
        cache_position=None,
        logits_to_keep=None,
        **kwargs,
    ):
        model_inputs = super().prepare_inputs_for_generation(
            input_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            cache_position=cache_position,
            logits_to_keep=logits_to_keep,
            **kwargs,
        )
        if cache_position[0] == 0:
            model_inputs["pixel_values"] = pixel_values
        return model_inputs
__all__ = ["Cohere2VisionForConditionalGeneration", "Cohere2VisionPreTrainedModel", "Cohere2VisionModel"]