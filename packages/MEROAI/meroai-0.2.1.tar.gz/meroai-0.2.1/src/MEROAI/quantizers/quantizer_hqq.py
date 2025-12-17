from collections import defaultdict
from typing import TYPE_CHECKING
from ..integrations import prepare_for_hqq_linear
from ..utils import is_hqq_available, is_torch_available, logging
from .base import HfQuantizer
from .quantizers_utils import get_module_from_name
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
if is_torch_available():
    import torch
if is_hqq_available():
    from hqq.core.quantize import HQQLinear
    @property
    def weight(self):
        return torch.empty(0, dtype=self.compute_dtype, device=self.device)
    HQQLinear.weight = weight
logger = logging.get_logger(__name__)
class HqqHfQuantizer(HfQuantizer):
    use_keep_in_fp32_modules = False
    requires_parameters_quantization = True
    requires_calibration = False
    required_packages = ["hqq"]
    def __init__(self, quantization_config, **kwargs):
        if not is_hqq_available():
            raise ImportError(
                "A valid HQQ version (>=0.2.1) is not available. Please follow the instructions to install it: `https://github.com/mobiusml/hqq/`."
            )
        super().__init__(quantization_config, **kwargs)
        self.dtype = None
        self.using_multi_gpu = False
        self.hqq_keys = HQQLinear(None, None).state_dict_keys() - {"bias"}
        if kwargs.get("from_tf", False) or kwargs.get("from_flax", False):
            raise ValueError(
                "Converting weights from tf/flax weights is currently not supported, please make"
                " sure the weights are in PyTorch format."
            )
        if self.dtype is None:
            if "dtype" in kwargs:
                self.dtype = kwargs["dtype"]
            else:
                self.dtype = torch.float32
                logger.info("Setting dtype to torch.float32 as the default value since it was not specified.")
        device_map = kwargs.get("device_map")
        if isinstance(device_map, dict):
            if "cpu" in device_map.values() or "disk" in device_map.values():
                raise ValueError(
                    "You are attempting to use an HQQ model with a device_map that contains a CPU or disk device."
                    " This is not supported. Please remove the CPU or disk device from the device_map."
                )
            else:
                self.using_multi_gpu = len(set(device_map.values())) > 1
    def update_missing_keys(
        self, model: "PreTrainedModel", missing_keys: list[str], prefix: str, **kwargs
    ) -> list[str]:
        if self.pre_quantized:
            return [key for key in missing_keys if ("weight" not in key)]
        else:
            return missing_keys
    def update_expected_keys(
        self, model: "PreTrainedModel", expected_keys: list[str], loaded_keys: list[str]
    ) -> list[str]:
        if not self.pre_quantized:
            return expected_keys
        def _find_hqq_quantizable_layers(model, layers):
            for name, module in model.named_children():
                if isinstance(module, (torch.nn.Linear)):
                    layers.add(module.name)
                _find_hqq_quantizable_layers(module, layers)
        new_keys = set(expected_keys)
        for name, module in model.named_modules():
            module.name = name
        _valid_modules = set()
        _find_hqq_quantizable_layers(model, _valid_modules)
        _skipped_modules = set()
        for _module in _valid_modules:
            for _skip_module in model.config.quantization_config["skip_modules"]:
                if _skip_module in _module:
                    _skipped_modules.add(_module)
        _valid_modules -= _skipped_modules
        _ref_keys = HQQLinear(
            linear_layer=None,
            quant_config=None,
            compute_dtype=torch.float16,
            device="cpu",
            del_orig=False,
        ).state_dict_keys() - {"bias"}
        _rm_keys = set()
        for key in new_keys:
            if any(_module in key for _module in _valid_modules):
                _rm_keys.add(key)
        new_keys -= _rm_keys
        for _module in _valid_modules:
            if _module + ".weight" in loaded_keys:
                new_keys.add(_module + ".weight")
            else:
                new_keys.update({_module + "." + _ref_key for _ref_key in _ref_keys})
            if _module + ".bias" in loaded_keys:
                new_keys.add(_module + ".bias")
        return list(new_keys)
    def param_needs_quantization(self, model: "PreTrainedModel", param_name: str, **kwargs) -> bool:
        module, _ = get_module_from_name(model, param_name)
        return isinstance(module, torch.nn.Linear)
    def create_quantized_param(
        self,
        model: "PreTrainedModel",
        param_value: "torch.Tensor",
        param_name: str,
        target_device: "torch.device",
        **kwargs,
    ):
        module, tensor_name = get_module_from_name(model, param_name)
        module_name = param_name.rsplit(".", 1)[0]
        parent_module, node = get_module_from_name(model, module_name)
        quant_config = model.config.quantization_config["quant_config"]
        skip_modules = model.config.quantization_config["skip_modules"]
        if any(skip_module in module.name for skip_module in skip_modules):
            module.load_state_dict(
                {tensor_name: param_value.to(device=target_device, dtype=self.dtype)}, strict=False, assign=True
            )
            return
        if self.pre_quantized:
            if not hasattr(self, "hqq_params"):
                self.hqq_params = defaultdict(dict)
            self.hqq_params[module_name].update({tensor_name: param_value})
            hqq_params = self.hqq_params[module_name]
            if all(k in hqq_params for k in self.hqq_keys) and ("bias" in hqq_params or module.bias is None):
                hqq_layer = HQQLinear(
                    linear_layer=None,
                    quant_config=None,
                    compute_dtype=self.dtype,
                    device=target_device,
                    del_orig=False,
                )
                hqq_layer.load_state_dict(hqq_params)
                if hqq_layer.bias is not None and isinstance(hqq_layer.bias, torch.Tensor):
                    hqq_layer.bias = torch.nn.Parameter(hqq_layer.bias)
                if self.using_multi_gpu:
                    hqq_layer = self._patch_layer_for_multigpu(hqq_layer)
                setattr(parent_module, node, hqq_layer)
                del self.hqq_params[module_name], module
            return
        module.load_state_dict({tensor_name: param_value}, strict=False, assign=True)
        module_is_ready = module.weight.device.type != "meta" and (
            module.bias is None or module.bias.device.type != "meta"
        )
        if module_is_ready:
            module_tag = ".".join(module.name.split(".")[-2:])
            if "weight_quant_params" in quant_config:
                module_quant_config = quant_config
            elif module_tag in quant_config:
                module_quant_config = quant_config[module_tag]
            hqq_layer = HQQLinear(
                module,
                quant_config=module_quant_config,
                compute_dtype=self.dtype,
                device=target_device,
                del_orig=True,
            )
            if hqq_layer.bias is not None and isinstance(hqq_layer.bias, torch.Tensor):
                hqq_layer.bias = torch.nn.Parameter(hqq_layer.bias)
            if self.using_multi_gpu:
                hqq_layer = self._patch_layer_for_multigpu(hqq_layer)
            setattr(parent_module, node, hqq_layer)
    def _patch_layer_for_multigpu(self, hqq_layer):
        def forward_with_device(self, x):
            out = torch.matmul(x.to(self.device), self.dequantize().t())
            if self.bias is not None:
                out += self.bias
            return out
        hqq_layer.forward = lambda x: forward_with_device(hqq_layer, x)
        return hqq_layer
    def _process_model_before_weight_loading(
        self,
        model: "PreTrainedModel",
        **kwargs,
    ):
        model = prepare_for_hqq_linear(model, quantization_config=self.quantization_config)
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        model.is_hqq_quantized = True
        model.is_hqq_serializable = self.is_serializable()
        return model
    def is_serializable(self, safe_serialization=None):
        return True
    @property
    def is_trainable(self) -> bool:
        return True