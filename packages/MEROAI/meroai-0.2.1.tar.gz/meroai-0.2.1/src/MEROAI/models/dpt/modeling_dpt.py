import collections.abc
from dataclasses import dataclass
from typing import Callable, Optional
import torch
from torch import nn
from torch.nn import CrossEntropyLoss
from ...activations import ACT2FN
from ...modeling_layers import GradientCheckpointingLayer
from ...modeling_outputs import BaseModelOutput, DepthEstimatorOutput, SemanticSegmenterOutput
from ...modeling_utils import ALL_ATTENTION_FUNCTIONS, PreTrainedModel
from ...pytorch_utils import find_pruneable_heads_and_indices, prune_linear_layer
from ...utils import ModelOutput, auto_docstring, logging, torch_int
from ...utils.backbone_utils import load_backbone
from ...utils.generic import can_return_tuple, check_model_inputs
from .configuration_dpt import DPTConfig
logger = logging.get_logger(__name__)
@dataclass
@auto_docstring(
)
class BaseModelOutputWithIntermediateActivations(ModelOutput):
    last_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_activations: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
@auto_docstring(
)
class BaseModelOutputWithPoolingAndIntermediateActivations(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    intermediate_activations: Optional[tuple[torch.FloatTensor, ...]] = None
class DPTViTHybridEmbeddings(nn.Module):
    def __init__(self, config: DPTConfig, feature_size: Optional[tuple[int, int]] = None):
        super().__init__()
        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.backbone = load_backbone(config)
        feature_dim = self.backbone.channels[-1]
        if len(self.backbone.channels) != 3:
            raise ValueError(f"Expected backbone to have 3 output features, got {len(self.backbone.channels)}")
        self.residual_feature_map_index = [0, 1]
        if feature_size is None:
            feat_map_shape = config.backbone_featmap_shape
            feature_size = feat_map_shape[-2:]
            feature_dim = feat_map_shape[1]
        else:
            feature_size = (
                feature_size if isinstance(feature_size, collections.abc.Iterable) else (feature_size, feature_size)
            )
            feature_dim = self.backbone.channels[-1]
        self.image_size = image_size
        self.patch_size = patch_size[0]
        self.num_channels = num_channels
        self.projection = nn.Conv2d(feature_dim, hidden_size, kernel_size=1)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.position_embeddings = nn.Parameter(torch.zeros(1, num_patches + 1, config.hidden_size))
    def _resize_pos_embed(self, posemb, grid_size_height, grid_size_width, start_index=1):
        posemb_tok = posemb[:, :start_index]
        posemb_grid = posemb[0, start_index:]
        old_grid_size = torch_int(len(posemb_grid) ** 0.5)
        posemb_grid = posemb_grid.reshape(1, old_grid_size, old_grid_size, -1).permute(0, 3, 1, 2)
        posemb_grid = nn.functional.interpolate(posemb_grid, size=(grid_size_height, grid_size_width), mode="bilinear")
        posemb_grid = posemb_grid.permute(0, 2, 3, 1).reshape(1, grid_size_height * grid_size_width, -1)
        posemb = torch.cat([posemb_tok, posemb_grid], dim=1)
        return posemb
    def forward(
        self, pixel_values: torch.Tensor, interpolate_pos_encoding: bool = False
    ) -> BaseModelOutputWithIntermediateActivations:
        batch_size, num_channels, height, width = pixel_values.shape
        if num_channels != self.num_channels:
            raise ValueError(
                "Make sure that the channel dimension of the pixel values match with the one set in the configuration."
            )
        if not interpolate_pos_encoding:
            if height != self.image_size[0] or width != self.image_size[1]:
                raise ValueError(
                    f"Input image size ({height}*{width}) doesn't match model"
                    f" ({self.image_size[0]}*{self.image_size[1]})."
                )
        position_embeddings = self._resize_pos_embed(
            self.position_embeddings, height // self.patch_size, width // self.patch_size
        )
        backbone_output = self.backbone(pixel_values)
        features = backbone_output.feature_maps[-1]
        output_hidden_states = [backbone_output.feature_maps[index] for index in self.residual_feature_map_index]
        embeddings = self.projection(features).flatten(2).transpose(1, 2)
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        embeddings = torch.cat((cls_tokens, embeddings), dim=1)
        embeddings = embeddings + position_embeddings
        return BaseModelOutputWithIntermediateActivations(
            last_hidden_states=embeddings,
            intermediate_activations=output_hidden_states,
        )
class DPTViTEmbeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.hidden_size))
        self.patch_embeddings = DPTViTPatchEmbeddings(config)
        num_patches = self.patch_embeddings.num_patches
        self.position_embeddings = nn.Parameter(torch.zeros(1, num_patches + 1, config.hidden_size))
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.config = config
    def _resize_pos_embed(self, posemb, grid_size_height, grid_size_width, start_index=1):
        posemb_tok = posemb[:, :start_index]
        posemb_grid = posemb[0, start_index:]
        old_grid_size = torch_int(posemb_grid.size(0) ** 0.5)
        posemb_grid = posemb_grid.reshape(1, old_grid_size, old_grid_size, -1).permute(0, 3, 1, 2)
        posemb_grid = nn.functional.interpolate(posemb_grid, size=(grid_size_height, grid_size_width), mode="bilinear")
        posemb_grid = posemb_grid.permute(0, 2, 3, 1).reshape(1, grid_size_height * grid_size_width, -1)
        posemb = torch.cat([posemb_tok, posemb_grid], dim=1)
        return posemb
    def forward(self, pixel_values: torch.Tensor) -> BaseModelOutputWithIntermediateActivations:
        batch_size, num_channels, height, width = pixel_values.shape
        patch_size = self.config.patch_size
        position_embeddings = self._resize_pos_embed(
            self.position_embeddings, height // patch_size, width // patch_size
        )
        embeddings = self.patch_embeddings(pixel_values)
        batch_size, seq_len, _ = embeddings.size()
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        embeddings = torch.cat((cls_tokens, embeddings), dim=1)
        embeddings = embeddings + position_embeddings
        embeddings = self.dropout(embeddings)
        return BaseModelOutputWithIntermediateActivations(last_hidden_states=embeddings)
class DPTViTPatchEmbeddings(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        image_size, patch_size = config.image_size, config.patch_size
        num_channels, hidden_size = config.num_channels, config.hidden_size
        image_size = image_size if isinstance(image_size, collections.abc.Iterable) else (image_size, image_size)
        patch_size = patch_size if isinstance(patch_size, collections.abc.Iterable) else (patch_size, patch_size)
        num_patches = (image_size[1] // patch_size[1]) * (image_size[0] // patch_size[0])
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.num_patches = num_patches
        self.projection = nn.Conv2d(num_channels, hidden_size, kernel_size=patch_size, stride=patch_size)
    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        batch_size, num_channels, height, width = pixel_values.shape
        if num_channels != self.num_channels:
            raise ValueError(
                "Make sure that the channel dimension of the pixel values match with the one set in the configuration."
            )
        embeddings = self.projection(pixel_values).flatten(2).transpose(1, 2)
        return embeddings
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
    attn_weights = torch.matmul(query, key.transpose(-1, -2)) * scaling
    attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(query.dtype)
    attn_weights = nn.functional.dropout(attn_weights, p=dropout, training=module.training)
    if attention_mask is not None:
        attn_weights = attn_weights * attention_mask
    attn_output = torch.matmul(attn_weights, value)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attn_weights
class DPTSelfAttention(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        if config.hidden_size % config.num_attention_heads != 0 and not hasattr(config, "embedding_size"):
            raise ValueError(
                f"The hidden size {config.hidden_size} is not a multiple of the number of attention "
                f"heads {config.num_attention_heads}."
            )
        self.config = config
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.dropout_prob = config.attention_probs_dropout_prob
        self.scaling = self.attention_head_size**-0.5
        self.is_causal = False
        self.query = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
        self.key = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
        self.value = nn.Linear(config.hidden_size, self.all_head_size, bias=config.qkv_bias)
    def forward(
        self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size = hidden_states.shape[0]
        new_shape = batch_size, -1, self.num_attention_heads, self.attention_head_size
        key_layer = self.key(hidden_states).view(*new_shape).transpose(1, 2)
        value_layer = self.value(hidden_states).view(*new_shape).transpose(1, 2)
        query_layer = self.query(hidden_states).view(*new_shape).transpose(1, 2)
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        context_layer, attention_probs = attention_interface(
            self,
            query_layer,
            key_layer,
            value_layer,
            head_mask,
            is_causal=self.is_causal,
            scaling=self.scaling,
            dropout=0.0 if not self.training else self.dropout_prob,
        )
        new_context_layer_shape = context_layer.size()[:-2] + (self.all_head_size,)
        context_layer = context_layer.reshape(new_context_layer_shape)
        return context_layer, attention_probs
class DPTViTSelfOutput(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        return hidden_states
class DPTViTAttention(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.attention = DPTSelfAttention(config)
        self.output = DPTViTSelfOutput(config)
        self.pruned_heads = set()
    def prune_heads(self, heads: set[int]):
        if len(heads) == 0:
            return
        heads, index = find_pruneable_heads_and_indices(
            heads, self.attention.num_attention_heads, self.attention.attention_head_size, self.pruned_heads
        )
        self.attention.query = prune_linear_layer(self.attention.query, index)
        self.attention.key = prune_linear_layer(self.attention.key, index)
        self.attention.value = prune_linear_layer(self.attention.value, index)
        self.output.dense = prune_linear_layer(self.output.dense, index, dim=1)
        self.attention.num_attention_heads = self.attention.num_attention_heads - len(heads)
        self.attention.all_head_size = self.attention.attention_head_size * self.attention.num_attention_heads
        self.pruned_heads = self.pruned_heads.union(heads)
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        self_attn_output, _ = self.attention(hidden_states, head_mask)
        output = self.output(self_attn_output, hidden_states)
        return output
class DPTViTIntermediate(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.intermediate_size)
        if isinstance(config.hidden_act, str):
            self.intermediate_act_fn = ACT2FN[config.hidden_act]
        else:
            self.intermediate_act_fn = config.hidden_act
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.intermediate_act_fn(hidden_states)
        return hidden_states
class DPTViTOutput(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.dense = nn.Linear(config.intermediate_size, config.hidden_size)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
    def forward(self, hidden_states: torch.Tensor, input_tensor: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.dropout(hidden_states)
        hidden_states = hidden_states + input_tensor
        return hidden_states
class DPTViTLayer(GradientCheckpointingLayer):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.chunk_size_feed_forward = config.chunk_size_feed_forward
        self.seq_len_dim = 1
        self.attention = DPTViTAttention(config)
        self.intermediate = DPTViTIntermediate(config)
        self.output = DPTViTOutput(config)
        self.layernorm_before = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.layernorm_after = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
    def forward(self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        hidden_states_norm = self.layernorm_before(hidden_states)
        attention_output = self.attention(hidden_states_norm, head_mask)
        hidden_states = attention_output + hidden_states
        layer_output = self.layernorm_after(hidden_states)
        layer_output = self.intermediate(layer_output)
        layer_output = self.output(layer_output, hidden_states)
        return layer_output
class DPTViTEncoder(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.config = config
        self.layer = nn.ModuleList([DPTViTLayer(config) for _ in range(config.num_hidden_layers)])
        self.gradient_checkpointing = False
    def forward(
        self, hidden_states: torch.Tensor, head_mask: Optional[torch.Tensor] = None, output_hidden_states: bool = False
    ) -> BaseModelOutput:
        all_hidden_states = [hidden_states] if output_hidden_states else None
        for i, layer_module in enumerate(self.layer):
            layer_head_mask = head_mask[i] if head_mask is not None else None
            hidden_states = layer_module(hidden_states, layer_head_mask)
            if all_hidden_states:
                all_hidden_states.append(hidden_states)
        return BaseModelOutput(
            last_hidden_state=hidden_states,
            hidden_states=tuple(all_hidden_states) if all_hidden_states else None,
        )
class DPTReassembleStage(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList()
        if config.is_hybrid:
            self._init_reassemble_dpt_hybrid(config)
        else:
            self._init_reassemble_dpt(config)
        self.neck_ignore_stages = config.neck_ignore_stages
    def _init_reassemble_dpt_hybrid(self, config):
        for i, factor in zip(range(len(config.neck_hidden_sizes)), config.reassemble_factors):
            if i <= 1:
                self.layers.append(nn.Identity())
            elif i > 1:
                self.layers.append(DPTReassembleLayer(config, channels=config.neck_hidden_sizes[i], factor=factor))
        if config.readout_type != "project":
            raise ValueError(f"Readout type {config.readout_type} is not supported for DPT-Hybrid.")
        self.readout_projects = nn.ModuleList()
        hidden_size = _get_backbone_hidden_size(config)
        for i in range(len(config.neck_hidden_sizes)):
            if i <= 1:
                self.readout_projects.append(nn.Sequential(nn.Identity()))
            elif i > 1:
                self.readout_projects.append(
                    nn.Sequential(nn.Linear(2 * hidden_size, hidden_size), ACT2FN[config.hidden_act])
                )
    def _init_reassemble_dpt(self, config):
        for i, factor in zip(range(len(config.neck_hidden_sizes)), config.reassemble_factors):
            self.layers.append(DPTReassembleLayer(config, channels=config.neck_hidden_sizes[i], factor=factor))
        if config.readout_type == "project":
            self.readout_projects = nn.ModuleList()
            hidden_size = _get_backbone_hidden_size(config)
            for _ in range(len(config.neck_hidden_sizes)):
                self.readout_projects.append(
                    nn.Sequential(nn.Linear(2 * hidden_size, hidden_size), ACT2FN[config.hidden_act])
                )
    def forward(self, hidden_states: list[torch.Tensor], patch_height=None, patch_width=None) -> list[torch.Tensor]:
        out = []
        for i, hidden_state in enumerate(hidden_states):
            if i not in self.neck_ignore_stages:
                cls_token, hidden_state = hidden_state[:, 0], hidden_state[:, 1:]
                batch_size, sequence_length, num_channels = hidden_state.shape
                if patch_height is not None and patch_width is not None:
                    hidden_state = hidden_state.reshape(batch_size, patch_height, patch_width, num_channels)
                else:
                    size = torch_int(sequence_length**0.5)
                    hidden_state = hidden_state.reshape(batch_size, size, size, num_channels)
                hidden_state = hidden_state.permute(0, 3, 1, 2).contiguous()
                feature_shape = hidden_state.shape
                if self.config.readout_type == "project":
                    hidden_state = hidden_state.flatten(2).permute((0, 2, 1))
                    readout = cls_token.unsqueeze(1).expand_as(hidden_state)
                    hidden_state = self.readout_projects[i](torch.cat((hidden_state, readout), -1))
                    hidden_state = hidden_state.permute(0, 2, 1).reshape(feature_shape)
                elif self.config.readout_type == "add":
                    hidden_state = hidden_state.flatten(2) + cls_token.unsqueeze(-1)
                    hidden_state = hidden_state.reshape(feature_shape)
                hidden_state = self.layers[i](hidden_state)
            out.append(hidden_state)
        return out
def _get_backbone_hidden_size(config):
    if config.backbone_config is not None and config.is_hybrid is False:
        return config.backbone_config.hidden_size
    else:
        return config.hidden_size
class DPTReassembleLayer(nn.Module):
    def __init__(self, config: DPTConfig, channels: int, factor: int):
        super().__init__()
        hidden_size = _get_backbone_hidden_size(config)
        self.projection = nn.Conv2d(in_channels=hidden_size, out_channels=channels, kernel_size=1)
        if factor > 1:
            self.resize = nn.ConvTranspose2d(channels, channels, kernel_size=factor, stride=factor, padding=0)
        elif factor == 1:
            self.resize = nn.Identity()
        elif factor < 1:
            self.resize = nn.Conv2d(channels, channels, kernel_size=3, stride=int(1 / factor), padding=1)
    def forward(self, hidden_state):
        hidden_state = self.projection(hidden_state)
        hidden_state = self.resize(hidden_state)
        return hidden_state
class DPTFeatureFusionStage(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.layers = nn.ModuleList()
        for _ in range(len(config.neck_hidden_sizes)):
            self.layers.append(DPTFeatureFusionLayer(config))
    def forward(self, hidden_states):
        hidden_states = hidden_states[::-1]
        fused_hidden_states = []
        fused_hidden_state = None
        for hidden_state, layer in zip(hidden_states, self.layers):
            if fused_hidden_state is None:
                fused_hidden_state = layer(hidden_state)
            else:
                fused_hidden_state = layer(fused_hidden_state, hidden_state)
            fused_hidden_states.append(fused_hidden_state)
        return fused_hidden_states
class DPTPreActResidualLayer(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.use_batch_norm = config.use_batch_norm_in_fusion_residual
        use_bias_in_fusion_residual = (
            config.use_bias_in_fusion_residual
            if config.use_bias_in_fusion_residual is not None
            else not self.use_batch_norm
        )
        self.activation1 = nn.ReLU()
        self.convolution1 = nn.Conv2d(
            config.fusion_hidden_size,
            config.fusion_hidden_size,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=use_bias_in_fusion_residual,
        )
        self.activation2 = nn.ReLU()
        self.convolution2 = nn.Conv2d(
            config.fusion_hidden_size,
            config.fusion_hidden_size,
            kernel_size=3,
            stride=1,
            padding=1,
            bias=use_bias_in_fusion_residual,
        )
        if self.use_batch_norm:
            self.batch_norm1 = nn.BatchNorm2d(config.fusion_hidden_size)
            self.batch_norm2 = nn.BatchNorm2d(config.fusion_hidden_size)
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        residual = hidden_state
        hidden_state = self.activation1(hidden_state)
        hidden_state = self.convolution1(hidden_state)
        if self.use_batch_norm:
            hidden_state = self.batch_norm1(hidden_state)
        hidden_state = self.activation2(hidden_state)
        hidden_state = self.convolution2(hidden_state)
        if self.use_batch_norm:
            hidden_state = self.batch_norm2(hidden_state)
        return hidden_state + residual
class DPTFeatureFusionLayer(nn.Module):
    def __init__(self, config: DPTConfig, align_corners: bool = True):
        super().__init__()
        self.align_corners = align_corners
        self.projection = nn.Conv2d(config.fusion_hidden_size, config.fusion_hidden_size, kernel_size=1, bias=True)
        self.residual_layer1 = DPTPreActResidualLayer(config)
        self.residual_layer2 = DPTPreActResidualLayer(config)
    def forward(self, hidden_state: torch.Tensor, residual: Optional[torch.Tensor] = None) -> torch.Tensor:
        if residual is not None:
            if hidden_state.shape != residual.shape:
                residual = nn.functional.interpolate(
                    residual, size=(hidden_state.shape[2], hidden_state.shape[3]), mode="bilinear", align_corners=False
                )
            hidden_state = hidden_state + self.residual_layer1(residual)
        hidden_state = self.residual_layer2(hidden_state)
        hidden_state = nn.functional.interpolate(
            hidden_state, scale_factor=2, mode="bilinear", align_corners=self.align_corners
        )
        hidden_state = self.projection(hidden_state)
        return hidden_state
@auto_docstring
class DPTPreTrainedModel(PreTrainedModel):
    config: DPTConfig
    base_model_prefix = "dpt"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = True
    _supports_sdpa = True
    _supports_flash_attn = True
    _supports_flex_attn = True
    _supports_attention_backend = True
    _can_record_outputs = {
        "attentions": DPTSelfAttention,
    }
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, (nn.LayerNorm, nn.BatchNorm2d)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        if isinstance(module, (DPTViTEmbeddings, DPTViTHybridEmbeddings)):
            module.cls_token.data.zero_()
            module.position_embeddings.data.zero_()
@auto_docstring
class DPTModel(DPTPreTrainedModel):
    def __init__(self, config: DPTConfig, add_pooling_layer: bool = True):
        super().__init__(config)
        self.config = config
        if config.is_hybrid:
            self.embeddings = DPTViTHybridEmbeddings(config)
        else:
            self.embeddings = DPTViTEmbeddings(config)
        self.encoder = DPTViTEncoder(config)
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.pooler = DPTViTPooler(config) if add_pooling_layer else None
        self.post_init()
    def get_input_embeddings(self):
        if self.config.is_hybrid:
            return self.embeddings
        else:
            return self.embeddings.patch_embeddings
    def _prune_heads(self, heads_to_prune):
        for layer, heads in heads_to_prune.items():
            self.encoder.layer[layer].attention.prune_heads(heads)
    @check_model_inputs(tie_last_hidden_states=False)
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        head_mask: Optional[torch.FloatTensor] = None,
        output_hidden_states: Optional[bool] = None,
        **kwargs,
    ) -> BaseModelOutputWithPoolingAndIntermediateActivations:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        embedding_output: BaseModelOutputWithIntermediateActivations = self.embeddings(pixel_values)
        embedding_last_hidden_states = embedding_output.last_hidden_states
        encoder_outputs: BaseModelOutput = self.encoder(
            embedding_last_hidden_states, head_mask=head_mask, output_hidden_states=output_hidden_states
        )
        sequence_output = encoder_outputs.last_hidden_state
        sequence_output = self.layernorm(sequence_output)
        pooled_output = self.pooler(sequence_output) if self.pooler is not None else None
        return BaseModelOutputWithPoolingAndIntermediateActivations(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            intermediate_activations=embedding_output.intermediate_activations,
            hidden_states=encoder_outputs.hidden_states,
        )
class DPTViTPooler(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.pooler_output_size)
        self.activation = ACT2FN[config.pooler_act]
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        first_token_tensor = hidden_states[:, 0]
        pooled_output = self.dense(first_token_tensor)
        pooled_output = self.activation(pooled_output)
        return pooled_output
class DPTNeck(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.config = config
        if config.backbone_config is not None and config.backbone_config.model_type == "swinv2":
            self.reassemble_stage = None
        else:
            self.reassemble_stage = DPTReassembleStage(config)
        self.convs = nn.ModuleList()
        for channel in config.neck_hidden_sizes:
            self.convs.append(nn.Conv2d(channel, config.fusion_hidden_size, kernel_size=3, padding=1, bias=False))
        self.fusion_stage = DPTFeatureFusionStage(config)
    def forward(
        self,
        hidden_states: list[torch.Tensor],
        patch_height: Optional[int] = None,
        patch_width: Optional[int] = None,
    ) -> list[torch.Tensor]:
        if not isinstance(hidden_states, (tuple, list)):
            raise TypeError("hidden_states should be a tuple or list of tensors")
        if len(hidden_states) != len(self.config.neck_hidden_sizes):
            raise ValueError("The number of hidden states should be equal to the number of neck hidden sizes.")
        if self.reassemble_stage is not None:
            hidden_states = self.reassemble_stage(hidden_states, patch_height, patch_width)
        features = [self.convs[i](feature) for i, feature in enumerate(hidden_states)]
        output = self.fusion_stage(features)
        return output
class DPTDepthEstimationHead(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.config = config
        self.projection = None
        if config.add_projection:
            self.projection = nn.Conv2d(256, 256, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        features = config.fusion_hidden_size
        self.head = nn.Sequential(
            nn.Conv2d(features, features // 2, kernel_size=3, stride=1, padding=1),
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
            nn.Conv2d(features // 2, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=1, stride=1, padding=0),
            nn.ReLU(),
        )
    def forward(self, hidden_states: list[torch.Tensor]) -> torch.Tensor:
        hidden_states = hidden_states[self.config.head_in_index]
        if self.projection is not None:
            hidden_states = self.projection(hidden_states)
            hidden_states = nn.ReLU()(hidden_states)
        predicted_depth = self.head(hidden_states)
        predicted_depth = predicted_depth.squeeze(dim=1)
        return predicted_depth
@auto_docstring(
)
class DPTForDepthEstimation(DPTPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.backbone = None
        if config.is_hybrid is False and (config.backbone_config is not None or config.backbone is not None):
            self.backbone = load_backbone(config)
        else:
            self.dpt = DPTModel(config, add_pooling_layer=False)
        self.neck = DPTNeck(config)
        self.head = DPTDepthEstimationHead(config)
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        head_mask: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        output_hidden_states: Optional[bool] = None,
        **kwargs,
    ) -> DepthEstimatorOutput:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        loss = None
        if labels is not None:
            raise NotImplementedError("Training is not implemented yet")
        if self.backbone is not None:
            outputs = self.backbone.forward_with_filtered_kwargs(pixel_values, output_hidden_states=True, **kwargs)
            hidden_states = outputs.feature_maps
        else:
            outputs = self.dpt(pixel_values, head_mask=head_mask, output_hidden_states=True, **kwargs)
            hidden_states = outputs.hidden_states
            if not self.config.is_hybrid:
                hidden_states = [
                    feature for idx, feature in enumerate(hidden_states[1:]) if idx in self.config.backbone_out_indices
                ]
            else:
                backbone_hidden_states = outputs.intermediate_activations
                backbone_hidden_states.extend(
                    feature
                    for idx, feature in enumerate(hidden_states[1:])
                    if idx in self.config.backbone_out_indices[2:]
                )
                hidden_states = backbone_hidden_states
        patch_height, patch_width = None, None
        if self.config.backbone_config is not None and self.config.is_hybrid is False:
            _, _, height, width = pixel_values.shape
            patch_size = self.config.backbone_config.patch_size
            patch_height = height // patch_size
            patch_width = width // patch_size
        hidden_states = self.neck(hidden_states, patch_height, patch_width)
        predicted_depth = self.head(hidden_states)
        return DepthEstimatorOutput(
            loss=loss,
            predicted_depth=predicted_depth,
            hidden_states=outputs.hidden_states if output_hidden_states else None,
            attentions=outputs.attentions,
        )
class DPTSemanticSegmentationHead(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        self.config = config
        features = config.fusion_hidden_size
        self.head = nn.Sequential(
            nn.Conv2d(features, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(features),
            nn.ReLU(),
            nn.Dropout(config.semantic_classifier_dropout),
            nn.Conv2d(features, config.num_labels, kernel_size=1),
            nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True),
        )
    def forward(self, hidden_states: list[torch.Tensor]) -> torch.Tensor:
        hidden_states = hidden_states[self.config.head_in_index]
        logits = self.head(hidden_states)
        return logits
class DPTAuxiliaryHead(nn.Module):
    def __init__(self, config: DPTConfig):
        super().__init__()
        features = config.fusion_hidden_size
        self.head = nn.Sequential(
            nn.Conv2d(features, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(features),
            nn.ReLU(),
            nn.Dropout(0.1, False),
            nn.Conv2d(features, config.num_labels, kernel_size=1),
        )
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        logits = self.head(hidden_states)
        return logits
@auto_docstring
class DPTForSemanticSegmentation(DPTPreTrainedModel):
    def __init__(self, config: DPTConfig):
        super().__init__(config)
        self.dpt = DPTModel(config, add_pooling_layer=False)
        self.neck = DPTNeck(config)
        self.head = DPTSemanticSegmentationHead(config)
        self.auxiliary_head = DPTAuxiliaryHead(config) if config.use_auxiliary_head else None
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        pixel_values: Optional[torch.FloatTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        output_hidden_states: Optional[bool] = None,
        **kwargs,
    ) -> SemanticSegmenterOutput:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        if labels is not None and self.config.num_labels == 1:
            raise ValueError("The number of labels should be greater than one")
        outputs: BaseModelOutputWithPoolingAndIntermediateActivations = self.dpt(
            pixel_values, head_mask=head_mask, output_hidden_states=True, **kwargs
        )
        hidden_states = outputs.hidden_states
        if not self.config.is_hybrid:
            hidden_states = [
                feature for idx, feature in enumerate(hidden_states[1:]) if idx in self.config.backbone_out_indices
            ]
        else:
            backbone_hidden_states = outputs.intermediate_activations
            backbone_hidden_states.extend(
                feature for idx, feature in enumerate(hidden_states[1:]) if idx in self.config.backbone_out_indices[2:]
            )
            hidden_states = backbone_hidden_states
        hidden_states = self.neck(hidden_states=hidden_states)
        logits = self.head(hidden_states)
        auxiliary_logits = None
        if self.auxiliary_head is not None:
            auxiliary_logits = self.auxiliary_head(hidden_states[-1])
        loss = None
        if labels is not None:
            upsampled_logits = nn.functional.interpolate(
                logits, size=labels.shape[-2:], mode="bilinear", align_corners=False
            )
            if auxiliary_logits is not None:
                upsampled_auxiliary_logits = nn.functional.interpolate(
                    auxiliary_logits, size=labels.shape[-2:], mode="bilinear", align_corners=False
                )
            loss_fct = CrossEntropyLoss(ignore_index=self.config.semantic_loss_ignore_index)
            main_loss = loss_fct(upsampled_logits, labels)
            auxiliary_loss = loss_fct(upsampled_auxiliary_logits, labels)
            loss = main_loss + self.config.auxiliary_loss_weight * auxiliary_loss
        return SemanticSegmenterOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states if output_hidden_states else None,
            attentions=outputs.attentions,
        )
__all__ = ["DPTForDepthEstimation", "DPTForSemanticSegmentation", "DPTModel", "DPTPreTrainedModel"]