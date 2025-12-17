import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_beit import BeitImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class BeitFeatureExtractor(BeitImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class BeitFeatureExtractor is deprecated and will be removed in version 5 of MEROAI. Please"
            " use BeitImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["BeitFeatureExtractor"]