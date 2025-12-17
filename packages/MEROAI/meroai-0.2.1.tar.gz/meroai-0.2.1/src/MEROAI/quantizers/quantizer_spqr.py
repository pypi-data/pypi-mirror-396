from typing import TYPE_CHECKING, Optional
from .base import HfQuantizer
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from ..integrations import replace_with_spqr_linear
from ..utils import is_accelerate_available, is_spqr_available, is_torch_available, logging
from ..utils.quantization_config import QuantizationConfigMixin
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class SpQRHfQuantizer(HfQuantizer):
    requires_calibration = True
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
        self.quantization_config = quantization_config
    def validate_environment(self, *args, **kwargs):
        if not torch.cuda.is_available():
            raise RuntimeError("GPU is required to run SpQR quantized model.")
        if not is_accelerate_available():
            raise ImportError("Using `spqr` quantization requires Accelerate: `pip install accelerate`")
        if not is_spqr_available():
            raise ImportError("Using `spqr` quantization requires SpQR: `pip install spqr_quant[gpu]`")
    def update_dtype(self, dtype: "torch.dtype") -> "torch.dtype":
        if dtype is None:
            dtype = torch.float16
            logger.info("Assuming SpQR inference on GPU and loading the model in `torch.float16`.")
        elif dtype != torch.float16:
            raise ValueError(
                "You cannot use any type other than torch.float16 for SpQR. Please either leave it None or set it to"
                "torch.float16 explicitly."
            )
        return dtype
    def _process_model_before_weight_loading(
        self,
        model: "PreTrainedModel",
        keep_in_fp32_modules: Optional[list[str]] = None,
        **kwargs,
    ):
        self.modules_to_not_convert = self.get_modules_to_not_convert(
            model, self.quantization_config.modules_to_not_convert, keep_in_fp32_modules
        )
        replace_with_spqr_linear(
            model,
            quantization_config=self.quantization_config,
            modules_to_not_convert=self.modules_to_not_convert,
        )
        model.config.quantization_config = self.quantization_config
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        return model
    @property
    def is_trainable(self):
        return False
    def is_serializable(self, safe_serialization=None):
        return True