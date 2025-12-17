import math
from typing import Any, Optional
import torch
import torch.nn.functional as F
import torch.nn.init as init
from torch import nn
from ...activations import ACT2CLS
from ...configuration_utils import PretrainedConfig
from ...image_transforms import corners_to_center_format
from ...utils import is_torchdynamo_compiling, logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
from ..rt_detr.modeling_rt_detr import (
    RTDetrConvNormLayer,
    RTDetrDecoder,
    RTDetrDecoderLayer,
    RTDetrDecoderOutput,
    RTDetrEncoder,
    RTDetrForObjectDetection,
    RTDetrHybridEncoder,
    RTDetrMLPPredictionHead,
    RTDetrModel,
    RTDetrPreTrainedModel,
    RTDetrRepVggBlock,
    inverse_sigmoid,
)
from ..rt_detr_v2.modeling_rt_detr_v2 import multi_scale_deformable_attention_v2
logger = logging.get_logger(__name__)
class DFineConfig(PretrainedConfig):
    model_type = "d_fine"
    layer_types = ["basic", "bottleneck"]
    attribute_map = {
        "hidden_size": "d_model",
        "num_attention_heads": "encoder_attention_heads",
    }
    def __init__(
        self,
        initializer_range=0.01,
        initializer_bias_prior_prob=None,
        layer_norm_eps=1e-5,
        batch_norm_eps=1e-5,
        backbone_config=None,
        backbone=None,
        use_pretrained_backbone=False,
        use_timm_backbone=False,
        freeze_backbone_batch_norms=True,
        backbone_kwargs=None,
        encoder_hidden_dim=256,
        encoder_in_channels=[512, 1024, 2048],
        feat_strides=[8, 16, 32],
        encoder_layers=1,
        encoder_ffn_dim=1024,
        encoder_attention_heads=8,
        dropout=0.0,
        activation_dropout=0.0,
        encode_proj_layers=[2],
        positional_encoding_temperature=10000,
        encoder_activation_function="gelu",
        activation_function="silu",
        eval_size=None,
        normalize_before=False,
        hidden_expansion=1.0,
        d_model=256,
        num_queries=300,
        decoder_in_channels=[256, 256, 256],
        decoder_ffn_dim=1024,
        num_feature_levels=3,
        decoder_n_points=4,
        decoder_layers=6,
        decoder_attention_heads=8,
        decoder_activation_function="relu",
        attention_dropout=0.0,
        num_denoising=100,
        label_noise_ratio=0.5,
        box_noise_scale=1.0,
        learn_initial_query=False,
        anchor_image_size=None,
        with_box_refine=True,
        is_encoder_decoder=True,
        matcher_alpha=0.25,
        matcher_gamma=2.0,
        matcher_class_cost=2.0,
        matcher_bbox_cost=5.0,
        matcher_giou_cost=2.0,
        use_focal_loss=True,
        auxiliary_loss=True,
        focal_loss_alpha=0.75,
        focal_loss_gamma=2.0,
        weight_loss_vfl=1.0,
        weight_loss_bbox=5.0,
        weight_loss_giou=2.0,
        weight_loss_fgl=0.15,
        weight_loss_ddf=1.5,
        eos_coefficient=1e-4,
        eval_idx=-1,
        layer_scale=1,
        max_num_bins=32,
        reg_scale=4.0,
        depth_mult=1.0,
        top_prob_values=4,
        lqe_hidden_dim=64,
        lqe_layers=2,
        decoder_offset_scale=0.5,
        decoder_method="default",
        up=0.5,
        **kwargs,
    ):
        self.initializer_range = initializer_range
        self.initializer_bias_prior_prob = initializer_bias_prior_prob
        self.layer_norm_eps = layer_norm_eps
        self.batch_norm_eps = batch_norm_eps
        if backbone_config is None and backbone is None:
            logger.info(
                "`backbone_config` and `backbone` are `None`. Initializing the config with the default `HGNet-V2` backbone."
            )
            backbone_model_type = "hgnet_v2"
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class(
                num_channels=3,
                embedding_size=64,
                hidden_sizes=[256, 512, 1024, 2048],
                depths=[3, 4, 6, 3],
                layer_type="bottleneck",
                hidden_act="relu",
                downsample_in_first_stage=False,
                downsample_in_bottleneck=False,
                out_features=None,
                out_indices=[2, 3, 4],
            )
        elif isinstance(backbone_config, dict):
            backbone_model_type = backbone_config.pop("model_type")
            config_class = CONFIG_MAPPING[backbone_model_type]
            backbone_config = config_class.from_dict(backbone_config)
        verify_backbone_config_arguments(
            use_timm_backbone=use_timm_backbone,
            use_pretrained_backbone=use_pretrained_backbone,
            backbone=backbone,
            backbone_config=backbone_config,
            backbone_kwargs=backbone_kwargs,
        )
        self.backbone_config = backbone_config
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.use_timm_backbone = use_timm_backbone
        self.freeze_backbone_batch_norms = freeze_backbone_batch_norms
        self.backbone_kwargs = backbone_kwargs
        self.encoder_hidden_dim = encoder_hidden_dim
        self.encoder_in_channels = encoder_in_channels
        self.feat_strides = feat_strides
        self.encoder_attention_heads = encoder_attention_heads
        self.encoder_ffn_dim = encoder_ffn_dim
        self.dropout = dropout
        self.activation_dropout = activation_dropout
        self.encode_proj_layers = encode_proj_layers
        self.encoder_layers = encoder_layers
        self.positional_encoding_temperature = positional_encoding_temperature
        self.eval_size = eval_size
        self.normalize_before = normalize_before
        self.encoder_activation_function = encoder_activation_function
        self.activation_function = activation_function
        self.hidden_expansion = hidden_expansion
        self.d_model = d_model
        self.num_queries = num_queries
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_in_channels = decoder_in_channels
        self.num_feature_levels = num_feature_levels
        self.decoder_n_points = decoder_n_points
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.decoder_activation_function = decoder_activation_function
        self.attention_dropout = attention_dropout
        self.num_denoising = num_denoising
        self.label_noise_ratio = label_noise_ratio
        self.box_noise_scale = box_noise_scale
        self.learn_initial_query = learn_initial_query
        self.anchor_image_size = anchor_image_size
        self.auxiliary_loss = auxiliary_loss
        self.with_box_refine = with_box_refine
        self.matcher_alpha = matcher_alpha
        self.matcher_gamma = matcher_gamma
        self.matcher_class_cost = matcher_class_cost
        self.matcher_bbox_cost = matcher_bbox_cost
        self.matcher_giou_cost = matcher_giou_cost
        self.use_focal_loss = use_focal_loss
        self.focal_loss_alpha = focal_loss_alpha
        self.focal_loss_gamma = focal_loss_gamma
        self.weight_loss_vfl = weight_loss_vfl
        self.weight_loss_bbox = weight_loss_bbox
        self.weight_loss_giou = weight_loss_giou
        self.weight_loss_fgl = weight_loss_fgl
        self.weight_loss_ddf = weight_loss_ddf
        self.eos_coefficient = eos_coefficient
        self.eval_idx = eval_idx
        self.layer_scale = layer_scale
        self.max_num_bins = max_num_bins
        self.reg_scale = reg_scale
        self.depth_mult = depth_mult
        self.decoder_offset_scale = decoder_offset_scale
        self.decoder_method = decoder_method
        self.top_prob_values = top_prob_values
        self.lqe_hidden_dim = lqe_hidden_dim
        self.lqe_layers = lqe_layers
        self.up = up
        if isinstance(self.decoder_n_points, list):
            if len(self.decoder_n_points) != self.num_feature_levels:
                raise ValueError(
                    f"Length of decoder_n_points list ({len(self.decoder_n_points)}) must match num_feature_levels ({self.num_feature_levels})."
                )
        head_dim = self.d_model // self.decoder_attention_heads
        if head_dim * self.decoder_attention_heads != self.d_model:
            raise ValueError(
                f"Embedded dimension {self.d_model} must be divisible by decoder_attention_heads {self.decoder_attention_heads}"
            )
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
    @property
    def num_attention_heads(self) -> int:
        return self.encoder_attention_heads
    @property
    def hidden_size(self) -> int:
        return self.d_model
    @property
    def sub_configs(self):
        return (
            {"backbone_config": type(self.backbone_config)}
            if getattr(self, "backbone_config", None) is not None
            else {}
        )
    @classmethod
    def from_backbone_configs(cls, backbone_config: PretrainedConfig, **kwargs):
        return cls(
            backbone_config=backbone_config,
            **kwargs,
        )
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
class DFineDecoderLayer(RTDetrDecoderLayer):
    def __init__(self, config: DFineConfig):
        super().__init__(config)
        self.encoder_attn = DFineMultiscaleDeformableAttention(config=config)
        self.gateway = DFineGate(config.d_model)
        del self.encoder_attn_layer_norm
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
class DFinePreTrainedModel(RTDetrPreTrainedModel):
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
class DFineDecoderOutput(RTDetrDecoderOutput):
    pass
class DFineDecoder(RTDetrDecoder):
    def __init__(self, config: DFineConfig):
        self.eval_idx = config.eval_idx if config.eval_idx >= 0 else config.decoder_layers + config.eval_idx
        super().__init__(config=config)
        self.reg_scale = nn.Parameter(torch.tensor([config.reg_scale]), requires_grad=False)
        self.max_num_bins = config.max_num_bins
        self.d_model = config.d_model
        self.layer_scale = config.layer_scale
        self.pre_bbox_head = DFineMLP(config.hidden_size, config.hidden_size, 4, 3)
        self.integral = DFineIntegral(config)
        self.num_head = config.decoder_attention_heads
        self.up = nn.Parameter(torch.tensor([config.up]), requires_grad=False)
        self.lqe_layers = nn.ModuleList([DFineLQE(config) for _ in range(config.decoder_layers)])
        self.layers = nn.ModuleList(
            [DFineDecoderLayer(config) for _ in range(config.decoder_layers)]
            + [DFineDecoderLayer(config) for _ in range(config.decoder_layers - self.eval_idx - 1)]
        )
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
class DFineModel(RTDetrModel):
    def __init__(self, config: DFineConfig):
        super().__init__(config)
        del self.decoder_input_proj
        self.encoder = DFineHybridEncoder(config=config)
        num_backbone_outs = len(config.decoder_in_channels)
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
        self.decoder = DFineDecoder(config)
class DFineForObjectDetection(RTDetrForObjectDetection, DFinePreTrainedModel):
    def __init__(self, config: DFineConfig):
        DFinePreTrainedModel.__init__(self, config)
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
    def forward(**super_kwargs):
        super().forward(**super_kwargs)
def weighting_function(max_num_bins: int, up: torch.Tensor, reg_scale: int) -> torch.Tensor:
    upper_bound1 = abs(up[0]) * abs(reg_scale)
    upper_bound2 = abs(up[0]) * abs(reg_scale) * 2
    step = (upper_bound1 + 1) ** (2 / (max_num_bins - 2))
    left_values = [-((step) ** i) + 1 for i in range(max_num_bins // 2 - 1, 0, -1)]
    right_values = [(step) ** i - 1 for i in range(1, max_num_bins // 2)]
    values = [-upper_bound2] + left_values + [torch.zeros_like(up[0][None])] + right_values + [upper_bound2]
    values = torch.cat(values, 0)
    return values
class DFineMLPPredictionHead(RTDetrMLPPredictionHead):
    pass
def distance2bbox(points, distance: torch.Tensor, reg_scale: float) -> torch.Tensor:
    reg_scale = abs(reg_scale)
    top_left_x = points[..., 0] - (0.5 * reg_scale + distance[..., 0]) * (points[..., 2] / reg_scale)
    top_left_y = points[..., 1] - (0.5 * reg_scale + distance[..., 1]) * (points[..., 3] / reg_scale)
    bottom_right_x = points[..., 0] + (0.5 * reg_scale + distance[..., 2]) * (points[..., 2] / reg_scale)
    bottom_right_y = points[..., 1] + (0.5 * reg_scale + distance[..., 3]) * (points[..., 3] / reg_scale)
    bboxes = torch.stack([top_left_x, top_left_y, bottom_right_x, bottom_right_y], -1)
    return corners_to_center_format(bboxes)
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
class DFineConvNormLayer(RTDetrConvNormLayer):
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
        super().__init__(config, in_channels, out_channels, kernel_size, stride, padding=None, activation=activation)
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            groups=groups,
            padding=(kernel_size - 1) // 2 if padding is None else padding,
            bias=False,
        )
class DFineRepVggBlock(RTDetrRepVggBlock):
    def __init__(self, config: DFineConfig, in_channels: int, out_channels: int):
        super().__init__(config)
        hidden_channels = in_channels
        self.conv1 = DFineConvNormLayer(config, hidden_channels, out_channels, 3, 1, padding=1)
        self.conv2 = DFineConvNormLayer(config, hidden_channels, out_channels, 1, 1, padding=0)
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
class DFineEncoder(RTDetrEncoder):
    pass
class DFineHybridEncoder(RTDetrHybridEncoder):
    def __init__(self, config: DFineConfig):
        nn.Module.__init__(self)
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
__all__ = [
    "DFineConfig",
    "DFineModel",
    "DFinePreTrainedModel",
    "DFineForObjectDetection",
]