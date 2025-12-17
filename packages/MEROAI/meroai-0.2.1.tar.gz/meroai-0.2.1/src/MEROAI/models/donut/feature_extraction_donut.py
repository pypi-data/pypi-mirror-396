import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_donut import DonutImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class DonutFeatureExtractor(DonutImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DonutFeatureExtractor is deprecated and will be removed in version 5 of MEROAI. Please"
            " use DonutImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["DonutFeatureExtractor"]