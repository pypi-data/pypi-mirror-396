from typing import Optional
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING, AutoConfig
logger = logging.get_logger(__name__)
class DeepseekVLHybridConfig(PretrainedConfig):
    model_type = "deepseek_vl_hybrid"
    sub_configs = {"text_config": AutoConfig, "vision_config": AutoConfig, "high_res_vision_config": AutoConfig}
    def __init__(
        self,
        text_config: Optional[AutoConfig] = None,
        vision_config: Optional[AutoConfig] = None,
        high_res_vision_config: Optional[AutoConfig] = None,
        image_token_id: int = 100015,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `LlamaConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. Initializing the `SiglipVisionConfig` with default values.")
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config.get("model_type", "llama")
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "siglip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        self.text_config = text_config
        self.vision_config = vision_config
        self.image_token_id = image_token_id
        if high_res_vision_config is None:
            high_res_vision_config = {}
            logger.info("`high_res_vision_config` is `None`. Initializing the `SamVisionConfig` with default values.")
        if isinstance(high_res_vision_config, dict):
            high_res_vision_config["model_type"] = high_res_vision_config.get("model_type", "sam_vision_model")
            high_res_vision_config = CONFIG_MAPPING[high_res_vision_config["model_type"]](**high_res_vision_config)
        self.high_res_vision_config = high_res_vision_config
__all__ = ["DeepseekVLHybridConfig"]