import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_convnext import ConvNextImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class ConvNextFeatureExtractor(ConvNextImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class ConvNextFeatureExtractor is deprecated and will be removed in version 5 of MEROAI."
            " Please use ConvNextImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["ConvNextFeatureExtractor"]