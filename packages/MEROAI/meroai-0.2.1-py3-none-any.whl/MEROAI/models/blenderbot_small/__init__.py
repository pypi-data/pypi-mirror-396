from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .configuration_blenderbot_small import *
    from .modeling_blenderbot_small import *
    from .modeling_flax_blenderbot_small import *
    from .modeling_tf_blenderbot_small import *
    from .tokenization_blenderbot_small import *
    from .tokenization_blenderbot_small_fast import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)