from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_blip import *
    from .image_processing_blip import *
    from .image_processing_blip_fast import *
    from .modeling_blip import *
    from .modeling_blip_text import *
    from .modeling_tf_blip import *
    from .modeling_tf_blip_text import *
    from .processing_blip import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)