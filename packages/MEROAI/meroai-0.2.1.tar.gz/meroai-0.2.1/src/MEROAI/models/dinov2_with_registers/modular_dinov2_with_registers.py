from typing import Optional, Union
import torch
from torch import nn
from ....MEROAI.models.dinov2.modeling_dinov2 import (
    Dinov2Backbone,
    Dinov2Encoder,
    Dinov2ForImageClassification,
    Dinov2Model,
    Dinov2PatchEmbeddings,
    Dinov2PreTrainedModel,
)
from ...configuration_utils import PretrainedConfig
from ...modeling_outputs import BackboneOutput, BaseModelOutput, BaseModelOutputWithPooling, ImageClassifierOutput
from ...processing_utils import Unpack
from ...utils import MEROAIKwargs, logging, torch_int
from ...utils.backbone_utils import BackboneConfigMixin, get_aligned_output_features_output_indices
logger = logging.get_logger(__name__)
class Dinov2WithRegistersConfig(BackboneConfigMixin, PretrainedConfig):
    model_type = "dinov2_with_registers"
    def __init__(
        self,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        mlp_ratio=4,
        hidden_act="gelu",
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        initializer_range=0.02,
        layer_norm_eps=1e-6,
        image_size=224,
        patch_size=16,
        num_channels=3,
        qkv_bias=True,
        layerscale_value=1.0,
        drop_path_rate=0.0,
        use_swiglu_ffn=False,
        num_register_tokens=4,
        out_features=None,
        out_indices=None,
        apply_layernorm=True,
        reshape_hidden_states=True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.mlp_ratio = mlp_ratio
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.qkv_bias = qkv_bias
        self.layerscale_value = layerscale_value
        self.drop_path_rate = drop_path_rate
        self.use_swiglu_ffn = use_swiglu_ffn
        self.num_register_tokens = num_register_tokens
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, num_hidden_layers + 1)]
        self._out_features, self._out_indices = get_aligned_output_features_output_indices(
            out_features=out_features, out_indices=out_indices, stage_names=self.stage_names
        )
        self.apply_layernorm = apply_layernorm
        self.reshape_hidden_states = reshape_hidden_states
class Dinov2WithRegistersPatchEmbeddings(Dinov2PatchEmbeddings):
    pass
class Dinov2WithRegistersEmbeddings(nn.Module):
    def __init__(self, config: Dinov2WithRegistersConfig) -> None:
        super().__init__()
        self.cls_token = nn.Parameter(torch.randn(1, 1, config.hidden_size))
        self.mask_token = nn.Parameter(torch.zeros(1, config.hidden_size))
        self.register_tokens = nn.Parameter(torch.zeros(1, config.num_register_tokens, config.hidden_size))
        self.patch_embeddings = Dinov2WithRegistersPatchEmbeddings(config)
        num_patches = self.patch_embeddings.num_patches
        self.position_embeddings = nn.Parameter(torch.randn(1, num_patches + 1, config.hidden_size))
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.patch_size = config.patch_size
        self.config = config
    def interpolate_pos_encoding(self, embeddings: torch.Tensor, height: int, width: int) -> torch.Tensor:
        num_patches = embeddings.shape[1] - 1
        num_positions = self.position_embeddings.shape[1] - 1
        if not torch.jit.is_tracing() and num_patches == num_positions and height == width:
            return self.position_embeddings
        class_pos_embed = self.position_embeddings[:, 0]
        patch_pos_embed = self.position_embeddings[:, 1:]
        dim = embeddings.shape[-1]
        height = height // self.config.patch_size
        width = width // self.config.patch_size
        sqrt_num_positions = torch_int(num_positions**0.5)
        patch_pos_embed = patch_pos_embed.reshape(1, sqrt_num_positions, sqrt_num_positions, dim)
        patch_pos_embed = patch_pos_embed.permute(0, 3, 1, 2)
        target_dtype = patch_pos_embed.dtype
        patch_pos_embed = nn.functional.interpolate(
            patch_pos_embed.to(dtype=torch.float32),
            size=(torch_int(height), torch_int(width)),
            mode="bicubic",
            align_corners=False,
            antialias=True,
        ).to(dtype=target_dtype)
        if not torch.jit.is_tracing():
            if int(height) != patch_pos_embed.shape[-2] or int(width) != patch_pos_embed.shape[-1]:
                raise ValueError("Width or height does not match with the interpolated position embeddings")
        patch_pos_embed = patch_pos_embed.permute(0, 2, 3, 1).view(1, -1, dim)
        return torch.cat((class_pos_embed.unsqueeze(0), patch_pos_embed), dim=1)
    def forward(self, pixel_values: torch.Tensor, bool_masked_pos: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, _, height, width = pixel_values.shape
        target_dtype = self.patch_embeddings.projection.weight.dtype
        embeddings = self.patch_embeddings(pixel_values.to(dtype=target_dtype))
        if bool_masked_pos is not None:
            embeddings = torch.where(
                bool_masked_pos.unsqueeze(-1), self.mask_token.to(embeddings.dtype).unsqueeze(0), embeddings
            )
        cls_tokens = self.cls_token.expand(batch_size, -1, -1)
        embeddings = torch.cat((cls_tokens, embeddings), dim=1)
        embeddings = embeddings + self.interpolate_pos_encoding(embeddings, height, width)
        embeddings = torch.cat(
            (embeddings[:, :1], self.register_tokens.expand(embeddings.shape[0], -1, -1), embeddings[:, 1:]), dim=1
        )
        embeddings = self.dropout(embeddings)
        return embeddings
class Dinov2WithRegistersEncoder(Dinov2Encoder):
    pass
class Dinov2WithRegistersPreTrainedModel(Dinov2PreTrainedModel):
    def _init_weights(self, module: Union[nn.Linear, nn.Conv2d, nn.LayerNorm]) -> None:
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data = nn.init.trunc_normal_(
                module.weight.data.to(torch.float32), mean=0.0, std=self.config.initializer_range
            ).to(module.weight.dtype)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, Dinov2WithRegistersEmbeddings):
            module.position_embeddings.data = nn.init.trunc_normal_(
                module.position_embeddings.data.to(torch.float32),
                mean=0.0,
                std=self.config.initializer_range,
            ).to(module.position_embeddings.dtype)
            module.cls_token.data = nn.init.trunc_normal_(
                module.cls_token.data.to(torch.float32),
                mean=0.0,
                std=self.config.initializer_range,
            ).to(module.cls_token.dtype)
            module.mask_token.data.zero_()
            module.register_tokens.data.zero_()
        elif isinstance(module, Dinov2WithRegistersLayerScale):
            module.lambda1.data.fill_(self.config.layerscale_value)
class Dinov2WithRegistersModel(Dinov2Model):
    pass
class Dinov2WithRegistersForImageClassification(Dinov2ForImageClassification):
    def forward(
        self,
        pixel_values: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        labels: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> ImageClassifierOutput:
        outputs: BaseModelOutputWithPooling = self.dinov2_with_registers(pixel_values, head_mask=head_mask, **kwargs)
        sequence_output = outputs.last_hidden_state
        cls_token = sequence_output[:, 0]
        patch_tokens = sequence_output[:, 1 + self.config.num_register_tokens :]
        linear_input = torch.cat([cls_token, patch_tokens.mean(dim=1)], dim=1)
        logits = self.classifier(linear_input)
        loss = None
        if labels is not None:
            loss = self.loss_function(labels, logits, self.config, **kwargs)
        return ImageClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
class Dinov2WithRegistersBackbone(Dinov2Backbone):
    def __init__(self, config):
        super().__init__(config)
        super()._init_backbone(config)
        self.num_register_tokens = config.num_register_tokens
        self.num_features = [config.hidden_size for _ in range(config.num_hidden_layers + 1)]
        self.embeddings = Dinov2WithRegistersEmbeddings(config)
        self.encoder = Dinov2WithRegistersEncoder(config)
        self.layernorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)
        self.post_init()
    def get_input_embeddings(self) -> Dinov2WithRegistersPatchEmbeddings:
        return self.embeddings.patch_embeddings
    def forward(
        self,
        pixel_values: torch.Tensor,
        output_hidden_states: Optional[bool] = None,
        **kwargs,
    ) -> BackboneOutput:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        embedding_output = self.embeddings(pixel_values)
        output: BaseModelOutput = self.encoder(embedding_output, output_hidden_states=True)
        hidden_states = output.hidden_states
        feature_maps = []
        for stage, hidden_state in zip(self.stage_names, hidden_states):
            if stage in self.out_features:
                if self.config.apply_layernorm:
                    hidden_state = self.layernorm(hidden_state)
                if self.config.reshape_hidden_states:
                    hidden_state = hidden_state[:, 1 + self.num_register_tokens :]
                    batch_size, _, height, width = pixel_values.shape
                    patch_size = self.config.patch_size
                    hidden_state = hidden_state.reshape(batch_size, height // patch_size, width // patch_size, -1)
                    hidden_state = hidden_state.permute(0, 3, 1, 2).contiguous()
                feature_maps.append(hidden_state)
        return BackboneOutput(
            feature_maps=tuple(feature_maps),
            hidden_states=hidden_states if output_hidden_states else None,
        )
__all__ = [
    "Dinov2WithRegistersConfig",
    "Dinov2WithRegistersPreTrainedModel",
    "Dinov2WithRegistersModel",
    "Dinov2WithRegistersForImageClassification",
    "Dinov2WithRegistersBackbone",
]