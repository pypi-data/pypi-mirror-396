from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_bart import *
    from .modeling_bart import *
    from .modeling_flax_bart import *
    from .modeling_tf_bart import *
    from .tokenization_bart import *
    from .tokenization_bart_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)