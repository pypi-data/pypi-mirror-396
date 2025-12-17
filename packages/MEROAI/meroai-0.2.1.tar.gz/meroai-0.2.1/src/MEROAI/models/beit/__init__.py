from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_beit import *
    from .feature_extraction_beit import *
    from .image_processing_beit import *
    from .image_processing_beit_fast import *
    from .modeling_beit import *
    from .modeling_flax_beit import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)