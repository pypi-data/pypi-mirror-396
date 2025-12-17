from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_chinese_clip import *
    from .feature_extraction_chinese_clip import *
    from .image_processing_chinese_clip import *
    from .image_processing_chinese_clip_fast import *
    from .modeling_chinese_clip import *
    from .processing_chinese_clip import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)