from dataclasses import dataclass
from typing import Callable, Optional, Union
import torch
from torch import nn
from ...activations import ACT2CLS, ACT2FN
from ...modeling_layers import GradientCheckpointingLayer
from ...modeling_outputs import BackboneOutput
from ...modeling_rope_utils import ROPE_INIT_FUNCTIONS
from ...modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from ...processing_utils import Unpack
from ...pytorch_utils import compile_compatible_method_lru_cache
from ...utils import (
    ModelOutput,
    MEROAIKwargs,
    auto_docstring,
    can_return_tuple,
    torch_int,
)
from ...utils.generic import check_model_inputs
from .configuration_efficientloftr import EfficientLoFTRConfig
@dataclass
@auto_docstring(
)
class KeypointMatchingOutput(ModelOutput):
    matches: Optional[torch.FloatTensor] = None
    matching_scores: Optional[torch.FloatTensor] = None
    keypoints: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[torch.FloatTensor]] = None
@compile_compatible_method_lru_cache(maxsize=32)
def compute_embeddings(inv_freq: torch.Tensor, embed_height: int, embed_width: int, hidden_size: int) -> torch.Tensor:
    i_indices = torch.ones(embed_height, embed_width, dtype=inv_freq.dtype, device=inv_freq.device)
    j_indices = torch.ones(embed_height, embed_width, dtype=inv_freq.dtype, device=inv_freq.device)
    i_indices = i_indices.cumsum(0).unsqueeze(-1)
    j_indices = j_indices.cumsum(1).unsqueeze(-1)
    emb = torch.zeros(1, embed_height, embed_width, hidden_size // 2, dtype=inv_freq.dtype, device=inv_freq.device)
    emb[:, :, :, 0::2] = i_indices * inv_freq
    emb[:, :, :, 1::2] = j_indices * inv_freq
    return emb
class EfficientLoFTRRotaryEmbedding(nn.Module):
    inv_freq: torch.Tensor
    def __init__(self, config: EfficientLoFTRConfig, device=None):
        super().__init__()
        self.config = config
        self.rope_type = config.rope_scaling["rope_type"]
        self.rope_init_fn = ROPE_INIT_FUNCTIONS[self.rope_type]
        inv_freq, _ = self.rope_init_fn(self.config, device)
        inv_freq_expanded = inv_freq[None, None, None, :].float().expand(1, 1, 1, -1)
        self.register_buffer("inv_freq", inv_freq_expanded, persistent=False)
    @torch.no_grad()
    def forward(
        self, x: torch.Tensor, position_ids: Optional[tuple[torch.LongTensor, torch.LongTensor]] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        feats_height, feats_width = x.shape[-2:]
        embed_height = (feats_height - self.config.q_aggregation_kernel_size) // self.config.q_aggregation_stride + 1
        embed_width = (feats_width - self.config.q_aggregation_kernel_size) // self.config.q_aggregation_stride + 1
        device_type = x.device.type if isinstance(x.device.type, str) and x.device.type != "mps" else "cpu"
        with torch.autocast(device_type=device_type, enabled=False):
            emb = compute_embeddings(self.inv_freq, embed_height, embed_width, self.config.hidden_size)
            sin = emb.sin()
            cos = emb.cos()
        sin = sin.repeat_interleave(2, dim=-1)
        cos = cos.repeat_interleave(2, dim=-1)
        sin = sin.to(device=x.device, dtype=x.dtype)
        cos = cos.to(device=x.device, dtype=x.dtype)
        return cos, sin
class EfficientLoFTRConvNormLayer(nn.Module):
    def __init__(self, config, in_channels, out_channels, kernel_size, stride, padding=None, activation=None):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding=(kernel_size - 1) // 2 if padding is None else padding,
            bias=False,
        )
        self.norm = nn.BatchNorm2d(out_channels, config.batch_norm_eps)
        self.activation = nn.Identity() if activation is None else ACT2CLS[activation]()
    def forward(self, hidden_state):
        hidden_state = self.conv(hidden_state)
        hidden_state = self.norm(hidden_state)
        hidden_state = self.activation(hidden_state)
        return hidden_state
class EfficientLoFTRRepVGGBlock(GradientCheckpointingLayer):
    def __init__(self, config: EfficientLoFTRConfig, stage_idx: int, block_idx: int):
        super().__init__()
        in_channels = config.stage_block_in_channels[stage_idx][block_idx]
        out_channels = config.stage_block_out_channels[stage_idx][block_idx]
        stride = config.stage_block_stride[stage_idx][block_idx]
        activation = config.activation_function
        self.conv1 = EfficientLoFTRConvNormLayer(
            config, in_channels, out_channels, kernel_size=3, stride=stride, padding=1
        )
        self.conv2 = EfficientLoFTRConvNormLayer(
            config, in_channels, out_channels, kernel_size=1, stride=stride, padding=0
        )
        self.identity = nn.BatchNorm2d(in_channels) if in_channels == out_channels and stride == 1 else None
        self.activation = nn.Identity() if activation is None else ACT2FN[activation]
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        if self.identity is not None:
            identity_out = self.identity(hidden_states)
        else:
            identity_out = 0
        hidden_states = self.conv1(hidden_states) + self.conv2(hidden_states) + identity_out
        hidden_states = self.activation(hidden_states)
        return hidden_states
class EfficientLoFTRRepVGGStage(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig, stage_idx: int):
        super().__init__()
        self.blocks = nn.ModuleList([])
        for block_idx in range(config.stage_num_blocks[stage_idx]):
            self.blocks.append(
                EfficientLoFTRRepVGGBlock(
                    config,
                    stage_idx,
                    block_idx,
                )
            )
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        for block in self.blocks:
            hidden_states = block(hidden_states)
        return hidden_states
class EfficientLoFTRepVGG(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__()
        self.stages = nn.ModuleList([])
        for stage_idx in range(len(config.stage_stride)):
            stage = EfficientLoFTRRepVGGStage(config, stage_idx)
            self.stages.append(stage)
    def forward(self, hidden_states: torch.Tensor) -> list[torch.Tensor]:
        outputs = []
        for stage in self.stages:
            hidden_states = stage(hidden_states)
            outputs.append(hidden_states)
        outputs = outputs[1:]
        return outputs
class EfficientLoFTRAggregationLayer(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__()
        hidden_size = config.hidden_size
        self.q_aggregation = nn.Conv2d(
            hidden_size,
            hidden_size,
            kernel_size=config.q_aggregation_kernel_size,
            padding=0,
            stride=config.q_aggregation_stride,
            bias=False,
            groups=hidden_size,
        )
        self.kv_aggregation = torch.nn.MaxPool2d(
            kernel_size=config.kv_aggregation_kernel_size, stride=config.kv_aggregation_stride
        )
        self.norm = nn.LayerNorm(hidden_size)
    def forward(
        self,
        hidden_states: torch.Tensor,
        encoder_hidden_states: Optional[torch.Tensor] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        query_states = hidden_states
        is_cross_attention = encoder_hidden_states is not None
        kv_states = encoder_hidden_states if is_cross_attention else hidden_states
        query_states = self.q_aggregation(query_states)
        kv_states = self.kv_aggregation(kv_states)
        query_states = query_states.permute(0, 2, 3, 1)
        kv_states = kv_states.permute(0, 2, 3, 1)
        hidden_states = self.norm(query_states)
        encoder_hidden_states = self.norm(kv_states)
        return hidden_states, encoder_hidden_states
def rotate_half(x):
    x1 = x[..., ::2]
    x2 = x[..., 1::2]
    rot_x = torch.stack([-x2, x1], dim=-1).flatten(-2)
    return rot_x
def apply_rotary_pos_emb(q, k, cos, sin, position_ids=None, unsqueeze_dim=1):
    dtype = q.dtype
    q = q.float()
    k = k.float()
    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed.to(dtype=dtype), k_embed.to(dtype=dtype)
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
def eager_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Optional[torch.Tensor],
    scaling: float,
    dropout: float = 0.0,
    **kwargs: Unpack[MEROAIKwargs],
):
    key_states = repeat_kv(key, module.num_key_value_groups)
    value_states = repeat_kv(value, module.num_key_value_groups)
    attn_weights = torch.matmul(query, key_states.transpose(2, 3)) * scaling
    if attention_mask is not None:
        causal_mask = attention_mask[:, :, :, : key_states.shape[-2]]
        attn_weights = attn_weights + causal_mask
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
    attn_weights = nn.functional.dropout(attn_weights, p=dropout, training=module.training)
    attn_output = torch.matmul(attn_weights, value_states)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attn_weights
class EfficientLoFTRAttention(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig, layer_idx: int):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        self.num_key_value_groups = config.num_attention_heads // config.num_key_value_heads
        self.scaling = self.head_dim**-0.5
        self.attention_dropout = config.attention_dropout
        self.is_causal = False
        self.q_proj = nn.Linear(
            config.hidden_size, config.num_attention_heads * self.head_dim, bias=config.attention_bias
        )
        self.k_proj = nn.Linear(
            config.hidden_size, config.num_key_value_heads * self.head_dim, bias=config.attention_bias
        )
        self.v_proj = nn.Linear(
            config.hidden_size, config.num_key_value_heads * self.head_dim, bias=config.attention_bias
        )
        self.o_proj = nn.Linear(
            config.num_attention_heads * self.head_dim, config.hidden_size, bias=config.attention_bias
        )
    def forward(
        self,
        hidden_states: torch.Tensor,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        position_embeddings: Optional[tuple[torch.Tensor, torch.Tensor]] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
        batch_size, seq_len, dim = hidden_states.shape
        input_shape = hidden_states.shape[:-1]
        query_states = self.q_proj(hidden_states).view(batch_size, seq_len, -1, dim)
        is_cross_attention = encoder_hidden_states is not None
        current_states = encoder_hidden_states if is_cross_attention else hidden_states
        key_states = self.k_proj(current_states).view(batch_size, seq_len, -1, dim)
        value_states = self.v_proj(current_states).view(batch_size, seq_len, -1, self.head_dim).transpose(1, 2)
        if position_embeddings is not None:
            cos, sin = position_embeddings
            query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin, unsqueeze_dim=2)
        query_states = query_states.view(batch_size, seq_len, -1, self.head_dim).transpose(1, 2)
        key_states = key_states.view(batch_size, seq_len, -1, self.head_dim).transpose(1, 2)
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, attn_weights = attention_interface(
            self,
            query_states,
            key_states,
            value_states,
            attention_mask=None,
            dropout=0.0 if not self.training else self.attention_dropout,
            scaling=self.scaling,
            **kwargs,
        )
        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights
class EfficientLoFTRMLP(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__()
        hidden_size = config.hidden_size
        intermediate_size = config.intermediate_size
        self.fc1 = nn.Linear(hidden_size * 2, intermediate_size, bias=False)
        self.activation = ACT2FN[config.mlp_activation_function]
        self.fc2 = nn.Linear(intermediate_size, hidden_size, bias=False)
        self.layer_norm = nn.LayerNorm(hidden_size)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.fc2(hidden_states)
        hidden_states = self.layer_norm(hidden_states)
        return hidden_states
class EfficientLoFTRAggregatedAttention(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig, layer_idx: int):
        super().__init__()
        self.q_aggregation_kernel_size = config.q_aggregation_kernel_size
        self.aggregation = EfficientLoFTRAggregationLayer(config)
        self.attention = EfficientLoFTRAttention(config, layer_idx)
        self.mlp = EfficientLoFTRMLP(config)
    def forward(
        self,
        hidden_states: torch.Tensor,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        position_embeddings: Optional[tuple[torch.Tensor, torch.Tensor]] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> torch.Tensor:
        batch_size, embed_dim, _, _ = hidden_states.shape
        aggregated_hidden_states, aggregated_encoder_hidden_states = self.aggregation(
            hidden_states, encoder_hidden_states
        )
        _, aggregated_h, aggregated_w, _ = aggregated_hidden_states.shape
        aggregated_hidden_states = aggregated_hidden_states.reshape(batch_size, -1, embed_dim)
        aggregated_encoder_hidden_states = aggregated_encoder_hidden_states.reshape(batch_size, -1, embed_dim)
        attn_output, _ = self.attention(
            aggregated_hidden_states,
            aggregated_encoder_hidden_states,
            position_embeddings=position_embeddings,
            **kwargs,
        )
        attn_output = attn_output.permute(0, 2, 1)
        attn_output = attn_output.reshape(batch_size, embed_dim, aggregated_h, aggregated_w)
        attn_output = torch.nn.functional.interpolate(
            attn_output, scale_factor=self.q_aggregation_kernel_size, mode="bilinear", align_corners=False
        )
        intermediate_states = torch.cat([hidden_states, attn_output], dim=1)
        intermediate_states = intermediate_states.permute(0, 2, 3, 1)
        output_states = self.mlp(intermediate_states)
        output_states = output_states.permute(0, 3, 1, 2)
        hidden_states = hidden_states + output_states
        return hidden_states
class EfficientLoFTRLocalFeatureTransformerLayer(GradientCheckpointingLayer):
    def __init__(self, config: EfficientLoFTRConfig, layer_idx: int):
        super().__init__()
        self.self_attention = EfficientLoFTRAggregatedAttention(config, layer_idx)
        self.cross_attention = EfficientLoFTRAggregatedAttention(config, layer_idx)
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        **kwargs: Unpack[MEROAIKwargs],
    ) -> torch.Tensor:
        batch_size, _, embed_dim, height, width = hidden_states.shape
        hidden_states = hidden_states.reshape(-1, embed_dim, height, width)
        hidden_states = self.self_attention(hidden_states, position_embeddings=position_embeddings, **kwargs)
        hidden_states = hidden_states.reshape(-1, 2, embed_dim, height, width)
        features_0 = hidden_states[:, 0]
        features_1 = hidden_states[:, 1]
        features_0 = self.cross_attention(features_0, features_1, **kwargs)
        features_1 = self.cross_attention(features_1, features_0, **kwargs)
        hidden_states = torch.stack((features_0, features_1), dim=1)
        return hidden_states
class EfficientLoFTRLocalFeatureTransformer(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__()
        self.layers = nn.ModuleList(
            [
                EfficientLoFTRLocalFeatureTransformerLayer(config, layer_idx=i)
                for i in range(config.num_attention_layers)
            ]
        )
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        **kwargs: Unpack[MEROAIKwargs],
    ) -> torch.Tensor:
        for layer in self.layers:
            hidden_states = layer(hidden_states, position_embeddings=position_embeddings, **kwargs)
        return hidden_states
class EfficientLoFTROutConvBlock(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig, hidden_size: int, intermediate_size: int):
        super().__init__()
        self.out_conv1 = nn.Conv2d(hidden_size, intermediate_size, kernel_size=1, stride=1, padding=0, bias=False)
        self.out_conv2 = nn.Conv2d(
            intermediate_size, intermediate_size, kernel_size=3, stride=1, padding=1, bias=False
        )
        self.batch_norm = nn.BatchNorm2d(intermediate_size)
        self.activation = ACT2CLS[config.mlp_activation_function]()
        self.out_conv3 = nn.Conv2d(intermediate_size, hidden_size, kernel_size=3, stride=1, padding=1, bias=False)
    def forward(self, hidden_states: torch.Tensor, residual_states: torch.Tensor) -> torch.Tensor:
        residual_states = self.out_conv1(residual_states)
        residual_states = residual_states + hidden_states
        residual_states = self.out_conv2(residual_states)
        residual_states = self.batch_norm(residual_states)
        residual_states = self.activation(residual_states)
        residual_states = self.out_conv3(residual_states)
        residual_states = nn.functional.interpolate(
            residual_states, scale_factor=2.0, mode="bilinear", align_corners=False
        )
        return residual_states
class EfficientLoFTRFineFusionLayer(nn.Module):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__()
        self.fine_kernel_size = config.fine_kernel_size
        fine_fusion_dims = config.fine_fusion_dims
        self.out_conv = nn.Conv2d(
            fine_fusion_dims[0], fine_fusion_dims[0], kernel_size=1, stride=1, padding=0, bias=False
        )
        self.out_conv_layers = nn.ModuleList()
        for i in range(1, len(fine_fusion_dims)):
            out_conv = EfficientLoFTROutConvBlock(config, fine_fusion_dims[i], fine_fusion_dims[i - 1])
            self.out_conv_layers.append(out_conv)
    def forward_pyramid(
        self,
        hidden_states: torch.Tensor,
        residual_states: list[torch.Tensor],
    ) -> torch.Tensor:
        hidden_states = self.out_conv(hidden_states)
        hidden_states = nn.functional.interpolate(
            hidden_states, scale_factor=2.0, mode="bilinear", align_corners=False
        )
        for i, layer in enumerate(self.out_conv_layers):
            hidden_states = layer(hidden_states, residual_states[i])
        return hidden_states
    def forward(
        self,
        coarse_features: torch.Tensor,
        residual_features: list[torch.Tensor],
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, _, embed_dim, coarse_height, coarse_width = coarse_features.shape
        coarse_features = coarse_features.reshape(-1, embed_dim, coarse_height, coarse_width)
        residual_features = list(reversed(residual_features))
        fine_features = self.forward_pyramid(coarse_features, residual_features)
        _, fine_embed_dim, fine_height, fine_width = fine_features.shape
        fine_features = fine_features.reshape(batch_size, 2, fine_embed_dim, fine_height, fine_width)
        fine_features_0 = fine_features[:, 0]
        fine_features_1 = fine_features[:, 1]
        stride = int(fine_height // coarse_height)
        fine_features_0 = nn.functional.unfold(
            fine_features_0, kernel_size=self.fine_kernel_size, stride=stride, padding=0
        )
        _, _, seq_len = fine_features_0.shape
        fine_features_0 = fine_features_0.reshape(batch_size, -1, self.fine_kernel_size**2, seq_len)
        fine_features_0 = fine_features_0.permute(0, 3, 2, 1)
        fine_features_1 = nn.functional.unfold(
            fine_features_1, kernel_size=self.fine_kernel_size + 2, stride=stride, padding=1
        )
        fine_features_1 = fine_features_1.reshape(batch_size, -1, (self.fine_kernel_size + 2) ** 2, seq_len)
        fine_features_1 = fine_features_1.permute(0, 3, 2, 1)
        return fine_features_0, fine_features_1
@auto_docstring
class EfficientLoFTRPreTrainedModel(PreTrainedModel):
    config_class = EfficientLoFTRConfig
    base_model_prefix = "efficientloftr"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _supports_flash_attn = True
    _supports_sdpa = True
    _can_record_outputs = {
        "hidden_states": EfficientLoFTRRepVGGBlock,
        "attentions": EfficientLoFTRAttention,
    }
    def _init_weights(self, module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.Conv1d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    def extract_one_channel_pixel_values(self, pixel_values: torch.FloatTensor) -> torch.FloatTensor:
        return pixel_values[:, 0, :, :][:, None, :, :]
@auto_docstring(
)
class EfficientLoFTRModel(EfficientLoFTRPreTrainedModel):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__(config)
        self.config = config
        self.backbone = EfficientLoFTRepVGG(config)
        self.local_feature_transformer = EfficientLoFTRLocalFeatureTransformer(config)
        self.rotary_emb = EfficientLoFTRRotaryEmbedding(config=config)
        self.post_init()
    @check_model_inputs()
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        labels: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> BackboneOutput:
        if labels is not None:
            raise ValueError("EfficientLoFTR is not trainable, no labels should be provided.")
        if pixel_values.ndim != 5 or pixel_values.size(1) != 2:
            raise ValueError("Input must be a 5D tensor of shape (batch_size, 2, num_channels, height, width)")
        batch_size, _, channels, height, width = pixel_values.shape
        pixel_values = pixel_values.reshape(batch_size * 2, channels, height, width)
        pixel_values = self.extract_one_channel_pixel_values(pixel_values)
        features = self.backbone(pixel_values)
        coarse_features = features[-1]
        residual_features = features[:-1]
        coarse_embed_dim, coarse_height, coarse_width = coarse_features.shape[-3:]
        cos, sin = self.rotary_emb(coarse_features)
        cos = cos.expand(batch_size * 2, -1, -1, -1).reshape(batch_size * 2, -1, coarse_embed_dim)
        sin = sin.expand(batch_size * 2, -1, -1, -1).reshape(batch_size * 2, -1, coarse_embed_dim)
        position_embeddings = (cos, sin)
        coarse_features = coarse_features.reshape(batch_size, 2, coarse_embed_dim, coarse_height, coarse_width)
        coarse_features = self.local_feature_transformer(
            coarse_features, position_embeddings=position_embeddings, **kwargs
        )
        features = (coarse_features,) + tuple(residual_features)
        return BackboneOutput(feature_maps=features)
def mask_border(tensor: torch.Tensor, border_margin: int, value: Union[bool, float, int]) -> torch.Tensor:
    if border_margin <= 0:
        return tensor
    tensor[:, :border_margin] = value
    tensor[:, :, :border_margin] = value
    tensor[:, :, :, :border_margin] = value
    tensor[:, :, :, :, :border_margin] = value
    tensor[:, -border_margin:] = value
    tensor[:, :, -border_margin:] = value
    tensor[:, :, :, -border_margin:] = value
    tensor[:, :, :, :, -border_margin:] = value
    return tensor
def create_meshgrid(
    height: Union[int, torch.Tensor],
    width: Union[int, torch.Tensor],
    normalized_coordinates: bool = False,
    device: Optional[torch.device] = None,
    dtype: Optional[torch.dtype] = None,
) -> torch.Tensor:
    xs = torch.linspace(0, width - 1, width, device=device, dtype=dtype)
    ys = torch.linspace(0, height - 1, height, device=device, dtype=dtype)
    if normalized_coordinates:
        xs = (xs / (width - 1) - 0.5) * 2
        ys = (ys / (height - 1) - 0.5) * 2
    grid = torch.stack(torch.meshgrid(ys, xs, indexing="ij"), dim=-1)
    grid = grid.permute(1, 0, 2).unsqueeze(0)
    return grid
def spatial_expectation2d(input: torch.Tensor, normalized_coordinates: bool = True) -> torch.Tensor:
    batch_size, embed_dim, height, width = input.shape
    grid = create_meshgrid(height, width, normalized_coordinates, input.device)
    grid = grid.to(input.dtype)
    pos_x = grid[..., 0].reshape(-1)
    pos_y = grid[..., 1].reshape(-1)
    input_flat = input.view(batch_size, embed_dim, -1)
    expected_y = torch.sum(pos_y * input_flat, -1, keepdim=True)
    expected_x = torch.sum(pos_x * input_flat, -1, keepdim=True)
    output = torch.cat([expected_x, expected_y], -1)
    return output.view(batch_size, embed_dim, 2)
@auto_docstring(
)
class EfficientLoFTRForKeypointMatching(EfficientLoFTRPreTrainedModel):
    def __init__(self, config: EfficientLoFTRConfig):
        super().__init__(config)
        self.config = config
        self.efficientloftr = EfficientLoFTRModel(config)
        self.refinement_layer = EfficientLoFTRFineFusionLayer(config)
        self.post_init()
    def _get_matches_from_scores(self, scores: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, height0, width0, height1, width1 = scores.shape
        scores = scores.view(batch_size, height0 * width0, height1 * width1)
        max_0 = scores.max(2, keepdim=True).values
        max_1 = scores.max(1, keepdim=True).values
        mask = scores > self.config.coarse_matching_threshold
        mask = mask.reshape(batch_size, height0, width0, height1, width1)
        mask = mask_border(mask, self.config.coarse_matching_border_removal, False)
        mask = mask.reshape(batch_size, height0 * width0, height1 * width1)
        mask = mask * (scores == max_0) * (scores == max_1)
        masked_scores = scores * mask
        matching_scores_0, max_indices_0 = masked_scores.max(1)
        matching_scores_1, max_indices_1 = masked_scores.max(2)
        matching_indices = torch.cat([max_indices_0, max_indices_1]).reshape(batch_size, 2, -1)
        matching_scores = torch.stack([matching_scores_0, matching_scores_1], dim=1)
        matching_indices = torch.where(matching_scores > 0, matching_indices, -1)
        return matching_indices, matching_scores
    def _coarse_matching(
        self, coarse_features: torch.Tensor, coarse_scale: float
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        batch_size, _, embed_dim, height, width = coarse_features.shape
        coarse_features = coarse_features.permute(0, 1, 3, 4, 2)
        coarse_features = coarse_features.reshape(batch_size, 2, -1, embed_dim)
        coarse_features = coarse_features / coarse_features.shape[-1] ** 0.5
        coarse_features_0 = coarse_features[:, 0]
        coarse_features_1 = coarse_features[:, 1]
        similarity = coarse_features_0 @ coarse_features_1.transpose(-1, -2)
        similarity = similarity / self.config.coarse_matching_temperature
        if self.config.coarse_matching_skip_softmax:
            confidence = similarity
        else:
            confidence = nn.functional.softmax(similarity, 1) * nn.functional.softmax(similarity, 2)
        confidence = confidence.view(batch_size, height, width, height, width)
        matched_indices, matching_scores = self._get_matches_from_scores(confidence)
        keypoints = torch.stack([matched_indices % width, matched_indices // width], dim=-1) * coarse_scale
        return keypoints, matching_scores, matched_indices
    def _get_first_stage_fine_matching(
        self,
        fine_confidence: torch.Tensor,
        coarse_matched_keypoints: torch.Tensor,
        fine_window_size: int,
        fine_scale: float,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, num_keypoints, _, _ = fine_confidence.shape
        fine_kernel_size = torch_int(fine_window_size**0.5)
        fine_confidence = fine_confidence.reshape(batch_size, num_keypoints, -1)
        values, indices = torch.max(fine_confidence, dim=-1)
        indices = indices[..., None]
        indices_0 = indices // fine_window_size
        indices_1 = indices % fine_window_size
        grid = create_meshgrid(
            fine_kernel_size,
            fine_kernel_size,
            normalized_coordinates=False,
            device=fine_confidence.device,
            dtype=fine_confidence.dtype,
        )
        grid = grid - (fine_kernel_size // 2) + 0.5
        grid = grid.reshape(1, 1, -1, 2).expand(batch_size, num_keypoints, -1, -1)
        delta_0 = torch.gather(grid, 1, indices_0.unsqueeze(-1).expand(-1, -1, -1, 2)).squeeze(2)
        delta_1 = torch.gather(grid, 1, indices_1.unsqueeze(-1).expand(-1, -1, -1, 2)).squeeze(2)
        fine_matches_0 = coarse_matched_keypoints[:, 0] + delta_0 * fine_scale
        fine_matches_1 = coarse_matched_keypoints[:, 1] + delta_1 * fine_scale
        indices = torch.stack([indices_0, indices_1], dim=1)
        fine_matches = torch.stack([fine_matches_0, fine_matches_1], dim=1)
        return indices, fine_matches
    def _get_second_stage_fine_matching(
        self,
        indices: torch.Tensor,
        fine_matches: torch.Tensor,
        fine_confidence: torch.Tensor,
        fine_window_size: int,
        fine_scale: float,
    ) -> torch.Tensor:
        batch_size, num_keypoints, _, _ = fine_confidence.shape
        fine_kernel_size = torch_int(fine_window_size**0.5)
        indices_0 = indices[:, 0]
        indices_1 = indices[:, 1]
        indices_1_i = indices_1 // fine_kernel_size
        indices_1_j = indices_1 % fine_kernel_size
        batch_indices = torch.arange(batch_size, device=indices_0.device).reshape(batch_size, 1, 1, 1)
        matches_indices = torch.arange(num_keypoints, device=indices_0.device).reshape(1, num_keypoints, 1, 1)
        indices_0 = indices_0[..., None]
        indices_1_i = indices_1_i[..., None]
        indices_1_j = indices_1_j[..., None]
        delta = create_meshgrid(3, 3, normalized_coordinates=True, device=indices_0.device).to(torch.long)
        delta = delta[None, ...]
        indices_1_i = indices_1_i + delta[..., 1]
        indices_1_j = indices_1_j + delta[..., 0]
        fine_confidence = fine_confidence.reshape(
            batch_size, num_keypoints, fine_window_size, fine_kernel_size + 2, fine_kernel_size + 2
        )
        fine_confidence = fine_confidence[batch_indices, matches_indices, indices_0, indices_1_i, indices_1_j]
        fine_confidence = fine_confidence.reshape(batch_size, num_keypoints, 9)
        fine_confidence = nn.functional.softmax(
            fine_confidence / self.config.fine_matching_regress_temperature, dim=-1
        )
        heatmap = fine_confidence.reshape(batch_size, num_keypoints, 3, 3)
        fine_coordinates_normalized = spatial_expectation2d(heatmap, True)[0]
        fine_matches_0 = fine_matches[:, 0]
        fine_matches_1 = fine_matches[:, 1] + (fine_coordinates_normalized * (3 // 2) * fine_scale)
        fine_matches = torch.stack([fine_matches_0, fine_matches_1], dim=1)
        return fine_matches
    def _fine_matching(
        self,
        fine_features_0: torch.Tensor,
        fine_features_1: torch.Tensor,
        coarse_matched_keypoints: torch.Tensor,
        fine_scale: float,
    ) -> torch.Tensor:
        batch_size, num_keypoints, fine_window_size, fine_embed_dim = fine_features_0.shape
        fine_matching_slice_dim = self.config.fine_matching_slice_dim
        fine_kernel_size = torch_int(fine_window_size**0.5)
        split_fine_features_0 = torch.split(fine_features_0, fine_embed_dim - fine_matching_slice_dim, -1)
        split_fine_features_1 = torch.split(fine_features_1, fine_embed_dim - fine_matching_slice_dim, -1)
        fine_features_0 = split_fine_features_0[0]
        fine_features_1 = split_fine_features_1[0]
        fine_features_0 = fine_features_0 / fine_features_0.shape[-1] ** 0.5
        fine_features_1 = fine_features_1 / fine_features_1.shape[-1] ** 0.5
        fine_confidence = fine_features_0 @ fine_features_1.transpose(-1, -2)
        fine_confidence = nn.functional.softmax(fine_confidence, 1) * nn.functional.softmax(fine_confidence, 2)
        fine_confidence = fine_confidence.reshape(
            batch_size, num_keypoints, fine_window_size, fine_kernel_size + 2, fine_kernel_size + 2
        )
        fine_confidence = fine_confidence[..., 1:-1, 1:-1]
        first_stage_fine_confidence = fine_confidence.reshape(
            batch_size, num_keypoints, fine_window_size, fine_window_size
        )
        fine_indices, fine_matches = self._get_first_stage_fine_matching(
            first_stage_fine_confidence,
            coarse_matched_keypoints,
            fine_window_size,
            fine_scale,
        )
        fine_features_0 = split_fine_features_0[1]
        fine_features_1 = split_fine_features_1[1]
        fine_features_1 = fine_features_1 / fine_matching_slice_dim**0.5
        second_stage_fine_confidence = fine_features_0 @ fine_features_1.transpose(-1, -2)
        fine_coordinates = self._get_second_stage_fine_matching(
            fine_indices,
            fine_matches,
            second_stage_fine_confidence,
            fine_window_size,
            fine_scale,
        )
        return fine_coordinates
    @auto_docstring
    @can_return_tuple
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        labels: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> KeypointMatchingOutput:
        if labels is not None:
            raise ValueError("SuperGlue is not trainable, no labels should be provided.")
        model_outputs: BackboneOutput = self.efficientloftr(pixel_values, **kwargs)
        features = model_outputs.feature_maps
        coarse_features = features[0]
        coarse_embed_dim, coarse_height, coarse_width = coarse_features.shape[-3:]
        batch_size, _, channels, height, width = pixel_values.shape
        coarse_scale = height / coarse_height
        coarse_keypoints, coarse_matching_scores, coarse_matched_indices = self._coarse_matching(
            coarse_features, coarse_scale
        )
        residual_features = features[1:]
        coarse_features = coarse_features / self.config.hidden_size**0.5
        fine_features_0, fine_features_1 = self.refinement_layer(coarse_features, residual_features)
        _, _, num_keypoints = coarse_matching_scores.shape
        batch_indices = torch.arange(batch_size)[..., None]
        fine_features_0 = fine_features_0[batch_indices, coarse_matched_indices[:, 0]]
        fine_features_1 = fine_features_1[batch_indices, coarse_matched_indices[:, 1]]
        fine_height = torch_int(coarse_height * coarse_scale)
        fine_scale = height / fine_height
        matching_keypoints = self._fine_matching(fine_features_0, fine_features_1, coarse_keypoints, fine_scale)
        matching_keypoints[:, :, :, 0] = matching_keypoints[:, :, :, 0] / width
        matching_keypoints[:, :, :, 1] = matching_keypoints[:, :, :, 1] / height
        return KeypointMatchingOutput(
            matches=coarse_matched_indices,
            matching_scores=coarse_matching_scores,
            keypoints=matching_keypoints,
            hidden_states=model_outputs.hidden_states,
            attentions=model_outputs.attentions,
        )
__all__ = ["EfficientLoFTRPreTrainedModel", "EfficientLoFTRModel", "EfficientLoFTRForKeypointMatching"]