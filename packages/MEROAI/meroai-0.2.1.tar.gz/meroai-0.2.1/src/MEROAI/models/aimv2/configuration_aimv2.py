from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class Aimv2VisionConfig(PretrainedConfig):
    model_type = "aimv2_vision_model"
    base_config_key = "vision_config"
    def __init__(
        self,
        hidden_size: int = 1024,
        intermediate_size: int = 2816,
        num_hidden_layers: int = 24,
        num_attention_heads: int = 8,
        num_channels: int = 3,
        image_size: int = 224,
        patch_size: int = 14,
        rms_norm_eps: float = 1e-5,
        attention_dropout: float = 0.0,
        qkv_bias: bool = False,
        mlp_bias: bool = False,
        hidden_act: str = "silu",
        initializer_range: float = 0.02,
        use_head: bool = True,
        is_native: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_channels = num_channels
        self.patch_size = patch_size
        self.image_size = image_size
        self.attention_dropout = attention_dropout
        self.hidden_act = hidden_act
        self.use_head = use_head
        self.initializer_range = initializer_range
        self.mlp_bias = mlp_bias
        self.qkv_bias = qkv_bias
        self.rms_norm_eps = rms_norm_eps
        self.is_native = is_native
class Aimv2TextConfig(PretrainedConfig):
    model_type = "aimv2_text_model"
    base_config_key = "text_config"
    def __init__(
        self,
        vocab_size: int = 49408,
        hidden_size: int = 768,
        intermediate_size: int = 2048,
        num_hidden_layers: int = 12,
        num_attention_heads: int = 6,
        rms_norm_eps: float = 1e-5,
        attention_dropout: float = 0.0,
        qkv_bias: bool = False,
        mlp_bias: bool = False,
        hidden_act: str = "silu",
        pad_token_id: Optional[int] = None,
        bos_token_id: Optional[int] = None,
        eos_token_id: int = 49407,
        max_position_embeddings: int = 77,
        initializer_range: bool = 0.02,
        **kwargs,
    ):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.hidden_act = hidden_act
        self.attention_dropout = attention_dropout
        self.initializer_range = initializer_range
        self.mlp_bias = mlp_bias
        self.qkv_bias = qkv_bias
        self.rms_norm_eps = rms_norm_eps
class Aimv2Config(PretrainedConfig):
    model_type = "aimv2"
    sub_configs = {"text_config": Aimv2TextConfig, "vision_config": Aimv2VisionConfig}
    def __init__(
        self, text_config=None, vision_config=None, projection_dim=512, logit_scale_init_value=2.6592, **kwargs
    ):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `Aimv2TextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. initializing the `Aimv2VisionConfig` with default values.")
        self.text_config = Aimv2TextConfig(**text_config)
        self.vision_config = Aimv2VisionConfig(**vision_config)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.max_logit_scale = 100.0
__all__ = ["Aimv2Config", "Aimv2VisionConfig", "Aimv2TextConfig"]