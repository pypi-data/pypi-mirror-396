from typing import TYPE_CHECKING
from .base import HfQuantizer
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from ..utils import is_auto_round_available, is_torch_available, logging
from ..utils.quantization_config import QuantizationConfigMixin
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class AutoRoundQuantizer(HfQuantizer):
    requires_calibration = True
    required_packages = ["auto_round"]
    def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs):
        super().__init__(quantization_config, **kwargs)
    def validate_environment(self, *args, **kwargs):
        self.device_map = kwargs.get("device_map")
        if not is_auto_round_available():
            raise ImportError(
                "Loading an AutoRound quantized model requires auto-round library (`pip install 'auto-round>=0.5'`)"
            )
    def update_dtype(self, dtype: "torch.dtype") -> "torch.dtype":
        if dtype is None:
            dtype = torch.bfloat16
            logger.info("Loading the model in `torch.bfloat16`. To overwrite it, set `dtype` manually.")
        return dtype
    def _process_model_before_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if model.__class__.main_input_name != "input_ids":
            logger.warning("AutoRound offers only limited support for models that are not strictly text-based.")
        from auto_round.inference.convert_model import convert_hf_model, infer_target_device
        if self.pre_quantized:
            target_device = infer_target_device(self.device_map)
            model, used_backends = convert_hf_model(model, target_device)
            self.used_backends = used_backends
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        if self.pre_quantized:
            from auto_round.inference.convert_model import post_init
            post_init(model, self.used_backends)
        else:
            raise ValueError("AutoRound only sports pre-quantized models.")
    @property
    def is_trainable(self) -> bool:
        return False
    def is_serializable(self, safe_serialization=None):
        return True