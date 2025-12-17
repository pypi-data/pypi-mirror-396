import math
from typing import Callable, Optional
import torch
import torch.nn as nn
import torch.utils.checkpoint
from torch import Tensor
from MEROAI.models.sam2.modeling_sam2 import (
    eager_attention_forward,
    window_partition,
)
from MEROAI.utils.generic import OutputRecorder
from ...activations import ACT2FN
from ...configuration_utils import PretrainedConfig
from ...modeling_flash_attention_utils import FlashAttentionKwargs
from ...modeling_utils import ALL_ATTENTION_FUNCTIONS
from ...processing_utils import Unpack
from ...pytorch_utils import compile_compatible_method_lru_cache
from ...utils import (
    auto_docstring,
)
from ..auto import CONFIG_MAPPING, AutoConfig
from ..sam2_video.configuration_sam2_video import (
    Sam2VideoConfig,
    Sam2VideoMaskDecoderConfig,
    Sam2VideoPromptEncoderConfig,
)
from ..sam2_video.modeling_sam2_video import (
    Sam2VideoAttention,
    Sam2VideoFeedForward,
    Sam2VideoInferenceSession,
    Sam2VideoLayerNorm,
    Sam2VideoMemoryAttention,
    Sam2VideoMemoryEncoder,
    Sam2VideoMemoryFuserCXBlock,
    Sam2VideoModel,
    Sam2VideoPositionEmbeddingSine,
    Sam2VideoPreTrainedModel,
    Sam2VideoTwoWayAttentionBlock,
    Sam2VideoVisionEncoderOutput,
    Sam2VideoVisionRotaryEmbedding,
    rotate_pairwise,
)
class EdgeTamVideoPromptEncoderConfig(Sam2VideoPromptEncoderConfig):
    pass
class EdgeTamVideoMaskDecoderConfig(Sam2VideoMaskDecoderConfig):
    pass
class EdgeTamVideoConfig(Sam2VideoConfig):
    model_type = "edgetam_video"
    sub_configs = {
        "vision_config": AutoConfig,
        "prompt_encoder_config": EdgeTamVideoPromptEncoderConfig,
        "mask_decoder_config": EdgeTamVideoMaskDecoderConfig,
    }
    def __init__(
        self,
        vision_config=None,
        prompt_encoder_config=None,
        mask_decoder_config=None,
        initializer_range=0.02,
        num_maskmem=7,
        image_size=1024,
        sigmoid_scale_for_mem_enc=20.0,
        sigmoid_bias_for_mem_enc=-10.0,
        enable_occlusion_spatial_embedding=True,
        multimask_output_in_sam=True,
        multimask_min_pt_num=0,
        multimask_max_pt_num=1,
        multimask_output_for_tracking=True,
        max_object_pointers_in_encoder=16,
        enable_temporal_pos_encoding_for_object_pointers=True,
        memory_attention_hidden_size=256,
        memory_attention_num_layers=2,
        memory_attention_num_attention_heads=1,
        memory_attention_downsample_rate=1,
        memory_attention_mlp_hidden_size=2048,
        memory_attention_mlp_hidden_act="relu",
        memory_attention_dropout=0.1,
        memory_attention_rope_theta=10000,
        memory_attention_rope_feat_sizes=None,
        memory_attention_rope_k_sizes=None,
        memory_attention_rope_dropout=0.1,
        perceiver_resampler_num_latents=256,
        perceiver_resampler_num_latents_2d=256,
        perceiver_resampler_hidden_size=64,
        perceiver_resampler_mlp_intermediate_size=256,
        perceiver_resampler_num_attention_heads=1,
        perceiver_resampler_attention_head_dim=64,
        perceiver_resampler_num_layers=2,
        perceiver_resampler_hidden_dropout=0.0,
        perceiver_resampler_attention_dropout=0.0,
        memory_encoder_hidden_size=256,
        memory_encoder_output_channels=64,
        mask_downsampler_embed_dim=256,
        memory_fuser_intermediate_dim=1024,
        mask_downsampler_kernel_size=3,
        mask_downsampler_stride=2,
        mask_downsampler_padding=1,
        mask_downsampler_total_stride=16,
        mask_downsampler_hidden_act="gelu",
        memory_fuser_num_layers=2,
        memory_fuser_embed_dim=256,
        memory_fuser_kernel_size=7,
        memory_fuser_padding=3,
        memory_fuser_layer_scale_init_value=1e-6,
        memory_fuser_hidden_act="gelu",
        **kwargs,
    ):
        PretrainedConfig.__init__(**kwargs)
        vision_config = vision_config if vision_config is not None else {}
        prompt_encoder_config = prompt_encoder_config if prompt_encoder_config is not None else {}
        mask_decoder_config = mask_decoder_config if mask_decoder_config is not None else {}
        memory_attention_rope_feat_sizes = (
            [64, 64] if memory_attention_rope_feat_sizes is None else memory_attention_rope_feat_sizes
        )
        memory_attention_rope_k_sizes = (
            [16, 16] if memory_attention_rope_k_sizes is None else memory_attention_rope_k_sizes
        )
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "sam2_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        if isinstance(prompt_encoder_config, EdgeTamVideoPromptEncoderConfig):
            prompt_encoder_config = prompt_encoder_config.to_dict()
        if isinstance(mask_decoder_config, EdgeTamVideoMaskDecoderConfig):
            mask_decoder_config = mask_decoder_config.to_dict()
        self.vision_config = vision_config
        self.prompt_encoder_config = EdgeTamVideoPromptEncoderConfig(**prompt_encoder_config)
        self.mask_decoder_config = EdgeTamVideoMaskDecoderConfig(**mask_decoder_config)
        self.initializer_range = initializer_range
        self.num_maskmem = num_maskmem
        self.image_size = image_size
        self.sigmoid_scale_for_mem_enc = sigmoid_scale_for_mem_enc
        self.sigmoid_bias_for_mem_enc = sigmoid_bias_for_mem_enc
        self.enable_occlusion_spatial_embedding = enable_occlusion_spatial_embedding
        self.multimask_output_in_sam = multimask_output_in_sam
        self.multimask_min_pt_num = multimask_min_pt_num
        self.multimask_max_pt_num = multimask_max_pt_num
        self.multimask_output_for_tracking = multimask_output_for_tracking
        self.max_object_pointers_in_encoder = max_object_pointers_in_encoder
        self.enable_temporal_pos_encoding_for_object_pointers = enable_temporal_pos_encoding_for_object_pointers
        self.memory_attention_hidden_size = memory_attention_hidden_size
        self.memory_attention_num_layers = memory_attention_num_layers
        self.memory_attention_num_attention_heads = memory_attention_num_attention_heads
        self.memory_attention_downsample_rate = memory_attention_downsample_rate
        self.memory_attention_mlp_hidden_size = memory_attention_mlp_hidden_size
        self.memory_attention_mlp_hidden_act = memory_attention_mlp_hidden_act
        self.memory_attention_dropout = memory_attention_dropout
        self.memory_attention_rope_theta = memory_attention_rope_theta
        self.memory_attention_rope_feat_sizes = memory_attention_rope_feat_sizes
        self.memory_attention_rope_k_sizes = memory_attention_rope_k_sizes
        self.memory_attention_rope_dropout = memory_attention_rope_dropout
        self.perceiver_resampler_num_latents = perceiver_resampler_num_latents
        self.perceiver_resampler_num_latents_2d = perceiver_resampler_num_latents_2d
        self.perceiver_resampler_hidden_size = perceiver_resampler_hidden_size
        self.perceiver_resampler_mlp_intermediate_size = perceiver_resampler_mlp_intermediate_size
        self.perceiver_resampler_attention_head_dim = perceiver_resampler_attention_head_dim
        self.perceiver_resampler_num_attention_heads = perceiver_resampler_num_attention_heads
        self.perceiver_resampler_num_layers = perceiver_resampler_num_layers
        self.perceiver_resampler_hidden_dropout = perceiver_resampler_hidden_dropout
        self.perceiver_resampler_attention_dropout = perceiver_resampler_attention_dropout
        self.memory_encoder_hidden_size = memory_encoder_hidden_size
        self.memory_encoder_output_channels = memory_encoder_output_channels
        self.mask_downsampler_embed_dim = mask_downsampler_embed_dim
        self.mask_downsampler_kernel_size = mask_downsampler_kernel_size
        self.mask_downsampler_stride = mask_downsampler_stride
        self.mask_downsampler_padding = mask_downsampler_padding
        self.mask_downsampler_total_stride = mask_downsampler_total_stride
        self.mask_downsampler_hidden_act = mask_downsampler_hidden_act
        self.memory_fuser_num_layers = memory_fuser_num_layers
        self.memory_fuser_embed_dim = memory_fuser_embed_dim
        self.memory_fuser_intermediate_dim = memory_fuser_intermediate_dim
        self.memory_fuser_kernel_size = memory_fuser_kernel_size
        self.memory_fuser_padding = memory_fuser_padding
        self.memory_fuser_layer_scale_init_value = memory_fuser_layer_scale_init_value
        self.memory_fuser_hidden_act = memory_fuser_hidden_act
class EdgeTamVideoLayerNorm(Sam2VideoLayerNorm):
    pass
class EdgeTamVideoMemoryFuserCXBlock(Sam2VideoMemoryFuserCXBlock):
    pass
class EdgeTamVideoVisionEncoderOutput(Sam2VideoVisionEncoderOutput):
    pass
class EdgeTamVideoVisionRotaryEmbedding(Sam2VideoVisionRotaryEmbedding):
    def __init__(self, config: EdgeTamVideoConfig, end_x: Optional[int] = None, end_y: Optional[int] = None):
        nn.Module.__init__()
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
class EdgeTamVideoAttention(Sam2VideoAttention):
    pass
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
class EdgeTamVideoTwoWayAttentionBlock(Sam2VideoTwoWayAttentionBlock):
    pass
class EdgeTamVideoPositionEmbeddingSine(Sam2VideoPositionEmbeddingSine):
    @compile_compatible_method_lru_cache(maxsize=2)
    def forward(self, **super_kwargs):
        return super().forward(**super_kwargs)
class EdgeTamVideoMemoryEncoder(Sam2VideoMemoryEncoder):
    pass
class EdgeTamVideoFeedForward(Sam2VideoFeedForward):
    pass
class EdgeTamVideoPreTrainedModel(Sam2VideoPreTrainedModel):
    pass
class EdgeTamVideoInferenceSession(Sam2VideoInferenceSession):
    pass
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
class EdgeTamVideoMemoryAttention(Sam2VideoMemoryAttention):
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__()
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
@auto_docstring
class EdgeTamVideoModel(Sam2VideoModel):
    _tied_weights_keys = ["prompt_encoder.shared_embedding.positional_embedding"]
    _keys_to_ignore_on_load_missing = ["prompt_encoder.shared_embedding.positional_embedding"]
    _keys_to_ignore_on_load_unexpected = []
    _can_record_outputs = {"mask_decoder_attentions": OutputRecorder(EdgeTamVideoTwoWayAttentionBlock, index=2)}
    def __init__(self, config: EdgeTamVideoConfig):
        super().__init__(config)
        self.spatial_perceiver = EdgeTamVideoPerceiverResampler(config)
        self.post_init()
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
__all__ = [
    "EdgeTamVideoMaskDecoderConfig",
    "EdgeTamVideoPromptEncoderConfig",
    "EdgeTamVideoConfig",
    "EdgeTamVideoModel",
    "EdgeTamVideoInferenceSession",
    "EdgeTamVideoPreTrainedModel",
]