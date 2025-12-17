from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_data2vec_audio import *
    from .configuration_data2vec_text import *
    from .configuration_data2vec_vision import *
    from .modeling_data2vec_audio import *
    from .modeling_data2vec_text import *
    from .modeling_data2vec_vision import *
    from .modeling_tf_data2vec_vision import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)