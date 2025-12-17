import importlib
import re
import types
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Union
from packaging import version
from .base import HfQuantizer
from .quantizers_utils import get_module_from_name
if TYPE_CHECKING:
    from ..modeling_utils import PreTrainedModel
from safetensors import safe_open
from ..utils import is_torch_available, is_torchao_available, logging
if is_torch_available():
    import torch
    import torch.nn as nn
if is_torchao_available():
    import torchao
    if version.parse(importlib.metadata.version("torchao")) >= version.parse("0.14.0"):
        from torchao.prototype.safetensors.safetensors_support import (
            flatten_tensor_state_dict,
            unflatten_tensor_state_dict,
        )
        from torchao.prototype.safetensors.safetensors_utils import is_metadata_torchao
logger = logging.get_logger(__name__)
def fuzzy_match_size(config_name: str) -> Optional[str]:
    config_name = config_name.lower()
    str_match = re.search(r"(\d)weight", config_name)
    if str_match:
        return str_match.group(1)
    return None
def _quantization_type(weight):
    from torchao.dtypes import AffineQuantizedTensor
    from torchao.quantization.linear_activation_quantized_tensor import LinearActivationQuantizedTensor
    if isinstance(weight, AffineQuantizedTensor):
        return f"{weight.__class__.__name__}({weight._quantization_type()})"
    if isinstance(weight, LinearActivationQuantizedTensor):
        return f"{weight.__class__.__name__}(activation={weight.input_quant_func}, weight={_quantization_type(weight.original_weight_tensor)})"
def _linear_extra_repr(self):
    weight = _quantization_type(self.weight)
    if weight is None:
        return f"in_features={self.weight.shape[1]}, out_features={self.weight.shape[0]}, weight=None"
    else:
        return f"in_features={self.weight.shape[1]}, out_features={self.weight.shape[0]}, weight={weight}"
if is_torchao_available():
    SUPPORTED_SAFE_SERIALIZATION_CONFIGS = [
        torchao.quantization.Float8WeightOnlyConfig,
        torchao.quantization.Float8DynamicActivationFloat8WeightConfig,
    ]
    TORCHAO_VERSION = version.parse(importlib.metadata.version("torchao"))
class TorchAoHfQuantizer(HfQuantizer):
    requires_parameters_quantization = True
    requires_calibration = False
    required_packages = ["torchao"]
    def __init__(self, quantization_config, **kwargs):
        super().__init__(quantization_config, **kwargs)
        if isinstance(self.quantization_config.quant_type, str):
            is_int_4 = "int4" in self.quantization_config.quant_type
        else:
            config_name = self.quantization_config.quant_type.__class__.__name__
            is_int_4 = fuzzy_match_size(config_name) == "4"
        if is_int_4:
            self.weight_ao_keys = ["qdata", "scale", "zero_point"]
        else:
            self.weight_ao_keys = ["qdata", "scale"]
        self.full_ao_keys = self.weight_ao_keys + ["_data"]
    def validate_environment(self, *args, **kwargs):
        if not is_torchao_available():
            raise ImportError("Loading an torchao quantized model requires torchao library (`pip install torchao`)")
        self.offload = False
        device_map = kwargs.get("device_map")
        if isinstance(device_map, dict):
            if ("disk" in device_map.values() or "cpu" in device_map.values()) and len(device_map) > 1:
                self.offload = True
                if self.pre_quantized and "disk" in device_map.values():
                    raise ValueError(
                        "You are attempting to perform disk offload with a pre-quantized torchao model "
                        "This is not supported yet . Please remove the disk device from the device_map."
                    )
        if self.pre_quantized:
            weights_only = kwargs.get("weights_only")
            if weights_only:
                torch_version = version.parse(importlib.metadata.version("torch"))
                if torch_version < version.parse("2.5.0"):
                    raise RuntimeError(
                        f"In order to use torchao pre-quantized model, you need to have torch>=2.5.0. However, the current version is {torch_version}."
                        f" You can also set with `weights_only=False` in `from_pretrained` if you don't want to update torch"
                    )
    def update_dtype(self, dtype):
        if self.quantization_config.quant_type == "int4_weight_only":
            if dtype is not None and dtype != torch.bfloat16:
                logger.warning_once(
                    f"Setting dtype to {dtype} for int4_weight_only quantization, but only bfloat16 is supported right now. Please set the dtype to bfloat16."
                )
            if dtype is None:
                logger.warning_once(
                    "Setting dtype to torch.bfloat16 for int4_weight_only quantization since only bfloat16 is supported right now. Please set dtype=torch.bfloat16 to remove this warning."
                )
                dtype = torch.bfloat16
        if self.quantization_config.quant_type == "int8_dynamic_activation_int8_weight":
            if dtype is None:
                logger.info(
                    "Setting dtype to torch.float32 for int8_dynamic_activation_int8_weight quantization as no dtype was specified in from_pretrained"
                )
                dtype = torch.float32
        return dtype
    def get_state_dict_and_metadata(self, model, safe_serialization: Optional[bool] = False):
        if type(self.quantization_config.quant_type) in SUPPORTED_SAFE_SERIALIZATION_CONFIGS and safe_serialization:
            if TORCHAO_VERSION >= version.parse("0.14.0"):
                return flatten_tensor_state_dict(model.state_dict())
            else:
                raise RuntimeError(
                    f"In order to use safetensors with torchao, please use torchao version >= 0.14.0. Current version: {TORCHAO_VERSION}"
                )
        else:
            return None, {}
    def adjust_target_dtype(self, dtype: "torch.dtype") -> "torch.dtype":
        if version.parse(importlib.metadata.version("accelerate")) > version.parse("0.19.0"):
            from accelerate.utils import CustomDtype
            if self.quantization_config._get_ao_version() > version.Version("0.9.0"):
                from torchao.core.config import AOBaseConfig
                quant_type = self.quantization_config.quant_type
                if isinstance(quant_type, AOBaseConfig):
                    config_name = quant_type.__class__.__name__
                    size_digit = fuzzy_match_size(config_name)
                    if size_digit == "4":
                        return CustomDtype.INT4
                    else:
                        return torch.int8
            map_to_target_dtype = {
                "int4_weight_only": CustomDtype.INT4,
                "int8_weight_only": torch.int8,
                "int8_dynamic_activation_int8_weight": torch.int8,
                "autoquant": None,
            }
            return map_to_target_dtype[self.quantization_config.quant_type]
        else:
            raise ValueError(
                "You are using `device_map='auto'` on a torchao quantized model. To automatically compute"
                " the appropriate device map, you should upgrade your `accelerate` library with "
                "`pip install --upgrade accelerate`"
            )
    def adjust_max_memory(self, max_memory: dict[str, Union[int, str]]) -> dict[str, Union[int, str]]:
        max_memory = {key: val * 0.9 for key, val in max_memory.items()}
        return max_memory
    def _process_model_before_weight_loading(
        self, model: "PreTrainedModel", keep_in_fp32_modules: Optional[list[str]] = None, **kwargs
    ):
        self.modules_to_not_convert = self.get_modules_to_not_convert(
            model, self.quantization_config.modules_to_not_convert, keep_in_fp32_modules
        )
        if self.quantization_config.include_input_output_embeddings:
            input_emb = model.get_input_embeddings()
            input_emb_names = [name for name, module in model.named_modules() if id(module) == id(input_emb)]
            output_emb = model.get_output_embeddings()
            output_emb_names = [name for name, module in model.named_modules() if id(module) == id(output_emb)]
            self.modules_to_not_convert = [
                x for x in self.modules_to_not_convert if x not in input_emb_names + output_emb_names
            ]
        return
    def update_unexpected_keys(self, model, unexpected_keys: list[str]) -> list[str]:
        return [k for k in unexpected_keys if not any(k.endswith(x) for x in self.full_ao_keys)]
    def param_needs_quantization(self, model: "PreTrainedModel", param_name: str, **kwargs) -> bool:
        if self.quantization_config.quant_type == "autoquant":
            return False
        if any(key + "." in param_name or key == param_name for key in self.modules_to_not_convert):
            return False
        elif any(param_name.endswith(f":{x}") for x in self.full_ao_keys):
            return True
        else:
            module, tensor_name = get_module_from_name(model, param_name)
            _QUANTIZABLE = [torch.nn.Linear]
            if self.quantization_config.include_input_output_embeddings:
                _QUANTIZABLE.append(torch.nn.Embedding)
            return isinstance(module, tuple(_QUANTIZABLE)) and tensor_name == "weight"
    def create_quantized_param(
        self,
        model: "PreTrainedModel",
        param_value: "torch.Tensor",
        param_name: str,
        target_device: "torch.device",
        **kwargs,
    ):
        from torchao.quantization import quantize_
        full_name = param_name
        if ":" in param_name:
            param_name = param_name.rsplit(":", 1)[0]
        module, tensor_name = get_module_from_name(model, param_name)
        if self.pre_quantized:
            is_unsafe_serialization = ":" not in full_name
            if tensor_name == "bias" or is_unsafe_serialization:
                module._parameters[tensor_name] = torch.nn.Parameter(
                    param_value.to(target_device), requires_grad=param_value.requires_grad
                )
                return
            elif not (TORCHAO_VERSION >= version.parse("0.14.0") and is_metadata_torchao(self.metadata)):
                raise ValueError("To use `safetensors` serialization, you should have `torchao>=0.14.0` installed")
            if not hasattr(self, "ao_params"):
                self.ao_params = defaultdict(dict)
            self.ao_params[param_name].update({full_name: param_value})
            if len(self.ao_params[param_name]) == len(self.weight_ao_keys):
                new_param = unflatten_tensor_state_dict(self.ao_params[param_name], self.metadata)[param_name]
                module._parameters[tensor_name] = torch.nn.Parameter(
                    new_param.to(target_device), requires_grad=new_param.requires_grad
                )
                del self.ao_params[param_name]
            if isinstance(module, nn.Linear):
                module.extra_repr = types.MethodType(_linear_extra_repr, module)
        else:
            module._parameters[tensor_name] = torch.nn.Parameter(
                param_value, requires_grad=param_value.requires_grad
            ).to(target_device)
            input_embed = model.get_input_embeddings()
            if self.quantization_config.untie_embedding_weights and id(module) == id(input_embed):
                model.tie_weights()
                setattr(model.config.get_text_config(decoder=True), "tie_word_embeddings", False)
            if self.quantization_config._get_ao_version() >= version.Version("0.12.0"):
                from torchao.quantization import ModuleFqnToConfig
                config = self.quantization_config.get_apply_tensor_subclass()
                if isinstance(config, ModuleFqnToConfig):
                    module_fqn, _ = param_name.rsplit(".", 1)
                    c = None
                    if module_fqn in config.module_fqn_to_config:
                        c = config.module_fqn_to_config[module_fqn]
                    else:
                        c = config.module_fqn_to_config.get("_default", None)
                    if c is not None:
                        quantize_(module, c, filter_fn=lambda x, fqn: True)
                    return
            quantize_(module, self.quantization_config.get_apply_tensor_subclass())
    def _process_model_after_weight_loading(self, model, **kwargs):
        if self.quantization_config.quant_type == "autoquant":
            from torchao import autoquant
            from torchao.quantization import ALL_AUTOQUANT_CLASS_LIST
            model = torch.compile(model, mode="max-autotune")
            model = autoquant(
                model,
                qtensor_class_list=ALL_AUTOQUANT_CLASS_LIST,
                set_inductor_config=False,
                **self.quantization_config.quant_type_kwargs,
            )
            return model
        return
    def is_serializable(self, safe_serialization=None) -> bool:
        if safe_serialization:
            _is_torchao_serializable = type(
                self.quantization_config.quant_type
            ) in SUPPORTED_SAFE_SERIALIZATION_CONFIGS and TORCHAO_VERSION >= version.parse("0.14.0")
            if not _is_torchao_serializable:
                logger.warning(
                    f"torchao quantized model only supports safe serialization for {SUPPORTED_SAFE_SERIALIZATION_CONFIGS}, \
                    and torchao version >= 0.14.0, please set `safe_serialization` to False for \
                    {type(self.quantization_config.quant_type)} and {TORCHAO_VERSION}."
                )
            return _is_torchao_serializable
        _is_torchao_serializable = version.parse(importlib.metadata.version("huggingface_hub")) >= version.parse(
            "0.25.0"
        )
        if not _is_torchao_serializable:
            logger.warning("torchao quantized model is only serializable after huggingface_hub >= 0.25.0 ")
        if self.offload and self.quantization_config.modules_to_not_convert is None:
            logger.warning(
                "The model contains offloaded modules and these modules are not quantized. We don't recommend saving the model as we won't be able to reload them."
                "If you want to specify modules to not quantize, please specify modules_to_not_convert in the quantization_config."
            )
            return False
        return _is_torchao_serializable
    def get_accelerator_warm_up_factor(self):
        if self.quantization_config._get_ao_version() > version.Version("0.9.0"):
            from torchao.core.config import AOBaseConfig
            quant_type = self.quantization_config.quant_type
            if isinstance(quant_type, AOBaseConfig):
                config_name = quant_type.__class__.__name__
                size_digit = fuzzy_match_size(config_name)
                if size_digit == "4":
                    return 8
                else:
                    return 4
        map_to_target_dtype = {
            "int4_weight_only": 8,
            "int8_weight_only": 4,
            "int8_dynamic_activation_int8_weight": 4,
            "autoquant": 4,
        }
        return map_to_target_dtype[self.quantization_config.quant_type]
    @property
    def is_trainable(self) -> bool:
        supported_quant_types_for_training = [
            "int8_weight_only",
            "int8_dynamic_activation_int8_weight",
        ]
        return self.quantization_config.quant_type in supported_quant_types_for_training
    @property
    def is_compileable(self) -> bool:
        return True
    def set_metadata(self, checkpoint_files: list[str]):
        if checkpoint_files[0].endswith(".safetensors"):
            metadata = {}
            for checkpoint in checkpoint_files:
                with safe_open(checkpoint, framework="pt") as f:
                    metadata_ = f.metadata() or {}
                    metadata.update(metadata_)
            self.metadata = metadata