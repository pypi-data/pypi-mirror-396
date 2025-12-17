from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class DINOv3ConvNextConfig(PretrainedConfig):
    model_type = "dinov3_convnext"
    def __init__(
        self,
        num_channels: int = 3,
        hidden_sizes: Optional[list[int]] = None,
        depths: Optional[list[int]] = None,
        hidden_act: str = "gelu",
        initializer_range: float = 0.02,
        layer_norm_eps: float = 1e-6,
        layer_scale_init_value: float = 1e-6,
        drop_path_rate: float = 0.0,
        image_size: int = 224,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.num_channels = num_channels
        self.hidden_sizes = [96, 192, 384, 768] if hidden_sizes is None else hidden_sizes
        self.depths = [3, 3, 9, 3] if depths is None else depths
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.layer_norm_eps = layer_norm_eps
        self.layer_scale_init_value = layer_scale_init_value
        self.drop_path_rate = drop_path_rate
        self.image_size = image_size
    @property
    def num_stages(self) -> int:
        return len(self.hidden_sizes)
__all__ = ["DINOv3ConvNextConfig"]