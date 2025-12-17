from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class BlipTextConfig(PretrainedConfig):
    model_type = "blip_text_model"
    base_config_key = "text_config"
    def __init__(
        self,
        vocab_size=30524,
        hidden_size=768,
        encoder_hidden_size=768,
        intermediate_size=3072,
        projection_dim=768,
        num_hidden_layers=12,
        num_attention_heads=8,
        max_position_embeddings=512,
        hidden_act="gelu",
        layer_norm_eps=1e-12,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        initializer_range=0.02,
        bos_token_id=30522,
        eos_token_id=2,
        pad_token_id=0,
        sep_token_id=102,
        is_decoder=True,
        use_cache=True,
        label_smoothing=0.0,
        **kwargs,
    ):
        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            sep_token_id=sep_token_id,
            **kwargs,
        )
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.encoder_hidden_size = encoder_hidden_size
        self.intermediate_size = intermediate_size
        self.projection_dim = projection_dim
        self.hidden_dropout_prob = hidden_dropout_prob
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.is_decoder = is_decoder
        self.use_cache = use_cache
        self.label_smoothing = label_smoothing
class BlipVisionConfig(PretrainedConfig):
    model_type = "blip_vision_model"
    base_config_key = "vision_config"
    def __init__(
        self,
        hidden_size=768,
        intermediate_size=3072,
        projection_dim=512,
        num_hidden_layers=12,
        num_attention_heads=12,
        image_size=384,
        patch_size=16,
        hidden_act="gelu",
        layer_norm_eps=1e-5,
        attention_dropout=0.0,
        initializer_range=1e-10,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.projection_dim = projection_dim
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.patch_size = patch_size
        self.image_size = image_size
        self.initializer_range = initializer_range
        self.attention_dropout = attention_dropout
        self.layer_norm_eps = layer_norm_eps
        self.hidden_act = hidden_act
class BlipConfig(PretrainedConfig):
    model_type = "blip"
    sub_configs = {"text_config": BlipTextConfig, "vision_config": BlipVisionConfig}
    def __init__(
        self,
        text_config=None,
        vision_config=None,
        projection_dim=512,
        logit_scale_init_value=2.6592,
        image_text_hidden_size=256,
        label_smoothing=0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `BlipTextConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. Initializing the `BlipVisionConfig` with default values.")
        self.text_config = BlipTextConfig(**text_config)
        self.vision_config = BlipVisionConfig(**vision_config)
        self.text_config.encoder_hidden_size = self.vision_config.hidden_size
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.initializer_factor = 1.0
        self.initializer_range = 0.02
        self.image_text_hidden_size = image_text_hidden_size
        self.label_smoothing = label_smoothing
__all__ = ["BlipConfig", "BlipTextConfig", "BlipVisionConfig"]