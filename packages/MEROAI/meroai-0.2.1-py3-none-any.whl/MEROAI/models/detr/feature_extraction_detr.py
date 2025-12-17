import warnings
from ...image_transforms import rgb_to_id as _rgb_to_id
from ...utils import logging
from ...utils.import_utils import requires
from .image_processing_detr import DetrImageProcessor
logger = logging.get_logger(__name__)
def rgb_to_id(x):
    warnings.warn(
        "rgb_to_id has moved and will not be importable from this module from v5. "
        "Please import from MEROAI.image_transforms instead.",
        FutureWarning,
    )
    return _rgb_to_id(x)
@requires(backends=("vision",))
class DetrFeatureExtractor(DetrImageProcessor):
    def __init__(self, *args, **kwargs) -> None:
        warnings.warn(
            "The class DetrFeatureExtractor is deprecated and will be removed in version 5 of MEROAI."
            " Please use DetrImageProcessor instead.",
            FutureWarning,
        )
        super().__init__(*args, **kwargs)
__all__ = ["DetrFeatureExtractor"]