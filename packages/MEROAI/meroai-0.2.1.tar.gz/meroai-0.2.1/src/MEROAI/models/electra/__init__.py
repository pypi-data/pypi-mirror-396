from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_electra import *
    from .modeling_electra import *
    from .modeling_flax_electra import *
    from .modeling_tf_electra import *
    from .tokenization_electra import *
    from .tokenization_electra_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)