import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_dpt import DPTImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class DPTFeatureExtractor(DPTImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DPTFeatureExtractor is deprecated and will be removed in version 5 of MEROAI. Please"
            " use DPTImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["DPTFeatureExtractor"]