from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...utils import add_start_docstrings, logging
from ..auto import CONFIG_MAPPING, AutoConfig
logger = logging.get_logger(__name__)
class BarkSubModelConfig(PretrainedConfig):
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {
        "num_attention_heads": "num_heads",
        "num_hidden_layers": "num_layers",
        "vocab_size": "input_vocab_size",
        "window_size": "block_size",
    }
    def __init__(
        self,
        block_size=1024,
        input_vocab_size=10_048,
        output_vocab_size=10_048,
        num_layers=12,
        num_heads=12,
        hidden_size=768,
        dropout=0.0,
        bias=True,
        initializer_range=0.02,
        use_cache=True,
        **kwargs,
    ):
        self.block_size = block_size
        self.input_vocab_size = input_vocab_size
        self.output_vocab_size = output_vocab_size
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.hidden_size = hidden_size
        self.dropout = dropout
        self.bias = bias
        self.use_cache = use_cache
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
@add_start_docstrings(
    BARK_SUBMODELCONFIG_START_DOCSTRING.format(config="BarkSemanticConfig", model="BarkSemanticModel"),
,
)
class BarkSemanticConfig(BarkSubModelConfig):
    model_type = "semantic"
    base_config_key = "semantic_config"
@add_start_docstrings(
    BARK_SUBMODELCONFIG_START_DOCSTRING.format(config="BarkCoarseConfig", model="BarkCoarseModel"),
,
)
class BarkCoarseConfig(BarkSubModelConfig):
    model_type = "coarse_acoustics"
    base_config_key = "coarse_acoustics_config"
@add_start_docstrings(
    BARK_SUBMODELCONFIG_START_DOCSTRING.format(config="BarkFineConfig", model="BarkFineModel"),
,
)
class BarkFineConfig(BarkSubModelConfig):
    model_type = "fine_acoustics"
    base_config_key = "fine_acoustics_config"
    def __init__(self, tie_word_embeddings=True, n_codes_total=8, n_codes_given=1, **kwargs):
        self.n_codes_total = n_codes_total
        self.n_codes_given = n_codes_given
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
class BarkConfig(PretrainedConfig):
    model_type = "bark"
    sub_configs = {
        "semantic_config": BarkSemanticConfig,
        "coarse_acoustics_config": BarkCoarseConfig,
        "fine_acoustics_config": BarkFineConfig,
        "codec_config": AutoConfig,
    }
    def __init__(
        self,
        semantic_config: Optional[dict] = None,
        coarse_acoustics_config: Optional[dict] = None,
        fine_acoustics_config: Optional[dict] = None,
        codec_config: Optional[dict] = None,
        initializer_range=0.02,
        **kwargs,
    ):
        if semantic_config is None:
            semantic_config = {}
            logger.info("semantic_config is None. initializing the semantic model with default values.")
        if coarse_acoustics_config is None:
            coarse_acoustics_config = {}
            logger.info("coarse_acoustics_config is None. initializing the coarse model with default values.")
        if fine_acoustics_config is None:
            fine_acoustics_config = {}
            logger.info("fine_acoustics_config is None. initializing the fine model with default values.")
        if codec_config is None:
            codec_config = {}
            logger.info("codec_config is None. initializing the codec model with default values.")
        self.semantic_config = BarkSemanticConfig(**semantic_config)
        self.coarse_acoustics_config = BarkCoarseConfig(**coarse_acoustics_config)
        self.fine_acoustics_config = BarkFineConfig(**fine_acoustics_config)
        codec_model_type = codec_config.get("model_type", "encodec")
        self.codec_config = CONFIG_MAPPING[codec_model_type](**codec_config)
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
    @classmethod
    def from_sub_model_configs(
        cls,
        semantic_config: BarkSemanticConfig,
        coarse_acoustics_config: BarkCoarseConfig,
        fine_acoustics_config: BarkFineConfig,
        codec_config: PretrainedConfig,
        **kwargs,
    ):
        return cls(
            semantic_config=semantic_config.to_dict(),
            coarse_acoustics_config=coarse_acoustics_config.to_dict(),
            fine_acoustics_config=fine_acoustics_config.to_dict(),
            codec_config=codec_config.to_dict(),
            **kwargs,
        )
__all__ = ["BarkCoarseConfig", "BarkConfig", "BarkFineConfig", "BarkSemanticConfig"]