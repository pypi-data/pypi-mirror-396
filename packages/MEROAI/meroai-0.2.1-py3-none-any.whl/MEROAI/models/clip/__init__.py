from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_clip import *
    from .feature_extraction_clip import *
    from .image_processing_clip import *
    from .image_processing_clip_fast import *
    from .modeling_clip import *
    from .modeling_flax_clip import *
    from .modeling_tf_clip import *
    from .processing_clip import *
    from .tokenization_clip import *
    from .tokenization_clip_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)