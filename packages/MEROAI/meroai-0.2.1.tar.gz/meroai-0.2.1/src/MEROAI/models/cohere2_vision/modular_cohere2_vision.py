from functools import lru_cache
from typing import Optional, Union
import numpy as np
import torch
from torch import nn
from MEROAI.models.aya_vision.modeling_aya_vision import (
    AyaVisionCausalLMOutputWithPast,
    AyaVisionForConditionalGeneration,
    AyaVisionModel,
    AyaVisionModelOutputWithPast,
)
from MEROAI.models.got_ocr2.image_processing_got_ocr2_fast import GotOcr2ImageProcessorFast
from ...cache_utils import Cache
from ...modeling_flash_attention_utils import FlashAttentionKwargs
from ...processing_utils import Unpack
from ...utils import MEROAIKwargs, auto_docstring, logging
from ...utils.generic import check_model_inputs
from .configuration_cohere2_vision import Cohere2VisionConfig
logger = logging.get_logger(__name__)
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
class Cohere2VisionModelOutputWithPast(AyaVisionModelOutputWithPast):
    pass
class Cohere2VisionCausalLMOutputWithPast(AyaVisionCausalLMOutputWithPast):
    pass
class Cohere2VisionModel(AyaVisionModel):
    _checkpoint_conversion_mapping = {}
    def get_image_features(self, pixel_values: torch.FloatTensor):
        image_features = self.vision_tower(pixel_values, output_hidden_states=True)
        selected_image_feature = image_features.last_hidden_state
        image_features = self.multi_modal_projector(selected_image_feature)
        return image_features
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
class Cohere2VisionForConditionalGeneration(AyaVisionForConditionalGeneration):
    _checkpoint_conversion_mapping = {}
    def get_image_features(self, pixel_values: torch.FloatTensor):
        return self.model.get_image_features(pixel_values=pixel_values)
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
@lru_cache(maxsize=10)
def get_all_supported_aspect_ratios(max_image_tiles: int) -> list[tuple[int, int]]:
    aspect_ratios = []
    for width in range(1, max_image_tiles + 1):
        for height in range(1, max_image_tiles + 1):
            if width * height <= max_image_tiles:
                aspect_ratios.append((width, height))
    return aspect_ratios
def get_optimal_tiled_canvas(
    original_image_size: tuple[int, int],
    target_tile_size: tuple[int, int],
    min_image_tiles: int,
    max_image_tiles: int,
) -> tuple[int, int]:
    possible_resolutions = get_all_supported_aspect_ratios(max_image_tiles)
    possible_resolutions = sorted(possible_resolutions, key=lambda x: x[0] * x[1])
    image_height, image_width = original_image_size
    patch_size_height, patch_size_width = target_tile_size
    candidate_resolutions = np.array(possible_resolutions) * patch_size_height
    original_size = np.stack([image_height, image_width])
    required_scales = candidate_resolutions / original_size
    required_scale = np.min(required_scales, axis=-1, keepdims=True)
    if np.all(required_scale < 1):
        best_grid = possible_resolutions[np.argmax(required_scale)]
    else:
        required_scale = np.where(required_scale < 1.0, 10e9, required_scale)
        best_grid = possible_resolutions[np.argmin(required_scale)]
    return best_grid
@auto_docstring
class Cohere2VisionImageProcessorFast(GotOcr2ImageProcessorFast):
    size = {"height": 512, "width": 512}
    min_patches = 1
    max_patches = 12
    crop_to_patches = True
    patch_size = 16
__all__ = [
    "Cohere2VisionForConditionalGeneration",
    "Cohere2VisionPreTrainedModel",
    "Cohere2VisionModel",
    "Cohere2VisionImageProcessorFast",
]