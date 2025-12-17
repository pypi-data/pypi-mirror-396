import math
from dataclasses import dataclass
from typing import Callable, Optional, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from MEROAI.utils.generic import OutputRecorder, MEROAIKwargs, check_model_inputs
from ...activations import ACT2FN
from ...modeling_outputs import BaseModelOutput
from ...modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from ...processing_utils import Unpack
from ...pytorch_utils import compile_compatible_method_lru_cache
from ...utils import ModelOutput, auto_docstring
from ..auto import AutoModel
from .configuration_edgetam import (
    EdgeTamConfig,
    EdgeTamMaskDecoderConfig,
    EdgeTamPromptEncoderConfig,
    EdgeTamVisionConfig,
)
if True:
    from MEROAI.models.timm_wrapper.modeling_timm_wrapper import TimmWrapperModel
class EdgeTamLayerNorm(nn.LayerNorm):
    def __init__(self, normalized_shape, *, eps=1e-6, data_format="channels_last", **kwargs):
        super().__init__(normalized_shape, eps=eps, **kwargs)
        if data_format not in ["channels_last", "channels_first"]:
            raise NotImplementedError(f"Unsupported data format: {data_format}")
        self.data_format = data_format
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        if self.data_format == "channels_first":
            features = features.permute(0, 2, 3, 1)
            features = super().forward(features)
            features = features.permute(0, 3, 1, 2)
        else:
            features = super().forward(features)
        return features
@dataclass
@auto_docstring(custom_intro="Base class for the vision encoder's outputs.")
class EdgeTamVisionEncoderOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    fpn_hidden_states: Optional[torch.FloatTensor] = None
    fpn_position_encoding: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
def eager_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Optional[torch.Tensor],
    scaling: float,
    dropout: float = 0.0,
    **kwargs,
):
    attn_weights = torch.matmul(query, key.transpose(2, 3)) * scaling
    if attention_mask is not None:
        attn_weights = attn_weights + attention_mask
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
    attn_weights = nn.functional.dropout(attn_weights, p=dropout, training=module.training)
    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attn_weights
class EdgeTamAttention(nn.Module):
    def __init__(self, config, downsample_rate=None):
        super().__init__()
        downsample_rate = config.attention_downsample_rate if downsample_rate is None else downsample_rate
        self.config = config
        self.hidden_size = config.hidden_size
        self.internal_dim = config.hidden_size // downsample_rate
        self.num_attention_heads = config.num_attention_heads
        self.head_dim = self.internal_dim // config.num_attention_heads
        self.scaling = self.head_dim**-0.5
        self.is_causal = False
        self.q_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.k_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.v_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.o_proj = nn.Linear(self.internal_dim, self.hidden_size)
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attention_similarity: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, point_batch_size = query.shape[:2]
        new_shape = (batch_size * point_batch_size, -1, self.num_attention_heads, self.head_dim)
        query = self.q_proj(query).view(*new_shape).transpose(1, 2)
        key = self.k_proj(key).view(*new_shape).transpose(1, 2)
        value = self.v_proj(value).view(*new_shape).transpose(1, 2)
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, attn_weights = attention_interface(
            self,
            query,
            key,
            value,
            attention_mask=attention_similarity,
            dropout=0.0,
            scaling=self.scaling,
            is_causal=self.is_causal,
            **kwargs,
        )
        attn_output = attn_output.reshape(
            batch_size, point_batch_size, -1, self.num_attention_heads * self.head_dim
        ).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights
class EdgeTamTwoWayAttentionBlock(nn.Module):
    def __init__(self, config: EdgeTamMaskDecoderConfig, skip_first_layer_pe: bool = False):
        super().__init__()
        self.self_attn = EdgeTamAttention(config, downsample_rate=1)
        self.layer_norm1 = nn.LayerNorm(config.hidden_size)
        self.cross_attn_token_to_image = EdgeTamAttention(config)
        self.layer_norm2 = nn.LayerNorm(config.hidden_size)
        self.mlp = EdgeTamFeedForward(
            config.hidden_size, config.mlp_dim, config.hidden_size, num_layers=config.num_hidden_layers
        )
        self.layer_norm3 = nn.LayerNorm(config.hidden_size)
        self.layer_norm4 = nn.LayerNorm(config.hidden_size)
        self.cross_attn_image_to_token = EdgeTamAttention(config)
        self.skip_first_layer_pe = skip_first_layer_pe
    def forward(
        self,
        queries: Tensor,
        keys: Tensor,
        query_point_embedding: Tensor,
        key_point_embedding: Tensor,
        attention_similarity: Tensor,
        **kwargs: Unpack[MEROAIKwargs],
    ):
        if self.skip_first_layer_pe:
            queries, _ = self.self_attn(query=queries, key=queries, value=queries)
        else:
            query = queries + query_point_embedding
            attn_out, _ = self.self_attn(query=query, key=query, value=queries)
            queries = queries + attn_out
        queries = self.layer_norm1(queries)
        query = queries + query_point_embedding
        key = keys + key_point_embedding
        attn_out, _ = self.cross_attn_token_to_image(
            query=query, key=key, value=keys, attention_similarity=attention_similarity
        )
        queries = queries + attn_out
        queries = self.layer_norm2(queries)
        mlp_out = self.mlp(queries)
        queries = queries + mlp_out
        queries = self.layer_norm3(queries)
        query = queries + query_point_embedding
        key = keys + key_point_embedding
        attn_out, _ = self.cross_attn_image_to_token(query=key, key=query, value=queries)
        keys = keys + attn_out
        keys = self.layer_norm4(keys)
        return queries, keys, attn_out
class EdgeTamFeedForward(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        num_layers: int,
        activation: str = "relu",
        sigmoid_output: bool = False,
    ):
        super().__init__()
        self.num_layers = num_layers
        self.activation = ACT2FN[activation]
        self.proj_in = nn.Linear(input_dim, hidden_dim)
        self.proj_out = nn.Linear(hidden_dim, output_dim)
        self.layers = nn.ModuleList([nn.Linear(hidden_dim, hidden_dim) for _ in range(num_layers - 2)])
        self.sigmoid_output = sigmoid_output
    def forward(self, hidden_states):
        hidden_states = self.proj_in(hidden_states)
        hidden_states = self.activation(hidden_states)
        for layer in self.layers:
            hidden_states = self.activation(layer(hidden_states))
        hidden_states = self.proj_out(hidden_states)
        if self.sigmoid_output:
            hidden_states = F.sigmoid(hidden_states)
        return hidden_states
@auto_docstring
class EdgeTamPreTrainedModel(PreTrainedModel):
    config_class = EdgeTamConfig
    base_model_prefix = "edgetam"
    main_input_name = "pixel_values"
    _supports_sdpa = True
    _supports_flash_attn_2 = True
    _supports_attention_backend = True
    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, (nn.LayerNorm, EdgeTamLayerNorm)):
            module.weight.data.fill_(1.0)
            module.bias.data.zero_()
        if isinstance(module, EdgeTamModel):
            if module.no_memory_embedding is not None:
                module.no_memory_embedding.data.zero_()
class EdgeTamSinePositionEmbedding(nn.Module):
    def __init__(
        self, num_pos_feats: int = 64, temperature: int = 10000, normalize: bool = False, scale: Optional[float] = None
    ):
        super().__init__()
        if scale is not None and normalize is False:
            raise ValueError("normalize should be True if scale is passed")
        self.num_pos_feats = num_pos_feats
        self.temperature = temperature
        self.normalize = normalize
        self.scale = 2 * math.pi if scale is None else scale
    @compile_compatible_method_lru_cache(maxsize=1)
    def forward(
        self,
        shape: torch.Size,
        device: Union[torch.device, str],
        dtype: torch.dtype,
        mask: Optional[Tensor] = None,
    ) -> Tensor:
        if mask is None:
            mask = torch.zeros((shape[0], shape[2], shape[3]), device=device, dtype=torch.bool)
        not_mask = (~mask).to(dtype)
        y_embed = not_mask.cumsum(1)
        x_embed = not_mask.cumsum(2)
        if self.normalize:
            eps = 1e-6
            y_embed = y_embed / (y_embed[:, -1:, :] + eps) * self.scale
            x_embed = x_embed / (x_embed[:, :, -1:] + eps) * self.scale
        dim_t = torch.arange(self.num_pos_feats, dtype=torch.int64, device=device).to(dtype)
        dim_t = self.temperature ** (2 * torch.div(dim_t, 2, rounding_mode="floor") / self.num_pos_feats)
        pos_x = x_embed[:, :, :, None] / dim_t
        pos_y = y_embed[:, :, :, None] / dim_t
        pos_x = torch.stack((pos_x[:, :, :, 0::2].sin(), pos_x[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos_y = torch.stack((pos_y[:, :, :, 0::2].sin(), pos_y[:, :, :, 1::2].cos()), dim=4).flatten(3)
        pos = torch.cat((pos_y, pos_x), dim=3).permute(0, 3, 1, 2)
        return pos
class EdgeTamVisionNeck(nn.Module):
    def __init__(self, config: EdgeTamVisionConfig):
        super().__init__()
        self.config = config
        self.position_encoding = EdgeTamSinePositionEmbedding(
            num_pos_feats=config.fpn_hidden_size // 2, normalize=True
        )
        self.convs = nn.ModuleList()
        for in_channels in config.backbone_channel_list:
            self.convs.append(
                nn.Conv2d(
                    in_channels=in_channels,
                    out_channels=config.fpn_hidden_size,
                    kernel_size=config.fpn_kernel_size,
                    stride=config.fpn_stride,
                    padding=config.fpn_padding,
                ),
            )
        self.fpn_top_down_levels = config.fpn_top_down_levels
    def forward(self, hidden_states: torch.Tensor) -> tuple[tuple[torch.Tensor, ...], tuple[torch.Tensor, ...]]:
        fpn_hidden_states = ()
        fpn_position_encoding = ()
        n = len(self.convs) - 1
        for i in range(n, -1, -1):
            lateral_features = hidden_states[i].permute(0, 3, 1, 2)
            lateral_features = self.convs[n - i](lateral_features)
            if i not in self.fpn_top_down_levels or i == n:
                prev_features = lateral_features
            else:
                top_down_features = F.interpolate(
                    prev_features.to(dtype=torch.float32),
                    scale_factor=2.0,
                    mode="nearest",
                    align_corners=None,
                    antialias=False,
                ).to(lateral_features.dtype)
                prev_features = lateral_features + top_down_features
            prev_position_encoding = self.position_encoding(
                prev_features.shape, prev_features.device, prev_features.dtype
            ).to(prev_features.dtype)
            fpn_hidden_states += (prev_features,)
            fpn_position_encoding += (prev_position_encoding,)
        return fpn_hidden_states, fpn_position_encoding
@auto_docstring(
)
class EdgeTamVisionModel(EdgeTamPreTrainedModel):
    config_class = EdgeTamVisionConfig
    main_input_name = "pixel_values"
    _can_record_outputs = {"hidden_states": TimmWrapperModel, "attentions": TimmWrapperModel}
    def __init__(self, config: EdgeTamVisionConfig):
        super().__init__(config)
        self.config = config
        self.backbone = AutoModel.from_config(config.backbone_config)
        self.neck = EdgeTamVisionNeck(config)
        self.num_feature_levels = config.num_feature_levels
        self.post_init()
    @check_model_inputs()
    def forward(
        self,
        pixel_values: Optional[torch.FloatTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> Union[tuple, EdgeTamVisionEncoderOutput]:
        if pixel_values is None:
            raise ValueError("You have to specify pixel_values")
        backbone_output = self.backbone(pixel_values)
        intermediate_hidden_states = backbone_output.last_hidden_state
        intermediate_hidden_states = [hidden_state.permute(0, 2, 3, 1) for hidden_state in intermediate_hidden_states]
        fpn_hidden_states, fpn_position_encoding = self.neck(intermediate_hidden_states)
        fpn_hidden_states = fpn_hidden_states[-self.num_feature_levels :][::-1]
        fpn_position_encoding = fpn_position_encoding[-self.num_feature_levels :][::-1]
        return EdgeTamVisionEncoderOutput(
            last_hidden_state=intermediate_hidden_states[-1],
            fpn_hidden_states=fpn_hidden_states,
            fpn_position_encoding=fpn_position_encoding,
        )
@dataclass
@auto_docstring(custom_intro="Base class for the EdgeTam model's output.")
class EdgeTamImageSegmentationOutput(ModelOutput):
    iou_scores: Optional[torch.FloatTensor] = None
    pred_masks: Optional[torch.FloatTensor] = None
    object_score_logits: Optional[torch.FloatTensor] = None
    image_embeddings: tuple[torch.FloatTensor, ...] = None
    vision_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    vision_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    mask_decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
class EdgeTamPositionalEmbedding(nn.Module):
    def __init__(self, config: EdgeTamPromptEncoderConfig):
        super().__init__()
        self.scale = config.scale
        positional_embedding = self.scale * torch.randn((2, config.hidden_size // 2))
        self.register_buffer("positional_embedding", positional_embedding)
    def forward(self, input_coords, input_shape=None):
        coordinates = input_coords.clone()
        if input_shape is not None:
            coordinates[:, :, :, 0] = coordinates[:, :, :, 0] / input_shape[1]
            coordinates[:, :, :, 1] = coordinates[:, :, :, 1] / input_shape[0]
        coordinates.to(torch.float32)
        coordinates = 2 * coordinates - 1
        coordinates = coordinates.to(self.positional_embedding.dtype)
        coordinates = coordinates @ self.positional_embedding
        coordinates = 2 * np.pi * coordinates
        return torch.cat([torch.sin(coordinates), torch.cos(coordinates)], dim=-1)
class EdgeTamMaskEmbedding(nn.Module):
    def __init__(self, config: EdgeTamPromptEncoderConfig):
        super().__init__()
        self.mask_input_channels = config.mask_input_channels // 4
        self.activation = ACT2FN[config.hidden_act]
        self.conv1 = nn.Conv2d(1, self.mask_input_channels, kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(self.mask_input_channels, config.mask_input_channels, kernel_size=2, stride=2)
        self.conv3 = nn.Conv2d(config.mask_input_channels, config.hidden_size, kernel_size=1)
        self.layer_norm1 = EdgeTamLayerNorm(
            self.mask_input_channels, eps=config.layer_norm_eps, data_format="channels_first"
        )
        self.layer_norm2 = EdgeTamLayerNorm(
            self.mask_input_channels * 4, eps=config.layer_norm_eps, data_format="channels_first"
        )
    def forward(self, masks):
        hidden_states = self.conv1(masks)
        hidden_states = self.layer_norm1(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.conv2(hidden_states)
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.activation(hidden_states)
        dense_embeddings = self.conv3(hidden_states)
        return dense_embeddings
class EdgeTamPromptEncoder(nn.Module):
    def __init__(self, config: EdgeTamPromptEncoderConfig):
        super().__init__()
        self.shared_embedding = EdgeTamPositionalEmbedding(config)
        self.mask_embed = EdgeTamMaskEmbedding(config)
        self.no_mask_embed = nn.Embedding(1, config.hidden_size)
        self.image_embedding_size = (config.image_size // config.patch_size, config.image_size // config.patch_size)
        self.mask_input_size = (4 * config.image_size // config.patch_size, 4 * config.image_size // config.patch_size)
        self.input_image_size = config.image_size
        self.point_embed = nn.Embedding(config.num_point_embeddings, config.hidden_size)
        self.hidden_size = config.hidden_size
        self.not_a_point_embed = nn.Embedding(1, config.hidden_size)
    def _embed_points(self, points: torch.Tensor, labels: torch.Tensor, pad: bool) -> torch.Tensor:
        points = points + 0.5
        if pad:
            points = torch.nn.functional.pad(points, (0, 0, 0, 1), mode="constant", value=0)
            labels = torch.nn.functional.pad(labels, (0, 1), mode="constant", value=-1)
        input_shape = (self.input_image_size, self.input_image_size)
        point_embedding = self.shared_embedding(points, input_shape)
        point_embedding = torch.where(labels[..., None] == -1, self.not_a_point_embed.weight, point_embedding)
        point_embedding = torch.where(
            labels[..., None] != -10,
            point_embedding,
            torch.zeros_like(point_embedding),
        )
        point_embedding = point_embedding + self.point_embed(labels.clamp(min=0)) * (labels >= 0).unsqueeze(-1)
        return point_embedding
    def _embed_boxes(self, boxes: torch.Tensor) -> torch.Tensor:
        boxes += 0.5
        coords = boxes.view(*boxes.shape[:2], 2, 2)
        coords = torch.nn.functional.pad(coords, (0, 0, 0, 1), mode="constant", value=0)
        corner_embedding = self.shared_embedding(coords, (self.input_image_size, self.input_image_size))
        corner_embedding[:, :, 0, :] += self.point_embed.weight[2]
        corner_embedding[:, :, 1, :] += self.point_embed.weight[3]
        corner_embedding[:, :, 2, :] = self.not_a_point_embed.weight.expand_as(corner_embedding[:, :, 2, :])
        return corner_embedding
    def forward(
        self,
        input_points: Optional[tuple[torch.Tensor, torch.Tensor]],
        input_labels: Optional[torch.Tensor],
        input_boxes: Optional[torch.Tensor],
        input_masks: Optional[torch.Tensor],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        sparse_embeddings = None
        batch_size = 1
        if input_points is not None:
            batch_size = input_points.shape[0]
            if input_labels is None:
                raise ValueError("If points are provided, labels must also be provided.")
            point_embeddings = self._embed_points(input_points, input_labels, pad=(input_boxes is None))
            sparse_embeddings = point_embeddings
        if input_boxes is not None:
            batch_size = input_boxes.shape[0]
            box_embeddings = self._embed_boxes(input_boxes)
            if sparse_embeddings is None:
                sparse_embeddings = box_embeddings
            else:
                sparse_embeddings = torch.cat([sparse_embeddings, box_embeddings], dim=2)
        if input_masks is not None:
            dense_embeddings = self.mask_embed(input_masks)
        else:
            dense_embeddings = self.no_mask_embed.weight.reshape(1, -1, 1, 1).expand(
                batch_size, -1, self.image_embedding_size[0], self.image_embedding_size[1]
            )
        return sparse_embeddings, dense_embeddings
class EdgeTamTwoWayTransformer(nn.Module):
    def __init__(self, config: EdgeTamMaskDecoderConfig):
        super().__init__()
        self.config = config
        self.num_hidden_layers = config.num_hidden_layers
        self.layers = nn.ModuleList()
        for i in range(self.num_hidden_layers):
            self.layers.append(EdgeTamTwoWayAttentionBlock(config, skip_first_layer_pe=(i == 0)))
        self.final_attn_token_to_image = EdgeTamAttention(config)
        self.layer_norm_final_attn = nn.LayerNorm(config.hidden_size)
    def forward(
        self,
        point_embeddings: Tensor,
        image_embeddings: Tensor,
        image_positional_embeddings: Tensor,
        attention_similarity: Tensor,
        target_embedding=None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> Union[tuple, BaseModelOutput]:
        if image_embeddings is None:
            raise ValueError("You have to specify an image_embedding")
        image_embeddings = image_embeddings.flatten(2).permute(0, 2, 1).unsqueeze(1)
        image_positional_embeddings = image_positional_embeddings.flatten(2).permute(0, 2, 1).unsqueeze(1)
        queries = point_embeddings
        keys = image_embeddings
        for layer in self.layers:
            if target_embedding is not None:
                queries += target_embedding
            queries, keys, _ = layer(
                queries=queries,
                keys=keys,
                query_point_embedding=point_embeddings,
                key_point_embedding=image_positional_embeddings,
                attention_similarity=attention_similarity,
                **kwargs,
            )
        query = queries + point_embeddings
        key = keys + image_positional_embeddings
        attn_out, _ = self.final_attn_token_to_image(query=query, key=key, value=keys)
        queries = queries + attn_out
        queries = self.layer_norm_final_attn(queries)
        return queries, keys
class EdgeTamMaskDecoder(nn.Module):
    def __init__(self, config: EdgeTamMaskDecoderConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_multimask_outputs = config.num_multimask_outputs
        self.num_mask_tokens = config.num_multimask_outputs + 1
        self.iou_token = nn.Embedding(1, self.hidden_size)
        self.mask_tokens = nn.Embedding(self.num_mask_tokens, self.hidden_size)
        self.transformer = EdgeTamTwoWayTransformer(config)
        self.upscale_conv1 = nn.ConvTranspose2d(self.hidden_size, self.hidden_size // 4, kernel_size=2, stride=2)
        self.upscale_conv2 = nn.ConvTranspose2d(self.hidden_size // 4, self.hidden_size // 8, kernel_size=2, stride=2)
        self.upscale_layer_norm = EdgeTamLayerNorm(self.hidden_size // 4, data_format="channels_first")
        self.activation = nn.GELU()
        mlps_list = []
        for _ in range(self.num_mask_tokens):
            mlps_list += [EdgeTamFeedForward(self.hidden_size, self.hidden_size, self.hidden_size // 8, 3)]
        self.output_hypernetworks_mlps = nn.ModuleList(mlps_list)
        self.iou_prediction_head = EdgeTamFeedForward(
            self.hidden_size,
            config.iou_head_hidden_dim,
            self.num_mask_tokens,
            config.iou_head_depth,
            sigmoid_output=True,
        )
        self.conv_s0 = nn.Conv2d(config.hidden_size, config.hidden_size // 8, kernel_size=1, stride=1)
        self.conv_s1 = nn.Conv2d(config.hidden_size, config.hidden_size // 4, kernel_size=1, stride=1)
        self.obj_score_token = nn.Embedding(1, self.hidden_size)
        self.pred_obj_score_head = EdgeTamFeedForward(self.hidden_size, self.hidden_size, 1, 3)
        self.dynamic_multimask_via_stability = config.dynamic_multimask_via_stability
        self.dynamic_multimask_stability_delta = config.dynamic_multimask_stability_delta
        self.dynamic_multimask_stability_thresh = config.dynamic_multimask_stability_thresh
    def forward(
        self,
        image_embeddings: torch.Tensor,
        image_positional_embeddings: torch.Tensor,
        sparse_prompt_embeddings: torch.Tensor,
        dense_prompt_embeddings: torch.Tensor,
        multimask_output: bool,
        high_resolution_features: list[torch.Tensor],
        attention_similarity: Optional[torch.Tensor] = None,
        target_embedding: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        batch_size, num_channels, height, width = image_embeddings.shape
        point_batch_size = sparse_prompt_embeddings.shape[1]
        output_tokens = torch.cat(
            [
                self.obj_score_token.weight,
                self.iou_token.weight,
                self.mask_tokens.weight,
            ],
            dim=0,
        )
        output_tokens = output_tokens.repeat(batch_size, point_batch_size, 1, 1)
        if sparse_prompt_embeddings.shape[0] != 0:
            tokens = torch.cat((output_tokens, sparse_prompt_embeddings), dim=2)
        else:
            tokens = output_tokens
        point_embeddings = tokens.to(self.iou_token.weight.dtype)
        image_embeddings = image_embeddings + dense_prompt_embeddings
        image_embeddings = image_embeddings.repeat_interleave(point_batch_size, dim=0)
        image_positional_embeddings = image_positional_embeddings.repeat_interleave(point_batch_size, 0)
        point_embeddings, image_embeddings = self.transformer(
            point_embeddings=point_embeddings,
            image_embeddings=image_embeddings,
            image_positional_embeddings=image_positional_embeddings,
            attention_similarity=attention_similarity,
            target_embedding=target_embedding,
            **kwargs,
        )
        iou_token_out = point_embeddings[:, :, 1, :]
        mask_tokens_out = point_embeddings[:, :, 2 : (2 + self.num_mask_tokens), :]
        image_embeddings = image_embeddings.transpose(2, 3).view(
            batch_size * point_batch_size, num_channels, height, width
        )
        feat_s0, feat_s1 = high_resolution_features
        feat_s0 = feat_s0.repeat_interleave(point_batch_size, dim=0)
        feat_s1 = feat_s1.repeat_interleave(point_batch_size, dim=0)
        upscaled_embedding = self.upscale_conv1(image_embeddings) + feat_s1
        upscaled_embedding = self.activation(self.upscale_layer_norm(upscaled_embedding))
        upscaled_embedding = self.activation(self.upscale_conv2(upscaled_embedding) + feat_s0)
        hyper_in_list: list[torch.Tensor] = []
        for i in range(self.num_mask_tokens):
            current_mlp = self.output_hypernetworks_mlps[i]
            hyper_in_list += [current_mlp(mask_tokens_out[:, :, i, :])]
        hyper_in = torch.stack(hyper_in_list, dim=2)
        _, num_channels, height, width = upscaled_embedding.shape
        upscaled_embedding = upscaled_embedding.view(batch_size, point_batch_size, num_channels, height * width)
        masks = (hyper_in @ upscaled_embedding).view(batch_size, point_batch_size, -1, height, width)
        iou_pred = self.iou_prediction_head(iou_token_out)
        object_score_logits = self.pred_obj_score_head(point_embeddings[:, :, 0, :])
        if multimask_output:
            mask_slice = slice(1, None)
            masks = masks[:, :, mask_slice, :, :]
            iou_pred = iou_pred[:, :, mask_slice]
        elif self.dynamic_multimask_via_stability and not self.training:
            mask_slice = slice(0, 1)
            masks, iou_pred = self._dynamic_multimask_via_stability(masks, iou_pred)
        else:
            mask_slice = slice(0, 1)
            masks = masks[:, :, mask_slice, :, :]
            iou_pred = iou_pred[:, :, mask_slice]
        sam_tokens_out = mask_tokens_out[:, :, mask_slice]
        return masks, iou_pred, sam_tokens_out, object_score_logits
    def _get_stability_scores(self, mask_logits):
        mask_logits = mask_logits.flatten(-2)
        stability_delta = self.dynamic_multimask_stability_delta
        area_i = torch.sum(mask_logits > stability_delta, dim=-1).float()
        area_u = torch.sum(mask_logits > -stability_delta, dim=-1).float()
        stability_scores = torch.where(area_u > 0, area_i / area_u, 1.0)
        return stability_scores
    def _dynamic_multimask_via_stability(self, all_mask_logits, all_iou_scores):
        multimask_logits = all_mask_logits[:, :, 1:, :, :]
        multimask_iou_scores = all_iou_scores[:, :, 1:]
        best_scores_inds = torch.argmax(multimask_iou_scores, dim=-1)
        best_scores_inds_expanded = best_scores_inds.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
        best_scores_inds_expanded = best_scores_inds_expanded.expand(
            -1, -1, 1, multimask_logits.size(-2), multimask_logits.size(-1)
        )
        best_multimask_logits = torch.gather(multimask_logits, 2, best_scores_inds_expanded)
        best_multimask_iou_scores = torch.gather(multimask_iou_scores, 2, best_scores_inds.unsqueeze(-1))
        singlemask_logits = all_mask_logits[:, :, 0:1, :, :]
        singlemask_iou_scores = all_iou_scores[:, :, 0:1]
        stability_scores = self._get_stability_scores(singlemask_logits)
        is_stable = stability_scores >= self.dynamic_multimask_stability_thresh
        mask_logits_out = torch.where(
            is_stable[..., None, None].expand_as(singlemask_logits),
            singlemask_logits,
            best_multimask_logits,
        )
        iou_scores_out = torch.where(
            is_stable.expand_as(singlemask_iou_scores),
            singlemask_iou_scores,
            best_multimask_iou_scores,
        )
        return mask_logits_out, iou_scores_out
@auto_docstring(
)
class EdgeTamModel(EdgeTamPreTrainedModel):
    _tied_weights_keys = ["prompt_encoder.shared_embedding.positional_embedding"]
    _keys_to_ignore_on_load_missing = ["prompt_encoder.shared_embedding.positional_embedding"]
    _can_record_outputs = {"mask_decoder_attentions": OutputRecorder(EdgeTamTwoWayAttentionBlock, index=2)}
    _keys_to_ignore_on_load_unexpected = [
        r"^memory_.*",
        r"^mask_downsample.*",
        r"spatial_perceiver.*",
        r"^object_pointer_proj.*",
        r"^temporal_positional_encoding_projection_layer.*",
        "no_memory_positional_encoding",
        "no_object_pointer",
        "occlusion_spatial_embedding_parameter",
    ]
    def __init__(self, config: EdgeTamConfig):
        super().__init__(config)
        self.shared_image_embedding = EdgeTamPositionalEmbedding(config.prompt_encoder_config)
        self.vision_encoder = AutoModel.from_config(config.vision_config)
        self.prompt_encoder = EdgeTamPromptEncoder(config.prompt_encoder_config)
        config.mask_decoder_config._attn_implementation = config._attn_implementation
        self.mask_decoder = EdgeTamMaskDecoder(config.mask_decoder_config)
        self.num_feature_levels = config.vision_config.num_feature_levels
        self.backbone_feature_sizes = config.vision_config.backbone_feature_sizes
        self.hidden_dim = config.vision_config.fpn_hidden_size
        self.no_memory_embedding = torch.nn.Parameter(torch.zeros(1, 1, self.hidden_dim))
        self.post_init()
    def _tie_weights(self):
        self.prompt_encoder.shared_embedding.positional_embedding.data = (
            self.shared_image_embedding.positional_embedding.data
        )
    def get_image_wide_positional_embeddings(self) -> torch.Tensor:
        size = self.prompt_encoder.image_embedding_size
        target_device = self.shared_image_embedding.positional_embedding.device
        target_dtype = self.shared_image_embedding.positional_embedding.dtype
        grid = torch.ones(size, device=target_device, dtype=target_dtype)
        y_embed = grid.cumsum(dim=0) - 0.5
        x_embed = grid.cumsum(dim=1) - 0.5
        y_embed = y_embed / size[0]
        x_embed = x_embed / size[1]
        positional_embedding = self.shared_image_embedding(torch.stack([x_embed, y_embed], dim=-1))
        return positional_embedding.permute(2, 0, 1).unsqueeze(0)
    @torch.no_grad()
    def get_image_embeddings(
        self,
        pixel_values: torch.FloatTensor,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> list[torch.Tensor]:
        batch_size = pixel_values.shape[0]
        feature_maps, _, _, _ = self.get_image_features(pixel_values, **kwargs)
        feature_maps[-1] = feature_maps[-1] + self.no_memory_embedding
        image_embeddings = [
            feat.permute(1, 2, 0).view(batch_size, -1, *feat_size)
            for feat, feat_size in zip(feature_maps, self.backbone_feature_sizes)
        ]
        return image_embeddings
    @torch.no_grad()
    def get_prompt_embeddings(
        self,
        input_points: Optional[torch.FloatTensor] = None,
        input_labels: Optional[torch.LongTensor] = None,
        input_boxes: Optional[torch.FloatTensor] = None,
        input_masks: Optional[torch.LongTensor] = None,
    ):
        prompt_output = self.prompt_encoder(
            input_points=input_points,
            input_labels=input_labels,
            input_boxes=input_boxes,
            input_masks=input_masks,
        )
        return prompt_output
    @check_model_inputs()
    @auto_docstring
    def forward(
        self,
        pixel_values: Optional[torch.FloatTensor] = None,
        input_points: Optional[torch.FloatTensor] = None,
        input_labels: Optional[torch.LongTensor] = None,
        input_boxes: Optional[torch.FloatTensor] = None,
        input_masks: Optional[torch.LongTensor] = None,
        image_embeddings: Optional[torch.FloatTensor] = None,
        multimask_output: bool = True,
        attention_similarity: Optional[torch.FloatTensor] = None,
        target_embedding: Optional[torch.FloatTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> EdgeTamImageSegmentationOutput:
        if not ((pixel_values is None) ^ (image_embeddings is None)):
            raise ValueError("Exactly one of pixel_values or image_embeddings must be provided.")
        if input_points is not None and input_boxes is not None:
            if input_points.shape[1] != input_boxes.shape[1]:
                raise ValueError(
                    f"You should provide as many bounding boxes as input points per box. Got {input_points.shape[1]} and {input_boxes.shape[1]}."
                )
        image_positional_embeddings = self.get_image_wide_positional_embeddings()
        batch_size = pixel_values.shape[0] if pixel_values is not None else image_embeddings[-1].shape[0]
        image_positional_embeddings = image_positional_embeddings.repeat(batch_size, 1, 1, 1)
        vision_attentions = None
        vision_hidden_states = None
        if pixel_values is not None:
            feature_maps, _, vision_hidden_states, vision_attentions = self.get_image_features(
                pixel_values,
                **kwargs,
            )
            feature_maps[-1] = feature_maps[-1] + self.no_memory_embedding
            image_embeddings = [
                feat.permute(1, 2, 0).view(batch_size, -1, *feat_size)
                for feat, feat_size in zip(feature_maps, self.backbone_feature_sizes)
            ]
        if input_points is not None and input_labels is None:
            input_labels = torch.ones_like(input_points[:, :, :, 0], dtype=torch.int, device=input_points.device)
        if input_points is None and input_boxes is None:
            input_points = torch.zeros(
                batch_size, 1, 1, 2, dtype=image_embeddings[-1].dtype, device=image_embeddings[-1].device
            )
            input_labels = -torch.ones(batch_size, 1, 1, dtype=torch.int32, device=image_embeddings[-1].device)
        if input_masks is not None:
            if input_masks.shape[-2:] != self.prompt_encoder.mask_input_size:
                input_masks = F.interpolate(
                    input_masks.float(),
                    size=self.prompt_encoder.mask_input_size,
                    align_corners=False,
                    mode="bilinear",
                    antialias=True,
                ).to(input_masks.dtype)
        sparse_embeddings, dense_embeddings = self.prompt_encoder(
            input_points=input_points,
            input_labels=input_labels,
            input_boxes=input_boxes,
            input_masks=input_masks,
        )
        low_res_multimasks, iou_scores, _, object_score_logits = self.mask_decoder(
            image_embeddings=image_embeddings[-1],
            image_positional_embeddings=image_positional_embeddings,
            sparse_prompt_embeddings=sparse_embeddings,
            dense_prompt_embeddings=dense_embeddings,
            multimask_output=multimask_output,
            high_resolution_features=image_embeddings[:-1],
            attention_similarity=attention_similarity,
            target_embedding=target_embedding,
            **kwargs,
        )
        return EdgeTamImageSegmentationOutput(
            iou_scores=iou_scores,
            pred_masks=low_res_multimasks,
            object_score_logits=object_score_logits,
            image_embeddings=image_embeddings,
            vision_hidden_states=vision_hidden_states,
            vision_attentions=vision_attentions,
        )
    def get_image_features(
        self,
        pixel_values: torch.FloatTensor,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> tuple[
        list[torch.Tensor],
        list[torch.Tensor],
        Optional[tuple[torch.FloatTensor, ...]],
        Optional[tuple[torch.FloatTensor, ...]],
    ]:
        vision_outputs: EdgeTamVisionEncoderOutput = self.vision_encoder(
            pixel_values,
            **kwargs,
        )
        feature_maps = vision_outputs.fpn_hidden_states
        feature_maps_position_embeddings = vision_outputs.fpn_position_encoding
        feature_maps = list(feature_maps)
        feature_maps[0] = self.mask_decoder.conv_s0(feature_maps[0])
        feature_maps[1] = self.mask_decoder.conv_s1(feature_maps[1])
        feature_maps = [feature_map.flatten(2).permute(2, 0, 1) for feature_map in feature_maps]
        feature_maps_position_embeddings = [
            feature_map_position_embedding.flatten(2).permute(2, 0, 1)
            for feature_map_position_embedding in feature_maps_position_embeddings
        ]
        return feature_maps, feature_maps_position_embeddings, vision_outputs.hidden_states, vision_outputs.attentions
__all__ = ["EdgeTamModel", "EdgeTamVisionModel", "EdgeTamPreTrainedModel"]