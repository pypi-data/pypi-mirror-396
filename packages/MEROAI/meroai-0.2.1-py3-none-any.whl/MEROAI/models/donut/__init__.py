from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_donut_swin import *
    from .feature_extraction_donut import *
    from .image_processing_donut import *
    from .image_processing_donut_fast import *
    from .modeling_donut_swin import *
    from .processing_donut import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)