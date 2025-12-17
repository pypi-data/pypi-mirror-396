from typing import TYPE_CHECKING
from ..utils import _LazyModule
_import_structure = {
    "config": [
        "EXTERNAL_DATA_FORMAT_SIZE_LIMIT",
        "OnnxConfig",
        "OnnxConfigWithPast",
        "OnnxSeq2SeqConfigWithPast",
        "PatchingSpec",
    ],
    "convert": ["export", "validate_model_outputs"],
    "features": ["FeaturesManager"],
    "utils": ["ParameterFormat", "compute_serialized_parameters_size"],
}
if TYPE_CHECKING:
    from .config import (
        EXTERNAL_DATA_FORMAT_SIZE_LIMIT,
        OnnxConfig,
        OnnxConfigWithPast,
        OnnxSeq2SeqConfigWithPast,
        PatchingSpec,
    )
    from .convert import export, validate_model_outputs
    from .features import FeaturesManager
    from .utils import ParameterFormat, compute_serialized_parameters_size
else:
    import sys
    sys.modules[__name__] = _LazyModule(__name__, globals()["__file__"], _import_structure, module_spec=__spec__)