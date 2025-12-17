import warnings
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_clip import CLIPImageProcessor
logger = logging.get_logger(__name__)
@requires(backends=("vision",))
class CLIPFeatureExtractor(CLIPImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class CLIPFeatureExtractor is deprecated and will be removed in version 5 of MEROAI. Please"
            " use CLIPImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["CLIPFeatureExtractor"]