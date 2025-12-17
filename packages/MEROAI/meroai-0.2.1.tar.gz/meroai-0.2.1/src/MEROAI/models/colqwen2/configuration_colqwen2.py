from copy import deepcopy
from typing import Any
from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class ColQwen2Config(PretrainedConfig):
    model_type = "colqwen2"
    sub_configs: dict[str, Any] = {"vlm_config": PretrainedConfig}
    def __init__(
        self,
        vlm_config=None,
        embedding_dim: int = 128,
        initializer_range: float = 0.02,
        **kwargs,
    ):
        if vlm_config is None:
            vlm_config = CONFIG_MAPPING["qwen2_vl"]()
            logger.info(
                "`vlm_config` is `None`. Initializing `vlm_config` with the `Qwen2VLConfig` with default values."
            )
        elif isinstance(vlm_config, dict):
            vlm_config = deepcopy(vlm_config)
            if "model_type" not in vlm_config:
                raise KeyError(
                    "The `model_type` key is missing in the `vlm_config` dictionary. Please provide the model type."
                )
            vlm_config = CONFIG_MAPPING[vlm_config["model_type"]](**vlm_config)
        elif not isinstance(vlm_config, PretrainedConfig):
            raise TypeError(
                f"Invalid type for `vlm_config`. Expected `PretrainedConfig`, `dict`, or `None`, but got {type(vlm_config)}."
            )
        self.vlm_config = vlm_config
        self.embedding_dim = embedding_dim
        self.initializer_range = initializer_range
        super().__init__(**kwargs)
    def get_text_config(self, *args, **kwargs) -> PretrainedConfig:
        return self.vlm_config.get_text_config(*args, **kwargs)
__all__ = ["ColQwen2Config"]