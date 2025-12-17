from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_deberta_v2 import *
    from .modeling_deberta_v2 import *
    from .modeling_tf_deberta_v2 import *
    from .tokenization_deberta_v2 import *
    from .tokenization_deberta_v2_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)