from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_big_bird import *
    from .modeling_big_bird import *
    from .modeling_flax_big_bird import *
    from .tokenization_big_bird import *
    from .tokenization_big_bird_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)