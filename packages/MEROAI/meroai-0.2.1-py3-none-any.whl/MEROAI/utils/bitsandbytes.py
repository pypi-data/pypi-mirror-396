import warnings
warnings.warn(
    "MEROAI.utils.bitsandbytes module is deprecated and will be removed in a future version. Please import bitsandbytes modules directly from MEROAI.integrations",
    FutureWarning,
)
from ..integrations import (
    get_keys_to_not_convert,
    replace_8bit_linear,
    replace_with_bnb_linear,
    set_module_8bit_tensor_to_device,
    set_module_quantized_tensor_to_device,
)