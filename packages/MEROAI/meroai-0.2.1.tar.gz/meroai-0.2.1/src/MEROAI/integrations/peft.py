import importlib
import inspect
import re
from typing import Any, Optional, Union
from packaging import version
from ..utils import (
    check_peft_version,
    find_adapter_config_file,
    is_accelerate_available,
    is_peft_available,
    is_torch_available,
    logging,
)
if is_torch_available():
    import torch
if is_accelerate_available():
    from accelerate import dispatch_model
    from accelerate.utils import get_balanced_memory, infer_auto_device_map
MIN_PEFT_VERSION = "0.5.0"
logger = logging.get_logger(__name__)
VLMS = [
    "aria",
    "ayavision",
    "emu3",
    "fuyu",
    "gotocr2",
    "gemma3",
    "internvl",
    "llava",
    "mistral3",
    "mllama",
    "paligemma",
    "qwen2vl",
    "qwen2_5_vl",
    "videollava",
    "vipllava",
]
class PeftAdapterMixin:
    _hf_peft_config_loaded = False
    def load_adapter(
        self,
        peft_model_id: Optional[str] = None,
        adapter_name: Optional[str] = None,
        revision: Optional[str] = None,
        token: Optional[str] = None,
        device_map: str = "auto",
        max_memory: Optional[str] = None,
        offload_folder: Optional[str] = None,
        offload_index: Optional[int] = None,
        peft_config: Optional[dict[str, Any]] = None,
        adapter_state_dict: Optional[dict[str, "torch.Tensor"]] = None,
        low_cpu_mem_usage: bool = False,
        is_trainable: bool = False,
        adapter_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        peft_load_kwargs = {}
        key_mapping = adapter_kwargs.pop("key_mapping", None) if adapter_kwargs is not None else None
        if key_mapping is None and any(allowed_name in self.__class__.__name__.lower() for allowed_name in VLMS):
            key_mapping = self._checkpoint_conversion_mapping
        if low_cpu_mem_usage:
            min_version_lcmu = "0.13.0"
            if version.parse(importlib.metadata.version("peft")) >= version.parse(min_version_lcmu):
                peft_load_kwargs["low_cpu_mem_usage"] = low_cpu_mem_usage
            else:
                raise ValueError(
                    "The version of PEFT you are using does not support `low_cpu_mem_usage` yet, "
                    f"please install PEFT >= {min_version_lcmu}."
                )
        adapter_name = adapter_name if adapter_name is not None else "default"
        if adapter_kwargs is None:
            adapter_kwargs = {}
        from peft import PeftConfig, inject_adapter_in_model, load_peft_weights
        from peft.utils import set_peft_model_state_dict
        if self._hf_peft_config_loaded and adapter_name in self.peft_config:
            raise ValueError(f"Adapter with name {adapter_name} already exists. Please use a different name.")
        if peft_model_id is None and (adapter_state_dict is None and peft_config is None):
            raise ValueError(
                "You should either pass a `peft_model_id` or a `peft_config` and `adapter_state_dict` to load an adapter."
            )
        if "device" not in adapter_kwargs:
            device = self.device if not hasattr(self, "hf_device_map") else list(self.hf_device_map.values())[0]
        else:
            device = adapter_kwargs.pop("device")
        if isinstance(device, torch.device):
            device = str(device)
        if revision is not None and "revision" not in adapter_kwargs:
            adapter_kwargs["revision"] = revision
        elif revision is not None and "revision" in adapter_kwargs and revision != adapter_kwargs["revision"]:
            logger.error(
                "You passed a `revision` argument both in `adapter_kwargs` and as a standalone argument. "
                "The one in `adapter_kwargs` will be used."
            )
        if "token" in adapter_kwargs:
            token = adapter_kwargs.pop("token")
        if peft_config is None:
            adapter_config_file = find_adapter_config_file(
                peft_model_id,
                token=token,
                **adapter_kwargs,
            )
            if adapter_config_file is None:
                raise ValueError(
                    f"adapter model file not found in {peft_model_id}. Make sure you are passing the correct path to the "
                    "adapter model."
                )
            peft_config = PeftConfig.from_pretrained(
                peft_model_id,
                token=token,
                **adapter_kwargs,
            )
            peft_config.inference_mode = not is_trainable
        inject_adapter_in_model(peft_config, self, adapter_name, **peft_load_kwargs)
        if not self._hf_peft_config_loaded:
            self._hf_peft_config_loaded = True
        if peft_model_id is not None:
            adapter_state_dict = load_peft_weights(peft_model_id, token=token, device=device, **adapter_kwargs)
        processed_adapter_state_dict = {}
        prefix = "base_model.model."
        for key, value in adapter_state_dict.items():
            if key.startswith(prefix):
                new_key = key[len(prefix) :]
            else:
                new_key = key
            if key_mapping:
                for pattern, replacement in key_mapping.items():
                    new_key, n_replace = re.subn(pattern, replacement, new_key)
                    if n_replace > 0:
                        break
            processed_adapter_state_dict[new_key] = value
        incompatible_keys = set_peft_model_state_dict(
            self, processed_adapter_state_dict, adapter_name, **peft_load_kwargs
        )
        if incompatible_keys is not None:
            err_msg = ""
            origin_name = peft_model_id if peft_model_id is not None else "state_dict"
            if hasattr(incompatible_keys, "unexpected_keys") and len(incompatible_keys.unexpected_keys) > 0:
                err_msg = (
                    f"Loading adapter weights from {origin_name} led to unexpected keys not found in the model: "
                    f"{', '.join(incompatible_keys.unexpected_keys)}. "
                )
            missing_keys = getattr(incompatible_keys, "missing_keys", None)
            if missing_keys:
                lora_missing_keys = [k for k in missing_keys if "lora_" in k and adapter_name in k]
                if lora_missing_keys:
                    err_msg += (
                        f"Loading adapter weights from {origin_name} led to missing keys in the model: "
                        f"{', '.join(lora_missing_keys)}"
                    )
            if err_msg:
                logger.warning(err_msg)
        if peft_config.inference_mode:
            self.eval()
        if (
            (getattr(self, "hf_device_map", None) is not None)
            and (len(set(self.hf_device_map.values()).intersection({"cpu", "disk"})) > 0)
            and len(self.peft_config) == 1
        ):
            self._dispatch_accelerate_model(
                device_map=device_map,
                max_memory=max_memory,
                offload_folder=offload_folder,
                offload_index=offload_index,
            )
    def add_adapter(self, adapter_config, adapter_name: Optional[str] = None) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        from peft import PeftConfig, inject_adapter_in_model
        adapter_name = adapter_name or "default"
        if not self._hf_peft_config_loaded:
            self._hf_peft_config_loaded = True
        elif adapter_name in self.peft_config:
            raise ValueError(f"Adapter with name {adapter_name} already exists. Please use a different name.")
        if not isinstance(adapter_config, PeftConfig):
            raise TypeError(f"adapter_config should be an instance of PeftConfig. Got {type(adapter_config)} instead.")
        adapter_config.base_model_name_or_path = self.__dict__.get("name_or_path", None)
        inject_adapter_in_model(adapter_config, self, adapter_name)
        self.set_adapter(adapter_name)
    def set_adapter(self, adapter_name: Union[list[str], str]) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        elif isinstance(adapter_name, list):
            missing = set(adapter_name) - set(self.peft_config)
            if len(missing) > 0:
                raise ValueError(
                    f"Following adapter(s) could not be found: {', '.join(missing)}. Make sure you are passing the correct adapter name(s)."
                    f" current loaded adapters are: {list(self.peft_config.keys())}"
                )
        elif adapter_name not in self.peft_config:
            raise ValueError(
                f"Adapter with name {adapter_name} not found. Please pass the correct adapter name among {list(self.peft_config.keys())}"
            )
        from peft.tuners.tuners_utils import BaseTunerLayer
        from peft.utils import ModulesToSaveWrapper
        _adapters_has_been_set = False
        for _, module in self.named_modules():
            if isinstance(module, (BaseTunerLayer, ModulesToSaveWrapper)):
                if hasattr(module, "set_adapter"):
                    module.set_adapter(adapter_name)
                else:
                    module.active_adapter = adapter_name
                _adapters_has_been_set = True
        if not _adapters_has_been_set:
            raise ValueError(
                "Did not succeeded in setting the adapter. Please make sure you are using a model that supports adapters."
            )
    def disable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        from peft.utils import ModulesToSaveWrapper
        for _, module in self.named_modules():
            if isinstance(module, (BaseTunerLayer, ModulesToSaveWrapper)):
                if hasattr(module, "enable_adapters"):
                    module.enable_adapters(enabled=False)
                else:
                    module.disable_adapters = True
    def enable_adapters(self) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                if hasattr(module, "enable_adapters"):
                    module.enable_adapters(enabled=True)
                else:
                    module.disable_adapters = False
    def active_adapters(self) -> list[str]:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not is_peft_available():
            raise ImportError("PEFT is not available. Please install PEFT to use this function: `pip install peft`.")
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft.tuners.tuners_utils import BaseTunerLayer
        for _, module in self.named_modules():
            if isinstance(module, BaseTunerLayer):
                active_adapters = module.active_adapter
                break
        if isinstance(active_adapters, str):
            active_adapters = [active_adapters]
        return active_adapters
    def get_adapter_state_dict(self, adapter_name: Optional[str] = None, state_dict: Optional[dict] = None) -> dict:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        from peft import get_peft_model_state_dict
        if adapter_name is None:
            adapter_name = self.active_adapters()[0]
        adapter_state_dict = get_peft_model_state_dict(self, state_dict=state_dict, adapter_name=adapter_name)
        return adapter_state_dict
    def _dispatch_accelerate_model(
        self,
        device_map: str,
        max_memory: Optional[int] = None,
        offload_folder: Optional[str] = None,
        offload_index: Optional[int] = None,
    ) -> None:
        dispatch_model_kwargs = {}
        if "offload_index" in inspect.signature(dispatch_model).parameters:
            dispatch_model_kwargs["offload_index"] = offload_index
        no_split_module_classes = self._no_split_modules
        if device_map != "sequential":
            max_memory = get_balanced_memory(
                self,
                max_memory=max_memory,
                no_split_module_classes=no_split_module_classes,
                low_zero=(device_map == "balanced_low_0"),
            )
        if isinstance(device_map, str):
            device_map = infer_auto_device_map(
                self, max_memory=max_memory, no_split_module_classes=no_split_module_classes
            )
        dispatch_model(
            self,
            device_map=device_map,
            offload_dir=offload_folder,
            **dispatch_model_kwargs,
        )
    def delete_adapter(self, adapter_names: Union[list[str], str]) -> None:
        check_peft_version(min_version=MIN_PEFT_VERSION)
        min_version_delete_adapter = "0.18.0"
        if not self._hf_peft_config_loaded:
            raise ValueError("No adapter loaded. Please load an adapter first.")
        def old_delete_adapter(model, adapter_name, prefix=None):
            from peft.tuners.tuners_utils import BaseTunerLayer
            from peft.utils import ModulesToSaveWrapper
            has_modules_to_save = False
            for module in model.modules():
                if isinstance(module, ModulesToSaveWrapper):
                    has_modules_to_save |= True
                    continue
                if isinstance(module, BaseTunerLayer):
                    if hasattr(module, "delete_adapter"):
                        module.delete_adapter(adapter_name)
                    else:
                        raise ValueError(
                            "The version of PEFT you are using is not compatible, please use a version that is greater than 0.6.1"
                        )
            if has_modules_to_save:
                logger.warning(
                    "The deleted adapter contains modules_to_save, which could not be deleted. For this to work, PEFT version "
                    f">= {min_version_delete_adapter} is required."
                )
        if version.parse(importlib.metadata.version("peft")) >= version.parse(min_version_delete_adapter):
            from peft.functional import delete_adapter
        else:
            delete_adapter = old_delete_adapter
        if isinstance(adapter_names, str):
            adapter_names = [adapter_names]
        missing_adapters = [name for name in adapter_names if name not in self.peft_config]
        if missing_adapters:
            raise ValueError(
                f"The following adapter(s) are not present and cannot be deleted: {', '.join(missing_adapters)}"
            )
        prefixes = [f"{self.peft_config[adapter_name].peft_type.value.lower()}_" for adapter_name in adapter_names]
        for adapter_name, prefix in zip(adapter_names, prefixes):
            delete_adapter(self, adapter_name=adapter_name, prefix=prefix)
            if getattr(self, "_hf_peft_config_loaded", False) and hasattr(self, "peft_config"):
                self.peft_config.pop(adapter_name, None)
        if len(self.peft_config) == 0:
            del self.peft_config
            self._hf_peft_config_loaded = False