from typing import TYPE_CHECKING, Optional
from .base import HfQuantizer
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from ..utils import is_accelerate_available, is_torch_available, is_vptq_available, logging
from ..utils.quantization_config import QuantizationConfigMixin
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class VptqHfQuantizer(HfQuantizer):
    requires_calibration = True
    required_packages = ["vptq"]
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
        self.quantization_config = quantization_config
    def validate_environment(self, *args, **kwargs):
        if not is_accelerate_available():
            raise ImportError("Using `vptq` quantization requires Accelerate: `pip install accelerate`")
        if not is_vptq_available():
            raise ImportError("Using `vptq` quantization requires VPTQ>=0.0.4: `pip install -U vptq`")
    def update_dtype(self, dtype: "torch.dtype") -> "torch.dtype":
        if dtype is None:
            if torch.cuda.is_available():
                dtype = torch.float16
                logger.info(
                    "CUDA available. Assuming VPTQ inference on GPU and loading the model in `torch.float16`. To overwrite it, set `dtype` manually."
                )
            else:
                import vptq
                device_availability = getattr(vptq, "device_availability", lambda device: False)
                if device_availability("cpu") is True:
                    raise RuntimeError("No GPU found. Please wait for the next release of VPTQ to use CPU inference")
                dtype = torch.float32
                logger.info("No GPU found. Assuming VPTQ inference on CPU and loading the model in `torch.float32`.")
        return dtype
    def _process_model_before_weight_loading(
        self,
        model: "PreTrainedModel",
        keep_in_fp32_modules: Optional[list[str]] = None,
        **kwargs,
    ):
        from ..integrations import replace_with_vptq_linear
        self.modules_to_not_convert = self.get_modules_to_not_convert(
            model, self.quantization_config.modules_to_not_convert, keep_in_fp32_modules
        )
        replace_with_vptq_linear(
            model,
            quantization_config=self.quantization_config,
            modules_to_not_convert=self.modules_to_not_convert,
        )
        model.config.quantization_config = self.quantization_config
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        return model
    @property
    def is_trainable(self) -> bool:
        return False
    def is_serializable(self, safe_serialization=None):
        return True