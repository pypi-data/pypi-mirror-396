from typing import TYPE_CHECKING
from ...utils import _LazyModule
from ...utils.import_utils import define_import_structure
if TYPE_CHECKING:
    from .bort import *
    from .deta import *
    from .efficientformer import *
    from .ernie_m import *
    from .gptsan_japanese import *
    from .graphormer import *
    from .jukebox import *
    from .mctct import *
    from .mega import *
    from .mmbt import *
    from .nat import *
    from .nezha import *
    from .open_llama import *
    from .qdqbert import *
    from .realm import *
    from .retribert import *
    from .speech_to_text_2 import *
    from .tapex import *
    from .trajectory_transformer import *
    from .transfo_xl import *
    from .tvlt import *
    from .van import *
    from .vit_hybrid import *
    from .xlm_prophetnet import *
else:
    import sys
    _file = globals()["__file__"]
    sys.modules[__name__] = _LazyModule(__name__, _file, define_import_structure(_file), module_spec=__spec__)