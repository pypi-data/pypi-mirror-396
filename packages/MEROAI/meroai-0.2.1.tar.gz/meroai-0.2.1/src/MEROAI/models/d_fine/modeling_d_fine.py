import math
from dataclasses import dataclass
from typing import Any, Optional, Union
import torch
import torch.nn.functional as F
import torch.nn.init as init
from torch import Tensor, nn
from ...activations import ACT2CLS, ACT2FN
from ...image_transforms import center_to_corners_format, corners_to_center_format
from ...modeling_outputs import BaseModelOutput
from ...modeling_utils import PreTrainedModel
from ...pytorch_utils import compile_compatible_method_lru_cache
from ...utils import ModelOutput, auto_docstring, is_torchdynamo_compiling, torch_int
from ...utils.backbone_utils import load_backbone
from .configuration_d_fine import DFineConfig
def multi_scale_deformable_attention_v2(
    value: Tensor,
    value_spatial_shapes: Tensor,
    sampling_locations: Tensor,
    attention_weights: Tensor,
    num_points_list: list[int],
    method="default",
) -> Tensor:
    batch_size, _, num_heads, hidden_dim = value.shape
    _, num_queries, num_heads, num_levels, num_points = sampling_locations.shape
    value_list = (
        value.permute(0, 2, 3, 1)
        .flatten(0, 1)
        .split([height * width for height, width in value_spatial_shapes], dim=-1)
    )
    if method == "default":
        sampling_grids = 2 * sampling_locations - 1
    elif method == "discrete":
        sampling_grids = sampling_locations
    sampling_grids = sampling_grids.permute(0, 2, 1, 3, 4).flatten(0, 1)
    sampling_grids = sampling_grids.split(num_points_list, dim=-2)
    sampling_value_list = []
    for level_id, (height, width) in enumerate(value_spatial_shapes):
        value_l_ = value_list[level_id].reshape(batch_size * num_heads, hidden_dim, height, width)
        sampling_grid_l_ = sampling_grids[level_id]
        if method == "default":
            sampling_value_l_ = nn.functional.grid_sample(
                value_l_, sampling_grid_l_, mode="bilinear", padding_mode="zeros", align_corners=False
            )
        elif method == "discrete":
            sampling_coord = (sampling_grid_l_ * torch.tensor([[width, height]], device=value.device) + 0.5).to(
                torch.int64
            )
            sampling_coord_x = sampling_coord[..., 0].clamp(0, width - 1)
            sampling_coord_y = sampling_coord[..., 1].clamp(0, height - 1)
            sampling_coord = torch.stack([sampling_coord_x, sampling_coord_y], dim=-1)
            sampling_coord = sampling_coord.reshape(batch_size * num_heads, num_queries * num_points_list[level_id], 2)
            sampling_idx = (
                torch.arange(sampling_coord.shape[0], device=value.device)
                .unsqueeze(-1)
                .repeat(1, sampling_coord.shape[1])
            )
            sampling_value_l_ = value_l_[sampling_idx, :, sampling_coord[..., 1], sampling_coord[..., 0]]
            sampling_value_l_ = sampling_value_l_.permute(0, 2, 1).reshape(
                batch_size * num_heads, hidden_dim, num_queries, num_points_list[level_id]
            )
        sampling_value_list.append(sampling_value_l_)
    attention_weights = attention_weights.permute(0, 2, 1, 3).reshape(
        batch_size * num_heads, 1, num_queries, sum(num_points_list)
    )
    output = (
        (torch.concat(sampling_value_list, dim=-1) * attention_weights)
        .sum(-1)
        .view(batch_size, num_heads * hidden_dim, num_queries)
    )
    return output.transpose(1, 2).contiguous()
class DFineMultiscaleDeformableAttention(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.d_model = config.d_model
        self.n_heads = config.decoder_attention_heads
        self.n_levels = config.num_feature_levels
        self.offset_scale = config.decoder_offset_scale
        self.decoder_method = config.decoder_method
        self.n_points = config.decoder_n_points
        if isinstance(self.n_points, list):
            num_points_list = self.n_points
        else:
            num_points_list = [self.n_points for _ in range(self.n_levels)]
        self.num_points_list = num_points_list
        num_points_scale = [1 / n for n in self.num_points_list for _ in range(n)]
        self.register_buffer("num_points_scale", torch.tensor(num_points_scale, dtype=torch.float32))
        self.total_points = self.n_heads * sum(self.num_points_list)
        self.sampling_offsets = nn.Linear(self.d_model, self.total_points * 2)
        self.attention_weights = nn.Linear(self.d_model, self.total_points)
        self.ms_deformable_attn_core = multi_scale_deformable_attention_v2
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        reference_points=None,
        encoder_hidden_states=None,
        spatial_shapes=None,
        spatial_shapes_list=None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        batch_size, num_queries, _ = hidden_states.shape
        batch_size, sequence_length, _ = encoder_hidden_states.shape
        if not is_torchdynamo_compiling() and (spatial_shapes[:, 0] * spatial_shapes[:, 1]).sum() != sequence_length:
            raise ValueError(
                "Make sure to align the spatial shapes with the sequence length of the encoder hidden states"
            )
        value = encoder_hidden_states.reshape(batch_size, sequence_length, self.n_heads, self.d_model // self.n_heads)
        if attention_mask is not None:
            value = value.masked_fill(~attention_mask[..., None], float(0))
        sampling_offsets: torch.Tensor = self.sampling_offsets(hidden_states)
        sampling_offsets = sampling_offsets.reshape(
            batch_size, num_queries, self.n_heads, sum(self.num_points_list), 2
        )
        attention_weights = self.attention_weights(hidden_states).reshape(
            batch_size, num_queries, self.n_heads, sum(self.num_points_list)
        )
        attention_weights = F.softmax(attention_weights, dim=-1)
        if reference_points.shape[-1] == 2:
            offset_normalizer = torch.tensor(spatial_shapes)
            offset_normalizer = offset_normalizer.flip([1]).reshape(1, 1, 1, self.n_levels, 1, 2)
            sampling_locations = (
                reference_points.reshape(batch_size, sequence_length, 1, self.n_levels, 1, 2)
                + sampling_offsets / offset_normalizer
            )
        elif reference_points.shape[-1] == 4:
            num_points_scale = self.num_points_scale.to(dtype=hidden_states.dtype).unsqueeze(-1)
            offset = sampling_offsets * num_points_scale * reference_points[:, :, None, :, 2:] * self.offset_scale
            sampling_locations = reference_points[:, :, None, :, :2] + offset
        else:
            raise ValueError(
                f"Last dim of reference_points must be 2 or 4, but get {reference_points.shape[-1]} instead."
            )
        output = self.ms_deformable_attn_core(
            value,
            spatial_shapes_list,
            sampling_locations,
            attention_weights,
            self.num_points_list,
            self.decoder_method,
        )
        return output, attention_weights
class DFineGate(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.gate = nn.Linear(2 * d_model, 2 * d_model)
        self.norm = nn.LayerNorm(d_model)
    def forward(self, second_residual: torch.Tensor, hidden_states: torch.Tensor) -> torch.Tensor:
        gate_input = torch.cat([second_residual, hidden_states], dim=-1)
        gates = torch.sigmoid(self.gate(gate_input))
        gate1, gate2 = gates.chunk(2, dim=-1)
        hidden_states = self.norm(gate1 * second_residual + gate2 * hidden_states)
        return hidden_states
class DFineMultiheadAttention(nn.Module):
    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.0,
        bias: bool = True,
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.dropout = dropout
        self.head_dim = embed_dim // num_heads
        if self.head_dim * num_heads != self.embed_dim:
            raise ValueError(
                f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`:"
                f" {num_heads})."
            )
        self.scaling = self.head_dim**-0.5
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
    def _reshape(self, tensor: torch.Tensor, seq_len: int, batch_size: int):
        return tensor.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2).contiguous()
    def with_pos_embed(self, tensor: torch.Tensor, position_embeddings: Optional[Tensor]):
        return tensor if position_embeddings is None else tensor + position_embeddings
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_embeddings: Optional[torch.Tensor] = None,
        output_attentions: bool = False,
    ) -> tuple[torch.Tensor, Optional[torch.Tensor], Optional[tuple[torch.Tensor]]]:
        batch_size, target_len, embed_dim = hidden_states.size()
        if position_embeddings is not None:
            hidden_states_original = hidden_states
            hidden_states = self.with_pos_embed(hidden_states, position_embeddings)
        query_states = self.q_proj(hidden_states) * self.scaling
        key_states = self._reshape(self.k_proj(hidden_states), -1, batch_size)
        value_states = self._reshape(self.v_proj(hidden_states_original), -1, batch_size)
        proj_shape = (batch_size * self.num_heads, -1, self.head_dim)
        query_states = self._reshape(query_states, target_len, batch_size).view(*proj_shape)
        key_states = key_states.view(*proj_shape)
        value_states = value_states.view(*proj_shape)
        source_len = key_states.size(1)
        attn_weights = torch.bmm(query_states, key_states.transpose(1, 2))
        if attn_weights.size() != (batch_size * self.num_heads, target_len, source_len):
            raise ValueError(
                f"Attention weights should be of size {(batch_size * self.num_heads, target_len, source_len)}, but is"
                f" {attn_weights.size()}"
            )
        if attention_mask is not None:
            attention_mask = attention_mask.expand(batch_size, 1, *attention_mask.size())
        if attention_mask is not None:
            if attention_mask.size() != (batch_size, 1, target_len, source_len):
                raise ValueError(
                    f"Attention mask should be of size {(batch_size, 1, target_len, source_len)}, but is"
                    f" {attention_mask.size()}"
                )
            if attention_mask.dtype == torch.bool:
                attention_mask = torch.zeros_like(attention_mask, dtype=attn_weights.dtype).masked_fill_(
                    attention_mask, -torch.inf
                )
            attn_weights = attn_weights.view(batch_size, self.num_heads, target_len, source_len) + attention_mask
            attn_weights = attn_weights.view(batch_size * self.num_heads, target_len, source_len)
        attn_weights = nn.functional.softmax(attn_weights, dim=-1)
        if output_attentions:
            attn_weights_reshaped = attn_weights.view(batch_size, self.num_heads, target_len, source_len)
            attn_weights = attn_weights_reshaped.view(batch_size * self.num_heads, target_len, source_len)
        else:
            attn_weights_reshaped = None
        attn_probs = nn.functional.dropout(attn_weights, p=self.dropout, training=self.training)
        attn_output = torch.bmm(attn_probs, value_states)
        if attn_output.size() != (batch_size * self.num_heads, target_len, self.head_dim):
            raise ValueError(
                f"`attn_output` should be of size {(batch_size, self.num_heads, target_len, self.head_dim)}, but is"
                f" {attn_output.size()}"
            )
        attn_output = attn_output.view(batch_size, self.num_heads, target_len, self.head_dim)
        attn_output = attn_output.transpose(1, 2)
        attn_output = attn_output.reshape(batch_size, target_len, embed_dim)
        attn_output = self.out_proj(attn_output)
        return attn_output, attn_weights_reshaped
class DFineDecoderLayer(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.self_attn = DFineMultiheadAttention(
            embed_dim=config.d_model,
            num_heads=config.decoder_attention_heads,
            dropout=config.attention_dropout,
        )
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.decoder_activation_function]
        self.activation_dropout = config.activation_dropout
        self.self_attn_layer_norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.encoder_attn = DFineMultiscaleDeformableAttention(config=config)
        self.fc1 = nn.Linear(config.d_model, config.decoder_ffn_dim)
        self.fc2 = nn.Linear(config.decoder_ffn_dim, config.d_model)
        self.final_layer_norm = nn.LayerNorm(config.d_model, eps=config.layer_norm_eps)
        self.gateway = DFineGate(config.d_model)
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: Optional[torch.Tensor] = None,
        reference_points=None,
        spatial_shapes=None,
        spatial_shapes_list=None,
        encoder_hidden_states: Optional[torch.Tensor] = None,
        encoder_attention_mask: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = False,
    ) -> tuple[torch.Tensor, Any, Any]:
        hidden_states_2, self_attn_weights = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=encoder_attention_mask,
            position_embeddings=position_embeddings,
            output_attentions=output_attentions,
        )
        hidden_states_2 = nn.functional.dropout(hidden_states_2, p=self.dropout, training=self.training)
        hidden_states = hidden_states + hidden_states_2
        hidden_states = self.self_attn_layer_norm(hidden_states)
        residual = hidden_states
        cross_attn_weights = None
        hidden_states = hidden_states if position_embeddings is None else hidden_states + position_embeddings
        hidden_states_2, cross_attn_weights = self.encoder_attn(
            hidden_states=hidden_states,
            encoder_hidden_states=encoder_hidden_states,
            reference_points=reference_points,
            spatial_shapes=spatial_shapes,
            spatial_shapes_list=spatial_shapes_list,
        )
        hidden_states_2 = nn.functional.dropout(hidden_states_2, p=self.dropout, training=self.training)
        hidden_states = self.gateway(residual, hidden_states_2)
        hidden_states_2 = self.activation_fn(self.fc1(hidden_states))
        hidden_states_2 = nn.functional.dropout(hidden_states_2, p=self.activation_dropout, training=self.training)
        hidden_states_2 = self.fc2(hidden_states_2)
        hidden_states_2 = nn.functional.dropout(hidden_states_2, p=self.dropout, training=self.training)
        hidden_states = hidden_states + hidden_states_2
        hidden_states = self.final_layer_norm(hidden_states.clamp(min=-65504, max=65504))
        outputs = (hidden_states,)
        if output_attentions:
            outputs += (self_attn_weights, cross_attn_weights)
        return outputs
@auto_docstring
class DFinePreTrainedModel(PreTrainedModel):
    config: DFineConfig
    base_model_prefix = "d_fine"
    main_input_name = "pixel_values"
    _no_split_modules = [r"DFineHybridEncoder", r"DFineDecoderLayer"]
    def _init_weights(self, module):
        if isinstance(module, (DFineForObjectDetection, DFineDecoder)):
            if module.class_embed is not None:
                for layer in module.class_embed:
                    prior_prob = self.config.initializer_bias_prior_prob or 1 / (self.config.num_labels + 1)
                    bias = float(-math.log((1 - prior_prob) / prior_prob))
                    nn.init.xavier_uniform_(layer.weight)
                    nn.init.constant_(layer.bias, bias)
            if module.bbox_embed is not None:
                for layer in module.bbox_embed:
                    nn.init.constant_(layer.layers[-1].weight, 0)
                    nn.init.constant_(layer.layers[-1].bias, 0)
            if hasattr(module, "reg_scale"):
                module.reg_scale.fill_(self.config.reg_scale)
            if hasattr(module, "up"):
                module.up.fill_(self.config.up)
        if isinstance(module, DFineMultiscaleDeformableAttention):
            nn.init.constant_(module.sampling_offsets.weight.data, 0.0)
            default_dtype = torch.get_default_dtype()
            thetas = torch.arange(module.n_heads, dtype=torch.int64).to(default_dtype) * (
                2.0 * math.pi / module.n_heads
            )
            grid_init = torch.stack([thetas.cos(), thetas.sin()], -1)
            grid_init = grid_init / grid_init.abs().max(-1, keepdim=True).values
            grid_init = grid_init.reshape(module.n_heads, 1, 2).tile([1, sum(module.num_points_list), 1])
            scaling = torch.concat([torch.arange(1, n + 1) for n in module.num_points_list]).reshape(1, -1, 1)
            grid_init *= scaling
            with torch.no_grad():
                module.sampling_offsets.bias.data[...] = grid_init.flatten()
            nn.init.constant_(module.attention_weights.weight.data, 0.0)
            nn.init.constant_(module.attention_weights.bias.data, 0.0)
        if isinstance(module, DFineModel):
            prior_prob = self.config.initializer_bias_prior_prob or 1 / (self.config.num_labels + 1)
            bias = float(-math.log((1 - prior_prob) / prior_prob))
            nn.init.xavier_uniform_(module.enc_score_head.weight)
            nn.init.constant_(module.enc_score_head.bias, bias)
        if isinstance(module, (nn.Linear, nn.Conv2d, nn.BatchNorm2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        if isinstance(module, DFineGate):
            bias = float(-math.log((1 - 0.5) / 0.5))
            init.constant_(module.gate.bias, bias)
            init.constant_(module.gate.weight, 0)
        if isinstance(module, DFineLQE):
            init.constant_(module.reg_conf.layers[-1].bias, 0)
            init.constant_(module.reg_conf.layers[-1].weight, 0)
        if isinstance(module, nn.LayerNorm):
            module.weight.data.fill_(1.0)
            module.bias.data.zero_()
        if hasattr(module, "weight_embedding") and self.config.learn_initial_query:
            nn.init.xavier_uniform_(module.weight_embedding.weight)
        if hasattr(module, "denoising_class_embed") and self.config.num_denoising > 0:
            nn.init.xavier_uniform_(module.denoising_class_embed.weight)
class DFineIntegral(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.max_num_bins = config.max_num_bins
    def forward(self, pred_corners: torch.Tensor, project: torch.Tensor) -> torch.Tensor:
        batch_size, num_queries, _ = pred_corners.shape
        pred_corners = F.softmax(pred_corners.reshape(-1, self.max_num_bins + 1), dim=1)
        pred_corners = F.linear(pred_corners, project.to(pred_corners.device)).reshape(-1, 4)
        pred_corners = pred_corners.reshape(batch_size, num_queries, -1)
        return pred_corners
@dataclass
@auto_docstring(
)
class DFineDecoderOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_logits: Optional[torch.FloatTensor] = None
    intermediate_reference_points: Optional[torch.FloatTensor] = None
    intermediate_predicted_corners: Optional[torch.FloatTensor] = None
    initial_reference_points: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor]] = None
def inverse_sigmoid(x, eps=1e-5):
    x = x.clamp(min=0, max=1)
    x1 = x.clamp(min=eps)
    x2 = (1 - x).clamp(min=eps)
    return torch.log(x1 / x2)
def weighting_function(max_num_bins: int, up: torch.Tensor, reg_scale: int) -> torch.Tensor:
    upper_bound1 = abs(up[0]) * abs(reg_scale)
    upper_bound2 = abs(up[0]) * abs(reg_scale) * 2
    step = (upper_bound1 + 1) ** (2 / (max_num_bins - 2))
    left_values = [-((step) ** i) + 1 for i in range(max_num_bins // 2 - 1, 0, -1)]
    right_values = [(step) ** i - 1 for i in range(1, max_num_bins // 2)]
    values = [-upper_bound2] + left_values + [torch.zeros_like(up[0][None])] + right_values + [upper_bound2]
    values = torch.cat(values, 0)
    return values
def distance2bbox(points, distance: torch.Tensor, reg_scale: float) -> torch.Tensor:
    reg_scale = abs(reg_scale)
    top_left_x = points[..., 0] - (0.5 * reg_scale + distance[..., 0]) * (points[..., 2] / reg_scale)
    top_left_y = points[..., 1] - (0.5 * reg_scale + distance[..., 1]) * (points[..., 3] / reg_scale)
    bottom_right_x = points[..., 0] + (0.5 * reg_scale + distance[..., 2]) * (points[..., 2] / reg_scale)
    bottom_right_y = points[..., 1] + (0.5 * reg_scale + distance[..., 3]) * (points[..., 3] / reg_scale)
    bboxes = torch.stack([top_left_x, top_left_y, bottom_right_x, bottom_right_y], -1)
    return corners_to_center_format(bboxes)
class DFineDecoder(DFinePreTrainedModel):
    def __init__(self, config: DFineConfig):
        super().__init__(config)
        self.eval_idx = config.eval_idx if config.eval_idx >= 0 else config.decoder_layers + config.eval_idx
        self.dropout = config.dropout
        self.layers = nn.ModuleList(
            [DFineDecoderLayer(config) for _ in range(config.decoder_layers)]
            + [DFineDecoderLayer(config) for _ in range(config.decoder_layers - self.eval_idx - 1)]
        )
        self.query_pos_head = DFineMLPPredictionHead(config, 4, 2 * config.d_model, config.d_model, num_layers=2)
        self.bbox_embed = None
        self.class_embed = None
        self.reg_scale = nn.Parameter(torch.tensor([config.reg_scale]), requires_grad=False)
        self.max_num_bins = config.max_num_bins
        self.d_model = config.d_model
        self.layer_scale = config.layer_scale
        self.pre_bbox_head = DFineMLP(config.hidden_size, config.hidden_size, 4, 3)
        self.integral = DFineIntegral(config)
        self.num_head = config.decoder_attention_heads
        self.up = nn.Parameter(torch.tensor([config.up]), requires_grad=False)
        self.lqe_layers = nn.ModuleList([DFineLQE(config) for _ in range(config.decoder_layers)])
        self.post_init()
    def forward(
        self,
        encoder_hidden_states: torch.Tensor,
        reference_points: torch.Tensor,
        inputs_embeds: torch.Tensor,
        spatial_shapes,
        level_start_index=None,
        spatial_shapes_list=None,
        output_hidden_states=None,
        encoder_attention_mask=None,
        memory_mask=None,
        output_attentions=None,
        return_dict=None,
    ) -> DFineDecoderOutput:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if inputs_embeds is not None:
            hidden_states = inputs_embeds
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        all_cross_attentions = () if (output_attentions and encoder_hidden_states is not None) else None
        intermediate = ()
        intermediate_reference_points = ()
        intermediate_logits = ()
        intermediate_predicted_corners = ()
        initial_reference_points = ()
        output_detach = pred_corners_undetach = 0
        project = weighting_function(self.max_num_bins, self.up, self.reg_scale)
        ref_points_detach = F.sigmoid(reference_points)
        for i, decoder_layer in enumerate(self.layers):
            ref_points_input = ref_points_detach.unsqueeze(2)
            query_pos_embed = self.query_pos_head(ref_points_detach).clamp(min=-10, max=10)
            if output_hidden_states:
                all_hidden_states += (hidden_states,)
            output = decoder_layer(
                hidden_states=hidden_states,
                position_embeddings=query_pos_embed,
                reference_points=ref_points_input,
                spatial_shapes=spatial_shapes,
                spatial_shapes_list=spatial_shapes_list,
                encoder_hidden_states=encoder_hidden_states,
                encoder_attention_mask=encoder_attention_mask,
                output_attentions=output_attentions,
            )
            hidden_states = output[0]
            if i == 0:
                new_reference_points = F.sigmoid(self.pre_bbox_head(output[0]) + inverse_sigmoid(ref_points_detach))
                ref_points_initial = new_reference_points.detach()
            if self.bbox_embed is not None:
                pred_corners = self.bbox_embed[i](hidden_states + output_detach) + pred_corners_undetach
                inter_ref_bbox = distance2bbox(
                    ref_points_initial, self.integral(pred_corners, project), self.reg_scale
                )
                pred_corners_undetach = pred_corners
                ref_points_detach = inter_ref_bbox.detach()
            output_detach = hidden_states.detach()
            intermediate += (hidden_states,)
            if self.class_embed is not None and (self.training or i == self.eval_idx):
                scores = self.class_embed[i](hidden_states)
                if i == 0:
                    intermediate_logits += (scores,)
                    intermediate_reference_points += (new_reference_points,)
                scores = self.lqe_layers[i](scores, pred_corners)
                intermediate_logits += (scores,)
                intermediate_reference_points += (inter_ref_bbox,)
                initial_reference_points += (ref_points_initial,)
                intermediate_predicted_corners += (pred_corners,)
            if output_attentions:
                all_self_attns += (output[1],)
                if encoder_hidden_states is not None:
                    all_cross_attentions += (output[2],)
        intermediate = torch.stack(intermediate)
        if self.class_embed is not None and self.bbox_embed is not None:
            intermediate_logits = torch.stack(intermediate_logits, dim=1)
            intermediate_predicted_corners = torch.stack(intermediate_predicted_corners, dim=1)
            initial_reference_points = torch.stack(initial_reference_points, dim=1)
            intermediate_reference_points = torch.stack(intermediate_reference_points, dim=1)
        if output_hidden_states:
            all_hidden_states += (hidden_states,)
        if not return_dict:
            return tuple(
                v
                for v in [
                    hidden_states,
                    intermediate,
                    intermediate_logits,
                    intermediate_reference_points,
                    intermediate_predicted_corners,
                    initial_reference_points,
                    all_hidden_states,
                    all_self_attns,
                    all_cross_attentions,
                ]
                if v is not None
            )
        return DFineDecoderOutput(
            last_hidden_state=hidden_states,
            intermediate_hidden_states=intermediate,
            intermediate_logits=intermediate_logits,
            intermediate_reference_points=intermediate_reference_points,
            intermediate_predicted_corners=intermediate_predicted_corners,
            initial_reference_points=initial_reference_points,
            hidden_states=all_hidden_states,
            attentions=all_self_attns,
            cross_attentions=all_cross_attentions,
        )
@dataclass
@auto_docstring(
)
class DFineModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_logits: Optional[torch.FloatTensor] = None
    intermediate_reference_points: Optional[torch.FloatTensor] = None
    intermediate_predicted_corners: Optional[torch.FloatTensor] = None
    initial_reference_points: Optional[torch.FloatTensor] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    init_reference_points: Optional[torch.FloatTensor] = None
    enc_topk_logits: Optional[torch.FloatTensor] = None
    enc_topk_bboxes: Optional[torch.FloatTensor] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
    denoising_meta_values: Optional[dict] = None
class DFineFrozenBatchNorm2d(nn.Module):
    def __init__(self, n):
        super().__init__()
        self.register_buffer("weight", torch.ones(n))
        self.register_buffer("bias", torch.zeros(n))
        self.register_buffer("running_mean", torch.zeros(n))
        self.register_buffer("running_var", torch.ones(n))
    def _load_from_state_dict(
        self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs
    ):
        num_batches_tracked_key = prefix + "num_batches_tracked"
        if num_batches_tracked_key in state_dict:
            del state_dict[num_batches_tracked_key]
        super()._load_from_state_dict(
            state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs
        )
    def forward(self, x):
        weight = self.weight.reshape(1, -1, 1, 1)
        bias = self.bias.reshape(1, -1, 1, 1)
        running_var = self.running_var.reshape(1, -1, 1, 1)
        running_mean = self.running_mean.reshape(1, -1, 1, 1)
        epsilon = 1e-5
        scale = weight * (running_var + epsilon).rsqrt()
        bias = bias - running_mean * scale
        return x * scale + bias
def replace_batch_norm(model):
    for name, module in model.named_children():
        if isinstance(module, nn.BatchNorm2d):
            new_module = DFineFrozenBatchNorm2d(module.num_features)
            if module.weight.device != torch.device("meta"):
                new_module.weight.data.copy_(module.weight)
                new_module.bias.data.copy_(module.bias)
                new_module.running_mean.data.copy_(module.running_mean)
                new_module.running_var.data.copy_(module.running_var)
            model._modules[name] = new_module
        if len(list(module.children())) > 0:
            replace_batch_norm(module)
class DFineConvEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        backbone = load_backbone(config)
        if config.freeze_backbone_batch_norms:
            with torch.no_grad():
                replace_batch_norm(backbone)
        self.model = backbone
        self.intermediate_channel_sizes = self.model.channels
    def forward(self, pixel_values: torch.Tensor, pixel_mask: torch.Tensor):
        features = self.model(pixel_values).feature_maps
        out = []
        for feature_map in features:
            mask = nn.functional.interpolate(pixel_mask[None].float(), size=feature_map.shape[-2:]).to(torch.bool)[0]
            out.append((feature_map, mask))
        return out
def get_contrastive_denoising_training_group(
    targets,
    num_classes,
    num_queries,
    class_embed,
    num_denoising_queries=100,
    label_noise_ratio=0.5,
    box_noise_scale=1.0,
):
    if num_denoising_queries <= 0:
        return None, None, None, None
    num_ground_truths = [len(t["class_labels"]) for t in targets]
    device = targets[0]["class_labels"].device
    max_gt_num = max(num_ground_truths)
    if max_gt_num == 0:
        return None, None, None, None
    num_groups_denoising_queries = num_denoising_queries // max_gt_num
    num_groups_denoising_queries = 1 if num_groups_denoising_queries == 0 else num_groups_denoising_queries
    batch_size = len(num_ground_truths)
    input_query_class = torch.full([batch_size, max_gt_num], num_classes, dtype=torch.int32, device=device)
    input_query_bbox = torch.zeros([batch_size, max_gt_num, 4], device=device)
    pad_gt_mask = torch.zeros([batch_size, max_gt_num], dtype=torch.bool, device=device)
    for i in range(batch_size):
        num_gt = num_ground_truths[i]
        if num_gt > 0:
            input_query_class[i, :num_gt] = targets[i]["class_labels"]
            input_query_bbox[i, :num_gt] = targets[i]["boxes"]
            pad_gt_mask[i, :num_gt] = 1
    input_query_class = input_query_class.tile([1, 2 * num_groups_denoising_queries])
    input_query_bbox = input_query_bbox.tile([1, 2 * num_groups_denoising_queries, 1])
    pad_gt_mask = pad_gt_mask.tile([1, 2 * num_groups_denoising_queries])
    negative_gt_mask = torch.zeros([batch_size, max_gt_num * 2, 1], device=device)
    negative_gt_mask[:, max_gt_num:] = 1
    negative_gt_mask = negative_gt_mask.tile([1, num_groups_denoising_queries, 1])
    positive_gt_mask = 1 - negative_gt_mask
    positive_gt_mask = positive_gt_mask.squeeze(-1) * pad_gt_mask
    denoise_positive_idx = torch.nonzero(positive_gt_mask)[:, 1]
    denoise_positive_idx = torch.split(
        denoise_positive_idx, [n * num_groups_denoising_queries for n in num_ground_truths]
    )
    num_denoising_queries = torch_int(max_gt_num * 2 * num_groups_denoising_queries)
    if label_noise_ratio > 0:
        mask = torch.rand_like(input_query_class, dtype=torch.float) < (label_noise_ratio * 0.5)
        new_label = torch.randint_like(mask, 0, num_classes, dtype=input_query_class.dtype)
        input_query_class = torch.where(mask & pad_gt_mask, new_label, input_query_class)
    if box_noise_scale > 0:
        known_bbox = center_to_corners_format(input_query_bbox)
        diff = torch.tile(input_query_bbox[..., 2:] * 0.5, [1, 1, 2]) * box_noise_scale
        rand_sign = torch.randint_like(input_query_bbox, 0, 2) * 2.0 - 1.0
        rand_part = torch.rand_like(input_query_bbox)
        rand_part = (rand_part + 1.0) * negative_gt_mask + rand_part * (1 - negative_gt_mask)
        rand_part *= rand_sign
        known_bbox += rand_part * diff
        known_bbox.clip_(min=0.0, max=1.0)
        input_query_bbox = corners_to_center_format(known_bbox)
        input_query_bbox = inverse_sigmoid(input_query_bbox)
    input_query_class = class_embed(input_query_class)
    target_size = num_denoising_queries + num_queries
    attn_mask = torch.full([target_size, target_size], 0, dtype=torch.float, device=device)
    attn_mask[num_denoising_queries:, :num_denoising_queries] = -torch.inf
    for i in range(num_groups_denoising_queries):
        idx_block_start = max_gt_num * 2 * i
        idx_block_end = max_gt_num * 2 * (i + 1)
        attn_mask[idx_block_start:idx_block_end, :idx_block_start] = -torch.inf
        attn_mask[idx_block_start:idx_block_end, idx_block_end:num_denoising_queries] = -torch.inf
    denoising_meta_values = {
        "dn_positive_idx": denoise_positive_idx,
        "dn_num_group": num_groups_denoising_queries,
        "dn_num_split": [num_denoising_queries, num_queries],
    }
    return input_query_class, input_query_bbox, attn_mask, denoising_meta_values
@auto_docstring(
)
class DFineModel(DFinePreTrainedModel):
    def __init__(self, config: DFineConfig):
        super().__init__(config)
        self.backbone = DFineConvEncoder(config)
        intermediate_channel_sizes = self.backbone.intermediate_channel_sizes
        num_backbone_outs = len(config.decoder_in_channels)
        encoder_input_proj_list = []
        for _ in range(num_backbone_outs):
            in_channels = intermediate_channel_sizes[_]
            encoder_input_proj_list.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, config.encoder_hidden_dim, kernel_size=1, bias=False),
                    nn.BatchNorm2d(config.encoder_hidden_dim),
                )
            )
        self.encoder_input_proj = nn.ModuleList(encoder_input_proj_list)
        self.encoder = DFineHybridEncoder(config=config)
        if config.num_denoising > 0:
            self.denoising_class_embed = nn.Embedding(
                config.num_labels + 1, config.d_model, padding_idx=config.num_labels
            )
        if config.learn_initial_query:
            self.weight_embedding = nn.Embedding(config.num_queries, config.d_model)
        self.enc_output = nn.Sequential(
            nn.Linear(config.d_model, config.d_model),
            nn.LayerNorm(config.d_model, eps=config.layer_norm_eps),
        )
        self.enc_score_head = nn.Linear(config.d_model, config.num_labels)
        self.enc_bbox_head = DFineMLPPredictionHead(config, config.d_model, config.d_model, 4, num_layers=3)
        if config.anchor_image_size:
            self.anchors, self.valid_mask = self.generate_anchors(dtype=self.dtype)
        num_backbone_outs = len(config.decoder_in_channels)
        decoder_input_proj_list = []
        for _ in range(num_backbone_outs):
            in_channels = config.decoder_in_channels[_]
            decoder_input_proj_list.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, config.d_model, kernel_size=1, bias=False),
                    nn.BatchNorm2d(config.d_model, config.batch_norm_eps),
                )
            )
        for _ in range(config.num_feature_levels - num_backbone_outs):
            decoder_input_proj_list.append(
                nn.Sequential(
                    nn.Conv2d(in_channels, config.d_model, kernel_size=3, stride=2, padding=1, bias=False),
                    nn.BatchNorm2d(config.d_model, config.batch_norm_eps),
                )
            )
            in_channels = config.d_model
        self.decoder = DFineDecoder(config)
        decoder_input_proj = []
        in_channels = config.decoder_in_channels[-1]
        for _ in range(num_backbone_outs):
            if config.hidden_size == config.decoder_in_channels[-1]:
                decoder_input_proj.append(nn.Identity())
            else:
                conv = nn.Conv2d(in_channels, config.d_model, kernel_size=1, bias=False)
                batchnorm = nn.BatchNorm2d(config.d_model, config.batch_norm_eps)
                decoder_input_proj.append(nn.Sequential(conv, batchnorm))
        for _ in range(config.num_feature_levels - num_backbone_outs):
            if config.hidden_size == config.decoder_in_channels[-1]:
                decoder_input_proj.append(nn.Identity())
            else:
                conv = nn.Conv2d(in_channels, config.d_model, kernel_size=3, stride=2, padding=1, bias=False)
                batchnorm = nn.BatchNorm2d(config.d_model, config.batch_norm_eps)
                decoder_input_proj.append(nn.Sequential(conv, batchnorm))
        self.decoder_input_proj = nn.ModuleList(decoder_input_proj)
        self.post_init()
    def get_encoder(self):
        return self.encoder
    def freeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad_(False)
    def unfreeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad_(True)
    @compile_compatible_method_lru_cache(maxsize=32)
    def generate_anchors(self, spatial_shapes=None, grid_size=0.05, device="cpu", dtype=torch.float32):
        if spatial_shapes is None:
            spatial_shapes = [
                [int(self.config.anchor_image_size[0] / s), int(self.config.anchor_image_size[1] / s)]
                for s in self.config.feat_strides
            ]
        anchors = []
        for level, (height, width) in enumerate(spatial_shapes):
            grid_y, grid_x = torch.meshgrid(
                torch.arange(end=height, device=device).to(dtype),
                torch.arange(end=width, device=device).to(dtype),
                indexing="ij",
            )
            grid_xy = torch.stack([grid_x, grid_y], -1)
            grid_xy = grid_xy.unsqueeze(0) + 0.5
            grid_xy[..., 0] /= width
            grid_xy[..., 1] /= height
            wh = torch.ones_like(grid_xy) * grid_size * (2.0**level)
            anchors.append(torch.concat([grid_xy, wh], -1).reshape(-1, height * width, 4))
        eps = 1e-2
        anchors = torch.concat(anchors, 1)
        valid_mask = ((anchors > eps) * (anchors < 1 - eps)).all(-1, keepdim=True)
        anchors = torch.log(anchors / (1 - anchors))
        anchors = torch.where(valid_mask, anchors, torch.tensor(torch.finfo(dtype).max, dtype=dtype, device=device))
        return anchors, valid_mask
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        pixel_mask: Optional[torch.LongTensor] = None,
        encoder_outputs: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        decoder_inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[list[dict]] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[tuple[torch.FloatTensor], DFineModelOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        batch_size, num_channels, height, width = pixel_values.shape
        device = pixel_values.device
        if pixel_mask is None:
            pixel_mask = torch.ones(((batch_size, height, width)), device=device)
        features = self.backbone(pixel_values, pixel_mask)
        proj_feats = [self.encoder_input_proj[level](source) for level, (source, mask) in enumerate(features)]
        if encoder_outputs is None:
            encoder_outputs = self.encoder(
                proj_feats,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
                return_dict=return_dict,
            )
        elif return_dict and not isinstance(encoder_outputs, BaseModelOutput):
            encoder_outputs = BaseModelOutput(
                last_hidden_state=encoder_outputs[0],
                hidden_states=encoder_outputs[1] if output_hidden_states else None,
                attentions=encoder_outputs[2]
                if len(encoder_outputs) > 2
                else encoder_outputs[1]
                if output_attentions
                else None,
            )
        sources = []
        for level, source in enumerate(encoder_outputs[0]):
            sources.append(self.decoder_input_proj[level](source))
        if self.config.num_feature_levels > len(sources):
            _len_sources = len(sources)
            sources.append(self.decoder_input_proj[_len_sources](encoder_outputs[0])[-1])
            for i in range(_len_sources + 1, self.config.num_feature_levels):
                sources.append(self.decoder_input_proj[i](encoder_outputs[0][-1]))
        source_flatten = []
        spatial_shapes_list = []
        spatial_shapes = torch.empty((len(sources), 2), device=device, dtype=torch.long)
        for level, source in enumerate(sources):
            height, width = source.shape[-2:]
            spatial_shapes[level, 0] = height
            spatial_shapes[level, 1] = width
            spatial_shapes_list.append((height, width))
            source = source.flatten(2).transpose(1, 2)
            source_flatten.append(source)
        source_flatten = torch.cat(source_flatten, 1)
        level_start_index = torch.cat((spatial_shapes.new_zeros((1,)), spatial_shapes.prod(1).cumsum(0)[:-1]))
        if self.training and self.config.num_denoising > 0 and labels is not None:
            (
                denoising_class,
                denoising_bbox_unact,
                attention_mask,
                denoising_meta_values,
            ) = get_contrastive_denoising_training_group(
                targets=labels,
                num_classes=self.config.num_labels,
                num_queries=self.config.num_queries,
                class_embed=self.denoising_class_embed,
                num_denoising_queries=self.config.num_denoising,
                label_noise_ratio=self.config.label_noise_ratio,
                box_noise_scale=self.config.box_noise_scale,
            )
        else:
            denoising_class, denoising_bbox_unact, attention_mask, denoising_meta_values = None, None, None, None
        batch_size = len(source_flatten)
        device = source_flatten.device
        dtype = source_flatten.dtype
        if self.training or self.config.anchor_image_size is None:
            spatial_shapes_tuple = tuple(spatial_shapes_list)
            anchors, valid_mask = self.generate_anchors(spatial_shapes_tuple, device=device, dtype=dtype)
        else:
            anchors, valid_mask = self.anchors, self.valid_mask
            anchors, valid_mask = anchors.to(device, dtype), valid_mask.to(device, dtype)
        memory = valid_mask.to(source_flatten.dtype) * source_flatten
        output_memory = self.enc_output(memory)
        enc_outputs_class = self.enc_score_head(output_memory)
        enc_outputs_coord_logits = self.enc_bbox_head(output_memory) + anchors
        _, topk_ind = torch.topk(enc_outputs_class.max(-1).values, self.config.num_queries, dim=1)
        reference_points_unact = enc_outputs_coord_logits.gather(
            dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, enc_outputs_coord_logits.shape[-1])
        )
        enc_topk_bboxes = F.sigmoid(reference_points_unact)
        if denoising_bbox_unact is not None:
            reference_points_unact = torch.concat([denoising_bbox_unact, reference_points_unact], 1)
        enc_topk_logits = enc_outputs_class.gather(
            dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, enc_outputs_class.shape[-1])
        )
        if self.config.learn_initial_query:
            target = self.weight_embedding.tile([batch_size, 1, 1])
        else:
            target = output_memory.gather(dim=1, index=topk_ind.unsqueeze(-1).repeat(1, 1, output_memory.shape[-1]))
            target = target.detach()
        if denoising_class is not None:
            target = torch.concat([denoising_class, target], 1)
        init_reference_points = reference_points_unact.detach()
        decoder_outputs = self.decoder(
            inputs_embeds=target,
            encoder_hidden_states=source_flatten,
            encoder_attention_mask=attention_mask,
            reference_points=init_reference_points,
            spatial_shapes=spatial_shapes,
            spatial_shapes_list=spatial_shapes_list,
            level_start_index=level_start_index,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        if not return_dict:
            enc_outputs = tuple(
                value
                for value in [enc_topk_logits, enc_topk_bboxes, enc_outputs_class, enc_outputs_coord_logits]
                if value is not None
            )
            dn_outputs = tuple(value if value is not None else None for value in [denoising_meta_values])
            tuple_outputs = decoder_outputs + encoder_outputs + (init_reference_points,) + enc_outputs + dn_outputs
            return tuple_outputs
        return DFineModelOutput(
            last_hidden_state=decoder_outputs.last_hidden_state,
            intermediate_hidden_states=decoder_outputs.intermediate_hidden_states,
            intermediate_logits=decoder_outputs.intermediate_logits,
            intermediate_reference_points=decoder_outputs.intermediate_reference_points,
            intermediate_predicted_corners=decoder_outputs.intermediate_predicted_corners,
            initial_reference_points=decoder_outputs.initial_reference_points,
            decoder_hidden_states=decoder_outputs.hidden_states,
            decoder_attentions=decoder_outputs.attentions,
            cross_attentions=decoder_outputs.cross_attentions,
            encoder_last_hidden_state=encoder_outputs.last_hidden_state,
            encoder_hidden_states=encoder_outputs.hidden_states,
            encoder_attentions=encoder_outputs.attentions,
            init_reference_points=init_reference_points,
            enc_topk_logits=enc_topk_logits,
            enc_topk_bboxes=enc_topk_bboxes,
            enc_outputs_class=enc_outputs_class,
            enc_outputs_coord_logits=enc_outputs_coord_logits,
            denoising_meta_values=denoising_meta_values,
        )
@dataclass
@auto_docstring(
)
class DFineObjectDetectionOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    loss_dict: Optional[dict] = None
    logits: Optional[torch.FloatTensor] = None
    pred_boxes: Optional[torch.FloatTensor] = None
    auxiliary_outputs: Optional[list[dict]] = None
    last_hidden_state: Optional[torch.FloatTensor] = None
    intermediate_hidden_states: Optional[torch.FloatTensor] = None
    intermediate_logits: Optional[torch.FloatTensor] = None
    intermediate_reference_points: Optional[torch.FloatTensor] = None
    intermediate_predicted_corners: Optional[torch.FloatTensor] = None
    initial_reference_points: Optional[torch.FloatTensor] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor]] = None
    init_reference_points: Optional[tuple[torch.FloatTensor]] = None
    enc_topk_logits: Optional[torch.FloatTensor] = None
    enc_topk_bboxes: Optional[torch.FloatTensor] = None
    enc_outputs_class: Optional[torch.FloatTensor] = None
    enc_outputs_coord_logits: Optional[torch.FloatTensor] = None
    denoising_meta_values: Optional[dict] = None
@auto_docstring(
)
class DFineForObjectDetection(DFinePreTrainedModel):
    _tied_weights_keys = ["bbox_embed", "class_embed"]
    _no_split_modules = None
    def __init__(self, config: DFineConfig):
        super().__init__(config)
        self.eval_idx = config.eval_idx if config.eval_idx >= 0 else config.decoder_layers + config.eval_idx
        self.model = DFineModel(config)
        scaled_dim = round(config.layer_scale * config.hidden_size)
        num_pred = config.decoder_layers
        self.class_embed = nn.ModuleList([nn.Linear(config.d_model, config.num_labels) for _ in range(num_pred)])
        self.bbox_embed = nn.ModuleList(
            [
                DFineMLP(config.hidden_size, config.hidden_size, 4 * (config.max_num_bins + 1), 3)
                for _ in range(self.eval_idx + 1)
            ]
            + [
                DFineMLP(scaled_dim, scaled_dim, 4 * (config.max_num_bins + 1), 3)
                for _ in range(config.decoder_layers - self.eval_idx - 1)
            ]
        )
        self.model.decoder.class_embed = self.class_embed
        self.model.decoder.bbox_embed = self.bbox_embed
        self.post_init()
    @torch.jit.unused
    def _set_aux_loss(self, outputs_class, outputs_coord):
        return [{"logits": a, "pred_boxes": b} for a, b in zip(outputs_class, outputs_coord)]
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.FloatTensor,
        pixel_mask: Optional[torch.LongTensor] = None,
        encoder_outputs: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        decoder_inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[list[dict]] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> Union[tuple[torch.FloatTensor], DFineObjectDetectionOutput]:
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.model(
            pixel_values,
            pixel_mask=pixel_mask,
            encoder_outputs=encoder_outputs,
            inputs_embeds=inputs_embeds,
            decoder_inputs_embeds=decoder_inputs_embeds,
            labels=labels,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        denoising_meta_values = (
            outputs.denoising_meta_values if return_dict else outputs[-1] if self.training else None
        )
        outputs_class = outputs.intermediate_logits if return_dict else outputs[2]
        outputs_coord = outputs.intermediate_reference_points if return_dict else outputs[3]
        predicted_corners = outputs.intermediate_predicted_corners if return_dict else outputs[4]
        initial_reference_points = outputs.initial_reference_points if return_dict else outputs[5]
        logits = outputs_class[:, -1]
        pred_boxes = outputs_coord[:, -1]
        loss, loss_dict, auxiliary_outputs, enc_topk_logits, enc_topk_bboxes = None, None, None, None, None
        if labels is not None:
            enc_topk_logits = outputs.enc_topk_logits if return_dict else outputs[-5]
            enc_topk_bboxes = outputs.enc_topk_bboxes if return_dict else outputs[-4]
            loss, loss_dict, auxiliary_outputs = self.loss_function(
                logits,
                labels,
                self.device,
                pred_boxes,
                self.config,
                outputs_class,
                outputs_coord,
                enc_topk_logits=enc_topk_logits,
                enc_topk_bboxes=enc_topk_bboxes,
                denoising_meta_values=denoising_meta_values,
                predicted_corners=predicted_corners,
                initial_reference_points=initial_reference_points,
                **kwargs,
            )
        if not return_dict:
            if auxiliary_outputs is not None:
                output = (logits, pred_boxes) + (auxiliary_outputs,) + outputs
            else:
                output = (logits, pred_boxes) + outputs
            return ((loss, loss_dict) + output) if loss is not None else output
        return DFineObjectDetectionOutput(
            loss=loss,
            loss_dict=loss_dict,
            logits=logits,
            pred_boxes=pred_boxes,
            auxiliary_outputs=auxiliary_outputs,
            last_hidden_state=outputs.last_hidden_state,
            intermediate_hidden_states=outputs.intermediate_hidden_states,
            intermediate_logits=outputs.intermediate_logits,
            intermediate_reference_points=outputs.intermediate_reference_points,
            intermediate_predicted_corners=outputs.intermediate_predicted_corners,
            initial_reference_points=outputs.initial_reference_points,
            decoder_hidden_states=outputs.decoder_hidden_states,
            decoder_attentions=outputs.decoder_attentions,
            cross_attentions=outputs.cross_attentions,
            encoder_last_hidden_state=outputs.encoder_last_hidden_state,
            encoder_hidden_states=outputs.encoder_hidden_states,
            encoder_attentions=outputs.encoder_attentions,
            init_reference_points=outputs.init_reference_points,
            enc_topk_logits=outputs.enc_topk_logits,
            enc_topk_bboxes=outputs.enc_topk_bboxes,
            enc_outputs_class=outputs.enc_outputs_class,
            enc_outputs_coord_logits=outputs.enc_outputs_coord_logits,
            denoising_meta_values=outputs.denoising_meta_values,
        )
class DFineMLPPredictionHead(nn.Module):
    def __init__(self, config, input_dim, d_model, output_dim, num_layers):
        super().__init__()
        self.num_layers = num_layers
        h = [d_model] * (num_layers - 1)
        self.layers = nn.ModuleList(nn.Linear(n, k) for n, k in zip([input_dim] + h, h + [output_dim]))
    def forward(self, x):
        for i, layer in enumerate(self.layers):
            x = nn.functional.relu(layer(x)) if i < self.num_layers - 1 else layer(x)
        return x
class DFineMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int, num_layers: int, act: str = "relu"):
        super().__init__()
        self.num_layers = num_layers
        hidden_dims = [hidden_dim] * (num_layers - 1)
        input_dims = [input_dim] + hidden_dims
        output_dims = hidden_dims + [output_dim]
        self.layers = nn.ModuleList(nn.Linear(in_dim, out_dim) for in_dim, out_dim in zip(input_dims, output_dims))
        self.act = ACT2CLS[act]()
    def forward(self, stat_features: torch.Tensor) -> torch.Tensor:
        for i, layer in enumerate(self.layers):
            stat_features = self.act(layer(stat_features)) if i < self.num_layers - 1 else layer(stat_features)
        return stat_features
class DFineLQE(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.top_prob_values = config.top_prob_values
        self.max_num_bins = config.max_num_bins
        self.reg_conf = DFineMLP(4 * (self.top_prob_values + 1), config.lqe_hidden_dim, 1, config.lqe_layers)
    def forward(self, scores: torch.Tensor, pred_corners: torch.Tensor) -> torch.Tensor:
        batch_size, length, _ = pred_corners.size()
        prob = F.softmax(pred_corners.reshape(batch_size, length, 4, self.max_num_bins + 1), dim=-1)
        prob_topk, _ = prob.topk(self.top_prob_values, dim=-1)
        stat = torch.cat([prob_topk, prob_topk.mean(dim=-1, keepdim=True)], dim=-1)
        quality_score = self.reg_conf(stat.reshape(batch_size, length, -1))
        scores = scores + quality_score
        return scores
class DFineConvNormLayer(nn.Module):
    def __init__(
        self,
        config: DFineConfig,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        stride: int,
        groups: int = 1,
        padding: Optional[int] = None,
        activation: Optional[str] = None,
    ):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            groups=groups,
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
class DFineRepVggBlock(nn.Module):
    def __init__(self, config: DFineConfig, in_channels: int, out_channels: int):
        super().__init__()
        activation = config.activation_function
        hidden_channels = in_channels
        self.conv1 = DFineConvNormLayer(config, hidden_channels, out_channels, 3, 1, padding=1)
        self.conv2 = DFineConvNormLayer(config, hidden_channels, out_channels, 1, 1, padding=0)
        self.activation = nn.Identity() if activation is None else ACT2CLS[activation]()
    def forward(self, x):
        y = self.conv1(x) + self.conv2(x)
        return self.activation(y)
class DFineCSPRepLayer(nn.Module):
    def __init__(
        self, config: DFineConfig, in_channels: int, out_channels: int, num_blocks: int, expansion: float = 1.0
    ):
        super().__init__()
        activation = config.activation_function
        hidden_channels = int(out_channels * expansion)
        self.conv1 = DFineConvNormLayer(config, in_channels, hidden_channels, 1, 1, activation=activation)
        self.conv2 = DFineConvNormLayer(config, in_channels, hidden_channels, 1, 1, activation=activation)
        self.bottlenecks = nn.ModuleList(
            [DFineRepVggBlock(config, hidden_channels, hidden_channels) for _ in range(num_blocks)]
        )
        if hidden_channels != out_channels:
            self.conv3 = DFineConvNormLayer(config, hidden_channels, out_channels, 1, 1, activation=activation)
        else:
            self.conv3 = nn.Identity()
    def forward(self, hidden_state: torch.Tensor) -> torch.Tensor:
        hidden_state_1 = self.conv1(hidden_state)
        for bottleneck in self.bottlenecks:
            hidden_state_1 = bottleneck(hidden_state_1)
        hidden_state_2 = self.conv2(hidden_state)
        hidden_state_3 = self.conv3(hidden_state_1 + hidden_state_2)
        return hidden_state_3
class DFineRepNCSPELAN4(nn.Module):
    def __init__(self, config: DFineConfig, act: str = "silu", numb_blocks: int = 3):
        super().__init__()
        conv1_dim = config.encoder_hidden_dim * 2
        conv2_dim = config.encoder_hidden_dim
        conv3_dim = config.encoder_hidden_dim * 2
        conv4_dim = round(config.hidden_expansion * config.encoder_hidden_dim // 2)
        self.conv_dim = conv3_dim // 2
        self.conv1 = DFineConvNormLayer(config, conv1_dim, conv3_dim, 1, 1, activation=act)
        self.csp_rep1 = DFineCSPRepLayer(config, conv3_dim // 2, conv4_dim, num_blocks=numb_blocks)
        self.conv2 = DFineConvNormLayer(config, conv4_dim, conv4_dim, 3, 1, activation=act)
        self.csp_rep2 = DFineCSPRepLayer(config, conv4_dim, conv4_dim, num_blocks=numb_blocks)
        self.conv3 = DFineConvNormLayer(config, conv4_dim, conv4_dim, 3, 1, activation=act)
        self.conv4 = DFineConvNormLayer(config, conv3_dim + (2 * conv4_dim), conv2_dim, 1, 1, activation=act)
    def forward(self, input_features: torch.Tensor) -> torch.Tensor:
        split_features = list(self.conv1(input_features).split((self.conv_dim, self.conv_dim), 1))
        branch1 = self.csp_rep1(split_features[-1])
        branch1 = self.conv2(branch1)
        branch2 = self.csp_rep2(branch1)
        branch2 = self.conv3(branch2)
        split_features.extend([branch1, branch2])
        merged_features = torch.cat(split_features, 1)
        merged_features = self.conv4(merged_features)
        return merged_features
class DFineSCDown(nn.Module):
    def __init__(self, config: DFineConfig, kernel_size: int, stride: int):
        super().__init__()
        self.conv1 = DFineConvNormLayer(config, config.encoder_hidden_dim, config.encoder_hidden_dim, 1, 1)
        self.conv2 = DFineConvNormLayer(
            config,
            config.encoder_hidden_dim,
            config.encoder_hidden_dim,
            kernel_size,
            stride,
            config.encoder_hidden_dim,
        )
    def forward(self, input_features: torch.Tensor) -> torch.Tensor:
        input_features = self.conv1(input_features)
        input_features = self.conv2(input_features)
        return input_features
class DFineEncoderLayer(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.normalize_before = config.normalize_before
        self.self_attn = DFineMultiheadAttention(
            embed_dim=config.encoder_hidden_dim,
            num_heads=config.num_attention_heads,
            dropout=config.dropout,
        )
        self.self_attn_layer_norm = nn.LayerNorm(config.encoder_hidden_dim, eps=config.layer_norm_eps)
        self.dropout = config.dropout
        self.activation_fn = ACT2FN[config.encoder_activation_function]
        self.activation_dropout = config.activation_dropout
        self.fc1 = nn.Linear(config.encoder_hidden_dim, config.encoder_ffn_dim)
        self.fc2 = nn.Linear(config.encoder_ffn_dim, config.encoder_hidden_dim)
        self.final_layer_norm = nn.LayerNorm(config.encoder_hidden_dim, eps=config.layer_norm_eps)
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: torch.Tensor,
        position_embeddings: Optional[torch.Tensor] = None,
        output_attentions: bool = False,
        **kwargs,
    ):
        residual = hidden_states
        if self.normalize_before:
            hidden_states = self.self_attn_layer_norm(hidden_states)
        hidden_states, attn_weights = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            position_embeddings=position_embeddings,
            output_attentions=output_attentions,
        )
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if not self.normalize_before:
            hidden_states = self.self_attn_layer_norm(hidden_states)
        if self.normalize_before:
            hidden_states = self.final_layer_norm(hidden_states)
        residual = hidden_states
        hidden_states = self.activation_fn(self.fc1(hidden_states))
        hidden_states = nn.functional.dropout(hidden_states, p=self.activation_dropout, training=self.training)
        hidden_states = self.fc2(hidden_states)
        hidden_states = nn.functional.dropout(hidden_states, p=self.dropout, training=self.training)
        hidden_states = residual + hidden_states
        if not self.normalize_before:
            hidden_states = self.final_layer_norm(hidden_states)
        if self.training:
            if torch.isinf(hidden_states).any() or torch.isnan(hidden_states).any():
                clamp_value = torch.finfo(hidden_states.dtype).max - 1000
                hidden_states = torch.clamp(hidden_states, min=-clamp_value, max=clamp_value)
        outputs = (hidden_states,)
        if output_attentions:
            outputs += (attn_weights,)
        return outputs
class DFineEncoder(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.layers = nn.ModuleList([DFineEncoderLayer(config) for _ in range(config.encoder_layers)])
    def forward(self, src, src_mask=None, pos_embed=None, output_attentions: bool = False) -> torch.Tensor:
        hidden_states = src
        for layer in self.layers:
            hidden_states = layer(
                hidden_states,
                attention_mask=src_mask,
                position_embeddings=pos_embed,
                output_attentions=output_attentions,
            )
        return hidden_states
class DFineHybridEncoder(nn.Module):
    def __init__(self, config: DFineConfig):
        super().__init__()
        self.config = config
        self.in_channels = config.encoder_in_channels
        self.num_fpn_stages = len(self.in_channels) - 1
        self.feat_strides = config.feat_strides
        self.encoder_hidden_dim = config.encoder_hidden_dim
        self.encode_proj_layers = config.encode_proj_layers
        self.positional_encoding_temperature = config.positional_encoding_temperature
        self.eval_size = config.eval_size
        self.out_channels = [self.encoder_hidden_dim for _ in self.in_channels]
        self.out_strides = self.feat_strides
        self.encoder = nn.ModuleList([DFineEncoder(config) for _ in range(len(self.encode_proj_layers))])
        self.lateral_convs = nn.ModuleList()
        self.fpn_blocks = nn.ModuleList()
        for _ in range(len(self.in_channels) - 1, 0, -1):
            lateral_layer = DFineConvNormLayer(config, self.encoder_hidden_dim, self.encoder_hidden_dim, 1, 1)
            self.lateral_convs.append(lateral_layer)
            num_blocks = round(3 * config.depth_mult)
            fpn_layer = DFineRepNCSPELAN4(config, numb_blocks=num_blocks)
            self.fpn_blocks.append(fpn_layer)
        self.downsample_convs = nn.ModuleList()
        self.pan_blocks = nn.ModuleList()
        for _ in range(len(self.in_channels) - 1):
            self.downsample_convs.append(DFineSCDown(config, 3, 2))
            num_blocks = round(3 * config.depth_mult)
            self.pan_blocks.append(DFineRepNCSPELAN4(config, numb_blocks=num_blocks))
    @staticmethod
    def build_2d_sincos_position_embedding(
        width, height, embed_dim=256, temperature=10000.0, device="cpu", dtype=torch.float32
    ):
        grid_w = torch.arange(torch_int(width), device=device).to(dtype)
        grid_h = torch.arange(torch_int(height), device=device).to(dtype)
        grid_w, grid_h = torch.meshgrid(grid_w, grid_h, indexing="ij")
        if embed_dim % 4 != 0:
            raise ValueError("Embed dimension must be divisible by 4 for 2D sin-cos position embedding")
        pos_dim = embed_dim // 4
        omega = torch.arange(pos_dim, device=device).to(dtype) / pos_dim
        omega = 1.0 / (temperature**omega)
        out_w = grid_w.flatten()[..., None] @ omega[None]
        out_h = grid_h.flatten()[..., None] @ omega[None]
        return torch.concat([out_w.sin(), out_w.cos(), out_h.sin(), out_h.cos()], dim=1)[None, :, :]
    def forward(
        self,
        inputs_embeds=None,
        attention_mask=None,
        position_embeddings=None,
        spatial_shapes=None,
        level_start_index=None,
        valid_ratios=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states = inputs_embeds
        encoder_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        if self.config.encoder_layers > 0:
            for i, enc_ind in enumerate(self.encode_proj_layers):
                if output_hidden_states:
                    encoder_states = encoder_states + (hidden_states[enc_ind],)
                height, width = hidden_states[enc_ind].shape[2:]
                src_flatten = hidden_states[enc_ind].flatten(2).permute(0, 2, 1)
                if self.training or self.eval_size is None:
                    pos_embed = self.build_2d_sincos_position_embedding(
                        width,
                        height,
                        self.encoder_hidden_dim,
                        self.positional_encoding_temperature,
                        device=src_flatten.device,
                        dtype=src_flatten.dtype,
                    )
                else:
                    pos_embed = None
                layer_outputs = self.encoder[i](
                    src_flatten,
                    pos_embed=pos_embed,
                    output_attentions=output_attentions,
                )
                hidden_states[enc_ind] = (
                    layer_outputs[0].permute(0, 2, 1).reshape(-1, self.encoder_hidden_dim, height, width).contiguous()
                )
                if output_attentions:
                    all_attentions = all_attentions + (layer_outputs[1],)
            if output_hidden_states:
                encoder_states = encoder_states + (hidden_states[enc_ind],)
        fpn_feature_maps = [hidden_states[-1]]
        for idx, (lateral_conv, fpn_block) in enumerate(zip(self.lateral_convs, self.fpn_blocks)):
            backbone_feature_map = hidden_states[self.num_fpn_stages - idx - 1]
            top_fpn_feature_map = fpn_feature_maps[-1]
            top_fpn_feature_map = lateral_conv(top_fpn_feature_map)
            fpn_feature_maps[-1] = top_fpn_feature_map
            top_fpn_feature_map = F.interpolate(top_fpn_feature_map, scale_factor=2.0, mode="nearest")
            fused_feature_map = torch.concat([top_fpn_feature_map, backbone_feature_map], dim=1)
            new_fpn_feature_map = fpn_block(fused_feature_map)
            fpn_feature_maps.append(new_fpn_feature_map)
        fpn_feature_maps = fpn_feature_maps[::-1]
        pan_feature_maps = [fpn_feature_maps[0]]
        for idx, (downsample_conv, pan_block) in enumerate(zip(self.downsample_convs, self.pan_blocks)):
            top_pan_feature_map = pan_feature_maps[-1]
            fpn_feature_map = fpn_feature_maps[idx + 1]
            downsampled_feature_map = downsample_conv(top_pan_feature_map)
            fused_feature_map = torch.concat([downsampled_feature_map, fpn_feature_map], dim=1)
            new_pan_feature_map = pan_block(fused_feature_map)
            pan_feature_maps.append(new_pan_feature_map)
        if not return_dict:
            return tuple(v for v in [pan_feature_maps, encoder_states, all_attentions] if v is not None)
        return BaseModelOutput(
            last_hidden_state=pan_feature_maps, hidden_states=encoder_states, attentions=all_attentions
        )
__all__ = ["DFineModel", "DFinePreTrainedModel", "DFineForObjectDetection"]