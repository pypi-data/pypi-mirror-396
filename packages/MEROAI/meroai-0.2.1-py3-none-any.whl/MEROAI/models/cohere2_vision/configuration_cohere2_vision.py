from ...configuration_utils import PretrainedConfig
from ..auto import CONFIG_MAPPING, AutoConfig
class Cohere2VisionConfig(PretrainedConfig):
    model_type = "cohere2_vision"
    sub_configs = {"text_config": AutoConfig, "vision_config": AutoConfig}
    def __init__(
        self,
        vision_config=None,
        text_config=None,
        downsample_factor=2,
        image_token_id=255036,
        alignment_intermediate_size=36864,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.downsample_factor = downsample_factor
        self.image_token_id = image_token_id
        self.alignment_intermediate_size = alignment_intermediate_size
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "siglip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["siglip_vision_model"](
                hidden_size=1152,
                intermediate_size=3072,
                image_size=512,
                num_hidden_layers=27,
                num_attention_heads=12,
            )
        self.vision_config = vision_config
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config.get("model_type", "cohere2")
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        elif text_config is None:
            text_config = CONFIG_MAPPING["cohere2"](tie_word_embeddings=True)
        self.text_config = text_config
__all__ = ["Cohere2VisionConfig"]