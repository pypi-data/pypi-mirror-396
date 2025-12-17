import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_deit import DeiTImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class DeiTFeatureExtractor(DeiTImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DeiTFeatureExtractor is deprecated and will be removed in version 5 of MEROAI. Please"
            " use DeiTImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["DeiTFeatureExtractor"]