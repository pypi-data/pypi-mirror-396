import importlib
from collections import defaultdict
from functools import cached_property
from typing import TYPE_CHECKING, Optional, Union
from packaging import version
from .base import HfQuantizer
from .quantizers_utils import get_module_from_name
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from ..utils import (
    ACCELERATE_MIN_VERSION,
    is_accelerate_available,
    is_bitsandbytes_available,
    is_torch_available,
    is_torch_hpu_available,
    is_torch_npu_available,
    is_torch_xpu_available,
    logging,
)
if is_torch_available():
    import torch
    from ..pytorch_utils import Conv1D
logger = logging.get_logger(__name__)
class Bnb4BitHfQuantizer(HfQuantizer):
    use_keep_in_fp32_modules = True
    requires_parameters_quantization = True
    requires_calibration = False
    required_packages = ["bitsandbytes", "accelerate"]
    def __init__(self, quantization_config, **kwargs):
        super().__init__(quantization_config, **kwargs)
        if self.quantization_config.llm_int8_skip_modules is not None:
            self.modules_to_not_convert = self.quantization_config.llm_int8_skip_modules
        self.bnb_keys = [
            f"quant_state.bitsandbytes__{self.quantization_config.bnb_4bit_quant_type}",
            "absmax",
            "quant_map",
        ]
        if self.quantization_config.bnb_4bit_use_double_quant:
            self.bnb_keys.extend(["nested_absmax", "nested_quant_map"])
    def validate_environment(self, *args, **kwargs):
        if not is_accelerate_available():
            raise ImportError(
                f"Using `bitsandbytes` 4-bit quantization requires Accelerate: `pip install 'accelerate>={ACCELERATE_MIN_VERSION}'`"
            )
        if not is_bitsandbytes_available(check_library_only=True):
            raise ImportError(
                "Using `bitsandbytes` 4-bit quantization requires the latest version of bitsandbytes: `pip install -U bitsandbytes`"
            )
        if not is_torch_available():
            raise ImportError(
                "The bitsandbytes library requires PyTorch but it was not found in your environment. "
                "You can install it with `pip install torch`."
            )
        if version.parse(importlib.metadata.version("bitsandbytes")) < version.parse("0.43.1"):
            if not torch.cuda.is_available():
                raise ImportError(
                    "The installed version of bitsandbytes (<0.43.1) requires CUDA, but CUDA is not available. "
                    "You may need to install PyTorch with CUDA support or upgrade bitsandbytes to >=0.43.1."
                )
        from ..integrations import validate_bnb_backend_availability
        from ..utils import is_bitsandbytes_multi_backend_available
        bnb_multibackend_is_enabled = is_bitsandbytes_multi_backend_available()
        validate_bnb_backend_availability(raise_exception=True)
        if kwargs.get("from_tf", False) or kwargs.get("from_flax", False):
            raise ValueError(
                "Converting into 4-bit or 8-bit weights from tf/flax weights is currently not supported, please make"
                " sure the weights are in PyTorch format."
            )
        device_map = kwargs.get("device_map")
        if (
            device_map is not None
            and isinstance(device_map, dict)
            and not self.quantization_config.llm_int8_enable_fp32_cpu_offload
        ):
            device_map_without_lm_head = {
                key: device_map[key] for key in device_map if key not in self.modules_to_not_convert
            }
            if set(device_map.values()) == {"cpu"} and bnb_multibackend_is_enabled:
                pass
            elif "cpu" in device_map_without_lm_head.values() or "disk" in device_map_without_lm_head.values():
                raise ValueError(
                    "Some modules are dispatched on the CPU or the disk. Make sure you have enough GPU RAM to fit the "
                    "quantized model. If you want to dispatch the model on the CPU or the disk while keeping these modules "
                    "in 32-bit, you need to set `llm_int8_enable_fp32_cpu_offload=True` and pass a custom `device_map` to "
                    "`from_pretrained`. Check "
                    "https://huggingface.co/docs/MEROAI/main/en/main_classes/quantization#offload-between-cpu-and-gpu "
                    "for more details. "
                )
    def adjust_target_dtype(self, target_dtype: "torch.dtype") -> "torch.dtype":
        if version.parse(importlib.metadata.version("accelerate")) > version.parse("0.19.0"):
            from accelerate.utils import CustomDtype
            if target_dtype != torch.int8:
                logger.info("target_dtype {target_dtype} is replaced by `CustomDtype.INT4` for 4-bit BnB quantization")
            return CustomDtype.INT4
        else:
            raise ValueError(
                "You are using `device_map='auto'` on a 4bit loaded version of the model. To automatically compute"
                " the appropriate device map, you should upgrade your `accelerate` library,"
                "`pip install --upgrade accelerate` or install it from source to support fp4 auto device map"
                "calculation. You may encounter unexpected behavior, or pass your own device map"
            )
    def update_unexpected_keys(self, model, unexpected_keys: list[str]) -> list[str]:
        return [k for k in unexpected_keys if not any(k.endswith(x) for x in self.bnb_keys)]
    def param_needs_quantization(self, model: "PreTrainedModel", param_name: str, **kwargs) -> bool:
        import bitsandbytes as bnb
        if any(param_name.endswith(x) for x in self.bnb_keys):
            return True
        module, name = get_module_from_name(model, param_name)
        return isinstance(module, bnb.nn.Linear4bit) and name != "bias"
    def get_param_name(self, param_name: str) -> str:
        if self.pre_quantized:
            if any(param_name.endswith(x) for x in self.bnb_keys):
                param_name = (
                    param_name.rsplit(".", 1)[0] if "quant_state." not in param_name else param_name.rsplit(".", 2)[0]
                )
        return param_name
    def create_quantized_param(
        self,
        model: "PreTrainedModel",
        param_value: "torch.Tensor",
        param_name: str,
        target_device: "torch.device",
        **kwargs,
    ):
        import bitsandbytes as bnb
        full_name = param_name
        param_name = self.get_param_name(param_name)
        module, tensor_name = get_module_from_name(model, param_name)
        if isinstance(target_device, int) and is_torch_npu_available():
            target_device = f"npu:{target_device}"
        if self.pre_quantized:
            module_name = param_name.rsplit(".", 1)[0]
            if not hasattr(self, "param_quant_stats"):
                self.param_quant_stats = defaultdict(dict)
            self.param_quant_stats[module_name].update({full_name: param_value})
            if len(self.param_quant_stats[module_name]) == len(self.bnb_keys) + 1:
                param_kwargs = {}
                if self.is_bnb_supports_quant_storage_module:
                    param_kwargs["module"] = module
                weight = self.param_quant_stats[module_name].pop(f"{module_name}.weight")
                new_value = bnb.nn.Params4bit.from_prequantized(
                    data=weight,
                    quantized_stats=self.param_quant_stats[module_name],
                    requires_grad=False,
                    device=target_device,
                    **param_kwargs,
                )
                module._parameters[tensor_name] = new_value
                del self.param_quant_stats[module_name]
        else:
            new_value = param_value.to("cpu")
            old_value = getattr(module, tensor_name)
            if issubclass(module.source_cls, Conv1D):
                new_value = new_value.T
            kwargs = old_value.__dict__
            kwargs.pop("_is_hf_initialized", None)
            new_value = bnb.nn.Params4bit(new_value, requires_grad=False, **kwargs).to(target_device)
            module._parameters[tensor_name] = new_value
    def adjust_max_memory(self, max_memory: dict[str, Union[int, str]]) -> dict[str, Union[int, str]]:
        max_memory = {key: val * 0.90 for key, val in max_memory.items()}
        return max_memory
    def update_dtype(self, dtype: "torch.dtype") -> "torch.dtype":
        if dtype is None:
            logger.info(
                "Overriding dtype=%s with `dtype=torch.float16` due to "
                "requirements of `bitsandbytes` to enable model loading in 8-bit or 4-bit. "
                "Pass your own dtype to specify the dtype of the remaining non-linear layers or pass"
                " dtype=torch.float16 to remove this warning.",
                dtype,
            )
            dtype = torch.float16
        return dtype
    def update_device_map(self, device_map):
        if device_map is None:
            if torch.cuda.is_available():
                device_map = {"": torch.cuda.current_device()}
            elif is_torch_npu_available():
                device_map = {"": f"npu:{torch.npu.current_device()}"}
            elif is_torch_hpu_available():
                device_map = {"": f"hpu:{torch.hpu.current_device()}"}
            elif is_torch_xpu_available():
                device_map = {"": torch.xpu.current_device()}
            else:
                device_map = {"": "cpu"}
            logger.info(
                "The device_map was not initialized. "
                f"Setting device_map to {device_map}. "
                "If you want to use the model for inference, please set device_map ='auto' "
            )
        return device_map
    def _process_model_before_weight_loading(
        self,
        model: "PreTrainedModel",
        device_map,
        keep_in_fp32_modules: Optional[list[str]] = None,
        **kwargs,
    ):
        from ..integrations import replace_with_bnb_linear
        llm_int8_enable_fp32_cpu_offload = self.quantization_config.llm_int8_enable_fp32_cpu_offload
        self.modules_to_not_convert = self.get_modules_to_not_convert(
            model, self.quantization_config.llm_int8_skip_modules, keep_in_fp32_modules
        )
        if isinstance(device_map, dict) and len(device_map.keys()) > 1:
            keys_on_cpu = [key for key, value in device_map.items() if value in ["disk", "cpu"]]
            if len(keys_on_cpu) > 0 and not llm_int8_enable_fp32_cpu_offload:
                raise ValueError(
                    "If you want to offload some keys to `cpu` or `disk`, you need to set "
                    "`llm_int8_enable_fp32_cpu_offload=True`. Note that these modules will not be "
                    " converted to 8-bit but kept in 32-bit."
                )
            self.modules_to_not_convert.extend(keys_on_cpu)
        model = replace_with_bnb_linear(
            model, modules_to_not_convert=self.modules_to_not_convert, quantization_config=self.quantization_config
        )
        model.config.quantization_config = self.quantization_config
    def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs):
        model.is_loaded_in_4bit = True
        model.is_4bit_serializable = self.is_serializable()
        return model
    def is_serializable(self, safe_serialization=None):
        _is_4bit_serializable = version.parse(importlib.metadata.version("bitsandbytes")) >= version.parse("0.41.3")
        if not _is_4bit_serializable:
            logger.warning(
                "You are calling `save_pretrained` to a 4-bit converted model, but your `bitsandbytes` version doesn't support it. "
                "If you want to save 4-bit models, make sure to have `bitsandbytes>=0.41.3` installed."
            )
            return False
        return True
    @cached_property
    def is_bnb_supports_quant_storage_module(self) -> bool:
        return version.parse(importlib.metadata.version("bitsandbytes")) >= version.parse("0.43.3")
    @property
    def is_trainable(self) -> bool:
        return True
    def _dequantize(self, model):
        from ..integrations import dequantize_and_replace
        model = dequantize_and_replace(
            model, self.modules_to_not_convert, quantization_config=self.quantization_config
        )
        return model