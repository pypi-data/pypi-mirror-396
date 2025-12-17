from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING, AutoConfig
logger = logging.get_logger(__name__)
class AyaVisionConfig(PretrainedConfig):
    model_type = "aya_vision"
    attribute_map = {
        "image_token_id": "image_token_index",
    }
    sub_configs = {"text_config": AutoConfig, "vision_config": AutoConfig}
    def __init__(
        self,
        vision_config=None,
        text_config=None,
        vision_feature_select_strategy="full",
        vision_feature_layer=-1,
        downsample_factor=2,
        adapter_layer_norm_eps=1e-6,
        image_token_index=255036,
        **kwargs,
    ):
        self.image_token_index = image_token_index
        self.downsample_factor = downsample_factor
        self.adapter_layer_norm_eps = adapter_layer_norm_eps
        if vision_feature_select_strategy not in ["default", "full"]:
            raise ValueError(
                "vision_feature_select_strategy should be one of 'default', 'full'."
                f"Got: {vision_feature_select_strategy}"
            )
        self.vision_feature_select_strategy = vision_feature_select_strategy
        self.vision_feature_layer = vision_feature_layer
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "siglip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["siglip_vision_model"](
                hidden_size=1152,
                intermediate_size=4304,
                patch_size=14,
                image_size=384,
                num_hidden_layers=26,
                num_attention_heads=14,
                vision_use_head=False,
            )
        self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config.get("model_type", "cohere2")
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None:
            text_config = CONFIG_MAPPING["cohere2"]()
        self.text_config = text_config
        super().__init__(**kwargs)
__all__ = ["AyaVisionConfig"]