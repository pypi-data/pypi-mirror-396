import math
from collections import OrderedDict
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, Callable, Optional, Union
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from tqdm import tqdm
from MEROAI.utils.generic import OutputRecorder
from ...activations import ACT2FN
from ...modeling_flash_attention_utils import FlashAttentionKwargs
from ...modeling_layers import GradientCheckpointingLayer
from ...modeling_outputs import BaseModelOutput
from ...modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from ...processing_utils import Unpack
from ...pytorch_utils import compile_compatible_method_lru_cache
from ...utils import ModelOutput, auto_docstring
from ...utils.generic import MEROAIKwargs
from ..auto import AutoModel
from .configuration_edgetam_video import (
    EdgeTamVideoConfig,
    EdgeTamVideoMaskDecoderConfig,
    EdgeTamVideoPromptEncoderConfig,
)
class EdgeTamVideoLayerNorm(nn.LayerNorm):
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
class EdgeTamVideoMemoryFuserCXBlock(GradientCheckpointingLayer):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.depthwise_conv = nn.Conv2d(
            config.memory_fuser_embed_dim,
            config.memory_fuser_embed_dim,
            kernel_size=config.memory_fuser_kernel_size,
            padding=config.memory_fuser_padding,
            groups=config.memory_fuser_embed_dim,
        )
        self.layer_norm = EdgeTamVideoLayerNorm(config.memory_fuser_embed_dim, eps=1e-6, data_format="channels_first")
        self.activation = ACT2FN[config.memory_fuser_hidden_act]
        self.pointwise_conv1 = nn.Linear(
            config.memory_fuser_embed_dim, config.memory_fuser_intermediate_dim
        )
        self.pointwise_conv2 = nn.Linear(config.memory_fuser_intermediate_dim, config.memory_fuser_embed_dim)
        self.scale = nn.Parameter(
            config.memory_fuser_layer_scale_init_value * torch.ones(config.memory_fuser_embed_dim),
            requires_grad=True,
        )
    def forward(self, hidden_states):
        input = hidden_states
        hidden_states = self.depthwise_conv(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = hidden_states.permute(0, 2, 3, 1)
        hidden_states = self.pointwise_conv1(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.pointwise_conv2(hidden_states)
        hidden_states = self.scale * hidden_states
        hidden_states = hidden_states.permute(0, 3, 1, 2)
        hidden_states = input + hidden_states
        return hidden_states
@dataclass
@auto_docstring(custom_intro="Base class for the vision encoder's outputs.")
class EdgeTamVideoVisionEncoderOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    fpn_hidden_states: Optional[torch.FloatTensor] = None
    fpn_position_encoding: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
class EdgeTamVideoVisionRotaryEmbedding(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig, end_x: Optional[int] = None, end_y: Optional[int] = None):
        super().__init__()
        dim = config.memory_attention_hidden_size // (
            config.memory_attention_downsample_rate * config.memory_attention_num_attention_heads
        )
        if dim % 4 != 0:
            raise ValueError("Dimension must be divisible by 4 for axial RoPE")
        end_x, end_y = config.memory_attention_rope_feat_sizes if end_x is None else (end_x, end_y)
        freqs = 1.0 / (config.memory_attention_rope_theta ** (torch.arange(0, dim, 4)[: (dim // 4)].float() / dim))
        flattened_indices = torch.arange(end_x * end_y, dtype=torch.long)
        x_positions = flattened_indices % end_x
        y_positions = torch.div(flattened_indices, end_x, rounding_mode="floor")
        freqs_x = torch.outer(x_positions, freqs).float()
        freqs_y = torch.outer(y_positions, freqs).float()
        inv_freq = torch.cat([freqs_x, freqs_y], dim=-1)
        inv_freq = inv_freq.repeat_interleave(2, dim=-1)
        self.register_buffer("rope_embeddings_cos", inv_freq.cos(), persistent=False)
        self.register_buffer("rope_embeddings_sin", inv_freq.sin(), persistent=False)
    @torch.no_grad()
    def forward(self) -> tuple[torch.Tensor, torch.Tensor]:
        return self.rope_embeddings_cos, self.rope_embeddings_sin
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
class EdgeTamVideoAttention(nn.Module):
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
def rotate_pairwise(x):
    x = x.view(*x.shape[:-1], -1, 2)
    x1, x2 = x.unbind(dim=-1)
    x = torch.stack((-x2, x1), dim=-1)
    return x.flatten(start_dim=-2)
def apply_rotary_pos_emb_2d_self_attn(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    q_embed = q.float()
    q_embed = (q_embed * cos) + (rotate_pairwise(q_embed) * sin)
    k_embed = k.float()
    k_embed = (k_embed * cos) + (rotate_pairwise(k_embed) * sin)
    return q_embed.type_as(q), k_embed.type_as(k)
class EdgeTamVideoRoPESelfAttention(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.memory_attention_hidden_size
        self.internal_dim = self.hidden_size // config.memory_attention_downsample_rate
        self.num_attention_heads = config.memory_attention_num_attention_heads
        self.head_dim = self.internal_dim // config.memory_attention_num_attention_heads
        self.scaling = self.head_dim**-0.5
        self.is_causal = False
        self.q_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.k_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.v_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.o_proj = nn.Linear(self.internal_dim, self.hidden_size)
        self.dropout_p = config.memory_attention_rope_dropout
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        **kwargs: Unpack[FlashAttentionKwargs],
    ) -> Tensor:
        batch_size, point_batch_size = query.shape[:2]
        new_shape = (batch_size * point_batch_size, -1, self.num_attention_heads, self.head_dim)
        query = self.q_proj(query).view(*new_shape).transpose(1, 2)
        key = self.k_proj(key).view(*new_shape).transpose(1, 2)
        value = self.v_proj(value).view(*new_shape).transpose(1, 2)
        cos, sin = position_embeddings
        query, key = apply_rotary_pos_emb_2d_self_attn(query, key, cos=cos, sin=sin)
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, attn_weights = attention_interface(
            self,
            query,
            key,
            value,
            attention_mask=None,
            dropout=0.0 if not self.training else self.dropout_p,
            scaling=self.scaling,
            is_causal=self.is_causal,
            **kwargs,
        )
        attn_output = attn_output.reshape(
            batch_size, point_batch_size, -1, self.num_attention_heads * self.head_dim
        ).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights
def apply_rotary_pos_emb_2d_cross_attn(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
    cos_k: torch.Tensor,
    sin_k: torch.Tensor,
    num_k_exclude_rope: int = 0,
    repeat_freqs_k: int = 1,
) -> tuple[torch.Tensor, torch.Tensor]:
    q_embed = q.float()
    q_embed = (q_embed * cos) + (rotate_pairwise(q_embed) * sin)
    num_total_k_tokens = k.shape[-2]
    k_for_rope = k[..., : num_total_k_tokens - num_k_exclude_rope, :]
    k_excluded = k[..., num_total_k_tokens - num_k_exclude_rope :, :]
    if k_for_rope.shape[-2] == 0:
        return q_embed.type_as(q), k_excluded
    batch_size, num_heads, k_seq_len, channels_per_head = k_for_rope.shape
    tokens_per_group = k_seq_len // repeat_freqs_k
    spatial_tokens = cos_k.shape[-2]
    temporal_tokens = tokens_per_group - spatial_tokens
    k_grouped = k_for_rope.view(batch_size, num_heads, repeat_freqs_k, tokens_per_group, channels_per_head)
    k_temporal = k_grouped[..., :temporal_tokens, :].reshape(batch_size, num_heads, -1, channels_per_head)
    k_spatial = k_grouped[..., temporal_tokens:, :].reshape(batch_size, num_heads, -1, channels_per_head)
    k_rope_input = k_spatial
    if repeat_freqs_k > 1:
        cos_k = cos_k.repeat(1, 1, repeat_freqs_k, 1)
        sin_k = sin_k.repeat(1, 1, repeat_freqs_k, 1)
    k_spatial_embed = k_rope_input.float()
    k_spatial_embed = (k_spatial_embed * cos_k) + (rotate_pairwise(k_spatial_embed) * sin_k)
    k_spatial_reshaped = k_spatial_embed.view(batch_size, num_heads, repeat_freqs_k, -1, channels_per_head)
    k_temporal_reshaped = k_temporal.view(batch_size, num_heads, repeat_freqs_k, -1, channels_per_head)
    k_final = torch.cat([k_temporal_reshaped, k_spatial_reshaped], dim=3)
    k_final = k_final.view(batch_size, num_heads, k_seq_len, channels_per_head)
    k_embed = torch.cat([k_final.type_as(k), k_excluded], dim=-2)
    return q_embed.type_as(q), k_embed
class EdgeTamVideoRoPECrossAttention(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig, kv_in_dim: int):
        super().__init__()
        self.config = config
        self.hidden_size = config.memory_attention_hidden_size
        self.internal_dim = self.hidden_size // config.memory_attention_downsample_rate
        self.num_attention_heads = config.memory_attention_num_attention_heads
        self.head_dim = self.internal_dim // config.memory_attention_num_attention_heads
        self.scaling = self.head_dim**-0.5
        self.is_causal = False
        self.kv_in_dim = kv_in_dim
        self.q_proj = nn.Linear(self.hidden_size, self.internal_dim)
        self.k_proj = nn.Linear(self.kv_in_dim, self.internal_dim)
        self.v_proj = nn.Linear(self.kv_in_dim, self.internal_dim)
        self.o_proj = nn.Linear(self.internal_dim, self.hidden_size)
        self.dropout_p = config.memory_attention_rope_dropout
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        position_embeddings_k: tuple[torch.Tensor, torch.Tensor],
        num_k_exclude_rope: int = 0,
        rope_k_repeat: int = 0,
        **kwargs: Unpack[FlashAttentionKwargs],
    ) -> Tensor:
        batch_size, point_batch_size = query.shape[:2]
        new_shape = (batch_size * point_batch_size, -1, self.num_attention_heads, self.head_dim)
        query = self.q_proj(query).view(*new_shape).transpose(1, 2)
        key = self.k_proj(key).view(*new_shape).transpose(1, 2)
        value = self.v_proj(value).view(*new_shape).transpose(1, 2)
        cos, sin = position_embeddings
        cos_k, sin_k = position_embeddings_k
        query, key = apply_rotary_pos_emb_2d_cross_attn(
            query,
            key,
            cos=cos,
            sin=sin,
            cos_k=cos_k,
            sin_k=sin_k,
            repeat_freqs_k=rope_k_repeat,
            num_k_exclude_rope=num_k_exclude_rope,
        )
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, attn_weights = attention_interface(
            self,
            query,
            key,
            value,
            attention_mask=None,
            dropout=0.0 if not self.training else self.dropout_p,
            scaling=self.scaling,
            is_causal=self.is_causal,
            **kwargs,
        )
        attn_output = attn_output.reshape(
            batch_size, point_batch_size, -1, self.num_attention_heads * self.head_dim
        ).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights
class EdgeTamVideoTwoWayAttentionBlock(nn.Module):
    def __init__(self, config: EdgeTamVideoMaskDecoderConfig, skip_first_layer_pe: bool = False):
        super().__init__()
        self.self_attn = EdgeTamVideoAttention(config, downsample_rate=1)
        self.layer_norm1 = nn.LayerNorm(config.hidden_size)
        self.cross_attn_token_to_image = EdgeTamVideoAttention(config)
        self.layer_norm2 = nn.LayerNorm(config.hidden_size)
        self.mlp = EdgeTamVideoFeedForward(
            config.hidden_size, config.mlp_dim, config.hidden_size, num_layers=config.num_hidden_layers
        )
        self.layer_norm3 = nn.LayerNorm(config.hidden_size)
        self.layer_norm4 = nn.LayerNorm(config.hidden_size)
        self.cross_attn_image_to_token = EdgeTamVideoAttention(config)
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
class EdgeTamVideoPositionEmbeddingSine(nn.Module):
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
    @compile_compatible_method_lru_cache(maxsize=2)
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
class EdgeTamVideoMemoryFuser(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.layers = nn.ModuleList(
            [EdgeTamVideoMemoryFuserCXBlock(config) for _ in range(config.memory_fuser_num_layers)]
        )
    def forward(self, hidden_states):
        for layer in self.layers:
            hidden_states = layer(hidden_states)
        return hidden_states
class EdgeTamVideoMaskDownSamplerLayer(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig, in_channels: int, out_channels: int):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=config.mask_downsampler_kernel_size,
            stride=config.mask_downsampler_stride,
            padding=config.mask_downsampler_padding,
        )
        self.layer_norm = EdgeTamVideoLayerNorm(out_channels, eps=1e-6, data_format="channels_first")
        self.activation = ACT2FN[config.mask_downsampler_hidden_act]
    def forward(self, x):
        return self.activation(self.layer_norm(self.conv(x)))
class EdgeTamVideoMaskDownSampler(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        num_layers = int(math.log2(config.mask_downsampler_total_stride) // math.log2(config.mask_downsampler_stride))
        self.layers = nn.ModuleList()
        self.activation = ACT2FN[config.mask_downsampler_hidden_act]
        mask_in_chans, mask_out_chans = 1, 1
        for _ in range(num_layers):
            mask_out_chans = mask_in_chans * (config.mask_downsampler_stride**2)
            self.layers.append(EdgeTamVideoMaskDownSamplerLayer(config, mask_in_chans, mask_out_chans))
            mask_in_chans = mask_out_chans
        self.final_conv = nn.Conv2d(mask_out_chans, config.mask_downsampler_embed_dim, kernel_size=1)
    def forward(self, x):
        for layer in self.layers:
            x = layer(x)
        x = self.final_conv(x)
        return x
class EdgeTamVideoMemoryEncoder(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        hidden_size = config.memory_encoder_hidden_size
        output_channels = config.memory_encoder_output_channels
        self.mask_downsampler = EdgeTamVideoMaskDownSampler(config)
        self.feature_projection = nn.Conv2d(hidden_size, hidden_size, kernel_size=1)
        self.memory_fuser = EdgeTamVideoMemoryFuser(config)
        self.position_encoding = EdgeTamVideoPositionEmbeddingSine(num_pos_feats=output_channels // 2, normalize=True)
        self.projection = nn.Conv2d(hidden_size, output_channels, kernel_size=1)
    def forward(
        self,
        vision_features: torch.Tensor,
        masks: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        masks = self.mask_downsampler(masks)
        vision_features = self.feature_projection(vision_features)
        vision_features = vision_features + masks
        vision_features = self.memory_fuser(vision_features)
        vision_features = self.projection(vision_features)
        vision_pos_enc = self.position_encoding(vision_features.shape, vision_features.device, vision_features.dtype)
        return vision_features, vision_pos_enc
class EdgeTamVideoFeedForward(nn.Module):
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
class EdgeTamVideoPreTrainedModel(PreTrainedModel):
    config_class = EdgeTamVideoConfig
    base_model_prefix = "edgetam_video"
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
        elif isinstance(module, (nn.LayerNorm, EdgeTamVideoLayerNorm)):
            module.weight.data.fill_(1.0)
            module.bias.data.zero_()
        elif isinstance(module, EdgeTamVideoModel):
            if module.no_memory_positional_encoding is not None:
                module.no_memory_positional_encoding.data.zero_()
            if module.memory_temporal_positional_encoding is not None:
                module.memory_temporal_positional_encoding.data.zero_()
            if module.no_object_pointer is not None:
                module.no_object_pointer.data.zero_()
            if module.occlusion_spatial_embedding_parameter is not None:
                module.occlusion_spatial_embedding_parameter.data.zero_()
        if isinstance(module, EdgeTamVideoMemoryFuserCXBlock):
            if module.scale is not None:
                module.scale.data.zero_()
class EdgeTamVideoInferenceCache:
    def __init__(
        self,
        inference_device: Union[torch.device, str] = "cpu",
        inference_state_device: Union[torch.device, str] = "cpu",
        max_vision_features_cache_size: int = 1,
    ):
        self.inference_device = inference_device
        self.inference_state_device = inference_state_device
        self.max_vision_features_cache_size = max_vision_features_cache_size
        self._vision_features = {}
    def cache_vision_features(self, frame_idx: int, features: dict):
        cached = {}
        if len(self._vision_features) >= self.max_vision_features_cache_size:
            self._vision_features.pop(min(self._vision_features.keys()))
        for key, value in features.items():
            if isinstance(value, torch.Tensor):
                cached[key] = value.to(self.inference_state_device, non_blocking=True)
            elif isinstance(value, (list, tuple)) and value and isinstance(value[0], torch.Tensor):
                cached[key] = [v.to(self.inference_state_device, non_blocking=True) for v in value]
            else:
                cached[key] = value
        self._vision_features[frame_idx] = cached
    def get_vision_features(self, frame_idx: int) -> Optional[dict]:
        if frame_idx not in self._vision_features:
            return None
        cached = self._vision_features[frame_idx]
        moved = {}
        for key, value in cached.items():
            if isinstance(value, torch.Tensor):
                moved[key] = value.to(self.inference_device, non_blocking=True)
            elif isinstance(value, (list, tuple)) and value and isinstance(value[0], torch.Tensor):
                moved[key] = [v.to(self.inference_device, non_blocking=True) for v in value]
            else:
                moved[key] = value
        return moved
    def clear_all(self):
        self._vision_features.clear()
class EdgeTamVideoInferenceSession:
    def __init__(
        self,
        video: Optional[torch.FloatTensor] = None,
        video_height: Optional[int] = None,
        video_width: Optional[int] = None,
        inference_device: Union[torch.device, str] = "cpu",
        inference_state_device: Union[torch.device, str] = "cpu",
        video_storage_device: Union[torch.device, str] = "cpu",
        dtype: Union[torch.dtype, str] = "float32",
        max_vision_features_cache_size: int = 1,
    ):
        self.processed_frames = (
            dict(enumerate(video.to(video_storage_device, dtype=dtype))) if video is not None else None
        )
        self.video_height = video_height
        self.video_width = video_width
        self.inference_device = inference_device
        self.inference_state_device = inference_state_device
        self.video_storage_device = video_storage_device
        self.dtype = dtype
        self.max_vision_features_cache_size = max_vision_features_cache_size
        self.cache = EdgeTamVideoInferenceCache(
            inference_device=self.inference_device,
            inference_state_device=self.inference_state_device,
            max_vision_features_cache_size=self.max_vision_features_cache_size,
        )
        self._obj_id_to_idx = OrderedDict()
        self._obj_idx_to_id = OrderedDict()
        self.obj_ids = []
        self.point_inputs_per_obj = {}
        self.mask_inputs_per_obj = {}
        self.output_dict_per_obj = {}
        self.frames_tracked_per_obj = {}
        self.obj_with_new_inputs = []
    @property
    def num_frames(self) -> Optional[int]:
        return len(self.processed_frames) if self.processed_frames is not None else None
    def obj_id_to_idx(self, obj_id: int) -> int:
        obj_idx = self._obj_id_to_idx.get(obj_id, None)
        if obj_idx is not None:
            return obj_idx
        obj_idx = len(self._obj_id_to_idx)
        self._obj_id_to_idx[obj_id] = obj_idx
        self._obj_idx_to_id[obj_idx] = obj_id
        self.obj_ids = list(self._obj_id_to_idx)
        self.point_inputs_per_obj[obj_idx] = {}
        self.mask_inputs_per_obj[obj_idx] = {}
        self.output_dict_per_obj[obj_idx] = {
            "cond_frame_outputs": {},
            "non_cond_frame_outputs": {},
        }
        self.frames_tracked_per_obj[obj_idx] = {}
        return obj_idx
    def obj_idx_to_id(self, obj_idx: int) -> int:
        return self._obj_idx_to_id[obj_idx]
    def get_obj_num(self) -> int:
        return len(self._obj_idx_to_id)
    def add_point_inputs(self, obj_idx: int, frame_idx: int, inputs: dict):
        device_inputs = {}
        for key, value in inputs.items():
            if isinstance(value, torch.Tensor):
                device_inputs[key] = value.to(self.inference_device, non_blocking=True)
            else:
                device_inputs[key] = value
        self.point_inputs_per_obj[obj_idx][frame_idx] = device_inputs
    def remove_point_inputs(self, obj_idx: int, frame_idx: int):
        self.point_inputs_per_obj[obj_idx].pop(frame_idx, None)
    def add_mask_inputs(self, obj_idx: int, frame_idx: int, inputs: torch.Tensor):
        self.mask_inputs_per_obj[obj_idx][frame_idx] = inputs.to(
            self.inference_device, dtype=self.dtype, non_blocking=True
        )
    def remove_mask_inputs(self, obj_idx: int, frame_idx: int):
        self.mask_inputs_per_obj[obj_idx].pop(frame_idx, None)
    def store_output(
        self,
        obj_idx: int,
        frame_idx: int,
        output_key: Optional[str] = None,
        output_value: Optional[Union[torch.Tensor, dict]] = None,
        is_conditioning_frame: bool = True,
    ):
        storage_key = "cond_frame_outputs" if is_conditioning_frame else "non_cond_frame_outputs"
        if output_key is None and isinstance(output_value, dict):
            self.output_dict_per_obj[obj_idx][storage_key][frame_idx] = {}
            for key, value in output_value.items():
                self.store_output(obj_idx, frame_idx, key, value, is_conditioning_frame)
            return
        if output_key in ["object_pointer", "object_score_logits"]:
            self.output_dict_per_obj[obj_idx][storage_key][frame_idx][output_key] = output_value
        elif isinstance(output_value, torch.Tensor):
            self.output_dict_per_obj[obj_idx][storage_key][frame_idx][output_key] = output_value.to(
                self.inference_state_device, non_blocking=True
            )
        else:
            self.output_dict_per_obj[obj_idx][storage_key][frame_idx][output_key] = output_value
    def get_output(
        self,
        obj_idx: int,
        frame_idx: int,
        output_key: str,
        is_conditioning_frame: bool = True,
    ):
        storage_key = "cond_frame_outputs" if is_conditioning_frame else "non_cond_frame_outputs"
        out = self.output_dict_per_obj[obj_idx][storage_key].get(frame_idx, None)
        if out is None:
            return None
        value = out[output_key]
        if isinstance(value, torch.Tensor):
            value = value.to(self.inference_device, non_blocking=True)
        return value
    def add_new_frame(self, pixel_values: torch.Tensor, frame_idx: Optional[int] = None) -> int:
        pixel_values = pixel_values.to(self.video_storage_device, dtype=self.dtype, non_blocking=True)
        if pixel_values.dim() == 4:
            pixel_values = pixel_values.squeeze(0)
        if frame_idx is None:
            frame_idx = len(self.processed_frames) if self.processed_frames is not None else 0
        if self.processed_frames is None:
            self.processed_frames = {frame_idx: pixel_values}
        else:
            self.processed_frames[frame_idx] = pixel_values
        return frame_idx
    def get_frame(self, frame_idx: int) -> torch.Tensor:
        return self.processed_frames[frame_idx].to(self.inference_device, non_blocking=True)
    def reset_tracking_data(self):
        self._obj_id_to_idx.clear()
        self._obj_idx_to_id.clear()
        self.obj_ids.clear()
        self.point_inputs_per_obj.clear()
        self.mask_inputs_per_obj.clear()
        self.output_dict_per_obj.clear()
        self.frames_tracked_per_obj.clear()
        self.obj_with_new_inputs = []
    def reset_inference_session(self):
        self._obj_id_to_idx.clear()
        self._obj_idx_to_id.clear()
        self.obj_ids.clear()
        self.point_inputs_per_obj.clear()
        self.mask_inputs_per_obj.clear()
        self.output_dict_per_obj.clear()
        self.frames_tracked_per_obj.clear()
        self.obj_with_new_inputs = []
        self.cache.clear_all()
class EdgeTamVideoMemoryAttentionMLP(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.memory_attention_hidden_size
        self.intermediate_size = config.memory_attention_mlp_hidden_size
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size)
        self.dropout = nn.Dropout(config.memory_attention_dropout)
        self.act_fn = ACT2FN[config.memory_attention_mlp_hidden_act]
    def forward(self, x):
        return self.down_proj(self.dropout(self.act_fn(self.up_proj(x))))
class EdgeTamVideoMemoryAttentionLayer(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        hidden_size = config.memory_attention_hidden_size
        self.self_attn = EdgeTamVideoRoPESelfAttention(config)
        self.cross_attn_image = EdgeTamVideoRoPECrossAttention(config, kv_in_dim=64)
        self.mlp = EdgeTamVideoMemoryAttentionMLP(config)
        self.layer_norm1 = nn.LayerNorm(hidden_size)
        self.layer_norm2 = nn.LayerNorm(hidden_size)
        self.layer_norm3 = nn.LayerNorm(hidden_size)
        self.dropout1 = nn.Dropout(config.memory_attention_dropout)
        self.dropout2 = nn.Dropout(config.memory_attention_dropout)
        self.dropout3 = nn.Dropout(config.memory_attention_dropout)
    def forward(
        self,
        queries: Tensor,
        keys: Tensor,
        key_point_embedding: Tensor,
        rope_position_embeddings: tuple[Tensor, Tensor],
        rope_position_embeddings_k: Optional[tuple[Tensor, Tensor]] = None,
        num_k_exclude_rope: int = 0,
        rope_k_repeat: int = 0,
    ) -> torch.Tensor:
        query = self.layer_norm1(queries)
        query, _ = self.self_attn(query=query, key=query, value=query, position_embeddings=rope_position_embeddings)
        queries = queries + self.dropout1(query)
        query = self.layer_norm2(queries)
        query, _ = self.cross_attn_image(
            query=query,
            key=keys + key_point_embedding,
            value=keys,
            position_embeddings=rope_position_embeddings,
            position_embeddings_k=rope_position_embeddings_k,
            num_k_exclude_rope=num_k_exclude_rope,
            rope_k_repeat=rope_k_repeat,
        )
        queries = queries + self.dropout2(query)
        query = self.layer_norm3(queries)
        query = self.mlp(query)
        queries = queries + self.dropout3(query)
        return queries
class EdgeTamVideoMemoryAttention(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.layers = nn.ModuleList(
            [EdgeTamVideoMemoryAttentionLayer(config) for _ in range(config.memory_attention_num_layers)]
        )
        self.layer_norm = nn.LayerNorm(config.memory_attention_hidden_size)
        self.rotary_emb = EdgeTamVideoVisionRotaryEmbedding(config=config)
        self.rotary_emb_k = EdgeTamVideoVisionRotaryEmbedding(
            config, end_x=config.memory_attention_rope_k_sizes[0], end_y=config.memory_attention_rope_k_sizes[1]
        )
    def forward(
        self,
        current_vision_features: torch.Tensor,
        memory: torch.Tensor,
        current_vision_position_embeddings: Optional[Tensor] = None,
        memory_posision_embeddings: Optional[Tensor] = None,
        num_object_pointer_tokens: int = 0,
        num_spatial_memory_tokens: int = -1,
    ):
        output = current_vision_features
        if current_vision_position_embeddings is not None:
            output = output + 0.1 * current_vision_position_embeddings
        output = output.transpose(0, 1)
        memory = memory.transpose(0, 1).unsqueeze(1)
        memory_posision_embeddings = memory_posision_embeddings.transpose(0, 1).unsqueeze(1)
        rope_position_embeddings = self.rotary_emb()
        rope_position_embeddings_k = self.rotary_emb_k()
        for layer in self.layers:
            output = layer(
                queries=output.unsqueeze(1) if output.ndim == 3 else output,
                keys=memory,
                key_point_embedding=memory_posision_embeddings,
                rope_position_embeddings=rope_position_embeddings,
                rope_position_embeddings_k=rope_position_embeddings_k,
                num_k_exclude_rope=num_object_pointer_tokens,
                rope_k_repeat=num_spatial_memory_tokens,
            )
        normed_output = self.layer_norm(output)
        normed_output = normed_output.transpose(0, 1)
        return normed_output
class EdgeTamVideoPerceiverMLP(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.hidden_size = config.perceiver_resampler_hidden_size
        self.intermediate_size = config.perceiver_resampler_mlp_intermediate_size
        self.layer_norm = nn.LayerNorm(self.hidden_size)
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=False)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=False)
        self.act_fn = nn.GELU()
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.layer_norm(hidden_states)
        hidden_states = self.down_proj(self.act_fn(self.up_proj(hidden_states)))
        return hidden_states
class EdgeTamVideoPerceiverAttention(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.perceiver_resampler_hidden_size
        self.num_attention_heads = config.perceiver_resampler_num_attention_heads
        self.head_dim = config.perceiver_resampler_attention_head_dim
        self.attention_dropout = config.perceiver_resampler_attention_dropout
        self.inner_dim = self.head_dim * self.num_attention_heads
        self.scaling = self.head_dim**-0.5
        self.is_causal = False
        self.q_proj = nn.Linear(self.hidden_size, self.inner_dim, bias=False)
        self.k_proj = nn.Linear(self.hidden_size, self.inner_dim, bias=False)
        self.v_proj = nn.Linear(self.hidden_size, self.inner_dim, bias=False)
        self.o_proj = nn.Linear(self.inner_dim, self.hidden_size, bias=False)
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        positional_encoding: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        query = self.q_proj(query)
        key = self.k_proj(key)
        value = self.v_proj(value)
        batch_size, seq_len_q = query.shape[:2]
        query = query.view(batch_size, seq_len_q, self.num_attention_heads, self.head_dim).transpose(1, 2)
        seq_len_kv = key.shape[1]
        key = key.view(batch_size, seq_len_kv, self.num_attention_heads, self.head_dim).transpose(1, 2)
        value = value.view(batch_size, seq_len_kv, self.num_attention_heads, self.head_dim).transpose(1, 2)
        if positional_encoding is not None:
            pos_encoding = positional_encoding.view(
                batch_size, seq_len_kv, self.num_attention_heads, self.head_dim
            ).transpose(1, 2)
            key = key + pos_encoding
            value = value + pos_encoding
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, _ = attention_interface(
            self,
            query,
            key,
            value,
            attention_mask=None,
            dropout=0.0 if not self.training else self.attention_dropout,
            scaling=self.scaling,
            is_causal=self.is_causal,
            **kwargs,
        )
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, seq_len_q, self.inner_dim)
        return self.o_proj(attn_output)
class EdgeTamVideoPerceiverEncoderLayer(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.cross_attention = EdgeTamVideoPerceiverAttention(config)
        self.mlp = EdgeTamVideoPerceiverMLP(config)
        self.dropout = nn.Dropout(config.perceiver_resampler_hidden_dropout)
        self.self_attention = EdgeTamVideoPerceiverAttention(config)
        self.self_mlp = EdgeTamVideoPerceiverMLP(config)
        self.layer_norm_input = nn.LayerNorm(config.perceiver_resampler_hidden_size)
        self.layer_norm_latents = nn.LayerNorm(config.perceiver_resampler_hidden_size)
        self.layer_norm_self = nn.LayerNorm(config.perceiver_resampler_hidden_size)
    def forward(
        self,
        latents: torch.Tensor,
        input_features: torch.Tensor,
        positional_encoding: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        normalized_latents = self.layer_norm_latents(latents)
        normalized_input = self.layer_norm_input(input_features)
        cross_attention_output = self.cross_attention(
            query=normalized_latents,
            key=normalized_input,
            value=normalized_input,
            positional_encoding=positional_encoding,
        )
        latents = latents + self.dropout(cross_attention_output)
        mlp_output = self.mlp(latents)
        latents = latents + mlp_output
        normalized_latents_self = self.layer_norm_self(latents)
        self_attention_output = self.self_attention(
            query=normalized_latents_self, key=normalized_latents_self, value=normalized_latents_self
        )
        latents = latents + self_attention_output
        self_mlp_output = self.self_mlp(latents)
        latents = latents + self_mlp_output
        return latents
def window_partition(hidden_state, window_size):
    batch_size, height, width, num_channels = hidden_state.shape
    pad_height = (window_size - height % window_size) % window_size
    pad_width = (window_size - width % window_size) % window_size
    hidden_state = nn.functional.pad(hidden_state, (0, 0, 0, pad_width, 0, pad_height))
    padded_height, padded_width = height + pad_height, width + pad_width
    hidden_state = hidden_state.view(
        batch_size, padded_height // window_size, window_size, padded_width // window_size, window_size, num_channels
    )
    windows = hidden_state.permute(0, 1, 3, 2, 4, 5).contiguous().view(-1, window_size, window_size, num_channels)
    return windows, (padded_height, padded_width)
class EdgeTamVideoPerceiverResampler(nn.Module):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.perceiver_resampler_hidden_size
        self.num_latents_1d = config.perceiver_resampler_num_latents
        self.num_latents_2d = config.perceiver_resampler_num_latents_2d
        self.num_layers = config.perceiver_resampler_num_layers
        if self.num_latents_1d > 0:
            self.latents_1d = nn.Parameter(torch.randn(self.num_latents_1d, self.hidden_size))
        if self.num_latents_2d > 0:
            self.latents_2d = nn.Parameter(torch.randn(self.num_latents_2d, self.hidden_size))
        self.positional_encoding = EdgeTamVideoPositionEmbeddingSine(
            num_pos_feats=self.hidden_size // 2, normalize=True
        )
        self.layers = nn.ModuleList([EdgeTamVideoPerceiverEncoderLayer(config) for _ in range(self.num_layers)])
        self.layer_norm = nn.LayerNorm(self.hidden_size)
    def forward(
        self,
        hidden_states: torch.Tensor,
        positional_encoding: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
        output_latents = []
        output_positional_encodings = []
        if self.num_latents_1d > 0:
            latents_1d, pos_1d = self._forward_1d(hidden_states, positional_encoding)
            output_latents.append(latents_1d)
            output_positional_encodings.append(pos_1d)
        if self.num_latents_2d > 0:
            latents_2d, pos_2d = self._forward_2d(hidden_states)
            output_latents.append(latents_2d)
            output_positional_encodings.append(pos_2d)
        combined_latents = torch.cat(output_latents, dim=1)
        combined_positional_encoding = None
        if positional_encoding is not None and output_positional_encodings:
            combined_positional_encoding = torch.cat(output_positional_encodings, dim=1)
        return combined_latents, combined_positional_encoding
    def _forward_1d(
        self,
        hidden_states: torch.Tensor,
        positional_encoding: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size = hidden_states.shape[0]
        latents = self.latents_1d.unsqueeze(0).expand(batch_size, -1, -1)
        flattened_features = hidden_states.permute(0, 2, 3, 1).flatten(1, 2)
        positional_features = None
        if positional_encoding is not None:
            positional_features = positional_encoding.permute(0, 2, 3, 1).flatten(1, 2)
        for layer in self.layers:
            latents = layer(latents, flattened_features, positional_features)
        latents = self.layer_norm(latents)
        output_positional_encoding = None
        if positional_encoding is not None:
            output_positional_encoding = torch.zeros_like(latents)
        return latents, output_positional_encoding
    def _forward_2d(self, hidden_states: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, channels, height, width = hidden_states.shape
        latents_2d = self.latents_2d.unsqueeze(0).expand(batch_size, -1, -1).view(-1, 1, channels)
        num_windows_per_dim = int(math.sqrt(self.num_latents_2d))
        window_size = height // num_windows_per_dim
        windowed_input = hidden_states.permute(0, 2, 3, 1)
        windowed_features, _ = window_partition(windowed_input, window_size)
        windowed_features = windowed_features.flatten(1, 2)
        for layer in self.layers:
            latents_2d = layer(latents_2d, windowed_features, positional_encoding=None)
        latents_2d = latents_2d.view(batch_size, num_windows_per_dim, num_windows_per_dim, channels).permute(
            0, 3, 1, 2
        )
        positional_encoding_2d = self.positional_encoding(latents_2d.shape, latents_2d.device, latents_2d.dtype).to(
            dtype=hidden_states.dtype
        )
        positional_encoding_2d = positional_encoding_2d.permute(0, 2, 3, 1).flatten(1, 2)
        latents_2d = latents_2d.permute(0, 2, 3, 1).flatten(1, 2)
        latents_2d = self.layer_norm(latents_2d)
        return latents_2d, positional_encoding_2d
@dataclass
@auto_docstring(custom_intro="Base class for the EdgeTamVideo model's output.")
class EdgeTamVideoImageSegmentationOutput(ModelOutput):
    iou_scores: Optional[torch.FloatTensor] = None
    pred_masks: Optional[torch.FloatTensor] = None
    object_score_logits: Optional[torch.FloatTensor] = None
    image_embeddings: tuple[torch.FloatTensor, ...] = None
    vision_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    vision_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    mask_decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    high_res_masks: Optional[torch.FloatTensor] = None
    object_pointer: Optional[torch.FloatTensor] = None
@dataclass
@auto_docstring(custom_intro="Base class for the Sam2 model's output.")
class EdgeTamVideoSegmentationOutput(ModelOutput):
    pred_masks: Optional[torch.FloatTensor] = None
    frame_idx: Optional[int] = None
class EdgeTamVideoPositionalEmbedding(nn.Module):
    def __init__(self, config: EdgeTamVideoPromptEncoderConfig):
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
class EdgeTamVideoMaskEmbedding(nn.Module):
    def __init__(self, config: EdgeTamVideoPromptEncoderConfig):
        super().__init__()
        self.mask_input_channels = config.mask_input_channels // 4
        self.activation = ACT2FN[config.hidden_act]
        self.conv1 = nn.Conv2d(1, self.mask_input_channels, kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(self.mask_input_channels, config.mask_input_channels, kernel_size=2, stride=2)
        self.conv3 = nn.Conv2d(config.mask_input_channels, config.hidden_size, kernel_size=1)
        self.layer_norm1 = EdgeTamVideoLayerNorm(
            self.mask_input_channels, eps=config.layer_norm_eps, data_format="channels_first"
        )
        self.layer_norm2 = EdgeTamVideoLayerNorm(
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
class EdgeTamVideoPromptEncoder(nn.Module):
    def __init__(self, config: EdgeTamVideoPromptEncoderConfig):
        super().__init__()
        self.shared_embedding = EdgeTamVideoPositionalEmbedding(config)
        self.mask_embed = EdgeTamVideoMaskEmbedding(config)
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
class EdgeTamVideoTwoWayTransformer(nn.Module):
    def __init__(self, config: EdgeTamVideoMaskDecoderConfig):
        super().__init__()
        self.config = config
        self.num_hidden_layers = config.num_hidden_layers
        self.layers = nn.ModuleList()
        for i in range(self.num_hidden_layers):
            self.layers.append(EdgeTamVideoTwoWayAttentionBlock(config, skip_first_layer_pe=(i == 0)))
        self.final_attn_token_to_image = EdgeTamVideoAttention(config)
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
class EdgeTamVideoMaskDecoder(nn.Module):
    def __init__(self, config: EdgeTamVideoMaskDecoderConfig):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_multimask_outputs = config.num_multimask_outputs
        self.num_mask_tokens = config.num_multimask_outputs + 1
        self.iou_token = nn.Embedding(1, self.hidden_size)
        self.mask_tokens = nn.Embedding(self.num_mask_tokens, self.hidden_size)
        self.transformer = EdgeTamVideoTwoWayTransformer(config)
        self.upscale_conv1 = nn.ConvTranspose2d(self.hidden_size, self.hidden_size // 4, kernel_size=2, stride=2)
        self.upscale_conv2 = nn.ConvTranspose2d(self.hidden_size // 4, self.hidden_size // 8, kernel_size=2, stride=2)
        self.upscale_layer_norm = EdgeTamVideoLayerNorm(self.hidden_size // 4, data_format="channels_first")
        self.activation = nn.GELU()
        mlps_list = []
        for _ in range(self.num_mask_tokens):
            mlps_list += [EdgeTamVideoFeedForward(self.hidden_size, self.hidden_size, self.hidden_size // 8, 3)]
        self.output_hypernetworks_mlps = nn.ModuleList(mlps_list)
        self.iou_prediction_head = EdgeTamVideoFeedForward(
            self.hidden_size,
            config.iou_head_hidden_dim,
            self.num_mask_tokens,
            config.iou_head_depth,
            sigmoid_output=True,
        )
        self.conv_s0 = nn.Conv2d(config.hidden_size, config.hidden_size // 8, kernel_size=1, stride=1)
        self.conv_s1 = nn.Conv2d(config.hidden_size, config.hidden_size // 4, kernel_size=1, stride=1)
        self.obj_score_token = nn.Embedding(1, self.hidden_size)
        self.pred_obj_score_head = EdgeTamVideoFeedForward(self.hidden_size, self.hidden_size, 1, 3)
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
NO_OBJ_SCORE = -1024.0
def get_1d_sine_pe(pos_inds, dim, temperature=10000):
    pe_dim = dim // 2
    dim_t = torch.arange(pe_dim, dtype=torch.float32, device=pos_inds.device)
    dim_t = temperature ** (2 * (dim_t // 2) / pe_dim)
    pos_embed = pos_inds.unsqueeze(-1) / dim_t
    pos_embed = torch.cat([pos_embed.sin(), pos_embed.cos()], dim=-1)
    return pos_embed
@auto_docstring
class EdgeTamVideoModel(EdgeTamVideoPreTrainedModel):
    _tied_weights_keys = ["prompt_encoder.shared_embedding.positional_embedding"]
    _keys_to_ignore_on_load_missing = ["prompt_encoder.shared_embedding.positional_embedding"]
    _can_record_outputs = {"mask_decoder_attentions": OutputRecorder(EdgeTamVideoTwoWayAttentionBlock, index=2)}
    _keys_to_ignore_on_load_unexpected = []
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__(config)
        self.shared_image_embedding = EdgeTamVideoPositionalEmbedding(config.prompt_encoder_config)
        self.vision_encoder = AutoModel.from_config(config.vision_config)
        self.prompt_encoder = EdgeTamVideoPromptEncoder(config.prompt_encoder_config)
        config.mask_decoder_config._attn_implementation = config._attn_implementation
        self.mask_decoder = EdgeTamVideoMaskDecoder(config.mask_decoder_config)
        self.num_feature_levels = config.vision_config.num_feature_levels
        self.backbone_feature_sizes = config.vision_config.backbone_feature_sizes
        self.hidden_dim = config.vision_config.fpn_hidden_size
        self.no_memory_embedding = torch.nn.Parameter(torch.zeros(1, 1, self.hidden_dim))
        self.config = config
        self.image_size = config.image_size
        self.memory_attention = EdgeTamVideoMemoryAttention(config)
        self.memory_encoder = EdgeTamVideoMemoryEncoder(config)
        self.no_memory_positional_encoding = torch.nn.Parameter(
            torch.zeros(1, 1, config.vision_config.fpn_hidden_size)
        )
        self.mem_dim = config.memory_encoder_output_channels
        self.num_maskmem = config.num_maskmem
        self.memory_temporal_positional_encoding = torch.nn.Parameter(
            torch.zeros(self.num_maskmem, 1, 1, self.mem_dim)
        )
        self.no_object_pointer = torch.nn.Parameter(torch.zeros(1, self.hidden_dim))
        self.mask_downsample = torch.nn.Conv2d(1, 1, kernel_size=4, stride=4)
        self.object_pointer_proj = EdgeTamVideoFeedForward(self.hidden_dim, self.hidden_dim, self.hidden_dim, 3)
        if self.config.enable_temporal_pos_encoding_for_object_pointers:
            self.temporal_positional_encoding_projection_layer = torch.nn.Linear(self.hidden_dim, self.mem_dim)
        else:
            self.temporal_positional_encoding_projection_layer = torch.nn.Identity()
        self.occlusion_spatial_embedding_parameter = None
        if config.enable_occlusion_spatial_embedding:
            self.occlusion_spatial_embedding_parameter = torch.nn.Parameter(torch.zeros(1, self.mem_dim))
        self.spatial_perceiver = EdgeTamVideoPerceiverResampler(config)
        self.post_init()
    def _tie_weights(self):
        self.prompt_encoder.shared_embedding.positional_embedding.data = (
            self.shared_image_embedding.positional_embedding.data
        )
    def get_input_embeddings(self):
        return self.vision_encoder.get_input_embeddings()
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
    ) -> tuple[torch.Tensor, torch.Tensor]:
        prompt_output = self.prompt_encoder(
            input_points=input_points,
            input_labels=input_labels,
            input_boxes=input_boxes,
            input_masks=input_masks,
        )
        return prompt_output
    @torch.inference_mode()
    @auto_docstring(custom_intro="Propagate the objects through a streamed video frame.")
    def forward(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        frame_idx: Optional[int] = None,
        frame: Optional[torch.Tensor] = None,
        reverse: bool = False,
    ) -> EdgeTamVideoSegmentationOutput:
        if frame is not None:
            frame_idx = inference_session.add_new_frame(frame, frame_idx)
        if frame is not None and inference_session.get_obj_num() == 0:
            raise ValueError("No objects are provided for tracking; please add inputs first.")
        num_objects = inference_session.get_obj_num()
        pred_masks_per_obj = [None] * num_objects
        for obj_idx in range(num_objects):
            obj_id = inference_session.obj_idx_to_id(obj_idx)
            has_new_inputs = obj_id in inference_session.obj_with_new_inputs
            has_cond_output = frame_idx in inference_session.output_dict_per_obj[obj_idx]["cond_frame_outputs"]
            if (not has_new_inputs) and has_cond_output:
                pred_masks = inference_session.get_output(obj_idx, frame_idx, "pred_masks", is_conditioning_frame=True)
                is_init_cond_frame = True
            else:
                is_init_cond_frame = False
                point_inputs = None
                mask_inputs = None
                if has_new_inputs:
                    is_init_cond_frame = frame_idx not in inference_session.frames_tracked_per_obj[obj_idx]
                    if is_init_cond_frame:
                        reverse = False
                    point_inputs = inference_session.point_inputs_per_obj[obj_idx].get(frame_idx, None)
                    mask_inputs = inference_session.mask_inputs_per_obj[obj_idx].get(frame_idx, None)
                    if point_inputs is not None or mask_inputs is not None:
                        inference_session.obj_with_new_inputs.remove(obj_id)
                current_out = self._run_single_frame_inference(
                    inference_session=inference_session,
                    obj_idx=obj_idx,
                    frame_idx=frame_idx,
                    batch_size=1,
                    is_init_cond_frame=is_init_cond_frame,
                    point_inputs=point_inputs,
                    mask_inputs=mask_inputs,
                    reverse=reverse,
                    run_mem_encoder=True,
                    streaming=frame is not None,
                )
                inference_session.store_output(
                    obj_idx, frame_idx, output_value=current_out, is_conditioning_frame=is_init_cond_frame
                )
                pred_masks = current_out["pred_masks"]
            pred_masks_per_obj[obj_idx] = pred_masks
            if not is_init_cond_frame:
                inference_session.frames_tracked_per_obj[obj_idx][frame_idx] = {"reverse": reverse}
        if len(pred_masks_per_obj) > 1:
            all_pred_masks = torch.cat(pred_masks_per_obj, dim=0)
        else:
            all_pred_masks = pred_masks_per_obj[0]
        return EdgeTamVideoSegmentationOutput(pred_masks=all_pred_masks, frame_idx=frame_idx)
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
        vision_outputs: EdgeTamVideoVisionEncoderOutput = self.vision_encoder(
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
    def _prepare_vision_features(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        frame_idx: int,
        batch_size: int,
    ) -> tuple[torch.Tensor, list[torch.Tensor]]:
        if cached_features := inference_session.cache.get_vision_features(frame_idx):
            vision_feats = cached_features["vision_feats"]
            vision_pos_embeds = cached_features["vision_pos_embeds"]
        else:
            image_batch = inference_session.get_frame(frame_idx).unsqueeze(0)
            vision_feats, vision_pos_embeds, _, _ = self.get_image_features(image_batch)
            inference_session.cache.cache_vision_features(
                frame_idx, {"vision_feats": vision_feats, "vision_pos_embeds": vision_pos_embeds}
            )
        if batch_size > 1:
            vision_feats = vision_feats.expand(batch_size, -1, -1, -1)
            vision_pos_embeds = [pe.expand(batch_size, -1, -1, -1) for pe in vision_pos_embeds]
        return vision_feats, vision_pos_embeds
    def _single_frame_forward(
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
    ) -> EdgeTamVideoImageSegmentationOutput:
        if not ((pixel_values is None) ^ (image_embeddings is None)):
            raise ValueError("Exactly one of pixel_values or image_embeddings must be provided.")
        if input_points is not None and input_boxes is not None:
            if input_points.shape[1] != input_boxes.shape[1]:
                raise ValueError(
                    f"You should provide as many bounding boxes as input points per box. Got {input_points.shape[1]} and {input_boxes.shape[1]}."
                )
        elif input_points is not None:
            num_objects = input_points.shape[1]
        elif input_boxes is not None:
            num_objects = input_boxes.shape[1]
        elif input_masks is not None:
            num_objects = input_masks.shape[1]
        else:
            num_objects = 1
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
        low_res_multimasks, iou_scores, sam_output_tokens, object_score_logits = self.mask_decoder(
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
        is_obj_appearing = object_score_logits > 0
        low_res_multimasks = torch.where(
            is_obj_appearing[:, None, None],
            low_res_multimasks,
            NO_OBJ_SCORE,
        )
        high_res_multimasks = (
            F.interpolate(
                low_res_multimasks.squeeze(1).float(),
                size=(self.image_size, self.image_size),
                mode="bilinear",
                align_corners=False,
            )
            .unsqueeze(1)
            .to(low_res_multimasks.dtype)
        )
        sam_output_token = sam_output_tokens[:, :, 0]
        if multimask_output:
            best_iou_inds = torch.argmax(iou_scores, dim=-1)
            batch_inds = torch.arange(batch_size, device=high_res_multimasks.device)
            object_batch_inds = torch.arange(num_objects, device=high_res_multimasks.device)
            low_res_masks = low_res_multimasks[batch_inds, object_batch_inds, best_iou_inds]
            high_res_masks = high_res_multimasks[batch_inds, object_batch_inds, best_iou_inds]
            if sam_output_tokens.size(2) > 1:
                sam_output_token = sam_output_tokens[batch_inds, object_batch_inds, best_iou_inds]
        else:
            low_res_masks, high_res_masks = low_res_multimasks[:, :, 0], high_res_multimasks[:, :, 0]
        object_pointer = self.object_pointer_proj(sam_output_token)
        lambda_is_obj_appearing = is_obj_appearing.to(object_pointer.dtype)
        object_pointer = lambda_is_obj_appearing * object_pointer
        object_pointer = object_pointer + (1 - lambda_is_obj_appearing) * self.no_object_pointer
        return EdgeTamVideoImageSegmentationOutput(
            iou_scores=iou_scores,
            pred_masks=low_res_masks,
            high_res_masks=high_res_masks,
            object_pointer=object_pointer,
            object_score_logits=object_score_logits,
            image_embeddings=image_embeddings,
            vision_hidden_states=vision_hidden_states,
            vision_attentions=vision_attentions,
        )
    def _use_mask_as_output(
        self,
        backbone_features: torch.Tensor,
        high_res_features: list[torch.Tensor],
        mask_inputs: torch.Tensor,
    ) -> EdgeTamVideoImageSegmentationOutput:
        out_scale, out_bias = 20.0, -10.0
        mask_inputs_float = mask_inputs.to(backbone_features[0].dtype)
        high_res_masks = mask_inputs_float * out_scale + out_bias
        low_res_masks = F.interpolate(
            high_res_masks.float(),
            size=(high_res_masks.size(-2) // 4, high_res_masks.size(-1) // 4),
            align_corners=False,
            mode="bilinear",
            antialias=True,
        ).to(backbone_features[0].dtype)
        iou_scores = mask_inputs.new_ones(mask_inputs.size(0), 1).to(backbone_features[0].dtype)
        object_pointer = self._single_frame_forward(
            input_masks=self.mask_downsample(mask_inputs_float.to(backbone_features[0].dtype)),
            image_embeddings=high_res_features + [backbone_features],
        ).object_pointer
        is_obj_appearing = torch.any(mask_inputs.flatten(1).float() > 0.0, dim=1)
        is_obj_appearing = is_obj_appearing[..., None]
        lambda_is_obj_appearing = is_obj_appearing.to(backbone_features[0].dtype)
        object_score_logits = out_scale * lambda_is_obj_appearing + out_bias
        object_pointer = lambda_is_obj_appearing * object_pointer
        object_pointer = object_pointer + (1 - lambda_is_obj_appearing) * self.no_object_pointer
        return EdgeTamVideoImageSegmentationOutput(
            iou_scores=iou_scores,
            pred_masks=low_res_masks,
            high_res_masks=high_res_masks,
            object_pointer=object_pointer,
            object_score_logits=object_score_logits,
            image_embeddings=high_res_features + [backbone_features],
        )
    def _gather_memory_frame_outputs(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        obj_idx: int,
        frame_idx: int,
        track_in_reverse_time: bool = False,
    ) -> list[tuple[int, dict]]:
        temporal_positions_and_previous_outputs = []
        conditioning_outputs = inference_session.output_dict_per_obj[obj_idx]["cond_frame_outputs"]
        if not conditioning_outputs:
            raise ValueError(
                "maskmem_features in conditioning outputs cannot be empty when not is_initial_conditioning_frame"
            )
        temporal_positions_and_previous_outputs = [(0, out) for out in conditioning_outputs.values()]
        for relative_temporal_offset in range(self.num_maskmem - 1, 0, -1):
            if not track_in_reverse_time:
                previous_frame_idx = frame_idx - relative_temporal_offset
            else:
                previous_frame_idx = frame_idx + relative_temporal_offset
            output_data = inference_session.output_dict_per_obj[obj_idx]["non_cond_frame_outputs"].get(
                previous_frame_idx, None
            )
            temporal_positions_and_previous_outputs.append((relative_temporal_offset, output_data))
        return temporal_positions_and_previous_outputs
    def _build_memory_attention_inputs(
        self,
        temporal_positions_and_previous_outputs: list[tuple[int, dict]],
        device: torch.device,
    ) -> tuple[list[torch.Tensor], list[torch.Tensor]]:
        memories_to_concatenate = []
        memory_positional_embeddings_to_concatenate = []
        for relative_temporal_offset, prev_output_data in temporal_positions_and_previous_outputs:
            if prev_output_data is None:
                continue
            memory_features = prev_output_data["maskmem_features"].to(device, non_blocking=True)
            memories_to_concatenate.append(memory_features.permute(1, 0, 2))
            spatial_memory_pos_embed = prev_output_data["maskmem_pos_enc"].to(device, non_blocking=True)
            spatial_memory_pos_embed = spatial_memory_pos_embed.squeeze(1).permute(1, 0, 2)
            combined_memory_pos_embed = (
                spatial_memory_pos_embed + self.memory_temporal_positional_encoding[relative_temporal_offset - 1]
            )
            memory_positional_embeddings_to_concatenate.append(combined_memory_pos_embed)
        return memories_to_concatenate, memory_positional_embeddings_to_concatenate
    def _get_object_pointers(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        obj_idx: int,
        frame_idx: int,
        num_total_frames: int,
        device: torch.device,
        track_in_reverse_time: bool = False,
        streaming: bool = False,
    ) -> tuple[list[int], list[torch.Tensor], int]:
        temporal_position_sign_multiplier = -1 if track_in_reverse_time else 1
        if streaming:
            max_object_pointers_to_use = self.config.max_object_pointers_in_encoder
        else:
            max_object_pointers_to_use = min(num_total_frames, self.config.max_object_pointers_in_encoder)
        temporal_offsets: list[int] = []
        pointer_tokens: list[torch.Tensor] = []
        conditioning_outputs = inference_session.output_dict_per_obj[obj_idx]["cond_frame_outputs"]
        eligible_conditioning_outputs = conditioning_outputs
        if not self.training:
            eligible_conditioning_outputs = {
                temporal_idx: out
                for temporal_idx, out in conditioning_outputs.items()
                if (temporal_idx >= frame_idx if track_in_reverse_time else temporal_idx <= frame_idx)
            }
        for temporal_idx, out_data in eligible_conditioning_outputs.items():
            temporal_difference = (frame_idx - temporal_idx) * temporal_position_sign_multiplier
            temporal_offsets.append(temporal_difference)
            pointer_tokens.append(out_data["object_pointer"].to(device))
        for t_diff_offset in range(1, max_object_pointers_to_use):
            ref_frame_idx = frame_idx + t_diff_offset if track_in_reverse_time else frame_idx - t_diff_offset
            if ref_frame_idx < 0 or (
                not streaming and num_total_frames is not None and ref_frame_idx >= num_total_frames
            ):
                break
            out_data = inference_session.output_dict_per_obj[obj_idx]["non_cond_frame_outputs"].get(
                ref_frame_idx, None
            )
            if out_data is not None:
                temporal_offsets.append(t_diff_offset)
                pointer_tokens.append(out_data["object_pointer"].to(device))
        return temporal_offsets, pointer_tokens, max_object_pointers_to_use
    def _process_object_pointers(
        self,
        temporal_offsets: list[int],
        pointer_tokens: list[torch.Tensor],
        max_object_pointers_to_use: int,
        batch_size: int,
        num_channels: int,
        device: torch.device,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not pointer_tokens:
            return None, None
        object_pointers = torch.stack(pointer_tokens, dim=0)
        if self.config.enable_temporal_pos_encoding_for_object_pointers:
            max_temporal_diff = float(max_object_pointers_to_use - 1)
            pointer_tpos_dim = num_channels
            normalized_temporal_diffs = (
                torch.tensor(temporal_offsets, device=device, dtype=torch.float32) / max_temporal_diff
            )
            sine_pe = get_1d_sine_pe(normalized_temporal_diffs, dim=pointer_tpos_dim).to(object_pointers.dtype)
            projected_sine_pe = self.temporal_positional_encoding_projection_layer(sine_pe)
            object_pointers_pos_embed = projected_sine_pe.unsqueeze(1).expand(-1, batch_size, self.mem_dim)
        else:
            object_pointers_pos_embed = object_pointers.new_zeros(
                len(temporal_offsets), batch_size, self.mem_dim, dtype=object_pointers.dtype
            )
        if self.mem_dim < num_channels:
            num_splits = num_channels // self.mem_dim
            object_pointers = object_pointers.reshape(-1, batch_size, num_splits, self.mem_dim)
            object_pointers = object_pointers.permute(0, 2, 1, 3).flatten(
                0, 1
            )
            object_pointers_pos_embed = object_pointers_pos_embed.repeat_interleave(num_splits, dim=0)
        return object_pointers, object_pointers_pos_embed
    def _prepare_memory_conditioned_features(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        frame_idx: int,
        obj_idx: int,
        is_initial_conditioning_frame: bool,
        current_vision_features: list[torch.Tensor],
        current_vision_positional_embeddings: list[torch.Tensor],
        num_total_frames: int,
        track_in_reverse_time: bool = False,
        streaming: bool = False,
    ) -> torch.Tensor:
        batch_size = current_vision_features.size(1)
        num_channels = self.hidden_dim
        height, width = self.backbone_feature_sizes[-1]
        device = current_vision_features.device
        if self.num_maskmem == 0:
            current_feature_map = current_vision_features.permute(1, 2, 0).view(
                batch_size, num_channels, height, width
            )
            return current_feature_map
        if is_initial_conditioning_frame:
            conditioned_feature_map_flat = current_vision_features + self.no_memory_embedding
            conditioned_feature_map = conditioned_feature_map_flat.permute(1, 2, 0).view(
                batch_size, num_channels, height, width
            )
            return conditioned_feature_map
        temporal_positions_and_previous_outputs = self._gather_memory_frame_outputs(
            inference_session, obj_idx, frame_idx, track_in_reverse_time
        )
        memories_to_concatenate, memory_positional_embeddings_to_concatenate = self._build_memory_attention_inputs(
            temporal_positions_and_previous_outputs, device
        )
        num_spatial_memory_tokens = len(memories_to_concatenate)
        temporal_offsets, pointer_tokens, max_object_pointers_to_use = self._get_object_pointers(
            inference_session, obj_idx, frame_idx, num_total_frames, device, track_in_reverse_time, streaming
        )
        num_object_pointer_tokens = 0
        if pointer_tokens:
            object_pointers, object_pointers_pos_embed = self._process_object_pointers(
                temporal_offsets, pointer_tokens, max_object_pointers_to_use, batch_size, num_channels, device
            )
            if object_pointers is not None:
                memories_to_concatenate.append(object_pointers)
                memory_positional_embeddings_to_concatenate.append(object_pointers_pos_embed)
                num_object_pointer_tokens = object_pointers.shape[0]
        combined_memory = torch.cat(memories_to_concatenate, dim=0)
        combined_memory_positional_embeddings = torch.cat(memory_positional_embeddings_to_concatenate, dim=0)
        conditioned_feature_map_flat = self.memory_attention(
            current_vision_features=current_vision_features,
            current_vision_position_embeddings=current_vision_positional_embeddings,
            memory=combined_memory,
            memory_posision_embeddings=combined_memory_positional_embeddings,
            num_object_pointer_tokens=num_object_pointer_tokens,
            num_spatial_memory_tokens=num_spatial_memory_tokens,
        )
        conditioned_feature_map = (
            conditioned_feature_map_flat.squeeze(1).permute(0, 2, 1).view(batch_size, num_channels, height, width)
        )
        return conditioned_feature_map
    def _use_multimask(self, is_init_cond_frame: bool, point_inputs: Optional[dict]) -> bool:
        num_pts = 0 if point_inputs is None else point_inputs["point_labels"].size(2)
        multimask_output = (
            self.config.multimask_output_in_sam
            and (is_init_cond_frame or self.config.multimask_output_for_tracking)
            and (self.config.multimask_min_pt_num <= num_pts <= self.config.multimask_max_pt_num)
        )
        return multimask_output
    def _run_single_frame_inference(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        frame_idx: int,
        obj_idx: int,
        batch_size: int,
        is_init_cond_frame: bool,
        point_inputs: Optional[torch.Tensor],
        mask_inputs: Optional[torch.Tensor],
        reverse: bool,
        run_mem_encoder: bool,
        prev_sam_mask_logits: Optional[torch.Tensor] = None,
        streaming: bool = False,
    ) -> dict[str, Any]:
        current_vision_feats, current_vision_pos_embeds = self._prepare_vision_features(
            inference_session, frame_idx, batch_size
        )
        if point_inputs is not None and mask_inputs is not None:
            raise ValueError(
                "point_inputs and mask_inputs should not appear as input simultaneously on the same frame"
            )
        if len(current_vision_feats) > 1:
            high_res_features = [
                x.permute(1, 2, 0).view(x.size(1), x.size(2), *s)
                for x, s in zip(current_vision_feats[:-1], self.backbone_feature_sizes[:-1])
            ]
        else:
            high_res_features = None
        if mask_inputs is not None:
            pix_feat = current_vision_feats[-1].permute(1, 2, 0)
            pix_feat = pix_feat.view(-1, self.hidden_dim, *self.backbone_feature_sizes[-1])
            sam_outputs = self._use_mask_as_output(pix_feat, high_res_features, mask_inputs)
        else:
            pix_feat = self._prepare_memory_conditioned_features(
                inference_session=inference_session,
                frame_idx=frame_idx,
                obj_idx=obj_idx,
                is_initial_conditioning_frame=is_init_cond_frame,
                current_vision_features=current_vision_feats[-1],
                current_vision_positional_embeddings=current_vision_pos_embeds[-1],
                num_total_frames=inference_session.num_frames,
                track_in_reverse_time=reverse,
                streaming=streaming,
            )
            if prev_sam_mask_logits is not None:
                mask_inputs = prev_sam_mask_logits
            multimask_output = self._use_multimask(is_init_cond_frame, point_inputs)
            sam_outputs = self._single_frame_forward(
                pixel_values=None,
                input_points=point_inputs["point_coords"] if point_inputs is not None else None,
                input_labels=point_inputs["point_labels"] if point_inputs is not None else None,
                input_masks=mask_inputs,
                image_embeddings=high_res_features + [pix_feat],
                multimask_output=multimask_output,
            )
        maskmem_features = None
        maskmem_pos_enc = None
        if run_mem_encoder and self.num_maskmem > 0:
            maskmem_features, maskmem_pos_enc = self._encode_new_memory(
                current_vision_feats=current_vision_feats[-1],
                pred_masks_high_res=sam_outputs.high_res_masks,
                object_score_logits=sam_outputs.object_score_logits,
                is_mask_from_pts=(point_inputs is not None or mask_inputs is not None),
            )
        current_out = {
            "pred_masks": sam_outputs.pred_masks,
            "object_pointer": sam_outputs.object_pointer,
            "maskmem_features": maskmem_features if maskmem_features is not None else None,
            "maskmem_pos_enc": maskmem_pos_enc,
        }
        if not self.training:
            current_out["object_score_logits"] = sam_outputs.object_score_logits
        return current_out
    def _encode_new_memory(
        self,
        current_vision_feats: torch.Tensor,
        pred_masks_high_res: torch.Tensor,
        object_score_logits: torch.Tensor,
        is_mask_from_pts: bool,
    ) -> tuple[torch.Tensor, list[torch.Tensor]]:
        batch_size = current_vision_feats.size(1)
        channels = self.hidden_dim
        height, width = self.backbone_feature_sizes[-1]
        pix_feat = current_vision_feats.permute(1, 2, 0).view(batch_size, channels, height, width)
        if is_mask_from_pts and not self.training:
            mask_for_mem = (pred_masks_high_res > 0).to(pred_masks_high_res.dtype)
        else:
            mask_for_mem = torch.sigmoid(pred_masks_high_res)
        mask_for_mem = mask_for_mem * self.config.sigmoid_scale_for_mem_enc
        mask_for_mem = mask_for_mem + self.config.sigmoid_bias_for_mem_enc
        maskmem_features, maskmem_pos_enc = self.memory_encoder(
            pix_feat,
            mask_for_mem,
        )
        if self.occlusion_spatial_embedding_parameter is not None:
            is_obj_appearing = (object_score_logits > 0).float()
            maskmem_features += (1 - is_obj_appearing[..., None]) * self.occlusion_spatial_embedding_parameter[
                ..., None, None
            ].expand(*maskmem_features.shape)
        maskmem_pos_enc = maskmem_pos_enc.to(pred_masks_high_res.dtype)
        maskmem_features, maskmem_pos_enc = self.spatial_perceiver(maskmem_features, maskmem_pos_enc)
        maskmem_features = maskmem_features.to(pred_masks_high_res.dtype)
        maskmem_pos_enc = maskmem_pos_enc.to(pred_masks_high_res.dtype)
        return maskmem_features, maskmem_pos_enc
    @torch.inference_mode()
    @auto_docstring(
    )
    def propagate_in_video_iterator(
        self,
        inference_session: EdgeTamVideoInferenceSession,
        start_frame_idx: Optional[int] = None,
        max_frame_num_to_track: Optional[int] = None,
        reverse: bool = False,
    ) -> Iterator[EdgeTamVideoSegmentationOutput]:
        num_frames = inference_session.num_frames
        if start_frame_idx is None:
            frames_with_inputs = [
                frame_idx
                for obj_output_dict in inference_session.output_dict_per_obj.values()
                for frame_idx in obj_output_dict["cond_frame_outputs"]
            ]
            if not frames_with_inputs:
                raise ValueError(
                    "Cannot determine the starting frame index; please specify it manually, or run inference on a frame with inputs first."
                )
            start_frame_idx = min(frames_with_inputs)
        if max_frame_num_to_track is None:
            max_frame_num_to_track = num_frames
        if reverse:
            end_frame_idx = max(start_frame_idx - max_frame_num_to_track, 0)
            if start_frame_idx > 0:
                processing_order = range(start_frame_idx, end_frame_idx - 1, -1)
            else:
                processing_order = []
        else:
            end_frame_idx = min(start_frame_idx + max_frame_num_to_track, num_frames - 1)
            processing_order = range(start_frame_idx, end_frame_idx + 1)
        for frame_idx in tqdm(processing_order, desc="propagate in video"):
            edgetam_video_output = self(inference_session, frame_idx=frame_idx, reverse=reverse)
            yield edgetam_video_output
__all__ = ["EdgeTamVideoModel", "EdgeTamVideoInferenceSession", "EdgeTamVideoPreTrainedModel"]