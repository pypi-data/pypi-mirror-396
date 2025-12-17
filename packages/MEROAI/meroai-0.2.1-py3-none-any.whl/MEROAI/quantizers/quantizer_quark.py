from typing import TYPE_CHECKING
from .base import HfQuantizer
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from ..utils import is_quark_available, logging
logger = logging.get_logger(__name__)
CHECKPOINT_KEYS = {
    "weight_scale": "weight_quantizer.scale",
    "bias_scale": "bias_quantizer.scale",
    "input_scale": "input_quantizer.scale",
    "output_scale": "output_quantizer.scale",
    "weight_zero_point": "weight_quantizer.zero_point",
    "bias_zero_point": "bias_quantizer.zero_point",
    "input_zero_point": "input_quantizer.zero_point",
    "output_zero_point": "output_quantizer.zero_point",
}
class QuarkHfQuantizer(HfQuantizer):
    requires_calibration = True
    required_packages = ["quark"]
    requires_parameters_quantization = True
    def __init__(self, quantization_config, **kwargs):
        super().__init__(quantization_config, **kwargs)
        self.json_export_config = quantization_config.json_export_config
    def validate_environment(self, *args, **kwargs):
        if not is_quark_available():
            raise ImportError(
                "Loading a Quark quantized model requires the `quark` library but it was not found in the environment. Please refer to https://quark.docs.amd.com/latest/install.html."
            )
    def _process_model_before_weight_loading(self, model: "PreTrainedModel", **kwargs):
        from quark.torch.export.api import _map_to_quark
        _map_to_quark(
            model,
            self.quantization_config.quant_config,
            pack_method=self.json_export_config.pack_method,
            custom_mode=self.quantization_config.custom_mode,
        )
        return model
    def param_needs_quantization(self, model: "PreTrainedModel", param_name: str, **kwargs) -> bool:
        return True
    def create_quantized_param(self, model, param, param_name, param_device, **kwargs):
        from ..modeling_utils import _load_parameter_into_model
        postfix = param_name.split(".")[-1]
        if postfix in CHECKPOINT_KEYS:
            param_name = param_name.replace(postfix, CHECKPOINT_KEYS[postfix])
        _load_parameter_into_model(model, param_name, param.to(param_device))
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        return model
    def is_serializable(self, safe_serialization=None):
        return False
    @property
    def is_trainable(self):
        return False