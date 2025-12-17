from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...modeling_rope_utils import rope_config_validation
class EfficientLoFTRConfig(PretrainedConfig):
    model_type = "efficientloftr"
    def __init__(
        self,
        stage_num_blocks: Optional[list[int]] = None,
        out_features: Optional[list[int]] = None,
        stage_stride: Optional[list[int]] = None,
        hidden_size: int = 256,
        activation_function: str = "relu",
        q_aggregation_kernel_size: int = 4,
        kv_aggregation_kernel_size: int = 4,
        q_aggregation_stride: int = 4,
        kv_aggregation_stride: int = 4,
        num_attention_layers: int = 4,
        num_attention_heads: int = 8,
        attention_dropout: float = 0.0,
        attention_bias: bool = False,
        mlp_activation_function: str = "leaky_relu",
        coarse_matching_skip_softmax: bool = False,
        coarse_matching_threshold: float = 0.2,
        coarse_matching_temperature: float = 0.1,
        coarse_matching_border_removal: int = 2,
        fine_kernel_size: int = 8,
        batch_norm_eps: float = 1e-5,
        rope_theta: float = 10000.0,
        partial_rotary_factor: float = 4.0,
        rope_scaling: Optional[dict] = None,
        fine_matching_slice_dim: int = 8,
        fine_matching_regress_temperature: float = 10.0,
        initializer_range: float = 0.02,
        **kwargs,
    ):
        self.stage_num_blocks = stage_num_blocks if stage_num_blocks is not None else [1, 2, 4, 14]
        self.stage_stride = stage_stride if stage_stride is not None else [2, 1, 2, 2]
        self.out_features = out_features if out_features is not None else [64, 64, 128, 256]
        self.stage_in_channels = [1] + self.out_features[:-1]
        self.stage_block_stride = [
            [stride] + [1] * (num_blocks - 1) for stride, num_blocks in zip(self.stage_stride, self.stage_num_blocks)
        ]
        self.stage_block_out_channels = [
            [self.out_features[stage_idx]] * num_blocks for stage_idx, num_blocks in enumerate(self.stage_num_blocks)
        ]
        self.stage_block_in_channels = [
            [self.stage_in_channels[stage_idx]] + self.stage_block_out_channels[stage_idx][:-1]
            for stage_idx in range(len(self.stage_num_blocks))
        ]
        self.fine_fusion_dims = list(reversed(self.out_features))[:-1]
        self.hidden_size = hidden_size
        if self.hidden_size != self.out_features[-1]:
            raise ValueError(
                f"hidden_size should be equal to the last value in out_features. hidden_size = {self.hidden_size}, out_features = {self.out_features[-1]}"
            )
        self.activation_function = activation_function
        self.q_aggregation_kernel_size = q_aggregation_kernel_size
        self.kv_aggregation_kernel_size = kv_aggregation_kernel_size
        self.q_aggregation_stride = q_aggregation_stride
        self.kv_aggregation_stride = kv_aggregation_stride
        self.num_attention_layers = num_attention_layers
        self.num_attention_heads = num_attention_heads
        self.attention_dropout = attention_dropout
        self.attention_bias = attention_bias
        self.intermediate_size = self.hidden_size * 2
        self.mlp_activation_function = mlp_activation_function
        self.coarse_matching_skip_softmax = coarse_matching_skip_softmax
        self.coarse_matching_threshold = coarse_matching_threshold
        self.coarse_matching_temperature = coarse_matching_temperature
        self.coarse_matching_border_removal = coarse_matching_border_removal
        self.fine_kernel_size = fine_kernel_size
        self.batch_norm_eps = batch_norm_eps
        self.fine_matching_slice_dim = fine_matching_slice_dim
        self.fine_matching_regress_temperature = fine_matching_regress_temperature
        self.num_key_value_heads = num_attention_heads
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling if rope_scaling is not None else {"rope_type": "default"}
        self.partial_rotary_factor = partial_rotary_factor
        rope_config_validation(self)
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
__all__ = ["EfficientLoFTRConfig"]