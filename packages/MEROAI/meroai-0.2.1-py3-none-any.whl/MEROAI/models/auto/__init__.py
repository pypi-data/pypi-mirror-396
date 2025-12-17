from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .auto_factory import *
    from .configuration_auto import *
    from .feature_extraction_auto import *
    from .image_processing_auto import *
    from .modeling_auto import *
    from .modeling_flax_auto import *
    from .modeling_tf_auto import *
    from .processing_auto import *
    from .tokenization_auto import *
    from .video_processing_auto import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)