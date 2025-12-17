import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_chinese_clip import ChineseCLIPImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class ChineseCLIPFeatureExtractor(ChineseCLIPImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class ChineseCLIPFeatureExtractor is deprecated and will be removed in version 5 of MEROAI."
            " Please use ChineseCLIPImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["ChineseCLIPFeatureExtractor"]