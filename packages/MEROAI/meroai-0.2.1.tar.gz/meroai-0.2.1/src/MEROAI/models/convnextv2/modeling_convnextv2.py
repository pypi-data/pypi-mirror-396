from typing import Optional
import torch
from torch import nn
from ...activations import ACT2FN
from ...modeling_outputs import (
    BackboneOutput,
    BaseModelOutputWithNoAttention,
    BaseModelOutputWithPoolingAndNoAttention,
    ImageClassifierOutputWithNoAttention,
)
from ...modeling_utils import PreTrainedModel
from ...utils import auto_docstring, logging
from ...utils.backbone_utils import BackboneMixin
from ...utils.generic import can_return_tuple
from .configuration_convnextv2 import ConvNextV2Config
logger = logging.get_logger(__name__)
def drop_path(input: torch.Tensor, drop_prob: float = 0.0, training: bool = False) -> torch.Tensor:
    if drop_prob == 0.0 or not training:
        return input
    keep_prob = 1 - drop_prob
    shape = (input.shape[0],) + (1,) * (input.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=input.dtype, device=input.device)
    random_tensor.floor_()
    output = input.div(keep_prob) * random_tensor
    return output
class ConvNextV2DropPath(nn.Module):
    def __init__(self, drop_prob: Optional[float] = None) -> None:
        super().__init__()
        self.drop_prob = drop_prob
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        return drop_path(hidden_states, self.drop_prob, self.training)
    def extra_repr(self) -> str:
        return f"p={self.drop_prob}"
class ConvNextV2GRN(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.weight = nn.Parameter(torch.zeros(1, 1, 1, dim))
        self.bias = nn.Parameter(torch.zeros(1, 1, 1, dim))
    def forward(self, hidden_states: torch.FloatTensor) -> torch.FloatTensor:
        global_features = torch.linalg.vector_norm(hidden_states, ord=2, dim=(1, 2), keepdim=True)
        norm_features = global_features / (global_features.mean(dim=-1, keepdim=True) + 1e-6)
        hidden_states = self.weight * (hidden_states * norm_features) + self.bias + hidden_states
        return hidden_states
class ConvNextV2LayerNorm(nn.LayerNorm):
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
class ConvNextV2Embeddings(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.patch_embeddings = nn.Conv2d(
            config.num_channels, config.hidden_sizes[0], kernel_size=config.patch_size, stride=config.patch_size
        )
        self.layernorm = ConvNextV2LayerNorm(config.hidden_sizes[0], eps=1e-6, data_format="channels_first")
        self.num_channels = config.num_channels
    def forward(self, pixel_values: torch.FloatTensor) -> torch.Tensor:
        num_channels = pixel_values.shape[1]
        if num_channels != self.num_channels:
            raise ValueError(
                "Make sure that the channel dimension of the pixel values match with the one set in the configuration."
            )
        embeddings = self.patch_embeddings(pixel_values)
        embeddings = self.layernorm(embeddings)
        return embeddings
class ConvNextV2Layer(nn.Module):
    def __init__(self, config, dim, drop_path=0):
        super().__init__()
        self.dwconv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.layernorm = ConvNextV2LayerNorm(dim, eps=1e-6)
        self.pwconv1 = nn.Linear(dim, 4 * dim)
        self.act = ACT2FN[config.hidden_act]
        self.grn = ConvNextV2GRN(4 * dim)
        self.pwconv2 = nn.Linear(4 * dim, dim)
        self.drop_path = ConvNextV2DropPath(drop_path) if drop_path > 0.0 else nn.Identity()
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        residual = features
        features = self.dwconv(features)
        features = features.permute(0, 2, 3, 1)
        features = self.layernorm(features)
        features = self.pwconv1(features)
        features = self.act(features)
        features = self.grn(features)
        features = self.pwconv2(features)
        features = features.permute(0, 3, 1, 2)
        features = residual + self.drop_path(features)
        return features
class ConvNextV2Stage(nn.Module):
    def __init__(self, config, in_channels, out_channels, kernel_size=2, stride=2, depth=2, drop_path_rates=None):
        super().__init__()
        if in_channels != out_channels or stride > 1:
            self.downsampling_layer = nn.ModuleList(
                [
                    ConvNextV2LayerNorm(in_channels, eps=1e-6, data_format="channels_first"),
                    nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, stride=stride),
                ]
            )
        else:
            self.downsampling_layer = nn.ModuleList()
        drop_path_rates = drop_path_rates or [0.0] * depth
        self.layers = nn.ModuleList(
            [ConvNextV2Layer(config, dim=out_channels, drop_path=drop_path_rates[j]) for j in range(depth)]
        )
    def forward(self, features: torch.Tensor) -> torch.Tensor:
        for layer in self.downsampling_layer:
            features = layer(features)
        for layer in self.layers:
            features = layer(features)
        return features
class ConvNextV2Encoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.stages = nn.ModuleList()
        drop_path_rates = [
            x.tolist()
            for x in torch.linspace(0, config.drop_path_rate, sum(config.depths), device="cpu").split(config.depths)
        ]
        prev_chs = config.hidden_sizes[0]
        for i in range(config.num_stages):
            out_chs = config.hidden_sizes[i]
            stage = ConvNextV2Stage(
                config,
                in_channels=prev_chs,
                out_channels=out_chs,
                stride=2 if i > 0 else 1,
                depth=config.depths[i],
                drop_path_rates=drop_path_rates[i],
            )
            self.stages.append(stage)
            prev_chs = out_chs
    def forward(
        self, hidden_states: torch.Tensor, output_hidden_states: Optional[bool] = False
    ) -> BaseModelOutputWithNoAttention:
        all_hidden_states = [hidden_states] if output_hidden_states else None
        for layer_module in self.stages:
            hidden_states = layer_module(hidden_states)
            if all_hidden_states is not None:
                all_hidden_states.append(hidden_states)
        return BaseModelOutputWithNoAttention(last_hidden_state=hidden_states, hidden_states=all_hidden_states)
@auto_docstring
class ConvNextV2PreTrainedModel(PreTrainedModel):
    config: ConvNextV2Config
    base_model_prefix = "convnextv2"
    main_input_name = "pixel_values"
    _no_split_modules = ["ConvNextV2Layer"]
    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, (nn.LayerNorm, ConvNextV2LayerNorm)):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
        elif isinstance(module, ConvNextV2GRN):
            module.weight.data.zero_()
            module.bias.data.zero_()
@auto_docstring
class ConvNextV2Model(ConvNextV2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.embeddings = ConvNextV2Embeddings(config)
        self.encoder = ConvNextV2Encoder(config)
        self.layernorm = nn.LayerNorm(config.hidden_sizes[-1], eps=config.layer_norm_eps)
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self, pixel_values: Optional[torch.FloatTensor] = None, output_hidden_states: Optional[bool] = None
    ) -> BaseModelOutputWithPoolingAndNoAttention:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        if pixel_values is None:
            raise ValueError("You have to specify pixel_values")
        embedding_output = self.embeddings(pixel_values)
        encoder_outputs: BaseModelOutputWithNoAttention = self.encoder(
            embedding_output, output_hidden_states=output_hidden_states
        )
        last_hidden_state = encoder_outputs.last_hidden_state
        pooled_output = self.layernorm(last_hidden_state.mean([-2, -1]))
        return BaseModelOutputWithPoolingAndNoAttention(
            last_hidden_state=last_hidden_state,
            pooler_output=pooled_output,
            hidden_states=encoder_outputs.hidden_states,
        )
@auto_docstring(
)
class ConvNextV2ForImageClassification(ConvNextV2PreTrainedModel):
    accepts_loss_kwargs = False
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = config.num_labels
        self.convnextv2 = ConvNextV2Model(config)
        if config.num_labels > 0:
            self.classifier = nn.Linear(config.hidden_sizes[-1], config.num_labels)
        else:
            self.classifier = nn.Identity()
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self, pixel_values: Optional[torch.FloatTensor] = None, labels: Optional[torch.LongTensor] = None, **kwargs
    ) -> ImageClassifierOutputWithNoAttention:
        outputs: BaseModelOutputWithPoolingAndNoAttention = self.convnextv2(pixel_values, **kwargs)
        pooled_output = outputs.pooler_output
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            loss = self.loss_function(labels=labels, pooled_logits=logits, config=self.config)
        return ImageClassifierOutputWithNoAttention(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
        )
@auto_docstring(
)
class ConvNextV2Backbone(ConvNextV2PreTrainedModel, BackboneMixin):
    has_attentions = False
    def __init__(self, config):
        super().__init__(config)
        super()._init_backbone(config)
        self.embeddings = ConvNextV2Embeddings(config)
        self.encoder = ConvNextV2Encoder(config)
        self.num_features = [config.hidden_sizes[0]] + config.hidden_sizes
        hidden_states_norms = {}
        for stage, num_channels in zip(self._out_features, self.channels):
            hidden_states_norms[stage] = ConvNextV2LayerNorm(num_channels, data_format="channels_first")
        self.hidden_states_norms = nn.ModuleDict(hidden_states_norms)
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        pixel_values: torch.Tensor,
        output_hidden_states: Optional[bool] = None,
    ) -> BackboneOutput:
        if output_hidden_states is None:
            output_hidden_states = self.config.output_hidden_states
        embedding_output = self.embeddings(pixel_values)
        outputs: BaseModelOutputWithPoolingAndNoAttention = self.encoder(embedding_output, output_hidden_states=True)
        hidden_states = outputs.hidden_states
        feature_maps = []
        for stage, hidden_state in zip(self.stage_names, hidden_states):
            if stage in self.out_features:
                hidden_state = self.hidden_states_norms[stage](hidden_state)
                feature_maps.append(hidden_state)
        return BackboneOutput(
            feature_maps=tuple(feature_maps),
            hidden_states=hidden_states if output_hidden_states else None,
        )
__all__ = ["ConvNextV2ForImageClassification", "ConvNextV2Model", "ConvNextV2PreTrainedModel", "ConvNextV2Backbone"]