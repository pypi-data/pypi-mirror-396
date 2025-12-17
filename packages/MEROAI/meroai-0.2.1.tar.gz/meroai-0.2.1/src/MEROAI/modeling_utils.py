import collections
import copy
import functools
import gc
import importlib.metadata
import inspect
import json
import os
import re
import sys
import warnings
from abc import abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from enum import Enum
from functools import partial, wraps
from threading import Thread
from typing import Any, Callable, Optional, TypeVar, Union, get_type_hints
from zipfile import is_zipfile
import torch
from huggingface_hub import split_torch_state_dict_into_shards
from packaging import version
from safetensors import safe_open
from safetensors.torch import load_file as safe_load_file
from safetensors.torch import save_file as safe_save_file
from torch import Tensor, nn
from torch.distributions import constraints
from torch.utils.checkpoint import checkpoint
from .configuration_utils import PretrainedConfig
from .distributed import DistributedConfig
from .dynamic_module_utils import custom_object_save
from .generation import CompileConfig, GenerationConfig
from .integrations import PeftAdapterMixin, deepspeed_config, is_deepspeed_zero3_enabled, is_fsdp_enabled
from .integrations.accelerate import find_tied_parameters, init_empty_weights
from .integrations.deepspeed import _load_state_dict_into_zero3_model
from .integrations.eager_paged import eager_paged_attention_forward
from .integrations.flash_attention import flash_attention_forward
from .integrations.flash_paged import paged_attention_forward
from .integrations.flex_attention import flex_attention_forward
from .integrations.hub_kernels import is_kernel, load_and_register_kernel
from .integrations.sdpa_attention import sdpa_attention_forward
from .integrations.sdpa_paged import sdpa_attention_paged_forward
from .integrations.tensor_parallel import (
    _get_parameter_tp_plan,
    distribute_model,
    initialize_tensor_parallelism,
    repack_weights,
    replace_state_dict_local_with_dtensor,
    shard_and_distribute_module,
    verify_tp_plan,
)
from .loss.loss_utils import LOSS_MAPPING
from .modeling_flash_attention_utils import lazy_import_flash_attention
from .pytorch_utils import id_tensor_storage
from .quantizers import HfQuantizer
from .quantizers.auto import get_hf_quantizer
from .quantizers.quantizers_utils import get_module_from_name
from .safetensors_conversion import auto_conversion
from .utils import (
    ADAPTER_SAFE_WEIGHTS_NAME,
    ADAPTER_WEIGHTS_NAME,
    CONFIG_NAME,
    DUMMY_INPUTS,
    FLAX_WEIGHTS_NAME,
    SAFE_WEIGHTS_INDEX_NAME,
    SAFE_WEIGHTS_NAME,
    TF2_WEIGHTS_NAME,
    TF_WEIGHTS_NAME,
    WEIGHTS_INDEX_NAME,
    WEIGHTS_NAME,
    ContextManagers,
    PushToHubMixin,
    cached_file,
    check_torch_load_is_safe,
    copy_func,
    download_url,
    extract_commit_hash,
    has_file,
    is_accelerate_available,
    is_bitsandbytes_available,
    is_flash_attn_2_available,
    is_flash_attn_3_available,
    is_kernels_available,
    is_offline_mode,
    is_optimum_available,
    is_peft_available,
    is_remote_url,
    is_torch_flex_attn_available,
    is_torch_greater_or_equal,
    is_torch_mlu_available,
    is_torch_npu_available,
    is_torch_xla_available,
    is_torch_xpu_available,
    logging,
)
from .utils.generic import _CAN_RECORD_REGISTRY, GeneralInterface, OutputRecorder
from .utils.hub import create_and_tag_model_card, get_checkpoint_shard_files
from .utils.import_utils import (
    ENV_VARS_TRUE_VALUES,
    is_huggingface_hub_greater_or_equal,
    is_sagemaker_mp_enabled,
    is_torch_fx_proxy,
    is_torchdynamo_compiling,
)
from .utils.quantization_config import BitsAndBytesConfig, QuantizationMethod
if is_accelerate_available():
    from accelerate import dispatch_model, infer_auto_device_map
    from accelerate.hooks import add_hook_to_module
    from accelerate.utils import (
        check_tied_parameters_on_same_device,
        extract_model_from_parallel,
        get_balanced_memory,
        get_max_memory,
        offload_weight,
        save_offload_index,
    )
    accelerate_version = version.parse(importlib.metadata.version("accelerate"))
    if accelerate_version >= version.parse("0.31"):
        from accelerate.utils.modeling import get_state_dict_from_offload
if is_peft_available():
    from .utils import find_adapter_config_file
_torch_distributed_available = torch.distributed.is_available()
_is_dtensor_available = _torch_distributed_available and is_torch_greater_or_equal("2.5")
if _is_dtensor_available:
    from torch.distributed.tensor import DTensor
if is_sagemaker_mp_enabled():
    import smdistributed.modelparallel.torch as smp
    from smdistributed.modelparallel import __version__ as SMP_VERSION
    IS_SAGEMAKER_MP_POST_1_10 = version.parse(SMP_VERSION) >= version.parse("1.10")
else:
    IS_SAGEMAKER_MP_POST_1_10 = False
logger = logging.get_logger(__name__)
XLA_USE_BF16 = os.environ.get("XLA_USE_BF16", "0").upper()
XLA_DOWNCAST_BF16 = os.environ.get("XLA_DOWNCAST_BF16", "0").upper()
SpecificPreTrainedModelType = TypeVar("SpecificPreTrainedModelType", bound="PreTrainedModel")
_init_weights = True
_is_quantized = False
_is_ds_init_called = False
def is_local_dist_rank_0():
    return (
        torch.distributed.is_available()
        and torch.distributed.is_initialized()
        and int(os.environ.get("LOCAL_RANK", "-1")) == 0
    )
TORCH_INIT_FUNCTIONS = {
    "uniform_": nn.init.uniform_,
    "normal_": nn.init.normal_,
    "trunc_normal_": nn.init.trunc_normal_,
    "constant_": nn.init.constant_,
    "xavier_uniform_": nn.init.xavier_uniform_,
    "xavier_normal_": nn.init.xavier_normal_,
    "kaiming_uniform_": nn.init.kaiming_uniform_,
    "kaiming_normal_": nn.init.kaiming_normal_,
    "uniform": nn.init.uniform,
    "normal": nn.init.normal,
    "xavier_uniform": nn.init.xavier_uniform,
    "xavier_normal": nn.init.xavier_normal,
    "kaiming_uniform": nn.init.kaiming_uniform,
    "kaiming_normal": nn.init.kaiming_normal,
}
VLMS = [
    "aria",
    "ayavision",
    "colpali",
    "emu3",
    "fuyu",
    "gotocr2",
    "gemma3",
    "internvl",
    "llava",
    "mistral3",
    "mllama",
    "paligemma",
    "shieldgemma2",
    "qwen2vl",
    "qwen2_5_vl",
    "videollava",
    "vipllava",
]
@contextmanager
def no_init_weights():
    global _init_weights
    old_init_weights = _init_weights
    _init_weights = False
    def _skip_init(*args, **kwargs):
        pass
    for name, init_func in TORCH_INIT_FUNCTIONS.items():
        setattr(torch.nn.init, name, _skip_init)
    try:
        yield
    finally:
        _init_weights = old_init_weights
        for name, init_func in TORCH_INIT_FUNCTIONS.items():
            setattr(torch.nn.init, name, init_func)
@contextmanager
def set_quantized_state():
    global _is_quantized
    _is_quantized = True
    try:
        yield
    finally:
        _is_quantized = False
@contextmanager
def set_zero3_state():
    global _is_ds_init_called
    _is_ds_init_called = True
    try:
        yield
    finally:
        _is_ds_init_called = False
def restore_default_dtype(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        old_dtype = torch.get_default_dtype()
        try:
            return func(*args, **kwargs)
        finally:
            torch.set_default_dtype(old_dtype)
    return _wrapper
def get_torch_context_manager_or_global_device():
    device_in_context = torch.tensor([]).device
    default_device = torch.get_default_device() if is_torch_greater_or_equal("2.3") else torch.device("cpu")
    if device_in_context == default_device:
        if default_device != torch.device("cpu"):
            return default_device
        return None
    return device_in_context
def get_parameter_device(parameter: Union[nn.Module, "ModuleUtilsMixin"]):
    try:
        return next(parameter.parameters()).device
    except StopIteration:
        def find_tensor_attributes(module: nn.Module) -> list[tuple[str, Tensor]]:
            tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
            return tuples
        gen = parameter._named_members(get_members_fn=find_tensor_attributes)
        first_tuple = next(gen)
        return first_tuple[1].device
def get_parameter_dtype(parameter: Union[nn.Module, "ModuleUtilsMixin"]):
    last_dtype = None
    for t in parameter.parameters():
        last_dtype = t.dtype
        if t.is_floating_point():
            if XLA_USE_BF16 in ENV_VARS_TRUE_VALUES and is_torch_xla_available():
                return torch.bfloat16
            if XLA_DOWNCAST_BF16 in ENV_VARS_TRUE_VALUES and is_torch_xla_available():
                if t.dtype == torch.float:
                    return torch.bfloat16
                if t.dtype == torch.double:
                    return torch.float32
            return t.dtype
    if last_dtype is not None:
        return last_dtype
    def find_tensor_attributes(module: nn.Module) -> list[tuple[str, Tensor]]:
        tuples = [(k, v) for k, v in module.__dict__.items() if torch.is_tensor(v)]
        return tuples
    gen = parameter._named_members(get_members_fn=find_tensor_attributes)
    last_tuple = None
    for gen_tuple in gen:
        last_tuple = gen_tuple
        if gen_tuple[1].is_floating_point():
            return gen_tuple[1].dtype
    if last_tuple is not None:
        return last_tuple[1].dtype
    for t in parameter.buffers():
        last_dtype = t.dtype
        if t.is_floating_point():
            return t.dtype
    return last_dtype
def get_state_dict_dtype(state_dict):
    for t in state_dict.values():
        if t.is_floating_point():
            return t.dtype
    return next(state_dict.values()).dtype
def load_sharded_checkpoint(model, folder, strict=True, prefer_safe=True):
    index_file = os.path.join(folder, WEIGHTS_INDEX_NAME)
    safe_index_file = os.path.join(folder, SAFE_WEIGHTS_INDEX_NAME)
    index_present = os.path.isfile(index_file)
    safe_index_present = os.path.isfile(safe_index_file)
    if not index_present and not safe_index_present:
        filenames = (WEIGHTS_INDEX_NAME, SAFE_WEIGHTS_INDEX_NAME)
        raise ValueError(f"Can't find a checkpoint index ({' or '.join(filenames)}) in {folder}.")
    load_safe = safe_index_present and (prefer_safe or not index_present)
    load_index = safe_index_file if load_safe else index_file
    with open(load_index, "r", encoding="utf-8") as f:
        index = json.load(f)
    shard_files = list(set(index["weight_map"].values()))
    loaded_keys = index["weight_map"].keys()
    model_keys = model.state_dict().keys()
    missing_keys = [key for key in model_keys if key not in loaded_keys]
    unexpected_keys = [key for key in loaded_keys if key not in model_keys]
    if strict and (len(missing_keys) > 0 or len(unexpected_keys) > 0):
        error_message = f"Error(s) in loading state_dict for {model.__class__.__name__}"
        if len(missing_keys) > 0:
            str_missing_keys = ",".join([f'"{k}"' for k in missing_keys])
            error_message += f"\nMissing key(s): {str_missing_keys}."
        if len(unexpected_keys) > 0:
            str_unexpected_keys = ",".join([f'"{k}"' for k in unexpected_keys])
            error_message += f"\nMissing key(s): {str_unexpected_keys}."
        raise RuntimeError(error_message)
    if load_safe:
        loader = safe_load_file
    else:
        check_torch_load_is_safe()
        loader = partial(torch.load, map_location="cpu", weights_only=True)
    for shard_file in shard_files:
        state_dict = loader(os.path.join(folder, shard_file))
        model.load_state_dict(state_dict, strict=False)
        del state_dict
        gc.collect()
    return torch.nn.modules.module._IncompatibleKeys(missing_keys, unexpected_keys)
str_to_torch_dtype = {
    "BOOL": torch.bool,
    "U8": torch.uint8,
    "I8": torch.int8,
    "I16": torch.int16,
    "F16": torch.float16,
    "BF16": torch.bfloat16,
    "I32": torch.int32,
    "F32": torch.float32,
    "F64": torch.float64,
    "I64": torch.int64,
    "F8_E4M3": torch.float8_e4m3fn,
    "F8_E5M2": torch.float8_e5m2,
}
if is_torch_greater_or_equal("2.3.0"):
    str_to_torch_dtype["U16"] = torch.uint16
    str_to_torch_dtype["U32"] = torch.uint32
    str_to_torch_dtype["U64"] = torch.uint64
def load_state_dict(
    checkpoint_file: Union[str, os.PathLike],
    is_quantized: bool = False,
    map_location: Optional[Union[str, torch.device]] = "cpu",
    weights_only: bool = True,
):
    if checkpoint_file.endswith(".safetensors"):
        with safe_open(checkpoint_file, framework="pt") as f:
            metadata = f.metadata()
            if metadata is not None and metadata.get("format") not in ["pt", "tf", "flax", "mlx"]:
                raise OSError(
                    f"The safetensors archive passed at {checkpoint_file} does not contain the valid metadata. Make sure "
                    "you save your model with the `save_pretrained` method."
                )
            state_dict = {}
            for k in f.keys():
                if map_location == "meta":
                    _slice = f.get_slice(k)
                    k_dtype = _slice.get_dtype()
                    if k_dtype in str_to_torch_dtype:
                        dtype = str_to_torch_dtype[k_dtype]
                    else:
                        raise ValueError(f"Cannot load safetensors of unknown dtype {k_dtype}")
                    state_dict[k] = torch.empty(size=_slice.get_shape(), dtype=dtype, device="meta")
                else:
                    state_dict[k] = f.get_tensor(k)
            return state_dict
    if weights_only:
        check_torch_load_is_safe()
    try:
        if map_location is None:
            if (
                (
                    is_deepspeed_zero3_enabled()
                    and torch.distributed.is_initialized()
                    and torch.distributed.get_rank() > 0
                )
                or (is_fsdp_enabled() and not is_local_dist_rank_0())
            ) and not is_quantized:
                map_location = "meta"
            else:
                map_location = "cpu"
        extra_args = {}
        if isinstance(checkpoint_file, str) and map_location != "meta" and is_zipfile(checkpoint_file):
            extra_args = {"mmap": True}
        return torch.load(
            checkpoint_file,
            map_location=map_location,
            weights_only=weights_only,
            **extra_args,
        )
    except Exception as e:
        try:
            with open(checkpoint_file) as f:
                if f.read(7) == "version":
                    raise OSError(
                        "You seem to have cloned a repository without having git-lfs installed. Please install "
                        "git-lfs and run `git lfs install` followed by `git lfs pull` in the folder "
                        "you cloned."
                    )
                else:
                    raise ValueError(
                        f"Unable to locate the file {checkpoint_file} which is necessary to load this pretrained "
                        "model. Make sure you have saved the model properly."
                    ) from e
        except (UnicodeDecodeError, ValueError):
            raise OSError(
                f"Unable to load weights from pytorch checkpoint file for '{checkpoint_file}' "
                f"at '{checkpoint_file}'. "
                "If you tried to load a PyTorch model from a TF 2.0 checkpoint, please set from_tf=True."
            )
def _end_ptr(tensor: torch.Tensor) -> int:
    if tensor.nelement():
        stop = tensor.view(-1)[-1].data_ptr() + tensor.element_size()
    else:
        stop = tensor.data_ptr()
    return stop
def _get_tied_weight_keys(module: nn.Module, prefix=""):
    tied_weight_keys = []
    if getattr(module, "_tied_weights_keys", None) is not None:
        names = [f"{prefix}.{k}" if prefix else k for k in module._tied_weights_keys]
        tied_weight_keys.extend(names)
    if getattr(module, "_dynamic_tied_weights_keys", None) is not None:
        names = [f"{prefix}.{k}" if prefix else k for k in module._dynamic_tied_weights_keys]
        tied_weight_keys.extend(names)
    for name, submodule in module.named_children():
        local_prefix = f"{prefix}.{name}" if prefix else name
        tied_weight_keys.extend(_get_tied_weight_keys(submodule, prefix=local_prefix))
    return tied_weight_keys
def _find_disjoint(tensors: list[set[str]], state_dict: dict[str, torch.Tensor]) -> tuple[list[set[str]], list[str]]:
    filtered_tensors = []
    for shared in tensors:
        if len(shared) < 2:
            filtered_tensors.append(shared)
            continue
        areas = []
        for name in shared:
            tensor = state_dict[name]
            areas.append((tensor.data_ptr(), _end_ptr(tensor), name))
        areas.sort()
        _, last_stop, last_name = areas[0]
        filtered_tensors.append({last_name})
        for start, stop, name in areas[1:]:
            if start >= last_stop:
                filtered_tensors.append({name})
            else:
                filtered_tensors[-1].add(name)
            last_stop = stop
    disjoint_tensors = []
    shared_tensors = []
    for tensors in filtered_tensors:
        if len(tensors) == 1:
            disjoint_tensors.append(tensors.pop())
        else:
            shared_tensors.append(tensors)
    return shared_tensors, disjoint_tensors
def _find_identical(tensors: list[set[str]], state_dict: dict[str, torch.Tensor]) -> tuple[list[set[str]], set[str]]:
    shared_tensors = []
    identical = []
    for shared in tensors:
        if len(shared) < 2:
            continue
        areas = collections.defaultdict(set)
        for name in shared:
            tensor = state_dict[name]
            area = (tensor.device, tensor.data_ptr(), _end_ptr(tensor))
            areas[area].add(name)
        if len(areas) == 1:
            identical.append(shared)
        else:
            shared_tensors.append(shared)
    return shared_tensors, identical
def _infer_parameter_dtype(
    model: "PreTrainedModel",
    param_name: str,
    empty_param: torch.Tensor,
    keep_in_fp32_regex: Optional[re.Pattern] = None,
    hf_quantizer: Optional[HfQuantizer] = None,
) -> Union[bool, Optional[torch.dtype]]:
    try:
        old_param = model.get_parameter_or_buffer(param_name)
    except Exception as e:
        if hf_quantizer is not None and hf_quantizer.quantization_config.quant_method in {
            QuantizationMethod.HQQ,
            QuantizationMethod.QUARK,
            QuantizationMethod.MXFP4,
            QuantizationMethod.BITS_AND_BYTES,
        }:
            return True, None
        else:
            raise e
    is_torch_e4m3fn_available = hasattr(torch, "float8_e4m3fn")
    casting_dtype = None
    is_param_float8_e4m3fn = is_torch_e4m3fn_available and empty_param.dtype == torch.float8_e4m3fn
    if empty_param.dtype.is_floating_point and not is_param_float8_e4m3fn:
        if keep_in_fp32_regex is not None and keep_in_fp32_regex.search(param_name):
            casting_dtype = torch.float32
        elif hf_quantizer is not None:
            casting_dtype = model.config._pre_quantization_dtype
        else:
            casting_dtype = old_param.dtype
    return old_param is not None and old_param.is_contiguous(), casting_dtype
def _load_parameter_into_model(model: "PreTrainedModel", param_name: str, tensor: torch.Tensor):
    module, param_type = get_module_from_name(model, param_name)
    module.load_state_dict({param_type: tensor}, strict=False, assign=True)
@torch.no_grad()
def _load_state_dict_into_meta_model(
    model: "PreTrainedModel",
    state_dict: dict,
    shard_file: str,
    reverse_renaming_mapping: dict[str, str],
    device_map: Optional[dict] = None,
    disk_offload_folder: Optional[str] = None,
    disk_offload_index: Optional[dict] = None,
    hf_quantizer: Optional[HfQuantizer] = None,
    keep_in_fp32_regex: Optional[re.Pattern] = None,
    device_mesh: Optional["torch.distributed.device_mesh.DeviceMesh"] = None,
) -> tuple[Optional[dict], Optional[dict]]:
    tensor_device = "cpu"
    if device_map is not None and device_map.get("", None) is not None:
        if device_map[""] not in ("cpu", torch.device("cpu")):
            tensor_device = device_map[""].index if isinstance(device_map[""], torch.device) else device_map[""]
    if device_map is not None:
        device_map_regex = "|".join([re.escape(k) for k in sorted(device_map.keys(), reverse=True)])
    is_quantized = hf_quantizer is not None
    is_safetensors = shard_file.endswith(".safetensors")
    is_meta_state_dict = is_safetensors
    file_pointer = safe_open(shard_file, framework="pt", device=tensor_device) if is_meta_state_dict else None
    params_to_load = list(state_dict.keys())
    for param_name in params_to_load:
        empty_param = state_dict[param_name]
        if is_meta_state_dict:
            serialized_param_name = reverse_renaming_mapping[param_name]
            param = file_pointer.get_slice(serialized_param_name)
        else:
            param = empty_param.to(tensor_device)
        to_contiguous, casting_dtype = _infer_parameter_dtype(
            model,
            param_name,
            empty_param,
            keep_in_fp32_regex,
            hf_quantizer,
        )
        if device_mesh is not None:
            if not is_quantized or not hf_quantizer.param_needs_quantization(model, param_name):
                shard_and_distribute_module(
                    model,
                    param,
                    empty_param,
                    param_name,
                    casting_dtype,
                    to_contiguous,
                    device_mesh.get_local_rank(),
                    device_mesh,
                )
            else:
                sharding_kwargs = {
                    "empty_param": empty_param,
                    "casting_dtype": casting_dtype,
                    "to_contiguous": to_contiguous,
                    "rank": device_mesh.get_local_rank(),
                    "device_mesh": device_mesh,
                }
                hf_quantizer.create_quantized_param(
                    model,
                    param,
                    param_name,
                    device_mesh.get_local_rank(),
                    **sharding_kwargs,
                )
        else:
            param = param[...]
            if casting_dtype is not None:
                param = param.to(casting_dtype)
            if to_contiguous:
                param = param.contiguous()
            if device_map is None:
                param_device = "cpu"
            else:
                module_layer = re.search(device_map_regex, param_name)
                if not module_layer:
                    raise ValueError(f"{param_name} doesn't have any device set.")
                else:
                    param_device = device_map[module_layer.group()]
            if param_device == "disk":
                if not is_safetensors:
                    disk_offload_index = offload_weight(param, param_name, disk_offload_folder, disk_offload_index)
            elif not is_quantized or not hf_quantizer.param_needs_quantization(model, param_name):
                if is_fsdp_enabled():
                    param_device = "cpu" if is_local_dist_rank_0() else "meta"
                _load_parameter_into_model(model, param_name, param.to(param_device))
            else:
                hf_quantizer.create_quantized_param(model, param, param_name, param_device)
                if is_fsdp_enabled() or is_deepspeed_zero3_enabled():
                    param_name = hf_quantizer.get_param_name(param_name)
                    module, param_type = get_module_from_name(model, param_name)
                    value = getattr(module, param_type)
                    if value.device.type == "meta":
                        continue
                    val_kwargs = value.__dict__
                    if not value.is_floating_point():
                        val_kwargs["requires_grad"] = False
                    device = "meta" if is_fsdp_enabled() and not is_local_dist_rank_0() else "cpu"
                    value = type(value)(value.data.to(device), **val_kwargs)
                    setattr(module, param_type, value)
        if not is_meta_state_dict:
            del state_dict[param_name]
    if file_pointer is not None:
        file_pointer.__exit__(None, None, None)
    return disk_offload_index
def load_shard_file(args):
    (
        shard_file,
        state_dict,
        disk_only_shard_files,
        is_quantized,
        device_map,
        hf_quantizer,
        key_renaming_mapping,
        weights_only,
        model,
        reverse_key_renaming_mapping,
        disk_offload_folder,
        disk_offload_index,
        keep_in_fp32_regex,
        device_mesh,
    ) = args
    if shard_file in disk_only_shard_files:
        return [], disk_offload_index
    map_location = "cpu"
    if shard_file.endswith(".safetensors") and not (is_deepspeed_zero3_enabled() and not is_quantized):
        map_location = "meta"
    if shard_file != "":
        state_dict = load_state_dict(
            shard_file, is_quantized=is_quantized, map_location=map_location, weights_only=weights_only
        )
    state_dict = {key_renaming_mapping[k]: v for k, v in state_dict.items() if k in key_renaming_mapping}
    error_msgs = []
    if is_deepspeed_zero3_enabled() and not is_quantized:
        error_msgs += _load_state_dict_into_zero3_model(model, state_dict)
    elif not (is_fsdp_enabled() and not is_local_dist_rank_0() and not is_quantized):
        disk_offload_index = _load_state_dict_into_meta_model(
            model,
            state_dict,
            shard_file,
            reverse_key_renaming_mapping,
            device_map=device_map,
            disk_offload_folder=disk_offload_folder,
            disk_offload_index=disk_offload_index,
            hf_quantizer=hf_quantizer,
            keep_in_fp32_regex=keep_in_fp32_regex,
            device_mesh=device_mesh,
        )
    return error_msgs, disk_offload_index
def load_shard_files_with_threadpool(args_list):
    num_workers = int(os.environ.get("HF_PARALLEL_LOADING_WORKERS", "8"))
    num_workers = min(len(args_list), num_workers)
    logger.info(f"Loading model weights in parallel with {num_workers} workers...")
    error_msgs = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        with logging.tqdm(total=len(args_list), desc="Loading checkpoint shards") as pbar:
            futures = [executor.submit(load_shard_file, arg) for arg in args_list]
            for future in as_completed(futures):
                _error_msgs, disk_offload_index = future.result()
                error_msgs += _error_msgs
                pbar.update(1)
    return error_msgs, disk_offload_index
def _add_variant(weights_name: str, variant: Optional[str] = None) -> str:
    if variant is not None:
        path, name = weights_name.rsplit(".", 1)
        weights_name = f"{path}.{variant}.{name}"
    return weights_name
def _get_resolved_checkpoint_files(
    pretrained_model_name_or_path: Optional[Union[str, os.PathLike]],
    subfolder: str,
    variant: Optional[str],
    gguf_file: Optional[str],
    from_tf: bool,
    from_flax: bool,
    use_safetensors: bool,
    cache_dir: str,
    force_download: bool,
    proxies: Optional[dict[str, str]],
    local_files_only: bool,
    token: Optional[Union[str, bool]],
    user_agent: dict,
    revision: str,
    commit_hash: Optional[str],
    is_remote_code: bool,
    MEROAI_explicit_filename: Optional[str] = None,
) -> tuple[Optional[list[str]], Optional[dict]]:
    is_sharded = False
    if pretrained_model_name_or_path is not None and gguf_file is None:
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if is_local:
            if MEROAI_explicit_filename is not None:
                archive_file = os.path.join(pretrained_model_name_or_path, subfolder, MEROAI_explicit_filename)
                is_sharded = MEROAI_explicit_filename.endswith(".safetensors.index.json")
            elif from_tf and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index")
            ):
                archive_file = os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index")
            elif from_tf and os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME)):
                archive_file = os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME)
            elif from_flax and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)
            ):
                archive_file = os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)
            elif use_safetensors is not False and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_NAME, variant))
            ):
                archive_file = os.path.join(
                    pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_NAME, variant)
                )
            elif use_safetensors is not False and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant))
            ):
                archive_file = os.path.join(
                    pretrained_model_name_or_path, subfolder, _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant)
                )
                is_sharded = True
            elif not use_safetensors and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_NAME, variant))
            ):
                archive_file = os.path.join(
                    pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_NAME, variant)
                )
            elif not use_safetensors and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_INDEX_NAME, variant))
            ):
                archive_file = os.path.join(
                    pretrained_model_name_or_path, subfolder, _add_variant(WEIGHTS_INDEX_NAME, variant)
                )
                is_sharded = True
            elif not use_safetensors and (
                os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF_WEIGHTS_NAME + ".index"))
                or os.path.isfile(os.path.join(pretrained_model_name_or_path, subfolder, TF2_WEIGHTS_NAME))
            ):
                raise OSError(
                    f"Error no file named {_add_variant(WEIGHTS_NAME, variant)} found in directory"
                    f" {pretrained_model_name_or_path} but there is a file for TensorFlow weights. Use"
                    " `from_tf=True` to load this model from those weights."
                )
            elif not use_safetensors and os.path.isfile(
                os.path.join(pretrained_model_name_or_path, subfolder, FLAX_WEIGHTS_NAME)
            ):
                raise OSError(
                    f"Error no file named {_add_variant(WEIGHTS_NAME, variant)} found in directory"
                    f" {pretrained_model_name_or_path} but there is a file for Flax weights. Use `from_flax=True`"
                    " to load this model from those weights."
                )
            elif use_safetensors:
                raise OSError(
                    f"Error no file named {_add_variant(SAFE_WEIGHTS_NAME, variant)} found in directory"
                    f" {pretrained_model_name_or_path}."
                )
            else:
                raise OSError(
                    f"Error no file named {_add_variant(WEIGHTS_NAME, variant)}, {_add_variant(SAFE_WEIGHTS_NAME, variant)},"
                    f" {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME + '.index'} or {FLAX_WEIGHTS_NAME} found in directory"
                    f" {pretrained_model_name_or_path}."
                )
        elif os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path)):
            archive_file = pretrained_model_name_or_path
            is_local = True
        elif os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path + ".index")):
            if not from_tf:
                raise ValueError(
                    f"We found a TensorFlow checkpoint at {pretrained_model_name_or_path + '.index'}, please set "
                    "from_tf to True to load from this checkpoint."
                )
            archive_file = os.path.join(subfolder, pretrained_model_name_or_path + ".index")
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            filename = pretrained_model_name_or_path
            resolved_archive_file = download_url(pretrained_model_name_or_path)
        else:
            if MEROAI_explicit_filename is not None:
                filename = MEROAI_explicit_filename
                is_sharded = MEROAI_explicit_filename.endswith(".safetensors.index.json")
            elif from_tf:
                filename = TF2_WEIGHTS_NAME
            elif from_flax:
                filename = FLAX_WEIGHTS_NAME
            elif use_safetensors is not False:
                filename = _add_variant(SAFE_WEIGHTS_NAME, variant)
            else:
                filename = _add_variant(WEIGHTS_NAME, variant)
            try:
                cached_file_kwargs = {
                    "cache_dir": cache_dir,
                    "force_download": force_download,
                    "proxies": proxies,
                    "local_files_only": local_files_only,
                    "token": token,
                    "user_agent": user_agent,
                    "revision": revision,
                    "subfolder": subfolder,
                    "_raise_exceptions_for_gated_repo": False,
                    "_raise_exceptions_for_missing_entries": False,
                    "_commit_hash": commit_hash,
                }
                resolved_archive_file = cached_file(pretrained_model_name_or_path, filename, **cached_file_kwargs)
                if resolved_archive_file is None and filename == _add_variant(SAFE_WEIGHTS_NAME, variant):
                    resolved_archive_file = cached_file(
                        pretrained_model_name_or_path,
                        _add_variant(SAFE_WEIGHTS_INDEX_NAME, variant),
                        **cached_file_kwargs,
                    )
                    if resolved_archive_file is not None:
                        is_sharded = True
                    elif use_safetensors:
                        if revision == "main":
                            resolved_archive_file, revision, is_sharded = auto_conversion(
                                pretrained_model_name_or_path, **cached_file_kwargs
                            )
                        cached_file_kwargs["revision"] = revision
                        if resolved_archive_file is None:
                            raise OSError(
                                f"{pretrained_model_name_or_path} does not appear to have a file named"
                                f" {_add_variant(SAFE_WEIGHTS_NAME, variant)} or {_add_variant(SAFE_WEIGHTS_INDEX_NAME, variant)} "
                                "and thus cannot be loaded with `safetensors`. Please make sure that the model has "
                                "been saved with `safe_serialization=True` or do not set `use_safetensors=True`."
                            )
                    else:
                        filename = _add_variant(WEIGHTS_NAME, variant)
                        resolved_archive_file = cached_file(
                            pretrained_model_name_or_path, filename, **cached_file_kwargs
                        )
                if resolved_archive_file is None and filename == _add_variant(WEIGHTS_NAME, variant):
                    resolved_archive_file = cached_file(
                        pretrained_model_name_or_path,
                        _add_variant(WEIGHTS_INDEX_NAME, variant),
                        **cached_file_kwargs,
                    )
                    if resolved_archive_file is not None:
                        is_sharded = True
                if not local_files_only and not is_offline_mode():
                    if resolved_archive_file is not None:
                        if (
                            filename in [WEIGHTS_NAME, WEIGHTS_INDEX_NAME]
                            and os.getenv("DISABLE_SAFETENSORS_CONVERSION", None) != "true"
                        ):
                            safe_weights_name = SAFE_WEIGHTS_INDEX_NAME if is_sharded else SAFE_WEIGHTS_NAME
                            has_file_kwargs = {
                                "revision": revision,
                                "proxies": proxies,
                                "token": token,
                                "cache_dir": cache_dir,
                                "local_files_only": local_files_only,
                            }
                            cached_file_kwargs = {
                                "cache_dir": cache_dir,
                                "force_download": force_download,
                                "local_files_only": local_files_only,
                                "user_agent": user_agent,
                                "subfolder": subfolder,
                                "_raise_exceptions_for_gated_repo": False,
                                "_raise_exceptions_for_missing_entries": False,
                                "_commit_hash": commit_hash,
                                **has_file_kwargs,
                            }
                            if (
                                not has_file(pretrained_model_name_or_path, safe_weights_name, **has_file_kwargs)
                                and not is_remote_code
                            ):
                                Thread(
                                    target=auto_conversion,
                                    args=(pretrained_model_name_or_path,),
                                    kwargs={"ignore_errors_during_conversion": True, **cached_file_kwargs},
                                    name="Thread-auto_conversion",
                                ).start()
                    else:
                        has_file_kwargs = {
                            "revision": revision,
                            "proxies": proxies,
                            "token": token,
                            "cache_dir": cache_dir,
                            "local_files_only": local_files_only,
                        }
                        if has_file(pretrained_model_name_or_path, TF2_WEIGHTS_NAME, **has_file_kwargs):
                            raise OSError(
                                f"{pretrained_model_name_or_path} does not appear to have a file named"
                                f" {_add_variant(WEIGHTS_NAME, variant)} but there is a file for TensorFlow weights."
                                " Use `from_tf=True` to load this model from those weights."
                            )
                        elif has_file(pretrained_model_name_or_path, FLAX_WEIGHTS_NAME, **has_file_kwargs):
                            raise OSError(
                                f"{pretrained_model_name_or_path} does not appear to have a file named"
                                f" {_add_variant(WEIGHTS_NAME, variant)} but there is a file for Flax weights. Use"
                                " `from_flax=True` to load this model from those weights."
                            )
                        elif variant is not None and has_file(
                            pretrained_model_name_or_path, WEIGHTS_NAME, **has_file_kwargs
                        ):
                            raise OSError(
                                f"{pretrained_model_name_or_path} does not appear to have a file named"
                                f" {_add_variant(WEIGHTS_NAME, variant)} but there is a file without the variant"
                                f" {variant}. Use `variant=None` to load this model from those weights."
                            )
                        else:
                            raise OSError(
                                f"{pretrained_model_name_or_path} does not appear to have a file named"
                                f" {_add_variant(WEIGHTS_NAME, variant)}, {_add_variant(SAFE_WEIGHTS_NAME, variant)},"
                                f" {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME} or {FLAX_WEIGHTS_NAME}."
                            )
            except OSError:
                raise
            except Exception as e:
                raise OSError(
                    f"Can't load the model for '{pretrained_model_name_or_path}'. If you were trying to load it"
                    " from 'https://huggingface.co/models', make sure you don't have a local directory with the"
                    f" same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a"
                    f" directory containing a file named {_add_variant(WEIGHTS_NAME, variant)},"
                    f" {TF2_WEIGHTS_NAME}, {TF_WEIGHTS_NAME} or {FLAX_WEIGHTS_NAME}."
                ) from e
        if is_local:
            logger.info(f"loading weights file {archive_file}")
            resolved_archive_file = archive_file
        else:
            logger.info(f"loading weights file {filename} from cache at {resolved_archive_file}")
    elif gguf_file:
        if os.path.isfile(gguf_file):
            resolved_archive_file = gguf_file
        else:
            cached_file_kwargs = {
                "cache_dir": cache_dir,
                "force_download": force_download,
                "proxies": proxies,
                "local_files_only": local_files_only,
                "token": token,
                "user_agent": user_agent,
                "revision": revision,
                "subfolder": subfolder,
                "_raise_exceptions_for_gated_repo": False,
                "_raise_exceptions_for_missing_entries": False,
                "_commit_hash": commit_hash,
            }
            resolved_archive_file = cached_file(pretrained_model_name_or_path, gguf_file, **cached_file_kwargs)
    sharded_metadata = None
    if is_sharded:
        checkpoint_files, sharded_metadata = get_checkpoint_shard_files(
            pretrained_model_name_or_path,
            resolved_archive_file,
            cache_dir=cache_dir,
            force_download=force_download,
            proxies=proxies,
            local_files_only=local_files_only,
            token=token,
            user_agent=user_agent,
            revision=revision,
            subfolder=subfolder,
            _commit_hash=commit_hash,
        )
    else:
        checkpoint_files = [resolved_archive_file] if pretrained_model_name_or_path is not None else None
    return checkpoint_files, sharded_metadata
def _get_dtype(
    cls,
    dtype: Optional[Union[str, torch.dtype, dict]],
    checkpoint_files: Optional[list[str]],
    config: PretrainedConfig,
    sharded_metadata: Optional[dict],
    state_dict: Optional[dict],
    weights_only: bool,
) -> tuple[PretrainedConfig, Optional[torch.dtype], Optional[torch.dtype]]:
    dtype_orig = None
    is_sharded = sharded_metadata is not None
    if dtype is not None:
        if isinstance(dtype, str):
            if dtype == "auto":
                if hasattr(config, "dtype") and config.dtype is not None:
                    dtype = config.dtype
                    logger.info(f"Will use dtype={dtype} as defined in model's config object")
                else:
                    if is_sharded and "dtype" in sharded_metadata:
                        dtype = sharded_metadata["dtype"]
                    elif state_dict is not None:
                        dtype = get_state_dict_dtype(state_dict)
                    else:
                        state_dict = load_state_dict(
                            checkpoint_files[0], map_location="meta", weights_only=weights_only
                        )
                        dtype = get_state_dict_dtype(state_dict)
                    logger.info(
                        "Since the `dtype` attribute can't be found in model's config object, "
                        "will use dtype={dtype} as derived from model's weights"
                    )
            elif hasattr(torch, dtype):
                dtype = getattr(torch, dtype)
                config.dtype = dtype
                for sub_config_key in config.sub_configs:
                    sub_config = getattr(config, sub_config_key)
                    sub_config.dtype = dtype
        elif isinstance(dtype, torch.dtype):
            config.dtype = dtype
            for sub_config_key in config.sub_configs:
                sub_config = getattr(config, sub_config_key)
                sub_config.dtype = dtype
        elif isinstance(dtype, dict):
            for key, curr_dtype in dtype.items():
                if hasattr(config, key):
                    value = getattr(config, key)
                    curr_dtype = curr_dtype if not isinstance(curr_dtype, str) else getattr(torch, curr_dtype)
                    value.dtype = curr_dtype
            dtype = dtype.get("")
            dtype = dtype if not isinstance(dtype, str) else getattr(torch, dtype)
            config.dtype = dtype
            if dtype is None:
                dtype = torch.float32
        else:
            raise ValueError(
                f"`dtype` can be one of: `torch.dtype`, `'auto'`, a string of a valid `torch.dtype` or a `dict` with valid `dtype` "
                f"for each sub-config in composite configs, but received {dtype}"
            )
        dtype_orig = cls._set_default_dtype(dtype)
    else:
        default_dtype = torch.get_default_dtype()
        config.dtype = default_dtype
        for key in config.sub_configs:
            value = getattr(config, key)
            value.dtype = default_dtype
    return config, dtype, dtype_orig
def _get_device_map(
    model: "PreTrainedModel",
    device_map: Optional[Union[dict, str]],
    max_memory: Optional[dict],
    hf_quantizer: Optional[HfQuantizer],
    dtype: Optional[torch.dtype],
    keep_in_fp32_regex: Optional[re.Pattern],
) -> dict:
    if isinstance(device_map, str):
        special_dtypes = {}
        if hf_quantizer is not None:
            special_dtypes.update(hf_quantizer.get_special_dtypes_update(model, dtype))
        if keep_in_fp32_regex is not None:
            special_dtypes.update(
                {name: torch.float32 for name, _ in model.named_parameters() if keep_in_fp32_regex.search(name)}
            )
        target_dtype = dtype
        if hf_quantizer is not None:
            target_dtype = hf_quantizer.adjust_target_dtype(target_dtype)
        no_split_modules = model._get_no_split_modules(device_map)
        device_map_kwargs = {"no_split_module_classes": no_split_modules}
        if "special_dtypes" in inspect.signature(infer_auto_device_map).parameters:
            device_map_kwargs["special_dtypes"] = special_dtypes
        elif len(special_dtypes) > 0:
            logger.warning(
                "This model has some weights that should be kept in higher precision, you need to upgrade "
                "`accelerate` to properly deal with them (`pip install --upgrade accelerate`)."
            )
        if device_map != "sequential":
            inferred_max_memory = get_balanced_memory(
                model,
                dtype=target_dtype,
                low_zero=(device_map == "balanced_low_0"),
                max_memory=max_memory,
                **device_map_kwargs,
            )
        else:
            inferred_max_memory = get_max_memory(max_memory)
        if hf_quantizer is not None:
            inferred_max_memory = hf_quantizer.adjust_max_memory(inferred_max_memory)
        for device_name in inferred_max_memory:
            if isinstance(device_name, int):
                if is_torch_xpu_available():
                    unused_memory = torch.xpu.memory_reserved(device_name) - torch.xpu.memory_allocated(device_name)
                else:
                    unused_memory = torch.cuda.memory_reserved(device_name) - torch.cuda.memory_allocated(device_name)
                inferred_max_memory[device_name] += unused_memory
            if max_memory is not None and device_name in max_memory:
                inferred_max_memory[device_name] = min(inferred_max_memory[device_name], max_memory[device_name])
        device_map_kwargs["max_memory"] = inferred_max_memory
        device_map = infer_auto_device_map(model, dtype=target_dtype, **device_map_kwargs)
        if hf_quantizer is not None:
            hf_quantizer.validate_environment(device_map=device_map)
    elif device_map is not None:
        tied_params = find_tied_parameters(model)
        check_tied_parameters_on_same_device(tied_params, device_map)
    return device_map
def _find_missing_and_unexpected_keys(
    model: "PreTrainedModel",
    original_checkpoint_keys: list[str],
    checkpoint_keys: list[str],
    loading_base_model_from_task_state_dict: bool,
    hf_quantizer: Optional[HfQuantizer],
) -> tuple[list[str], list[str]]:
    prefix = model.base_model_prefix
    expected_keys = list(model.state_dict().keys())
    if hf_quantizer is not None:
        expected_keys = hf_quantizer.update_expected_keys(model, expected_keys, checkpoint_keys)
    missing_keys = sorted(set(expected_keys) - set(checkpoint_keys))
    unexpected_keys = set(checkpoint_keys) - set(expected_keys)
    if loading_base_model_from_task_state_dict:
        task_specific_keys = [k for k in original_checkpoint_keys if not k.startswith(f"{prefix}.")]
        unexpected_keys.update(task_specific_keys)
    model_buffers = {n for n, _ in model.named_buffers()}
    unexpected_keys = sorted(unexpected_keys - model_buffers)
    tied_params = find_tied_parameters(model)
    for group in tied_params:
        missing_in_group = [k for k in missing_keys if k in group]
        if len(missing_in_group) > 0 and len(missing_in_group) < len(group):
            missing_keys = [k for k in missing_keys if k not in missing_in_group]
    if hf_quantizer is not None:
        missing_keys = hf_quantizer.update_missing_keys(model, missing_keys, prefix)
        unexpected_keys = hf_quantizer.update_unexpected_keys(model, unexpected_keys)
    return missing_keys, unexpected_keys
def _find_mismatched_keys(
    model: "PreTrainedModel",
    state_dict: Optional[dict],
    checkpoint_files: Optional[list[str]],
    ignore_mismatched_sizes: bool,
    keys_to_rename_mapping: dict[str, str],
    is_quantized: bool,
    weights_only: bool,
) -> tuple[list[str], list[tuple[int, int]]]:
    if not ignore_mismatched_sizes:
        return [], []
    if state_dict is not None:
        checkpoint_files = [""]
    model_state_dict = model.state_dict()
    mismatched_keys = []
    mismatched_shapes = []
    for shard_file in checkpoint_files:
        if shard_file != "":
            state_dict = load_state_dict(
                shard_file, is_quantized=is_quantized, map_location="meta", weights_only=weights_only
            )
        new_state_dict = {keys_to_rename_mapping[k]: v for k, v in state_dict.items() if k in keys_to_rename_mapping}
        for key, tensor in new_state_dict.items():
            if key in model_state_dict and tensor.shape != model_state_dict[key].shape:
                if not (
                    is_quantized and tensor.shape[-1] == 1 and tensor.numel() * 2 == model_state_dict[key].numel()
                ):
                    mismatched_keys.append(key)
                    mismatched_shapes.append((tensor.shape, model_state_dict[key].shape))
    return mismatched_keys, mismatched_shapes
class PipelineParallel(Enum):
    inputs = 0
    outputs = 1
class ModuleUtilsMixin:
    @staticmethod
    def _hook_rss_memory_pre_forward(module, *args, **kwargs):
        try:
            import psutil
        except ImportError:
            raise ImportError("You need to install psutil (pip install psutil) to use memory tracing.")
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        module.mem_rss_pre_forward = mem.rss
        return None
    @staticmethod
    def _hook_rss_memory_post_forward(module, *args, **kwargs):
        try:
            import psutil
        except ImportError:
            raise ImportError("You need to install psutil (pip install psutil) to use memory tracing.")
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        module.mem_rss_post_forward = mem.rss
        mem_rss_diff = module.mem_rss_post_forward - module.mem_rss_pre_forward
        module.mem_rss_diff = mem_rss_diff + (module.mem_rss_diff if hasattr(module, "mem_rss_diff") else 0)
        return None
    def add_memory_hooks(self):
        for module in self.modules():
            module.register_forward_pre_hook(self._hook_rss_memory_pre_forward)
            module.register_forward_hook(self._hook_rss_memory_post_forward)
        self.reset_memory_hooks_state()
    def reset_memory_hooks_state(self):
        for module in self.modules():
            module.mem_rss_diff = 0
            module.mem_rss_post_forward = 0
            module.mem_rss_pre_forward = 0
    @property
    def device(self) -> torch.device:
        return get_parameter_device(self)
    @property
    def dtype(self) -> torch.dtype:
        return get_parameter_dtype(self)
    def invert_attention_mask(self, encoder_attention_mask: Tensor) -> Tensor:
        if encoder_attention_mask.dim() == 3:
            encoder_extended_attention_mask = encoder_attention_mask[:, None, :, :]
        if encoder_attention_mask.dim() == 2:
            encoder_extended_attention_mask = encoder_attention_mask[:, None, None, :]
        encoder_extended_attention_mask = encoder_extended_attention_mask.to(dtype=self.dtype)
        encoder_extended_attention_mask = (1.0 - encoder_extended_attention_mask) * torch.finfo(self.dtype).min
        return encoder_extended_attention_mask
    @staticmethod
    def create_extended_attention_mask_for_decoder(input_shape, attention_mask, device=None):
        if device is not None:
            warnings.warn(
                "The `device` argument is deprecated and will be removed in v5 of MEROAI.", FutureWarning
            )
        else:
            device = attention_mask.device
        batch_size, seq_length = input_shape
        seq_ids = torch.arange(seq_length, device=device)
        causal_mask = seq_ids[None, None, :].repeat(batch_size, seq_length, 1) <= seq_ids[None, :, None]
        causal_mask = causal_mask.to(attention_mask.dtype)
        if causal_mask.shape[1] < attention_mask.shape[1]:
            prefix_seq_len = attention_mask.shape[1] - causal_mask.shape[1]
            causal_mask = torch.cat(
                [
                    torch.ones((batch_size, seq_length, prefix_seq_len), device=device, dtype=causal_mask.dtype),
                    causal_mask,
                ],
                axis=-1,
            )
        extended_attention_mask = causal_mask[:, None, :, :] * attention_mask[:, None, None, :]
        return extended_attention_mask
    def get_extended_attention_mask(
        self,
        attention_mask: Tensor,
        input_shape: tuple[int, ...],
        device: Optional[torch.device] = None,
        dtype: Optional[torch.dtype] = None,
    ) -> Tensor:
        if dtype is None:
            dtype = self.dtype
        if not (attention_mask.dim() == 2 and self.config.is_decoder):
            if device is not None:
                warnings.warn(
                    "The `device` argument is deprecated and will be removed in v5 of MEROAI.", FutureWarning
                )
        if attention_mask.dim() == 3:
            extended_attention_mask = attention_mask[:, None, :, :]
        elif attention_mask.dim() == 2:
            if self.config.is_decoder:
                extended_attention_mask = ModuleUtilsMixin.create_extended_attention_mask_for_decoder(
                    input_shape, attention_mask, device
                )
            else:
                extended_attention_mask = attention_mask[:, None, None, :]
        else:
            raise ValueError(
                f"Wrong shape for input_ids (shape {input_shape}) or attention_mask (shape {attention_mask.shape})"
            )
        extended_attention_mask = extended_attention_mask.to(dtype=dtype)
        extended_attention_mask = (1.0 - extended_attention_mask) * torch.finfo(dtype).min
        return extended_attention_mask
    def get_head_mask(
        self, head_mask: Optional[Tensor], num_hidden_layers: int, is_attention_chunked: bool = False
    ) -> Tensor:
        if head_mask is not None:
            head_mask = self._convert_head_mask_to_5d(head_mask, num_hidden_layers)
            if is_attention_chunked is True:
                head_mask = head_mask.unsqueeze(-1)
        else:
            head_mask = [None] * num_hidden_layers
        return head_mask
    def _convert_head_mask_to_5d(self, head_mask, num_hidden_layers):
        if head_mask.dim() == 1:
            head_mask = head_mask.unsqueeze(0).unsqueeze(0).unsqueeze(-1).unsqueeze(-1)
            head_mask = head_mask.expand(num_hidden_layers, -1, -1, -1, -1)
        elif head_mask.dim() == 2:
            head_mask = head_mask.unsqueeze(1).unsqueeze(-1).unsqueeze(-1)
        assert head_mask.dim() == 5, f"head_mask.dim != 5, instead {head_mask.dim()}"
        head_mask = head_mask.to(dtype=self.dtype)
        return head_mask
    def num_parameters(self, only_trainable: bool = False, exclude_embeddings: bool = False) -> int:
        if exclude_embeddings:
            embedding_param_names = [
                f"{name}.weight" for name, module_type in self.named_modules() if isinstance(module_type, nn.Embedding)
            ]
            total_parameters = [
                parameter for name, parameter in self.named_parameters() if name not in embedding_param_names
            ]
        else:
            total_parameters = list(self.parameters())
        total_numel = []
        is_loaded_in_4bit = getattr(self, "is_loaded_in_4bit", False)
        if is_loaded_in_4bit:
            if is_bitsandbytes_available():
                import bitsandbytes as bnb
            else:
                raise ValueError(
                    "bitsandbytes is not installed but it seems that the model has been loaded in 4bit precision, something went wrong"
                    " make sure to install bitsandbytes with `pip install bitsandbytes`. You also need a GPU. "
                )
        for param in total_parameters:
            if param.requires_grad or not only_trainable:
                if is_loaded_in_4bit and isinstance(param, bnb.nn.Params4bit):
                    if hasattr(param, "element_size"):
                        num_bytes = param.element_size()
                    elif hasattr(param, "quant_storage"):
                        num_bytes = param.quant_storage.itemsize
                    else:
                        num_bytes = 1
                    total_numel.append(param.numel() * 2 * num_bytes)
                else:
                    total_numel.append(param.numel())
        return sum(total_numel)
    def estimate_tokens(self, input_dict: dict[str, Union[torch.Tensor, Any]]) -> int:
        if not hasattr(self, "warnings_issued"):
            self.warnings_issued = {}
        if self.main_input_name in input_dict:
            return input_dict[self.main_input_name].numel()
        elif "estimate_tokens" not in self.warnings_issued:
            logger.warning(
                "Could not estimate the number of tokens of the input, floating-point operations will not be computed"
            )
            self.warnings_issued["estimate_tokens"] = True
        return 0
    def floating_point_ops(
        self, input_dict: dict[str, Union[torch.Tensor, Any]], exclude_embeddings: bool = True
    ) -> int:
        return 6 * self.estimate_tokens(input_dict) * self.num_parameters(exclude_embeddings=exclude_embeddings)
class EmbeddingAccessMixin:
    _input_embed_layer = "embed_tokens"
    def get_input_embeddings(self) -> nn.Module:
        name = getattr(self, "_input_embed_layer", "embed_tokens")
        if (default_embedding := getattr(self, name, None)) is not None:
            return default_embedding
        if hasattr(self, "model") and hasattr(self.model, "embed_tokens"):
            return self.model.embed_tokens
        elif hasattr(self, "embed_tokens"):
            return self.embed_tokens
        else:
            base_model = getattr(self, "base_model_prefix", None)
            if base_model is not None:
                base_model = getattr(self, base_model, None)
                if base_model is not None and base_model is not self:
                    return base_model.get_input_embeddings()
            raise NotImplementedError(
                f"`get_input_embeddings` not auto‑handled for {self.__class__.__name__}; "
                "please override in the subclass."
            )
    def set_input_embeddings(self, value: nn.Module):
        name = getattr(self, "_input_embed_layer", "embed_tokens")
        if hasattr(self, "model") and hasattr(self.model, name):
            setattr(self.model, name, value)
        elif hasattr(self, name):
            setattr(self, name, value)
        elif getattr(self, self.base_model_prefix, self) is not self:
            base_model = getattr(self, self.base_model_prefix, self)
            base_model.set_input_embeddings(value)
        else:
            raise NotImplementedError(
                f"`set_input_embeddings` not auto‑handled for {self.__class__.__name__}; please override in the subclass."
            )
    def get_output_embeddings(self):
        if not hasattr(self, "lm_head"):
            return None
        try:
            self.get_input_embeddings()
        except NotImplementedError:
            return None
        return self.lm_head
    def set_output_embeddings(self, new_embeddings):
        if getattr(self, "lm_head"):
            self.lm_head = new_embeddings
class PreTrainedModel(nn.Module, EmbeddingAccessMixin, ModuleUtilsMixin, PushToHubMixin, PeftAdapterMixin):
    config_class = None
    base_model_prefix = ""
    main_input_name = "input_ids"
    model_tags = None
    _checkpoint_conversion_mapping = {}
    _auto_class = None
    _no_split_modules = None
    _skip_keys_device_placement = None
    _keep_in_fp32_modules = None
    _keep_in_fp32_modules_strict = None
    _keys_to_ignore_on_load_missing = None
    _keys_to_ignore_on_load_unexpected = None
    _keys_to_ignore_on_save = None
    _tied_weights_keys = None
    is_parallelizable = False
    supports_gradient_checkpointing = False
    _is_stateful = False
    _supports_flash_attn = False
    _supports_sdpa = False
    _supports_flex_attn = False
    _can_compile_fullgraph = False
    _tp_plan = None
    _tp_size = None
    _pp_plan = None
    _supports_attention_backend = False
    _can_record_outputs = None
    @property
    @torch._dynamo.allow_in_graph
    def can_record_outputs(self) -> dict[str, OutputRecorder]:
        return self._can_record_outputs or {}
    @property
    def dummy_inputs(self) -> dict[str, torch.Tensor]:
        return {"input_ids": torch.tensor(DUMMY_INPUTS)}
    @property
    def framework(self) -> str:
        return "pt"
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        child_annotation = cls.__dict__.get("__annotations__", {}).get("config", None)
        child_attribute = cls.__dict__.get("config_class", None)
        full_annotation = get_type_hints(cls).get("config", None)
        full_attribute = cls.config_class
        if child_attribute is not None:
            cls.config_class = child_attribute
        elif child_annotation is not None:
            cls.config_class = child_annotation
        elif full_attribute is not None:
            cls.config_class = full_attribute
        elif full_annotation is not None:
            cls.config_class = full_annotation
    def __init__(self, config: PretrainedConfig, *inputs, **kwargs):
        super().__init__()
        if not isinstance(config, PretrainedConfig):
            raise TypeError(
                f"Parameter config in `{self.__class__.__name__}(config)` should be an instance of class "
                "`PretrainedConfig`. To create a model from a pretrained model use "
                f"`model = {self.__class__.__name__}.from_pretrained(PRETRAINED_MODEL_NAME)`"
            )
        self.config = config
        self.config._attn_implementation_internal = self._check_and_adjust_attn_implementation(
            self.config._attn_implementation, is_init_check=True
        )
        loss_type = self.__class__.__name__
        if loss_type not in LOSS_MAPPING:
            loss_groups = f"({'|'.join(LOSS_MAPPING)})"
            loss_type = re.findall(loss_groups, self.__class__.__name__)
            if len(loss_type) > 0:
                loss_type = loss_type[0]
            else:
                loss_type = None
        self.loss_type = loss_type
        self.name_or_path = config.name_or_path
        self.warnings_issued = {}
        self.generation_config = GenerationConfig.from_model_config(config) if self.can_generate() else None
        self._keep_in_fp32_modules = copy.copy(self.__class__._keep_in_fp32_modules)
        self._keep_in_fp32_modules_strict = copy.copy(self.__class__._keep_in_fp32_modules_strict)
        self._no_split_modules = self._no_split_modules or []
        _CAN_RECORD_REGISTRY[str(self.__class__)] = self._can_record_outputs
    def post_init(self):
        self.init_weights()
        self._backward_compatibility_gradient_checkpointing()
        if self._keep_in_fp32_modules is not None or self._keep_in_fp32_modules_strict is not None:
            all_parameters = {name for name, _ in self.named_parameters() if len(name) > 0}
            unique_module_names = set()
            for param in all_parameters:
                unique_module_names.update(
                    [name for name in param.split(".") if not name.isnumeric() and name not in ["weight", "bias"]]
                )
            if self._keep_in_fp32_modules is not None:
                for module in self._keep_in_fp32_modules:
                    if module not in unique_module_names:
                        raise ValueError(
                            f"{module} was specified in the `_keep_in_fp32_modules` list, but is not part of the modules in"
                            f" {self.__class__.__name__}"
                        )
            if self._keep_in_fp32_modules_strict is not None:
                for module in self._keep_in_fp32_modules_strict:
                    if module not in unique_module_names:
                        raise ValueError(
                            f"{module} was specified in the `_keep_in_fp32_modules_strict` list, but is not part of the modules in"
                            f" {self.__class__.__name__}"
                        )
        self._pp_plan = self.config.base_model_pp_plan.copy() if self.config.base_model_pp_plan is not None else {}
        self._tp_plan = self.config.base_model_tp_plan.copy() if self.config.base_model_tp_plan is not None else {}
        self._ep_plan = self.config.base_model_ep_plan.copy() if self.config.base_model_ep_plan is not None else {}
        for name, module in self.named_children():
            if plan := getattr(module, "_ep_plan", None):
                self._ep_plan.update({f"{name}.{k}": v for k, v in plan.copy().items()})
            if plan := getattr(module, "_tp_plan", None):
                self._tp_plan.update({f"{name}.{k}": v for k, v in plan.copy().items()})
            if plan := getattr(module, "_pp_plan", None):
                self._pp_plan.update({f"{name}.{k}": v for k, v in plan.copy().items()})
    @property
    def tp_plan(self) -> dict[str, str]:
        if hasattr(self.config, "distributed_config") and self.config.distributed_config.enable_expert_parallel:
            return self._ep_plan
        return self._tp_plan
    @property
    def pp_plan(self) -> dict[str, tuple[str, str]]:
        return self._pp_plan
    @tp_plan.setter
    def tp_plan(self, plan: dict[str, str]):
        if plan is not None:
            from .integrations.tensor_parallel import ALL_PARALLEL_STYLES
            for layer_pattern, parallel_style in plan.items():
                if parallel_style not in ALL_PARALLEL_STYLES:
                    raise ValueError(
                        f"Unsupported tensor parallel style '{parallel_style}' for layer '{layer_pattern}'. "
                        f"Supported styles are {list(ALL_PARALLEL_STYLES.keys())}"
                    )
            if hasattr(self, "named_parameters"):
                model_param_names = [name for name, _ in self.named_parameters()]
                if model_param_names:
                    for layer_pattern in plan.keys():
                        regex_pattern = layer_pattern.replace("*", r"\d+")
                        pattern_matched = False
                        for param_name in model_param_names:
                            if re.match(regex_pattern, param_name):
                                pattern_matched = True
                                break
                        if not pattern_matched:
                            pattern_parts = layer_pattern.split(".")
                            flexible_matched = False
                            for param_name in model_param_names:
                                param_parts = param_name.split(".")
                                if len(pattern_parts) <= len(param_parts):
                                    match_count = 0
                                    for i, pattern_part in enumerate(pattern_parts):
                                        if pattern_part == "*":
                                            match_count += 1
                                        elif i < len(param_parts) and pattern_part == param_parts[i]:
                                            match_count += 1
                                    if match_count == len(pattern_parts):
                                        flexible_matched = True
                                        break
                            if not flexible_matched:
                                warnings.warn(
                                    f"Layer pattern '{layer_pattern}' does not match any parameters in the model. "
                                    f"This rule may not be applied during tensor parallelization."
                                )
        self._tp_plan = plan if plan is not None else {}
    @pp_plan.setter
    def pp_plan(self, plan: dict[str, tuple[str, str]]):
        self._pp_plan = plan
    def dequantize(self):
        hf_quantizer = getattr(self, "hf_quantizer", None)
        if hf_quantizer is None:
            raise ValueError("You need to first quantize your model in order to dequantize it")
        return hf_quantizer.dequantize(self)
    def _backward_compatibility_gradient_checkpointing(self):
        if self.supports_gradient_checkpointing and getattr(self.config, "gradient_checkpointing", False):
            self.gradient_checkpointing_enable()
            delattr(self.config, "gradient_checkpointing")
    def add_model_tags(self, tags: Union[list[str], str]) -> None:
        if isinstance(tags, str):
            tags = [tags]
        if self.model_tags is None:
            self.model_tags = []
        for tag in tags:
            if tag not in self.model_tags:
                self.model_tags.append(tag)
    @classmethod
    @restore_default_dtype
    def _from_config(cls, config, **kwargs):
        dtype = kwargs.pop("dtype", config.dtype)
        if (torch_dtype := kwargs.pop("torch_dtype", None)) is not None:
            logger.warning_once("`torch_dtype` is deprecated! Use `dtype` instead!")
            dtype = dtype if dtype != config.dtype else torch_dtype
        if isinstance(dtype, str):
            dtype = getattr(torch, dtype)
        dtype_orig = None
        if dtype is not None:
            dtype_orig = cls._set_default_dtype(dtype)
        if "attn_implementation" in kwargs:
            config._attn_implementation = kwargs.pop("attn_implementation")
        if is_deepspeed_zero3_enabled() and not _is_quantized and not _is_ds_init_called:
            logger.info("Detected DeepSpeed ZeRO-3: activating zero.init() for this model")
            import deepspeed
            init_contexts = [deepspeed.zero.Init(config_dict_or_path=deepspeed_config()), set_zero3_state()]
            with ContextManagers(init_contexts):
                model = cls(config, **kwargs)
        else:
            model = cls(config, **kwargs)
        if dtype_orig is not None:
            torch.set_default_dtype(dtype_orig)
        return model
    @classmethod
    def _set_default_dtype(cls, dtype: torch.dtype) -> torch.dtype:
        if not dtype.is_floating_point:
            raise ValueError(
                f"Can't instantiate {cls.__name__} model under dtype={dtype} since it is not a floating point dtype"
            )
        logger.info(f"Instantiating {cls.__name__} model under default dtype {dtype}.")
        dtype_orig = torch.get_default_dtype()
        torch.set_default_dtype(dtype)
        return dtype_orig
    @property
    def base_model(self) -> nn.Module:
        return getattr(self, self.base_model_prefix, self)
    @classmethod
    def can_generate(cls) -> bool:
        if "GenerationMixin" in str(cls.__bases__):
            return True
        for base in cls.__bases__:
            if not hasattr(base, "can_generate"):
                continue
            if "PreTrainedModel" not in str(base) and base.can_generate():
                return True
        if hasattr(cls, "prepare_inputs_for_generation"):
            logger.warning(
                f"{cls.__name__} has generative capabilities, as `prepare_inputs_for_generation` is explicitly "
                "defined. However, it doesn't directly inherit from `GenerationMixin`. From 👉v4.50👈 onwards, "
                "`PreTrainedModel` will NOT inherit from `GenerationMixin`, and this model will lose the ability "
                "to call `generate` and other related functions."
                "\n  - If you're using `trust_remote_code=True`, you can get rid of this warning by loading the "
                "model with an auto class. See https://huggingface.co/docs/MEROAI/en/model_doc/auto#auto-classes"
                "\n  - If you are the owner of the model architecture code, please modify your model class such that "
                "it inherits from `GenerationMixin` (after `PreTrainedModel`, otherwise you'll get an exception)."
                "\n  - If you are not the owner of the model architecture class, please contact the model code owner "
                "to update it."
            )
        return False
    def _flash_attn_2_can_dispatch(self, is_init_check: bool = False) -> bool:
        dtype = self.config.dtype
        if not (self._supports_flash_attn or getattr(self, "_supports_flash_attn_2", False)):
            raise ValueError(
                f"{self.__class__.__name__} does not support Flash Attention 2.0 yet. Please request to add support where"
                f" the model is hosted, on its model hub page: https://huggingface.co/{self.config._name_or_path}/discussions/new"
                " or in the MEROAI GitHub repo: https://github.com/huggingface/MEROAI/issues/new"
            )
        if not is_flash_attn_2_available():
            preface = "FlashAttention2 has been toggled on, but it cannot be used due to the following error:"
            install_message = "Please refer to the documentation of https://huggingface.co/docs/MEROAI/perf_infer_gpu_one#flashattention-2 to install Flash Attention 2."
            if is_torch_npu_available():
                logger.info("Detect using FlashAttention2 on Ascend NPU.")
                return True
            if importlib.util.find_spec("flash_attn") is None:
                raise ImportError(f"{preface} the package flash_attn seems to be not installed. {install_message}")
            else:
                flash_attention_version = version.parse(importlib.metadata.version("flash_attn"))
                if torch.version.cuda:
                    if flash_attention_version < version.parse("2.1.0"):
                        raise ImportError(
                            f"{preface} you need flash_attn package version to be greater or equal than 2.1.0. Detected version {flash_attention_version}. {install_message}"
                        )
                    elif not torch.cuda.is_available():
                        raise ValueError(
                            f"{preface} Flash Attention 2 is not available on CPU. Please make sure torch can access a CUDA device."
                        )
                    else:
                        raise ImportError(f"{preface} Flash Attention 2 is not available. {install_message}")
                elif torch.version.hip:
                    if flash_attention_version < version.parse("2.0.4"):
                        raise ImportError(
                            f"{preface} you need flash_attn package version to be greater or equal than 2.0.4. Detected version {flash_attention_version}. {install_message}"
                        )
                    else:
                        raise ImportError(f"{preface} Flash Attention 2 is not available. {install_message}")
        if dtype is None:
            logger.warning_once(
                "You are attempting to use Flash Attention 2 without specifying a torch dtype. This might lead to unexpected behaviour"
            )
        elif dtype is not None and dtype not in [torch.float16, torch.bfloat16]:
            logger.warning_once(
                "Flash Attention 2 only supports torch.float16 and torch.bfloat16 dtypes, but"
                f" the current dype in {self.__class__.__name__} is {dtype}. You should run training or inference using Automatic Mixed-Precision via the `with torch.autocast(device_type='torch_device'):` decorator,"
                ' or load the model with the `dtype` argument. Example: `model = AutoModel.from_pretrained("openai/whisper-tiny", attn_implementation="flash_attention_2", dtype=torch.float16)`'
            )
        if not is_init_check:
            if getattr(self, "use_bettertransformer", False):
                raise ValueError(
                    "Flash Attention 2 and BetterTransformer API are not compatible. Please make sure to disable BetterMEROAI by doing model.reverse_bettertransformer()"
                )
            param_devices = list({param.device for param in self.parameters()})
            if len(param_devices) == 1 and param_devices[0].type == "cpu":
                if torch.cuda.is_available():
                    logger.warning_once(
                        "You are attempting to use Flash Attention 2 with a model not initialized on GPU. Make sure to move the model to GPU"
                        " after initializing it on CPU with `model.to('cuda')`."
                    )
                elif is_torch_mlu_available():
                    logger.warning_once(
                        "You are attempting to use Flash Attention 2 with a model not initialized on MLU. Make sure to move the model to MLU"
                        " after initializing it on CPU with `model.to('mlu')`."
                    )
                else:
                    raise ValueError(
                        "You are attempting to use Flash Attention 2 with a model not initialized on GPU and with no GPU available. "
                        "This is not supported yet. Please make sure to have access to a GPU and either initialise the model on a GPU by passing a device_map "
                        "or initialising the model on CPU and then moving it to GPU."
                    )
        return True
    def _flash_attn_3_can_dispatch(self, is_init_check: bool = False) -> bool:
        dtype = self.config.dtype
        if not self._supports_flash_attn:
            raise ValueError(
                f"{self.__class__.__name__} does not support Flash Attention 3 yet. Please request to add support where"
                f" the model is hosted, on its model hub page: https://huggingface.co/{self.config._name_or_path}/discussions/new"
                " or in the MEROAI GitHub repo: https://github.com/huggingface/MEROAI/issues/new"
            )
        if not is_flash_attn_3_available():
            preface = "FlashAttention3 has been toggled on, but it cannot be used due to the following error:"
            if importlib.util.find_spec("flash_attn_3") is None:
                raise ImportError(f"{preface} the package flash_attn_3 seems to be not installed.")
            if torch.cuda.is_available():
                major, _ = torch.cuda.get_device_capability()
                if major < 9:
                    raise ValueError(
                        f"{preface} Flash Attention 3 requires compute capability >= 9.0, but found {torch.cuda.get_device_capability()} with compute capability {major}.0."
                    )
                else:
                    raise ImportError(f"{preface} Flash Attention 3 is not available.")
            else:
                raise ValueError(
                    f"{preface} Flash Attention 3 is not available on CPU. Please make sure torch can access a CUDA device."
                )
        if dtype is None:
            logger.warning_once(
                "You are attempting to use Flash Attention 3 without specifying a torch dtype. This might lead to unexpected behaviour"
            )
        elif dtype is not None and dtype not in [torch.float16, torch.bfloat16]:
            logger.warning_once(
                "Flash Attention 3 only supports torch.float16 and torch.bfloat16 dtypes, but"
                f" the current dype in {self.__class__.__name__} is {dtype}. You should run training or inference using Automatic Mixed-Precision via the `with torch.autocast(device_type='torch_device'):` decorator,"
                ' or load the model with the `dtype` argument. Example: `model = AutoModel.from_pretrained("meta-llama/Llama-3.2-1B", attn_implementation="flash_attention_3", dtype=torch.float16)`'
            )
        if getattr(self.config, "alibi", False) or getattr(self.config, "use_alibi", False):
            raise ValueError("Model is configured to use ALiBi, which is not supported by Flash Attention 3.")
        if hasattr(self.config, "attention_dropout") and self.config.attention_dropout > 0:
            raise ValueError(
                f"Model has attention_dropout={self.config.attention_dropout}, which is not supported by Flash Attention 3."
            )
        if not is_init_check:
            param_devices = list({param.device for param in self.parameters()})
            if len(param_devices) == 1 and param_devices[0].type == "cpu":
                if torch.cuda.is_available():
                    logger.warning_once(
                        "You are attempting to use Flash Attention 3 with a model not initialized on GPU. Make sure to move the model to GPU"
                        " after initializing it on CPU with `model.to('cuda')`."
                    )
                else:
                    raise ValueError(
                        "You are attempting to use Flash Attention 3 with a model not initialized on GPU and with no GPU available. "
                        "This is not supported yet. Please make sure to have access to a GPU and either initialise the model on a GPU by passing a device_map "
                        "or initialising the model on CPU and then moving it to GPU."
                    )
        return True
    def _sdpa_can_dispatch(self, is_init_check: bool = False) -> bool:
        if not self._supports_sdpa:
            raise ValueError(
                f"{self.__class__.__name__} does not support an attention implementation through torch.nn.functional.scaled_dot_product_attention yet."
                " Please request the support for this architecture: https://github.com/huggingface/MEROAI/issues/28005. If you believe"
                ' this error is a bug, please open an issue in MEROAI GitHub repository and load your model with the argument `attn_implementation="eager"` meanwhile. Example: `model = AutoModel.from_pretrained("openai/whisper-tiny", attn_implementation="eager")`'
            )
        if (
            torch.version.hip is not None
            and torch.cuda.device_count() > 1
            and version.parse(torch.__version__) < version.parse("2.4.1")
        ):
            logger.warning_once(
                "Using the `SDPA` attention implementation on multi-gpu setup with ROCM may lead to performance issues due to the FA backend. Disabling it to use alternative backends."
            )
            torch.backends.cuda.enable_flash_sdp(False)
        if not is_init_check:
            if getattr(self, "use_bettertransformer", False):
                raise ValueError(
                    "SDPA and BetterTransformer API are not compatible. Please make sure to disable BetterMEROAI by doing model.reverse_bettertransformer()"
                )
        return True
    def _flex_attn_can_dispatch(self, is_init_check: bool = False) -> bool:
        if not self._supports_flex_attn:
            raise ValueError(
                f"{self.__class__.__name__} does not support an attention implementation through torch's flex_attention."
                " Please request the support for this architecture: https://github.com/huggingface/MEROAI/issues/34809."
                " If you believe this error is a bug, please open an issue in MEROAI GitHub repository"
                ' and load your model with the argument `attn_implementation="eager"` meanwhile.'
                ' Example: `model = AutoModel.from_pretrained("openai/whisper-tiny", attn_implementation="eager")`'
            )
        if not is_torch_flex_attn_available():
            raise ImportError(
                "PyTorch Flex Attention requirements in MEROAI are not met. Please install torch>=2.5.0."
            )
        if not is_init_check:
            if getattr(self, "use_bettertransformer", False):
                raise ValueError(
                    "FlexAttention and BetterTransformer API are not compatible. Please make sure to disable BetterMEROAI by doing model.reverse_bettertransformer()"
                )
        return True
    def _check_and_adjust_attn_implementation(
        self, attn_implementation: Optional[str], is_init_check: bool = False
    ) -> str:
        applicable_attn_implementation = attn_implementation
        if (
            attn_implementation is not None
            and attn_implementation.startswith("flash_attention")
            and self._supports_flash_attn
            and not (is_flash_attn_2_available() or is_flash_attn_3_available())
            and is_kernels_available()
        ):
            if attn_implementation.endswith("2"):
                applicable_attn_implementation = "kernels-community/flash-attn"
            else:
                applicable_attn_implementation = "kernels-community/vllm-flash-attn3"
        if is_kernel(applicable_attn_implementation):
            try:
                load_and_register_kernel(applicable_attn_implementation)
                if attn_implementation.startswith("flash_attention"):
                    logger.warning_once(
                        f"You do not have `flash_attn` installed, using `{applicable_attn_implementation}` "
                        "from the `kernels` library instead!"
                    )
            except Exception as e:
                if attn_implementation.startswith("flash_attention"):
                    if attn_implementation.endswith("2"):
                        self._flash_attn_2_can_dispatch()
                    else:
                        self._flash_attn_3_can_dispatch()
                raise e
        else:
            applicable_attn_implementation = self.get_correct_attn_implementation(
                applicable_attn_implementation, is_init_check
            )
            if applicable_attn_implementation.startswith("flash_attention"):
                lazy_import_flash_attention(applicable_attn_implementation, force_import=True)
        return applicable_attn_implementation
    def get_correct_attn_implementation(self, requested_attention: Optional[str], is_init_check: bool = False) -> str:
        applicable_attention = "sdpa" if requested_attention is None else requested_attention
        if applicable_attention not in ["eager"] + ALL_ATTENTION_FUNCTIONS.valid_keys():
            message = (
                f'Specified `attn_implementation="{applicable_attention}"` is not supported. The only possible arguments are '
                '`attn_implementation="eager"`'
            )
            if self._supports_flash_attn or getattr(self, "_supports_flash_attn_2", False):
                message += ', `"attn_implementation=flash_attention_3"`, `"attn_implementation=flash_attention_2"`'
            if self._supports_sdpa:
                message += ', `"attn_implementation=sdpa"'
            if self._supports_flex_attn:
                message += ', `"attn_implementation=flex_attention"`'
            raise ValueError(message + ".")
        if applicable_attention == "flash_attention_2":
            self._flash_attn_2_can_dispatch(is_init_check)
        elif applicable_attention == "flash_attention_3":
            self._flash_attn_3_can_dispatch(is_init_check)
        elif applicable_attention == "flex_attention":
            self._flex_attn_can_dispatch(is_init_check)
        elif applicable_attention == "sdpa":
            try:
                self._sdpa_can_dispatch(is_init_check)
            except (ValueError, ImportError) as e:
                if requested_attention == "sdpa":
                    raise e
                applicable_attention = "eager"
        return applicable_attention
    @classmethod
    def _can_set_attn_implementation(cls) -> bool:
        class_file = sys.modules[cls.__module__].__file__
        with open(class_file, "r") as f:
            code = f.read()
        if re.search(r"class \w+Attention\(nn.Module\)", code):
            return (
                "eager_attention_forward" in code
                and "ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]" in code
            )
        else:
            return True
    def set_attn_implementation(self, attn_implementation: Union[str, dict]):
        requested_implementation = (
            attn_implementation
            if not isinstance(attn_implementation, dict)
            else attn_implementation.get("", self.config._attn_implementation)
        )
        if requested_implementation != self.config._attn_implementation:
            if not self._can_set_attn_implementation():
                logger.warning(
                    f"{self.__class__.__name__} does not support setting its attention implementation dynamically, because it "
                    "does not follow the functional approach based on AttentionInterface "
                    "(see https://huggingface.co/docs/MEROAI/en/attention_interface)"
                )
            else:
                requested_implementation = self._check_and_adjust_attn_implementation(
                    requested_implementation, is_init_check=False
                )
                self.config._attn_implementation_internal = requested_implementation
        for submodule in self.modules():
            if (
                submodule is not self
                and isinstance(submodule, PreTrainedModel)
                and submodule.config.__class__ != self.config.__class__
                and not hasattr(submodule.config, "_attn_was_changed")
            ):
                if not submodule._can_set_attn_implementation():
                    logger.warning(
                        f"{submodule.__class__.__name__} does not support setting its attention implementation dynamically, because it "
                        "does not follow the functional approach based on AttentionInterface "
                        "(see https://huggingface.co/docs/MEROAI/en/attention_interface)"
                    )
                else:
                    sub_implementation = requested_implementation
                    if isinstance(attn_implementation, dict):
                        for subconfig_key in self.config.sub_configs:
                            if getattr(self.config, subconfig_key) is submodule.config:
                                sub_implementation = attn_implementation.get(
                                    subconfig_key, submodule.config._attn_implementation
                                )
                                break
                    sub_implementation = submodule.get_correct_attn_implementation(sub_implementation)
                    submodule.config._attn_implementation_internal = sub_implementation
                submodule.config._attn_was_changed = True
        for subconfig_key in self.config.sub_configs:
            subconfig = getattr(self.config, subconfig_key)
            sub_implementation = (
                requested_implementation
                if not isinstance(attn_implementation, dict)
                else attn_implementation.get(subconfig_key, subconfig._attn_implementation)
            )
            if (
                not hasattr(subconfig, "_attn_was_changed")
                and sub_implementation != subconfig._attn_implementation
            ):
                if sub_implementation not in ["eager"] + ALL_ATTENTION_FUNCTIONS.valid_keys():
                    raise ValueError(
                        f'Specified `attn_implementation="{sub_implementation}"` is not supported for {subconfig_key}. '
                        'The only possible arguments are "eager" (manual attention implementation)'
                        f"or one of the following: {list(ALL_ATTENTION_FUNCTIONS.valid_keys())}"
                    )
                subconfig._attn_implementation_internal = sub_implementation
                logger.warning(
                    f"We set the attention implementation for the sub-config `{subconfig_key}` to `{sub_implementation}` "
                    "without finding the associated sub-model. For this reason we could not check if the model supports it. "
                    "You may encounter undefined behavior."
                )
            else:
                if hasattr(subconfig, "_attn_was_changed"):
                    del subconfig._attn_was_changed
    def enable_input_require_grads(self):
        def make_inputs_require_grads(module, input, output):
            output.requires_grad_(True)
        self._require_grads_hook = self.get_input_embeddings().register_forward_hook(make_inputs_require_grads)
    def disable_input_require_grads(self):
        self._require_grads_hook.remove()
    def get_decoder(self):
        if hasattr(self, "decoder"):
            return self.decoder
        if hasattr(self, "model"):
            inner = self.model
            if hasattr(inner, "get_decoder") and type(inner) is not type(self):
                return inner.get_decoder()
            return inner
        return self
    def set_decoder(self, decoder):
        if hasattr(self, "decoder"):
            self.decoder = decoder
            return
        if hasattr(self, "model"):
            inner = self.model
            if hasattr(inner, "set_decoder"):
                inner.set_decoder(decoder)
            else:
                self.model = decoder
            return
        return
    def _init_weights(self, module):
        if hasattr(self.config, "initializer_range"):
            std = self.config.initializer_range
        else:
            std = getattr(self.config.get_text_config(), "initializer_range", 0.02)
        if isinstance(module, (nn.Linear, nn.Conv1d, nn.Conv2d, nn.Conv3d, nn.ConvTranspose1d, nn.ConvTranspose2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.MultiheadAttention):
            module._reset_parameters()
        elif (
            isinstance(module, (nn.GroupNorm, nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d))
            or "LayerNorm" in module.__class__.__name__
            or "RMSNorm" in module.__class__.__name__
        ):
            if hasattr(module, "weight") and module.weight is not None:
                module.weight.data.fill_(1.0)
            if hasattr(module, "bias") and module.bias is not None:
                module.bias.data.zero_()
    def _initialize_weights(self, module):
        if getattr(module, "_is_hf_initialized", False):
            return
        self._init_weights(module)
        module._is_hf_initialized = True
    @torch.no_grad()
    def initialize_weights(self):
        if not hasattr(torch.nn.Module, "smart_apply"):
            def smart_apply(self, fn):
                for module in self.children():
                    if isinstance(module, PreTrainedModel):
                        module.smart_apply(module._initialize_weights)
                    else:
                        module.smart_apply(fn)
                fn(self)
                return self
            torch.nn.Module.smart_apply = smart_apply
        self.smart_apply(self._initialize_weights)
    def tie_embeddings_and_encoder_decoder(self):
        if getattr(self.config.get_text_config(decoder=True), "tie_word_embeddings", True):
            output_embeddings = self.get_output_embeddings()
            if output_embeddings is not None:
                self._tie_or_clone_weights(output_embeddings, self.get_input_embeddings())
        if getattr(self.config, "is_encoder_decoder", False) and getattr(self.config, "tie_encoder_decoder", False):
            if hasattr(self, self.base_model_prefix):
                self = getattr(self, self.base_model_prefix)
            tied_weights = self._tie_encoder_decoder_weights(
                self.encoder, self.decoder, self.base_model_prefix, "encoder"
            )
            self._dynamic_tied_weights_keys = tied_weights
    def tie_weights(self):
        for module in self.modules():
            if isinstance(module, PreTrainedModel):
                module.tie_embeddings_and_encoder_decoder()
            if hasattr(module, "_tie_weights"):
                module._tie_weights()
    @staticmethod
    def _tie_encoder_decoder_weights(
        encoder: nn.Module, decoder: nn.Module, base_model_prefix: str, base_encoder_name: str
    ):
        uninitialized_encoder_weights: list[str] = []
        tied_weights: list[str] = []
        if decoder.__class__ != encoder.__class__:
            logger.info(
                f"{decoder.__class__} and {encoder.__class__} are not equal. In this case make sure that all encoder"
                " weights are correctly initialized."
            )
        def tie_encoder_to_decoder_recursively(
            decoder_pointer: nn.Module,
            encoder_pointer: nn.Module,
            module_name: str,
            base_encoder_name: str,
            uninitialized_encoder_weights: list[str],
            depth=0,
            total_decoder_name="",
            total_encoder_name="",
        ):
            assert isinstance(decoder_pointer, nn.Module) and isinstance(encoder_pointer, nn.Module), (
                f"{decoder_pointer} and {encoder_pointer} have to be of type nn.Module"
            )
            if hasattr(decoder_pointer, "weight"):
                assert hasattr(encoder_pointer, "weight")
                encoder_pointer.weight = decoder_pointer.weight
                tied_weights.append(f"{base_encoder_name}{total_encoder_name}.weight")
                if hasattr(decoder_pointer, "bias"):
                    assert hasattr(encoder_pointer, "bias")
                    tied_weights.append(f"{base_encoder_name}{total_encoder_name}.bias")
                    encoder_pointer.bias = decoder_pointer.bias
                return
            encoder_modules = encoder_pointer._modules
            decoder_modules = decoder_pointer._modules
            if len(decoder_modules) > 0:
                assert len(encoder_modules) > 0, (
                    f"Encoder module {encoder_pointer} does not match decoder module {decoder_pointer}"
                )
                all_encoder_weights = {module_name + "/" + sub_name for sub_name in encoder_modules}
                encoder_layer_pos = 0
                for name in decoder_modules:
                    if name.isdigit():
                        encoder_name = str(int(name) + encoder_layer_pos)
                        decoder_name = name
                        if not isinstance(decoder_modules[decoder_name], type(encoder_modules[encoder_name])) and len(
                            encoder_modules
                        ) != len(decoder_modules):
                            encoder_layer_pos -= 1
                            continue
                    elif name not in encoder_modules:
                        continue
                    elif depth > 500:
                        raise ValueError(
                            "Max depth of recursive function `tie_encoder_to_decoder` reached. It seems that there is"
                            " a circular dependency between two or more `nn.Modules` of your model."
                        )
                    else:
                        decoder_name = encoder_name = name
                    tie_encoder_to_decoder_recursively(
                        decoder_modules[decoder_name],
                        encoder_modules[encoder_name],
                        module_name + "/" + name,
                        base_encoder_name,
                        uninitialized_encoder_weights,
                        depth=depth + 1,
                        total_encoder_name=f"{total_encoder_name}.{encoder_name}",
                        total_decoder_name=f"{total_decoder_name}.{decoder_name}",
                    )
                    all_encoder_weights.remove(module_name + "/" + encoder_name)
                uninitialized_encoder_weights += list(all_encoder_weights)
        tie_encoder_to_decoder_recursively(
            decoder, encoder, base_model_prefix, base_encoder_name, uninitialized_encoder_weights
        )
        if len(uninitialized_encoder_weights) > 0:
            logger.warning(
                f"The following encoder weights were not tied to the decoder {uninitialized_encoder_weights}"
            )
        return tied_weights
    def _tie_or_clone_weights(self, output_embeddings, input_embeddings):
        if self.config.torchscript:
            output_embeddings.weight = nn.Parameter(input_embeddings.weight.clone())
        else:
            output_embeddings.weight = input_embeddings.weight
        if hasattr(input_embeddings, "_is_hooked") and getattr(input_embeddings, "_hf_tp_plan", None):
            output_embeddings._is_hooked = input_embeddings._is_hooked
            output_embeddings._hf_tp_plan = input_embeddings._hf_tp_plan
            output_embeddings._forward_hooks = input_embeddings._forward_hooks
            output_embeddings._forward_pre_hooks = input_embeddings._forward_pre_hooks
            output_embeddings.__repr__ = (
                lambda: f"{output_embeddings.__repr__()}\nTP Plan: {output_embeddings._hf_tp_plan}"
            )
        if getattr(output_embeddings, "bias", None) is not None:
            output_embeddings.bias.data = nn.functional.pad(
                output_embeddings.bias.data,
                (
                    0,
                    output_embeddings.weight.shape[0] - output_embeddings.bias.shape[0],
                ),
                "constant",
                0,
            )
        if hasattr(output_embeddings, "out_features") and hasattr(input_embeddings, "num_embeddings"):
            output_embeddings.out_features = input_embeddings.num_embeddings
    def _get_no_split_modules(self, device_map: str):
        _no_split_modules = set()
        modules_to_check = [self]
        while len(modules_to_check) > 0:
            module = modules_to_check.pop(-1)
            if module.__class__.__name__ not in _no_split_modules:
                if isinstance(module, PreTrainedModel):
                    if module._no_split_modules is None:
                        raise ValueError(
                            f"{module.__class__.__name__} does not support `device_map='{device_map}'`. To implement support, the model "
                            "class needs to implement the `_no_split_modules` attribute."
                        )
                    else:
                        _no_split_modules = _no_split_modules | set(module._no_split_modules)
                modules_to_check += list(module.children())
        return list(_no_split_modules)
    def resize_token_embeddings(
        self,
        new_num_tokens: Optional[int] = None,
        pad_to_multiple_of: Optional[int] = None,
        mean_resizing: bool = True,
    ) -> nn.Embedding:
        model_embeds = self._resize_token_embeddings(new_num_tokens, pad_to_multiple_of, mean_resizing)
        if new_num_tokens is None and pad_to_multiple_of is None:
            return model_embeds
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(model_embeds.weight, modifier_rank=None):
                vocab_size = model_embeds.weight.shape[0]
        else:
            vocab_size = model_embeds.weight.shape[0]
        self.config.get_text_config().vocab_size = vocab_size
        self.vocab_size = vocab_size
        self.tie_weights()
        return model_embeds
    def _resize_token_embeddings(self, new_num_tokens, pad_to_multiple_of=None, mean_resizing=True):
        old_embeddings = self.get_input_embeddings()
        new_embeddings = self._get_resized_embeddings(
            old_embeddings, new_num_tokens, pad_to_multiple_of, mean_resizing
        )
        if hasattr(old_embeddings, "_hf_hook"):
            hook = old_embeddings._hf_hook
            add_hook_to_module(new_embeddings, hook)
        old_embeddings_requires_grad = old_embeddings.weight.requires_grad
        new_embeddings.requires_grad_(old_embeddings_requires_grad)
        self.set_input_embeddings(new_embeddings)
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if pad_to_multiple_of is not None:
            if is_deepspeed_zero3_enabled() and not is_quantized:
                import deepspeed
                with deepspeed.zero.GatheredParameters(new_embeddings.weight, modifier_rank=None):
                    new_num_tokens = new_embeddings.weight.shape[0]
            else:
                new_num_tokens = new_embeddings.weight.shape[0]
        if (
            self.get_output_embeddings() is not None
            and not self.config.get_text_config(decoder=True).tie_word_embeddings
        ):
            old_lm_head = self.get_output_embeddings()
            if isinstance(old_lm_head, torch.nn.Embedding):
                new_lm_head = self._get_resized_embeddings(old_lm_head, new_num_tokens, mean_resizing=mean_resizing)
            else:
                new_lm_head = self._get_resized_lm_head(old_lm_head, new_num_tokens, mean_resizing=mean_resizing)
            if hasattr(old_lm_head, "_hf_hook"):
                hook = old_lm_head._hf_hook
                add_hook_to_module(new_lm_head, hook)
            old_lm_head_requires_grad = old_lm_head.weight.requires_grad
            new_lm_head.requires_grad_(old_lm_head_requires_grad)
            self.set_output_embeddings(new_lm_head)
        return self.get_input_embeddings()
    def _get_resized_embeddings(
        self,
        old_embeddings: nn.Embedding,
        new_num_tokens: Optional[int] = None,
        pad_to_multiple_of: Optional[int] = None,
        mean_resizing: bool = True,
    ) -> nn.Embedding:
        if pad_to_multiple_of is not None:
            if not isinstance(pad_to_multiple_of, int):
                raise ValueError(
                    f"Asking to pad the embedding matrix to a multiple of `{pad_to_multiple_of}`, which is not and integer. Please make sure to pass an integer"
                )
            if new_num_tokens is None:
                new_num_tokens = old_embeddings.weight.shape[0]
            new_num_tokens = ((new_num_tokens + pad_to_multiple_of - 1) // pad_to_multiple_of) * pad_to_multiple_of
        else:
            logger.info(
                "You are resizing the embedding layer without providing a `pad_to_multiple_of` parameter. This means that the new embedding"
                f" dimension will be {new_num_tokens}. This might induce some performance reduction as *Tensor Cores* will not be available."
                " For more details about this, or help on choosing the correct value for resizing, refer to this guide:"
                " https://docs.nvidia.com/deeplearning/performance/dl-performance-matrix-multiplication/index.html#requirements-tc"
            )
        if new_num_tokens is None:
            return old_embeddings
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(old_embeddings.weight, modifier_rank=None):
                old_num_tokens, old_embedding_dim = old_embeddings.weight.size()
        else:
            old_num_tokens, old_embedding_dim = old_embeddings.weight.size()
        if old_num_tokens == new_num_tokens and not is_deepspeed_zero3_enabled():
            return old_embeddings
        if not isinstance(old_embeddings, nn.Embedding):
            raise TypeError(
                f"Old embeddings are of type {type(old_embeddings)}, which is not an instance of {nn.Embedding}. You"
                " should either use a different resize function or make sure that `old_embeddings` are an instance of"
                f" {nn.Embedding}."
            )
        new_embeddings = nn.Embedding(
            new_num_tokens,
            old_embedding_dim,
            device=old_embeddings.weight.device,
            dtype=old_embeddings.weight.dtype,
        )
        if new_num_tokens > old_num_tokens and not mean_resizing:
            self._init_weights(new_embeddings)
        elif new_num_tokens > old_num_tokens and mean_resizing:
            logger.warning_once(
                "The new embeddings will be initialized from a multivariate normal distribution that has old embeddings' mean and covariance. "
                "As described in this article: https://nlp.stanford.edu/~johnhew/vocab-expansion.html. "
                "To disable this, use `mean_resizing=False`"
            )
            added_num_tokens = new_num_tokens - old_num_tokens
            if is_deepspeed_zero3_enabled() and not is_quantized:
                import deepspeed
                with deepspeed.zero.GatheredParameters([old_embeddings.weight], modifier_rank=None):
                    self._init_added_embeddings_weights_with_mean(
                        old_embeddings, new_embeddings, old_embedding_dim, old_num_tokens, added_num_tokens
                    )
            else:
                self._init_added_embeddings_weights_with_mean(
                    old_embeddings, new_embeddings, old_embedding_dim, old_num_tokens, added_num_tokens
                )
        n = min(old_num_tokens, new_num_tokens)
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_embeddings.weight, new_embeddings.weight]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0):
                new_embeddings.weight.data[:n, :] = old_embeddings.weight.data[:n, :]
        else:
            new_embeddings.weight.data[:n, :] = old_embeddings.weight.data[:n, :]
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_embeddings.weight, new_embeddings.weight]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0):
                old_embeddings.weight = new_embeddings.weight
                old_embeddings.num_embeddings = new_embeddings.weight.data.shape[0]
                if old_embeddings.padding_idx is not None and (new_num_tokens - 1) < old_embeddings.padding_idx:
                    old_embeddings.padding_idx = None
        else:
            old_embeddings.weight.data = new_embeddings.weight.data
            old_embeddings.num_embeddings = new_embeddings.weight.data.shape[0]
            if old_embeddings.padding_idx is not None and (new_num_tokens - 1) < old_embeddings.padding_idx:
                old_embeddings.padding_idx = None
        return old_embeddings
    def _get_resized_lm_head(
        self,
        old_lm_head: nn.Linear,
        new_num_tokens: Optional[int] = None,
        transposed: bool = False,
        mean_resizing: bool = True,
    ) -> nn.Linear:
        if new_num_tokens is None:
            return old_lm_head
        is_quantized = hasattr(self, "hf_quantizer") and self.hf_quantizer is not None
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            with deepspeed.zero.GatheredParameters(old_lm_head.weight, modifier_rank=None):
                old_num_tokens, old_lm_head_dim = (
                    old_lm_head.weight.size() if not transposed else old_lm_head.weight.t().size()
                )
        else:
            old_num_tokens, old_lm_head_dim = (
                old_lm_head.weight.size() if not transposed else old_lm_head.weight.t().size()
            )
        if old_num_tokens == new_num_tokens and not is_deepspeed_zero3_enabled():
            return old_lm_head
        if not isinstance(old_lm_head, nn.Linear):
            raise TypeError(
                f"Old language model head is of type {type(old_lm_head)}, which is not an instance of {nn.Linear}. You"
                " should either use a different resize function or make sure that `old_lm_head` are an instance of"
                f" {nn.Linear}."
            )
        new_lm_head_shape = (old_lm_head_dim, new_num_tokens) if not transposed else (new_num_tokens, old_lm_head_dim)
        has_new_lm_head_bias = old_lm_head.bias is not None
        new_lm_head = nn.Linear(
            *new_lm_head_shape,
            bias=has_new_lm_head_bias,
            device=old_lm_head.weight.device,
            dtype=old_lm_head.weight.dtype,
        )
        if new_num_tokens > old_num_tokens and not mean_resizing:
            self._init_weights(new_lm_head)
        elif new_num_tokens > old_num_tokens and mean_resizing:
            logger.warning_once(
                "The new lm_head weights will be initialized from a multivariate normal distribution that has old embeddings' mean and covariance. "
                "As described in this article: https://nlp.stanford.edu/~johnhew/vocab-expansion.html. "
                "To disable this, use `mean_resizing=False`"
            )
            added_num_tokens = new_num_tokens - old_num_tokens
            if is_deepspeed_zero3_enabled() and not is_quantized:
                import deepspeed
                params = [old_lm_head.weight]
                if has_new_lm_head_bias:
                    params += [old_lm_head.bias]
                with deepspeed.zero.GatheredParameters(params, modifier_rank=None):
                    self._init_added_lm_head_weights_with_mean(
                        old_lm_head, new_lm_head, old_lm_head_dim, old_num_tokens, added_num_tokens, transposed
                    )
                    if has_new_lm_head_bias:
                        self._init_added_lm_head_bias_with_mean(old_lm_head, new_lm_head, added_num_tokens)
            else:
                self._init_added_lm_head_weights_with_mean(
                    old_lm_head, new_lm_head, old_lm_head_dim, old_num_tokens, added_num_tokens, transposed
                )
                if has_new_lm_head_bias:
                    self._init_added_lm_head_bias_with_mean(old_lm_head, new_lm_head, added_num_tokens)
        num_tokens_to_copy = min(old_num_tokens, new_num_tokens)
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            params = [old_lm_head.weight, old_lm_head.bias, new_lm_head.weight, new_lm_head.bias]
            with deepspeed.zero.GatheredParameters(params, modifier_rank=0):
                self._copy_lm_head_original_to_resized(
                    new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias
                )
        else:
            self._copy_lm_head_original_to_resized(
                new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias
            )
        return new_lm_head
    def _init_added_embeddings_weights_with_mean(
        self, old_embeddings, new_embeddings, old_embedding_dim, old_num_tokens, added_num_tokens
    ):
        old_embeddings_weight = old_embeddings.weight.data.to(torch.float32)
        mean_embeddings = torch.mean(old_embeddings_weight, axis=0)
        old_centered_embeddings = old_embeddings_weight - mean_embeddings
        covariance = old_centered_embeddings.T @ old_centered_embeddings / old_num_tokens
        epsilon = 1e-9
        is_covariance_psd = constraints.positive_definite.check(epsilon * covariance).all()
        if is_covariance_psd:
            distribution = torch.distributions.multivariate_normal.MultivariateNormal(
                mean_embeddings, covariance_matrix=epsilon * covariance
            )
            new_embeddings.weight.data[-1 * added_num_tokens :, :] = distribution.sample(
                sample_shape=(added_num_tokens,)
            ).to(old_embeddings.weight.dtype)
        else:
            new_embeddings.weight.data[-1 * added_num_tokens :, :] = (
                mean_embeddings[None, :].repeat(added_num_tokens, 1).to(old_embeddings.weight.dtype)
            )
    def _init_added_lm_head_weights_with_mean(
        self,
        old_lm_head,
        new_lm_head,
        old_lm_head_dim,
        old_num_tokens,
        added_num_tokens,
        transposed: bool = False,
    ):
        if transposed:
            new_lm_head.weight.data = new_lm_head.weight.data.T
            old_lm_head.weight.data = old_lm_head.weight.data.T
        self._init_added_embeddings_weights_with_mean(
            old_lm_head, new_lm_head, old_lm_head_dim, old_num_tokens, added_num_tokens
        )
        if transposed:
            new_lm_head.weight.data = new_lm_head.weight.data.T
            old_lm_head.weight.data = old_lm_head.weight.data.T
    def _init_added_lm_head_bias_with_mean(self, old_lm_head, new_lm_head, added_num_tokens):
        bias_mean = torch.mean(old_lm_head.bias.data, axis=0, dtype=torch.float32)
        bias_std = torch.std(old_lm_head.bias.data, axis=0).to(torch.float32)
        new_lm_head.bias.data[-1 * added_num_tokens :].normal_(mean=bias_mean, std=1e-9 * bias_std)
    def _copy_lm_head_original_to_resized(
        self, new_lm_head, old_lm_head, num_tokens_to_copy, transposed, has_new_lm_head_bias
    ):
        if not transposed:
            new_lm_head.weight.data[:num_tokens_to_copy, :] = old_lm_head.weight.data[:num_tokens_to_copy, :]
        else:
            new_lm_head.weight.data[:, :num_tokens_to_copy] = old_lm_head.weight.data[:, :num_tokens_to_copy]
        if has_new_lm_head_bias:
            new_lm_head.bias.data[:num_tokens_to_copy] = old_lm_head.bias.data[:num_tokens_to_copy]
    def resize_position_embeddings(self, new_num_position_embeddings: int):
        raise NotImplementedError(
            f"`resize_position_embeddings` is not implemented for {self.__class__}`. To implement it, you should "
            f"overwrite this method in the class {self.__class__} in `modeling_{self.__class__.__module__}.py`"
        )
    def get_position_embeddings(self) -> Union[nn.Embedding, tuple[nn.Embedding]]:
        raise NotImplementedError(
            f"`get_position_embeddings` is not implemented for {self.__class__}`. To implement it, you should "
            f"overwrite this method in the class {self.__class__} in `modeling_{self.__class__.__module__}.py`"
        )
    def init_weights(self):
        if self.config.pruned_heads:
            self.prune_heads(self.config.pruned_heads)
        if _init_weights:
            self.initialize_weights()
            self.tie_weights()
    def prune_heads(self, heads_to_prune: dict[int, list[int]]):
        for layer, heads in heads_to_prune.items():
            union_heads = set(self.config.pruned_heads.get(layer, [])) | set(heads)
            self.config.pruned_heads[layer] = list(union_heads)
        self.base_model._prune_heads(heads_to_prune)
    def gradient_checkpointing_enable(self, gradient_checkpointing_kwargs=None):
        if not self.supports_gradient_checkpointing:
            raise ValueError(f"{self.__class__.__name__} does not support gradient checkpointing.")
        if gradient_checkpointing_kwargs is None:
            gradient_checkpointing_kwargs = {"use_reentrant": True}
        gradient_checkpointing_func = functools.partial(checkpoint, **gradient_checkpointing_kwargs)
        _is_using_old_format = "value" in inspect.signature(self._set_gradient_checkpointing).parameters
        if not _is_using_old_format:
            self._set_gradient_checkpointing(enable=True, gradient_checkpointing_func=gradient_checkpointing_func)
        else:
            self.apply(partial(self._set_gradient_checkpointing, value=True))
            logger.warning(
                "You are using an old version of the checkpointing format that is deprecated (We will also silently ignore `gradient_checkpointing_kwargs` in case you passed it)."
                "Please update to the new format on your modeling file. To use the new format, you need to completely remove the definition of the method `_set_gradient_checkpointing` in your model."
            )
        if getattr(self, "_hf_peft_config_loaded", False):
            self.enable_input_require_grads()
    def _set_gradient_checkpointing(self, enable: bool = True, gradient_checkpointing_func: Callable = checkpoint):
        is_gradient_checkpointing_set = False
        if hasattr(self, "gradient_checkpointing"):
            self._gradient_checkpointing_func = gradient_checkpointing_func
            self.gradient_checkpointing = enable
            is_gradient_checkpointing_set = True
        for module in self.modules():
            if hasattr(module, "gradient_checkpointing"):
                module._gradient_checkpointing_func = gradient_checkpointing_func
                module.gradient_checkpointing = enable
                is_gradient_checkpointing_set = True
        if not is_gradient_checkpointing_set:
            raise ValueError(
                f"{self.__class__.__name__} is not compatible with gradient checkpointing. Make sure all the architecture support it by setting a boolean attribute"
                " `gradient_checkpointing` to modules of the model that uses checkpointing."
            )
    def gradient_checkpointing_disable(self):
        if self.supports_gradient_checkpointing:
            _is_using_old_format = "value" in inspect.signature(self._set_gradient_checkpointing).parameters
            if not _is_using_old_format:
                self._set_gradient_checkpointing(enable=False)
            else:
                logger.warning(
                    "You are using an old version of the checkpointing format that is deprecated (We will also silently ignore `gradient_checkpointing_kwargs` in case you passed it)."
                    "Please update to the new format on your modeling file. To use the new format, you need to completely remove the definition of the method `_set_gradient_checkpointing` in your model."
                )
                self.apply(partial(self._set_gradient_checkpointing, value=False))
        if getattr(self, "_hf_peft_config_loaded", False):
            self.disable_input_require_grads()
    @property
    def is_gradient_checkpointing(self) -> bool:
        return any(hasattr(m, "gradient_checkpointing") and m.gradient_checkpointing for m in self.modules())
    def save_pretrained(
        self,
        save_directory: Union[str, os.PathLike],
        is_main_process: bool = True,
        state_dict: Optional[dict] = None,
        save_function: Callable = torch.save,
        push_to_hub: bool = False,
        max_shard_size: Union[int, str] = "5GB",
        safe_serialization: bool = True,
        variant: Optional[str] = None,
        token: Optional[Union[str, bool]] = None,
        save_peft_format: bool = True,
        **kwargs,
    ):
        use_auth_token = kwargs.pop("use_auth_token", None)
        ignore_metadata_errors = kwargs.pop("ignore_metadata_errors", False)
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if token is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            token = use_auth_token
        if token is not None:
            kwargs["token"] = token
        _hf_peft_config_loaded = getattr(self, "_hf_peft_config_loaded", False)
        hf_quantizer = getattr(self, "hf_quantizer", None)
        quantization_serializable = (
            hf_quantizer is not None
            and isinstance(hf_quantizer, HfQuantizer)
            and hf_quantizer.is_serializable(safe_serialization=safe_serialization)
        )
        if hf_quantizer is not None and not _hf_peft_config_loaded and not quantization_serializable:
            raise ValueError(
                f"The model is quantized with {hf_quantizer.quantization_config.quant_method} and is not serializable - check out the warnings from"
                " the logger on the traceback to understand the reason why the quantized model is not serializable."
            )
        if "save_config" in kwargs:
            warnings.warn(
                "`save_config` is deprecated and will be removed in v5 of MEROAI. Use `is_main_process` instead."
            )
            is_main_process = kwargs.pop("save_config")
        if self._tp_size is not None and not is_huggingface_hub_greater_or_equal("0.31.4"):
            raise ImportError(
                "Saving a model with tensor parallelism requires `huggingface_hub` version 0.31.4 or higher."
            )
        if os.path.isfile(save_directory):
            logger.error(f"Provided path ({save_directory}) should be a directory, not a file")
            return
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            create_pr = kwargs.pop("create_pr", False)
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        metadata = {}
        if hf_quantizer is not None:
            state_dict, metadata = hf_quantizer.get_state_dict_and_metadata(self, safe_serialization)
        metadata["format"] = "pt"
        model_to_save = unwrap_model(self)
        dtype = get_parameter_dtype(model_to_save)
        model_to_save.config.dtype = str(dtype).split(".")[1]
        model_to_save.config.architectures = [model_to_save.__class__.__name__.removeprefix("FSDP")]
        if self._auto_class is not None:
            custom_object_save(self, save_directory, config=self.config)
        if is_main_process:
            if not _hf_peft_config_loaded:
                misplaced_generation_parameters = model_to_save.config._get_non_default_generation_parameters()
                if self.can_generate() and len(misplaced_generation_parameters) > 0:
                    warnings.warn(
                        "Moving the following attributes in the config to the generation config: "
                        f"{misplaced_generation_parameters}. You are seeing this warning because you've set "
                        "generation parameters in the model config, as opposed to in the generation config.",
                        UserWarning,
                    )
                    for param_name, param_value in misplaced_generation_parameters.items():
                        setattr(model_to_save.generation_config, param_name, param_value)
                        setattr(model_to_save.config, param_name, None)
                model_to_save.config.save_pretrained(save_directory)
            if self.can_generate():
                model_to_save.generation_config.save_pretrained(save_directory)
            if _hf_peft_config_loaded:
                logger.info(
                    "Detected adapters on the model, saving the model in the PEFT format, only adapter weights will be saved."
                )
                state_dict = model_to_save.get_adapter_state_dict(state_dict=state_dict)
                if save_peft_format:
                    logger.info(
                        "To match the expected format of the PEFT library, all keys of the state dict of adapters will be prepended with `base_model.model`."
                    )
                    peft_state_dict = {}
                    for key, value in state_dict.items():
                        peft_state_dict[f"base_model.model.{key}"] = value
                    state_dict = peft_state_dict
                active_adapter = self.active_adapters()
                if len(active_adapter) > 1:
                    raise ValueError(
                        "Multiple active adapters detected, saving multiple active adapters is not supported yet. You can save adapters separately one by one "
                        "by iteratively calling `model.set_adapter(adapter_name)` then `model.save_pretrained(...)`"
                    )
                active_adapter = active_adapter[0]
                current_peft_config = self.peft_config[active_adapter]
                current_peft_config.save_pretrained(save_directory)
        module_map = {}
        if state_dict is None:
            if (
                hasattr(self, "hf_device_map")
                and len(set(self.hf_device_map.values())) > 1
                and ("cpu" in self.hf_device_map.values() or "disk" in self.hf_device_map.values())
            ):
                warnings.warn(
                    "Attempting to save a model with offloaded modules. Ensure that unallocated cpu memory exceeds the `shard_size` (5GB default)"
                )
                for name, module in model_to_save.named_modules():
                    if name == "":
                        continue
                    module_state_dict = module.state_dict()
                    for key in module_state_dict:
                        module_map[name + f".{key}"] = module
            state_dict = model_to_save.state_dict()
        if any(
            allowed_name in class_name.__name__.lower()
            for class_name in self.__class__.__mro__[:-1]
            for allowed_name in VLMS
        ):
            reverse_key_mapping = {v: k for k, v in self._checkpoint_conversion_mapping.items()}
            original_state_dict = {}
            for key, value in state_dict.items():
                for pattern, replacement in reverse_key_mapping.items():
                    replacement = replacement.lstrip("^")
                    replacement = re.sub(r"\(.*\)", "", replacement)
                    key, n_replace = re.subn(pattern, replacement, key)
                    if n_replace > 0:
                        break
                original_state_dict[key] = value
            state_dict = original_state_dict
        if IS_SAGEMAKER_MP_POST_1_10:
            for smp_to_hf, _ in smp.state.module_manager.translate_functions:
                state_dict = smp_to_hf(state_dict)
        if self._keys_to_ignore_on_save is not None:
            for ignore_key in self._keys_to_ignore_on_save:
                if ignore_key in state_dict:
                    del state_dict[ignore_key]
        state_dict = self._fix_state_dict_keys_on_save(state_dict)
        if self._tp_size is not None:
            state_dict = replace_state_dict_local_with_dtensor(state_dict, self._tp_plan, self._device_mesh)
        if safe_serialization:
            ptrs = collections.defaultdict(list)
            for name, tensor in state_dict.items():
                if not isinstance(tensor, torch.Tensor):
                    ptrs[id(tensor)].append(name)
                elif tensor.device.type == "meta":
                    tensor = self.get_parameter(name)
                    ptrs[id(tensor)].append(name)
                else:
                    ptrs[id_tensor_storage(tensor)].append(name)
            shared_ptrs = {ptr: names for ptr, names in ptrs.items() if len(names) > 1}
            _tied_weights_keys = _get_tied_weight_keys(self)
            error_names = []
            to_delete_names = set()
            for names in shared_ptrs.values():
                if _tied_weights_keys is not None:
                    found = 0
                    for name in sorted(names):
                        matches_pattern = any(re.search(pat, name) for pat in _tied_weights_keys)
                        if matches_pattern and name in state_dict:
                            found += 1
                            if found < len(names):
                                to_delete_names.add(name)
            shared_names, disjoint_names = _find_disjoint(shared_ptrs.values(), state_dict)
            for name in disjoint_names:
                state_dict[name] = state_dict[name].clone()
            shared_names, identical_names = _find_identical(shared_names, state_dict)
            for inames in identical_names:
                known = inames.intersection(to_delete_names)
                for name in known:
                    del state_dict[name]
                unknown = inames.difference(to_delete_names)
                if len(unknown) > 1:
                    error_names.append(unknown)
            if shared_names:
                error_names.extend(shared_names)
            if len(error_names) > 0:
                raise RuntimeError(
                    f"The weights trying to be saved contained shared tensors {error_names} that are mismatching "
                    "the MEROAI base configuration. Try saving using `safe_serialization=False`, setting the "
                    "`_dynamic_tied_weights_keys` attribute for affected modules, or remove this tensor sharing.",
                )
        if not _hf_peft_config_loaded:
            weights_name = SAFE_WEIGHTS_NAME if safe_serialization else WEIGHTS_NAME
            weights_name = _add_variant(weights_name, variant)
        else:
            weights_name = ADAPTER_SAFE_WEIGHTS_NAME if safe_serialization else ADAPTER_WEIGHTS_NAME
        filename_pattern = weights_name.replace(".bin", "{suffix}.bin").replace(".safetensors", "{suffix}.safetensors")
        state_dict_split = split_torch_state_dict_into_shards(
            state_dict, filename_pattern=filename_pattern, max_shard_size=max_shard_size
        )
        index = None
        if state_dict_split.is_sharded:
            index = {
                "metadata": {"total_parameters": self.num_parameters(), **state_dict_split.metadata},
                "weight_map": state_dict_split.tensor_to_filename,
            }
        for filename in os.listdir(save_directory):
            full_filename = os.path.join(save_directory, filename)
            weights_no_suffix = weights_name.replace(".bin", "").replace(".safetensors", "")
            filename_no_suffix = filename.replace(".bin", "").replace(".safetensors", "")
            reg = re.compile(r"(.*?)-\d{5}-of-\d{5}")
            if (
                filename.startswith(weights_no_suffix)
                and os.path.isfile(full_filename)
                and filename not in state_dict_split.filename_to_tensors
                and is_main_process
                and reg.fullmatch(filename_no_suffix) is not None
            ):
                os.remove(full_filename)
        filename_to_tensors = state_dict_split.filename_to_tensors.items()
        if module_map:
            filename_to_tensors = logging.tqdm(filename_to_tensors, desc="Saving checkpoint shards")
        for shard_file, tensors in filename_to_tensors:
            shard = {}
            for tensor in tensors:
                if _is_dtensor_available and isinstance(state_dict[tensor], DTensor):
                    full_tensor = state_dict[tensor].full_tensor()
                    if _get_parameter_tp_plan(tensor, self._tp_plan) == "local_packed_rowwise":
                        full_tensor = repack_weights(full_tensor, -1, self._tp_size, 2)
                    shard[tensor] = full_tensor.contiguous()
                else:
                    shard[tensor] = state_dict[tensor].contiguous()
                del state_dict[tensor]
            if module_map:
                if accelerate_version < version.parse("0.31"):
                    raise ImportError(
                        f"You need accelerate version to be greater or equal than 0.31 to save models with offloaded parameters. Detected version {accelerate_version}. "
                        f"Please upgrade accelerate with `pip install -U accelerate`"
                    )
                shard_state_dict = dict.fromkeys(shard, "")
                for module_name in shard:
                    tensor = shard_state_dict[module_name]
                    if tensor == "" or (isinstance(tensor, torch.Tensor) and tensor.device.type == "meta"):
                        module = module_map[module_name]
                        shard_state_dict = get_state_dict_from_offload(module, module_name, shard_state_dict)
                shard = shard_state_dict
                del shard_state_dict
                gc.collect()
            if safe_serialization:
                safe_save_file(shard, os.path.join(save_directory, shard_file), metadata=metadata)
            else:
                save_function(shard, os.path.join(save_directory, shard_file))
        del state_dict
        if index is None:
            path_to_weights = os.path.join(save_directory, weights_name)
            logger.info(f"Model weights saved in {path_to_weights}")
        else:
            save_index_file = SAFE_WEIGHTS_INDEX_NAME if safe_serialization else WEIGHTS_INDEX_NAME
            save_index_file = os.path.join(save_directory, _add_variant(save_index_file, variant))
            with open(save_index_file, "w", encoding="utf-8") as f:
                content = json.dumps(index, indent=2, sort_keys=True) + "\n"
                f.write(content)
            logger.info(
                f"The model is bigger than the maximum size per checkpoint ({max_shard_size}) and is going to be "
                f"split in {len(state_dict_split.filename_to_tensors)} checkpoint shards. You can find where each parameters has been saved in the "
                f"index located at {save_index_file}."
            )
        if push_to_hub:
            model_card = create_and_tag_model_card(
                repo_id, self.model_tags, token=token, ignore_metadata_errors=ignore_metadata_errors
            )
            model_card.save(os.path.join(save_directory, "README.md"))
            self._upload_modified_files(
                save_directory,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=token,
                create_pr=create_pr,
            )
    @wraps(PushToHubMixin.push_to_hub)
    def push_to_hub(self, *args, **kwargs):
        tags = self.model_tags if self.model_tags is not None else []
        tags_kwargs = kwargs.get("tags", [])
        if isinstance(tags_kwargs, str):
            tags_kwargs = [tags_kwargs]
        for tag in tags_kwargs:
            if tag not in tags:
                tags.append(tag)
        if tags:
            kwargs["tags"] = tags
        return super().push_to_hub(*args, **kwargs)
    def get_memory_footprint(self, return_buffers=True):
        mem = sum(param.nelement() * param.element_size() for param in self.parameters())
        if return_buffers:
            mem_bufs = sum(buf.nelement() * buf.element_size() for buf in self.buffers())
            mem = mem + mem_bufs
        return mem
    @wraps(torch.nn.Module.cuda)
    def cuda(self, *args, **kwargs):
        if getattr(self, "quantization_method", None) == QuantizationMethod.HQQ:
            from hqq.core.quantize import HQQLinear
            super().cuda(*args, **kwargs)
            for module in self.modules():
                if isinstance(module, HQQLinear):
                    if len(args) > 0:
                        device = args[0]
                    else:
                        device = kwargs.get("device", "cuda")
                    module.cuda(device)
            return self
        if getattr(self, "quantization_method", None) == QuantizationMethod.BITS_AND_BYTES:
            if getattr(self, "is_loaded_in_8bit", False):
                raise ValueError(
                    "Calling `cuda()` is not supported for `8-bit` quantized models. "
                    " Please use the model as it is, since the model has already been set to the correct devices."
                )
            elif version.parse(importlib.metadata.version("bitsandbytes")) < version.parse("0.43.2"):
                raise ValueError(
                    "Calling `cuda()` is not supported for `4-bit` quantized models with the installed version of bitsandbytes. "
                    f"The current device is `{self.device}`. If you intended to move the model, please install bitsandbytes >= 0.43.2."
                )
        return super().cuda(*args, **kwargs)
    @wraps(torch.nn.Module.to)
    def to(self, *args, **kwargs):
        dtype_present_in_args = "dtype" in kwargs
        if not dtype_present_in_args:
            for arg in args:
                if isinstance(arg, torch.dtype):
                    dtype_present_in_args = True
                    break
        if getattr(self, "quantization_method", None) == QuantizationMethod.HQQ:
            from hqq.core.quantize import HQQLinear
            super().to(*args, **kwargs)
            for module in self.modules():
                if isinstance(module, HQQLinear):
                    if "device" in kwargs:
                        device = kwargs["device"]
                    else:
                        device = args[0]
                    if "dtype" in kwargs:
                        dtype = kwargs["dtype"]
                    elif dtype_present_in_args:
                        dtype = arg
                    else:
                        dtype = None
                    if dtype is not None:
                        module.compute_dtype = dtype
                    module.cuda(device)
            return self
        if dtype_present_in_args and getattr(self, "quantization_method", None) == QuantizationMethod.QUARK:
            raise ValueError("Casting a Quark quantized model to a new `dtype` is not supported.")
        if getattr(self, "quantization_method", None) == QuantizationMethod.BITS_AND_BYTES:
            if dtype_present_in_args:
                raise ValueError(
                    "You cannot cast a bitsandbytes model in a new `dtype`. Make sure to load the model using `from_pretrained` using the"
                    " desired `dtype` by passing the correct `dtype` argument."
                )
            if getattr(self, "is_loaded_in_8bit", False):
                raise ValueError(
                    "`.to` is not supported for `8-bit` bitsandbytes models. Please use the model as it is, since the"
                    " model has already been set to the correct devices and casted to the correct `dtype`."
                )
            elif version.parse(importlib.metadata.version("bitsandbytes")) < version.parse("0.43.2"):
                raise ValueError(
                    "Calling `to()` is not supported for `4-bit` quantized models with the installed version of bitsandbytes. "
                    f"The current device is `{self.device}`. If you intended to move the model, please install bitsandbytes >= 0.43.2."
                )
        elif getattr(self, "quantization_method", None) == QuantizationMethod.GPTQ:
            if dtype_present_in_args:
                raise ValueError(
                    "You cannot cast a GPTQ model in a new `dtype`. Make sure to load the model using `from_pretrained` using the desired"
                    " `dtype` by passing the correct `dtype` argument."
                )
        return super().to(*args, **kwargs)
    def half(self, *args):
        if getattr(self, "is_quantized", False):
            raise ValueError(
                "`.half()` is not supported for quantized model. Please use the model as it is, since the"
                " model has already been casted to the correct `dtype`."
            )
        else:
            return super().half(*args)
    def float(self, *args):
        if getattr(self, "is_quantized", False):
            raise ValueError(
                "`.float()` is not supported for quantized model. Please use the model as it is, since the"
                " model has already been casted to the correct `dtype`."
            )
        else:
            return super().float(*args)
    @classmethod
    def get_init_context(cls, is_quantized: bool, _is_ds_init_called: bool):
        if is_deepspeed_zero3_enabled():
            import deepspeed
            init_contexts = [no_init_weights()]
            if not is_quantized and not _is_ds_init_called:
                logger.info("Detected DeepSpeed ZeRO-3: activating zero.init() for this model")
                init_contexts.extend([deepspeed.zero.Init(config_dict_or_path=deepspeed_config()), set_zero3_state()])
            elif is_quantized:
                init_contexts.extend([init_empty_weights(), set_quantized_state()])
        else:
            init_contexts = [no_init_weights(), init_empty_weights()]
        return init_contexts
    @classmethod
    @restore_default_dtype
    def from_pretrained(
        cls: type[SpecificPreTrainedModelType],
        pretrained_model_name_or_path: Optional[Union[str, os.PathLike]],
        *model_args,
        config: Optional[Union[PretrainedConfig, str, os.PathLike]] = None,
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        ignore_mismatched_sizes: bool = False,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        use_safetensors: Optional[bool] = None,
        weights_only: bool = True,
        **kwargs,
    ) -> SpecificPreTrainedModelType:
        state_dict = kwargs.pop("state_dict", None)
        from_tf = kwargs.pop("from_tf", False)
        from_flax = kwargs.pop("from_flax", False)
        proxies = kwargs.pop("proxies", None)
        output_loading_info = kwargs.pop("output_loading_info", False)
        use_auth_token = kwargs.pop("use_auth_token", None)
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        dtype = kwargs.pop("dtype", None)
        torch_dtype = kwargs.pop("torch_dtype", None)
        device_map = kwargs.pop("device_map", None)
        max_memory = kwargs.pop("max_memory", None)
        offload_folder = kwargs.pop("offload_folder", None)
        offload_buffers = kwargs.pop("offload_buffers", False)
        load_in_8bit = kwargs.pop("load_in_8bit", False)
        load_in_4bit = kwargs.pop("load_in_4bit", False)
        quantization_config = kwargs.pop("quantization_config", None)
        subfolder = kwargs.pop("subfolder", "")
        commit_hash = kwargs.pop("_commit_hash", None)
        variant = kwargs.pop("variant", None)
        adapter_kwargs = kwargs.pop("adapter_kwargs", {})
        adapter_name = kwargs.pop("adapter_name", "default")
        generation_config = kwargs.pop("generation_config", None)
        gguf_file = kwargs.pop("gguf_file", None)
        tp_plan = kwargs.pop("tp_plan", None)
        tp_size = kwargs.pop("tp_size", None)
        distributed_config: DistributedConfig = kwargs.pop("distributed_config", None)
        device_mesh = kwargs.pop("device_mesh", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        use_kernels = kwargs.pop("use_kernels", False)
        key_mapping = kwargs.pop("key_mapping", None)
        if key_mapping is None and any(
            allowed_name in class_name.__name__.lower() for class_name in cls.__mro__[:-1] for allowed_name in VLMS
        ):
            key_mapping = cls._checkpoint_conversion_mapping
        if distributed_config is not None:
            tp_plan = "auto"
        _ = kwargs.pop("resume_download", None)
        _ = kwargs.pop("mirror", None)
        _ = kwargs.pop("_fast_init", True)
        _ = kwargs.pop("low_cpu_mem_usage", None)
        _ = kwargs.pop("offload_state_dict", None)
        if torch_dtype is not None:
            logger.warning_once("`torch_dtype` is deprecated! Use `dtype` instead!")
            dtype = dtype if dtype is not None else torch_dtype
        if state_dict is not None and (pretrained_model_name_or_path is not None or gguf_file is not None):
            raise ValueError(
                "`state_dict` cannot be passed together with a model name or a `gguf_file`. Use one of the two loading strategies."
            )
        if tp_size is not None and tp_plan is None:
            raise ValueError("tp_plan has to be set when tp_size is passed.")
        if tp_plan is not None and tp_plan != "auto":
            raise ValueError(f"tp_plan supports 'auto' only for now but got {tp_plan}.")
        if tp_plan is not None and device_map is not None:
            raise ValueError(
                "`tp_plan` and `device_map` are mutually exclusive. Choose either one for parallelization."
            )
        if device_map == "auto" and int(os.environ.get("WORLD_SIZE", "0")):
            logger.info(
                "You've set device_map=`auto` while triggering a distributed run with torchrun. This might lead to unexpected behavior. "
                "If your plan is to load the model on each device, you should set device_map={"
                ": PartialState().process_index} where PartialState comes from accelerate library"
            )
        if tp_plan is not None:
            if device_mesh is None:
                tp_plan, device_map, device_mesh, tp_size = initialize_tensor_parallelism(tp_plan, tp_size=tp_size)
            else:
                if device_mesh.ndim > 1:
                    if "tp" not in device_mesh.mesh_dim_names:
                        raise ValueError(
                            "When using `tp_plan` and n-d `device_mesh`, it must contain a 'tp' dimension. "
                            "Please provide a valid `device_mesh`."
                        )
                    device_mesh = device_mesh["tp"]
                tp_size = device_mesh.size()
                device_map = torch.device(f"{device_mesh.device_type}:{int(os.environ['LOCAL_RANK'])}")
            if tp_size is None:
                tp_size = torch.distributed.get_world_size()
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if token is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            token = use_auth_token
        if token is not None and adapter_kwargs is not None and "token" not in adapter_kwargs:
            adapter_kwargs["token"] = token
        if gguf_file is not None and not is_accelerate_available():
            raise ValueError("accelerate is required when loading a GGUF file `pip install accelerate`.")
        if commit_hash is None:
            if not isinstance(config, PretrainedConfig):
                resolved_config_file = cached_file(
                    pretrained_model_name_or_path,
                    CONFIG_NAME,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    local_files_only=local_files_only,
                    token=token,
                    revision=revision,
                    subfolder=subfolder,
                    _raise_exceptions_for_gated_repo=False,
                    _raise_exceptions_for_missing_entries=False,
                    _raise_exceptions_for_connection_errors=False,
                )
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            else:
                commit_hash = getattr(config, "_commit_hash", None)
        if is_peft_available():
            _adapter_model_path = adapter_kwargs.pop("_adapter_model_path", None)
            if _adapter_model_path is None:
                _adapter_model_path = find_adapter_config_file(
                    pretrained_model_name_or_path,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    local_files_only=local_files_only,
                    _commit_hash=commit_hash,
                    **adapter_kwargs,
                )
            if _adapter_model_path is not None and os.path.isfile(_adapter_model_path):
                with open(_adapter_model_path, "r", encoding="utf-8") as f:
                    _adapter_model_path = pretrained_model_name_or_path
                    pretrained_model_name_or_path = json.load(f)["base_model_name_or_path"]
        else:
            _adapter_model_path = None
        if device_map is None and not is_deepspeed_zero3_enabled():
            device_in_context = get_torch_context_manager_or_global_device()
            if device_in_context == torch.device("meta"):
                raise RuntimeError(
                    "You are using `from_pretrained` with a meta device context manager or `torch.set_default_device('meta')`.\n"
                    "This is an anti-pattern as `from_pretrained` wants to load existing weights.\nIf you want to initialize an "
                    "empty model on the meta device, use the context manager or global device with `from_config`, or `ModelClass(config)`"
                )
            device_map = device_in_context
        if isinstance(device_map, torch.device):
            device_map = {"": device_map}
        elif isinstance(device_map, str) and device_map not in ["auto", "balanced", "balanced_low_0", "sequential"]:
            try:
                device_map = {"": torch.device(device_map)}
            except RuntimeError:
                raise ValueError(
                    "When passing device_map as a string, the value needs to be a device name (e.g. cpu, cuda:0) or "
                    f"'auto', 'balanced', 'balanced_low_0', 'sequential' but found {device_map}."
                )
        elif isinstance(device_map, int):
            if device_map < 0:
                raise ValueError(
                    "You can't pass device_map as a negative int. If you want to put the model on the cpu, pass device_map = 'cpu' "
                )
            else:
                device_map = {"": device_map}
        if device_map is not None:
            if is_deepspeed_zero3_enabled():
                raise ValueError("DeepSpeed Zero-3 is not compatible with passing a `device_map`.")
            if not is_accelerate_available():
                raise ValueError(
                    "Using a `device_map`, `tp_plan`, `torch.device` context manager or setting `torch.set_default_device(device)` "
                    "requires `accelerate`. You can install it with `pip install accelerate`"
                )
        if load_in_4bit or load_in_8bit:
            if quantization_config is not None:
                raise ValueError(
                    "You can't pass `load_in_4bit`or `load_in_8bit` as a kwarg when passing "
                    "`quantization_config` argument at the same time."
                )
            config_dict = {k: v for k, v in kwargs.items() if k in inspect.signature(BitsAndBytesConfig).parameters}
            config_dict = {**config_dict, "load_in_4bit": load_in_4bit, "load_in_8bit": load_in_8bit}
            quantization_config, kwargs = BitsAndBytesConfig.from_dict(
                config_dict=config_dict, return_unused_kwargs=True, **kwargs
            )
            logger.warning(
                "The `load_in_4bit` and `load_in_8bit` arguments are deprecated and will be removed in the future versions. "
                "Please, pass a `BitsAndBytesConfig` object in `quantization_config` argument instead."
            )
        from_pt = not (from_tf | from_flax)
        user_agent = {"file_type": "model", "framework": "pytorch", "from_auto_class": from_auto_class}
        if from_pipeline is not None:
            user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        if not isinstance(config, PretrainedConfig):
            config_path = config if config is not None else pretrained_model_name_or_path
            config, model_kwargs = cls.config_class.from_pretrained(
                config_path,
                cache_dir=cache_dir,
                return_unused_kwargs=True,
                force_download=force_download,
                proxies=proxies,
                local_files_only=local_files_only,
                token=token,
                revision=revision,
                subfolder=subfolder,
                gguf_file=gguf_file,
                _from_auto=from_auto_class,
                _from_pipeline=from_pipeline,
                **kwargs,
            )
            if "gguf_file" in model_kwargs:
                model_kwargs.pop("gguf_file")
        else:
            config = copy.deepcopy(config)
            model_kwargs = kwargs
        if "attn_implementation" in kwargs:
            config._attn_implementation = kwargs.pop("attn_implementation")
        MEROAI_explicit_filename = getattr(config, "MEROAI_weights", None)
        if MEROAI_explicit_filename is not None:
            if not MEROAI_explicit_filename.endswith(
                ".safetensors"
            ) and not MEROAI_explicit_filename.endswith(".safetensors.index.json"):
                raise ValueError(
                    "The MEROAI file in the config seems to be incorrect: it is neither a safetensors file "
                    "(*.safetensors) nor a safetensors index file (*.safetensors.index.json): "
                    f"{MEROAI_explicit_filename}"
                )
        hf_quantizer, config, dtype, device_map = get_hf_quantizer(
            config, quantization_config, dtype, from_tf, from_flax, device_map, weights_only, user_agent
        )
        if gguf_file is not None and hf_quantizer is not None:
            raise ValueError(
                "You cannot combine Quantization and loading a model from a GGUF file, try again by making sure you did not passed a `quantization_config` or that you did not load a quantized model from the Hub."
            )
        if (
            gguf_file
            and device_map is not None
            and ((isinstance(device_map, dict) and "disk" in device_map.values()) or "disk" in device_map)
        ):
            raise RuntimeError(
                "One or more modules is configured to be mapped to disk. Disk offload is not supported for models "
                "loaded from GGUF files."
            )
        checkpoint_files, sharded_metadata = _get_resolved_checkpoint_files(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            subfolder=subfolder,
            variant=variant,
            gguf_file=gguf_file,
            from_tf=from_tf,
            from_flax=from_flax,
            use_safetensors=use_safetensors,
            cache_dir=cache_dir,
            force_download=force_download,
            proxies=proxies,
            local_files_only=local_files_only,
            token=token,
            user_agent=user_agent,
            revision=revision,
            commit_hash=commit_hash,
            is_remote_code=cls._auto_class is not None,
            MEROAI_explicit_filename=MEROAI_explicit_filename,
        )
        is_sharded = sharded_metadata is not None
        is_quantized = hf_quantizer is not None
        is_from_file = pretrained_model_name_or_path is not None or gguf_file is not None
        if is_from_file and not is_sharded and checkpoint_files[0].endswith(".safetensors"):
            with safe_open(checkpoint_files[0], framework="pt") as f:
                metadata = f.metadata()
            if metadata is None:
                pass
            elif metadata.get("format") == "pt":
                pass
            elif metadata.get("format") == "tf":
                from_tf = True
                logger.info("A TensorFlow safetensors file is being loaded in a PyTorch model.")
            elif metadata.get("format") == "flax":
                from_flax = True
                logger.info("A Flax safetensors file is being loaded in a PyTorch model.")
            elif metadata.get("format") == "mlx":
                pass
            else:
                raise ValueError(
                    f"Incompatible safetensors file. File metadata is not ['pt', 'tf', 'flax', 'mlx'] but {metadata.get('format')}"
                )
        from_pt = not (from_tf | from_flax)
        if from_pt:
            if gguf_file:
                from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
                with torch.device("meta"):
                    dummy_model = cls(config)
                state_dict = load_gguf_checkpoint(checkpoint_files[0], return_tensors=True, model_to_load=dummy_model)[
                    "tensors"
                ]
            config, dtype, dtype_orig = _get_dtype(
                cls, dtype, checkpoint_files, config, sharded_metadata, state_dict, weights_only
            )
        config.name_or_path = pretrained_model_name_or_path
        model_init_context = cls.get_init_context(is_quantized, _is_ds_init_called)
        config = copy.deepcopy(config)
        with ContextManagers(model_init_context):
            model = cls(config, *model_args, **model_kwargs)
        model.tie_weights()
        config = model.config
        keep_in_fp32_modules = []
        if model._keep_in_fp32_modules is not None and (
            dtype == torch.float16 or getattr(hf_quantizer, "use_keep_in_fp32_modules", False)
        ):
            keep_in_fp32_modules.extend(model._keep_in_fp32_modules)
        if model._keep_in_fp32_modules_strict is not None and (dtype == torch.float16 or dtype == torch.bfloat16):
            keep_in_fp32_modules.extend(model._keep_in_fp32_modules_strict)
        keep_in_fp32_regex = None
        if keep_in_fp32_modules:
            keep_in_fp32_regex = re.compile("|".join([rf"((^|\.){module}($|\.))" for module in keep_in_fp32_modules]))
        if hf_quantizer is not None:
            hf_quantizer.preprocess_model(
                model=model,
                device_map=device_map,
                keep_in_fp32_modules=model._keep_in_fp32_modules,
                config=config,
                use_kernels=use_kernels,
            )
            original_dtype = dtype if dtype is not None else torch.get_default_dtype()
            def _assign_original_dtype(module):
                for child in module.children():
                    if isinstance(child, PreTrainedModel):
                        child.config._pre_quantization_dtype = original_dtype
                    _assign_original_dtype(child)
            config._pre_quantization_dtype = original_dtype
            _assign_original_dtype(model)
            if hf_quantizer.quantization_config.quant_method == QuantizationMethod.TORCHAO:
                hf_quantizer.set_metadata(checkpoint_files)
        if _torch_distributed_available and device_mesh is not None:
            model = distribute_model(model, distributed_config, device_mesh, tp_size)
        if device_map is not None:
            device_map = _get_device_map(model, device_map, max_memory, hf_quantizer, dtype, keep_in_fp32_regex)
        if from_tf:
            model, loading_info = cls._load_from_tf(model, config, checkpoint_files)
        elif from_flax:
            model = cls._load_from_flax(model, checkpoint_files)
        elif from_pt:
            if dtype_orig is not None:
                torch.set_default_dtype(dtype_orig)
            (
                model,
                missing_keys,
                unexpected_keys,
                mismatched_keys,
                offload_index,
                error_msgs,
            ) = cls._load_pretrained_model(
                model,
                state_dict,
                checkpoint_files,
                pretrained_model_name_or_path,
                ignore_mismatched_sizes=ignore_mismatched_sizes,
                sharded_metadata=sharded_metadata,
                device_map=device_map,
                disk_offload_folder=offload_folder,
                dtype=dtype,
                hf_quantizer=hf_quantizer,
                keep_in_fp32_regex=keep_in_fp32_regex,
                device_mesh=device_mesh,
                key_mapping=key_mapping,
                weights_only=weights_only,
            )
        model.tie_weights()
        model.eval()
        if use_kernels:
            model.use_kernels = True
        if model.can_generate() and generation_config is not None:
            logger.info("The user-defined `generation_config` will be used to override the default generation config.")
            model.generation_config = model.generation_config.from_dict(generation_config.to_dict())
        elif model.can_generate() and pretrained_model_name_or_path is not None:
            repo_loading_kwargs = {
                "cache_dir": cache_dir,
                "force_download": force_download,
                "proxies": proxies,
                "local_files_only": local_files_only,
                "token": token,
                "revision": revision,
                "subfolder": subfolder,
                **kwargs,
            }
            try:
                model.generation_config = GenerationConfig.from_pretrained(
                    pretrained_model_name_or_path,
                    _from_auto=from_auto_class,
                    _from_pipeline=from_pipeline,
                    **repo_loading_kwargs,
                )
            except OSError:
                logger.info(
                    "Generation config file not found, using a generation config created from the model config."
                )
                pass
            if hasattr(model, "load_custom_generate"):
                try:
                    custom_generate = model.load_custom_generate(
                        pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **repo_loading_kwargs
                    )
                    model.generate = functools.partial(custom_generate, model=model)
                except OSError:
                    pass
        if device_map is not None and device_mesh is None:
            device_map_kwargs = {
                "device_map": device_map,
                "offload_dir": offload_folder,
                "offload_index": offload_index,
                "offload_buffers": offload_buffers,
            }
            if "skip_keys" in inspect.signature(dispatch_model).parameters:
                device_map_kwargs["skip_keys"] = model._skip_keys_device_placement
            if (
                "force_hooks" in inspect.signature(dispatch_model).parameters
                and hf_quantizer is not None
                and hf_quantizer.quantization_config.quant_method == QuantizationMethod.HQQ
            ):
                device_map_kwargs["force_hooks"] = True
            if (
                hf_quantizer is not None
                and hf_quantizer.quantization_config.quant_method == QuantizationMethod.FBGEMM_FP8
                and isinstance(device_map, dict)
                and ("cpu" in device_map.values() or "disk" in device_map.values())
            ):
                device_map_kwargs["offload_buffers"] = True
            if not is_fsdp_enabled() and not is_deepspeed_zero3_enabled():
                dispatch_model(model, **device_map_kwargs)
        if hf_quantizer is not None:
            model.hf_quantizer = hf_quantizer
            hf_quantizer.postprocess_model(model, config=config)
        if _adapter_model_path is not None:
            adapter_kwargs["key_mapping"] = key_mapping
            model.load_adapter(
                _adapter_model_path,
                adapter_name=adapter_name,
                token=token,
                adapter_kwargs=adapter_kwargs,
            )
        if output_loading_info:
            if from_pt:
                loading_info = {
                    "missing_keys": missing_keys,
                    "unexpected_keys": unexpected_keys,
                    "mismatched_keys": mismatched_keys,
                    "error_msgs": error_msgs,
                }
            elif from_flax:
                loading_info = None
            return model, loading_info
        return model
    @staticmethod
    def _fix_state_dict_key_on_load(key: str) -> tuple[str, bool]:
        if key.endswith("LayerNorm.beta"):
            return key.replace("LayerNorm.beta", "LayerNorm.bias"), True
        if key.endswith("LayerNorm.gamma"):
            return key.replace("LayerNorm.gamma", "LayerNorm.weight"), True
        if hasattr(nn.utils.parametrizations, "weight_norm"):
            if key.endswith("weight_g"):
                return key.replace("weight_g", "parametrizations.weight.original0"), True
            if key.endswith("weight_v"):
                return key.replace("weight_v", "parametrizations.weight.original1"), True
        else:
            if key.endswith("parametrizations.weight.original0"):
                return key.replace("parametrizations.weight.original0", "weight_g"), True
            if key.endswith("parametrizations.weight.original1"):
                return key.replace("parametrizations.weight.original1", "weight_v"), True
        return key, False
    def _get_key_renaming_mapping(
        self,
        checkpoint_keys: list[str],
        key_mapping: Optional[dict[str, str]] = None,
        loading_base_model_from_task_state_dict: bool = False,
        loading_task_model_from_base_state_dict: bool = False,
    ):
        prefix = self.base_model_prefix
        _prefix = f"{prefix}."
        if loading_task_model_from_base_state_dict:
            task_specific_expected_keys, base_model_keys = [], []
            for key in self.state_dict():
                if key.startswith(_prefix):
                    base_model_keys.append(key[len(_prefix) :])
                else:
                    task_specific_expected_keys.append(key)
        renamed_keys = {}
        key_renaming_mapping = {}
        for key in checkpoint_keys:
            new_key, has_changed = self._fix_state_dict_key_on_load(key)
            if key_mapping is not None:
                for pattern, replacement in key_mapping.items():
                    new_key, n_replace = re.subn(pattern, replacement, new_key)
                    if n_replace > 0:
                        has_changed = True
                        break
            if loading_task_model_from_base_state_dict:
                if new_key in task_specific_expected_keys and new_key not in base_model_keys:
                    raise ValueError(
                        "The state dictionary of the model you are trying to load is corrupted. Are you sure it was "
                        "properly saved?"
                    )
                new_key = ".".join([prefix, new_key])
            elif loading_base_model_from_task_state_dict:
                if not new_key.startswith(_prefix):
                    continue
                new_key = new_key[len(_prefix) :]
            key_renaming_mapping[key] = new_key
            if has_changed:
                if key.endswith("LayerNorm.gamma"):
                    renamed_keys["LayerNorm.gamma"] = (key, new_key)
                elif key.endswith("LayerNorm.beta"):
                    renamed_keys["LayerNorm.beta"] = (key, new_key)
        if renamed_keys:
            warning_msg = f"A pretrained model of type `{self.__class__.__name__}` "
            warning_msg += "contains parameters that have been renamed internally (a few are listed below but more are present in the model):\n"
            for old_key, new_key in renamed_keys.values():
                warning_msg += f"* `{old_key}` -> `{new_key}`\n"
            warning_msg += "If you are using a model from the Hub, consider submitting a PR to adjust these weights and help future users."
            logger.info_once(warning_msg)
        return key_renaming_mapping
    @staticmethod
    def _fix_state_dict_key_on_save(key) -> tuple[str, bool]:
        return key, False
    def _fix_state_dict_keys_on_save(self, state_dict):
        return {self._fix_state_dict_key_on_save(key)[0]: value for key, value in state_dict.items()}
    @classmethod
    def _load_pretrained_model(
        cls,
        model: "PreTrainedModel",
        state_dict: Optional[dict],
        checkpoint_files: Optional[list[str]],
        pretrained_model_name_or_path: Optional[str],
        ignore_mismatched_sizes: bool = False,
        sharded_metadata: Optional[dict] = None,
        device_map: Optional[dict] = None,
        disk_offload_folder: Optional[str] = None,
        dtype: Optional[torch.dtype] = None,
        hf_quantizer: Optional[HfQuantizer] = None,
        keep_in_fp32_regex: Optional[re.Pattern] = None,
        device_mesh: Optional["torch.distributed.device_mesh.DeviceMesh"] = None,
        key_mapping: Optional[dict[str, str]] = None,
        weights_only: bool = True,
    ):
        is_quantized = hf_quantizer is not None
        is_hqq_or_quark = is_quantized and hf_quantizer.quantization_config.quant_method in {
            QuantizationMethod.HQQ,
            QuantizationMethod.QUARK,
        }
        if sharded_metadata is not None:
            original_checkpoint_keys = sharded_metadata["all_checkpoint_keys"]
        elif state_dict is not None:
            original_checkpoint_keys = list(state_dict.keys())
        else:
            original_checkpoint_keys = list(
                load_state_dict(checkpoint_files[0], map_location="meta", weights_only=weights_only).keys()
            )
        prefix = model.base_model_prefix
        has_prefix_module = any(s.startswith(prefix) for s in original_checkpoint_keys) if len(prefix) > 0 else False
        expects_prefix_module = hasattr(model, prefix) if len(prefix) > 0 else False
        loading_task_model_from_base_state_dict = not has_prefix_module and expects_prefix_module
        loading_base_model_from_task_state_dict = has_prefix_module and not expects_prefix_module
        key_renaming_mapping = model._get_key_renaming_mapping(
            original_checkpoint_keys,
            key_mapping,
            loading_base_model_from_task_state_dict,
            loading_task_model_from_base_state_dict,
        )
        checkpoint_keys = list(key_renaming_mapping.values())
        missing_keys, unexpected_keys = _find_missing_and_unexpected_keys(
            model, original_checkpoint_keys, checkpoint_keys, loading_base_model_from_task_state_dict, hf_quantizer
        )
        mismatched_keys, mismatched_shapes = _find_mismatched_keys(
            model,
            state_dict,
            checkpoint_files,
            ignore_mismatched_sizes,
            key_renaming_mapping,
            is_quantized,
            weights_only,
        )
        key_renaming_mapping = {
            k: v for k, v in key_renaming_mapping.items() if v not in mismatched_keys and v not in unexpected_keys
        }
        checkpoint_keys = list(key_renaming_mapping.values())
        model._move_missing_keys_from_meta_to_cpu(missing_keys + mismatched_keys, dtype, hf_quantizer)
        model._initialize_missing_keys(missing_keys + mismatched_keys, is_quantized)
        if keep_in_fp32_regex is not None:
            for name, param in model.named_parameters():
                if keep_in_fp32_regex.search(name):
                    param.data = param.data.to(torch.float32)
        reverse_key_renaming_mapping = {v: k for k, v in key_renaming_mapping.items()}
        is_offloaded_safetensors = False
        disk_offload_index = None
        disk_only_shard_files = []
        if device_map is not None and "disk" in device_map.values():
            if disk_offload_folder is not None:
                os.makedirs(disk_offload_folder, exist_ok=True)
            is_offloaded_safetensors = checkpoint_files is not None and checkpoint_files[0].endswith(".safetensors")
            if disk_offload_folder is None and not is_offloaded_safetensors:
                raise ValueError(
                    "The current `device_map` had weights offloaded to the disk. Please provide an `offload_folder`"
                    " for them. Alternatively, make sure you have `safetensors` installed if the model you are using"
                    " offers the weights in this format."
                )
            if is_offloaded_safetensors:
                param_device_map = expand_device_map(device_map, checkpoint_keys)
                str_dtype = str(dtype).replace("torch.", "") if dtype is not None else "float32"
                if sharded_metadata is None:
                    weight_map = dict.fromkeys(checkpoint_keys, checkpoint_files[0])
                else:
                    folder = os.path.sep.join(checkpoint_files[0].split(os.path.sep)[:-1])
                    weight_map = {
                        key_renaming_mapping[k]: v
                        for k, v in sharded_metadata["weight_map"].items()
                        if k in key_renaming_mapping
                    }
                    weight_map = {k: os.path.join(folder, v) for k, v in weight_map.items()}
                    disk_only_shard_files = get_disk_only_shard_files(device_map, weight_map)
                disk_offload_index = {
                    name: {
                        "safetensors_file": file,
                        "weight_name": reverse_key_renaming_mapping[name],
                        "dtype": str_dtype,
                    }
                    for name, file in weight_map.items()
                    if param_device_map[name] == "disk"
                }
            else:
                disk_offload_index = {}
        elif state_dict is not None:
            checkpoint_files = [""]
        expected_keys = list(model.state_dict().keys())
        if hf_quantizer is not None:
            expected_keys = hf_quantizer.update_expected_keys(model, expected_keys, checkpoint_keys)
        if logger.level >= logging.WARNING:
            verify_tp_plan(expected_keys, getattr(model, "_tp_plan", None))
        if device_map is not None and not is_hqq_or_quark:
            expanded_device_map = expand_device_map(device_map, expected_keys)
            caching_allocator_warmup(model, expanded_device_map, hf_quantizer)
        args_list = [
            (
                shard_file,
                state_dict,
                disk_only_shard_files,
                is_quantized,
                device_map,
                hf_quantizer,
                key_renaming_mapping,
                weights_only,
                model,
                reverse_key_renaming_mapping,
                disk_offload_folder,
                disk_offload_index,
                keep_in_fp32_regex,
                device_mesh,
            )
            for shard_file in checkpoint_files
        ]
        error_msgs = []
        if (
            os.environ.get("HF_ENABLE_PARALLEL_LOADING", "").upper() in ENV_VARS_TRUE_VALUES
            and not is_deepspeed_zero3_enabled()
        ):
            _error_msgs, disk_offload_index = load_shard_files_with_threadpool(args_list)
            error_msgs += _error_msgs
        else:
            if len(args_list) > 1:
                args_list = logging.tqdm(args_list, desc="Loading checkpoint shards")
            for args in args_list:
                _error_msgs, disk_offload_index = load_shard_file(args)
                error_msgs += _error_msgs
        if disk_offload_index is not None and len(disk_offload_index) > 0 and not is_offloaded_safetensors:
            save_offload_index(disk_offload_index, disk_offload_folder)
            disk_offload_index = None
        if device_mesh is not None:
            tp_device = list(device_map.values())[0]
            for buffer in model.buffers():
                if buffer.device != tp_device:
                    buffer.data = buffer.to(tp_device)
            if loading_task_model_from_base_state_dict:
                parameters_to_initialize = {
                    name: param for name, param in model.named_parameters() if not name.startswith(prefix)
                }
                for name, param in parameters_to_initialize.items():
                    if param.device.type == "meta":
                        continue
                    to_contiguous, casting_dtype = _infer_parameter_dtype(model, name, param, keep_in_fp32_regex)
                    shard_and_distribute_module(
                        model,
                        param.to(tp_device),
                        param,
                        name,
                        casting_dtype,
                        to_contiguous,
                        device_mesh.get_local_rank(),
                        device_mesh,
                    )
        missing_keys, unexpected_keys = model._adjust_missing_and_unexpected_keys(
            missing_keys, unexpected_keys, loading_task_model_from_base_state_dict
        )
        if len(error_msgs) > 0:
            error_msg = "\n\t".join(error_msgs)
            if "size mismatch" in error_msg:
                error_msg += (
                    "\n\tYou may consider adding `ignore_mismatched_sizes=True` in the model `from_pretrained` method."
                )
            raise RuntimeError(f"Error(s) in loading state_dict for {model.__class__.__name__}:\n\t{error_msg}")
        if len(unexpected_keys) > 0:
            archs = [] if model.config.architectures is None else model.config.architectures
            warner = logger.warning if model.__class__.__name__ in archs else logger.info
            warner(
                f"Some weights of the model checkpoint at {pretrained_model_name_or_path} were not used when"
                f" initializing {model.__class__.__name__}: {unexpected_keys}\n- This IS expected if you are"
                f" initializing {model.__class__.__name__} from the checkpoint of a model trained on another task or"
                " with another architecture (e.g. initializing a BertForSequenceClassification model from a"
                " BertForPreTraining model).\n- This IS NOT expected if you are initializing"
                f" {model.__class__.__name__} from the checkpoint of a model that you expect to be exactly identical"
                " (initializing a BertForSequenceClassification model from a BertForSequenceClassification model)."
            )
        if len(missing_keys) > 0:
            logger.warning(
                f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at"
                f" {pretrained_model_name_or_path} and are newly initialized: {missing_keys}\nYou should probably"
                " TRAIN this model on a down-stream task to be able to use it for predictions and inference."
            )
        if len(mismatched_keys) > 0:
            mismatched_warning = "\n".join(
                [
                    f"- {key}: found shape {shape1} in the checkpoint and {shape2} in the model instantiated"
                    for key, (shape1, shape2) in zip(mismatched_keys, mismatched_shapes)
                ]
            )
            logger.warning(
                f"Some weights of {model.__class__.__name__} were not initialized from the model checkpoint at"
                f" {pretrained_model_name_or_path} and are newly initialized because the shapes did not"
                f" match:\n{mismatched_warning}\nYou should probably TRAIN this model on a down-stream task to be able"
                " to use it for predictions and inference."
            )
        return model, missing_keys, unexpected_keys, mismatched_keys, disk_offload_index, error_msgs
    @classmethod
    def _load_from_tf(cls, model, config, checkpoint_files):
        if checkpoint_files[0].endswith(".index"):
            model = cls.load_tf_weights(model, config, checkpoint_files[0][:-6])
            loading_info = None
        else:
            try:
                from .modeling_tf_pytorch_utils import load_tf2_checkpoint_in_pytorch_model
                model, loading_info = load_tf2_checkpoint_in_pytorch_model(
                    model, checkpoint_files[0], allow_missing_keys=True, output_loading_info=True
                )
            except ImportError:
                logger.error(
                    "Loading a TensorFlow model in PyTorch, requires both PyTorch and TensorFlow to be installed."
                    " Please see https://pytorch.org/ and https://www.tensorflow.org/install/ for installation"
                    " instructions."
                )
                raise
        return model, loading_info
    @classmethod
    def _load_from_flax(cls, model, checkpoint_files):
        try:
            from .modeling_flax_pytorch_utils import load_flax_checkpoint_in_pytorch_model
            model = load_flax_checkpoint_in_pytorch_model(model, checkpoint_files[0])
        except ImportError:
            logger.error(
                "Loading a Flax model in PyTorch, requires both PyTorch and Flax to be installed. Please see"
                " https://pytorch.org/ and https://flax.readthedocs.io/en/latest/installation.html for"
                " installation instructions."
            )
            raise
        return model
    def retrieve_modules_from_names(self, names, add_prefix=False, remove_prefix=False):
        module_keys = {".".join(key.split(".")[:-1]) for key in names}
        module_keys = module_keys.union(
            {".".join(key.split(".")[:-2]) for key in names if len(key) > 0 and key[-1].isdigit()}
        )
        retrieved_modules = []
        for name, module in self.named_modules():
            if remove_prefix:
                _prefix = f"{self.base_model_prefix}."
                name = name.removeprefix(_prefix)
            elif add_prefix:
                name = ".".join([self.base_model_prefix, name]) if len(name) > 0 else self.base_model_prefix
            if name in module_keys:
                retrieved_modules.append(module)
        return retrieved_modules
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoModel"):
        if not isinstance(auto_class, str):
            auto_class = auto_class.__name__
        import MEROAI.models.auto as auto_module
        if not hasattr(auto_module, auto_class):
            raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    def to_bettertransformer(self) -> "PreTrainedModel":
        if not is_optimum_available():
            raise ImportError("The package `optimum` is required to use Better Transformer.")
        from optimum.version import __version__ as optimum_version
        if version.parse(optimum_version) < version.parse("1.7.0"):
            raise ImportError(
                f"Please install optimum>=1.7.0 to use Better Transformer. The version {optimum_version} was found."
            )
        from optimum.bettertransformer import BetterTransformer
        return BetterTransformer.transform(self)
    def reverse_bettertransformer(self):
        if not is_optimum_available():
            raise ImportError("The package `optimum` is required to use Better Transformer.")
        from optimum.version import __version__ as optimum_version
        if version.parse(optimum_version) < version.parse("1.7.0"):
            raise ImportError(
                f"Please install optimum>=1.7.0 to use Better Transformer. The version {optimum_version} was found."
            )
        from optimum.bettertransformer import BetterTransformer
        return BetterTransformer.reverse(self)
    def warn_if_padding_and_no_attention_mask(self, input_ids, attention_mask):
        if is_torch_fx_proxy(input_ids) or torch.jit.is_tracing() or is_torchdynamo_compiling():
            return
        if (attention_mask is not None) or (self.config.pad_token_id is None):
            return
        if self.config.pad_token_id in input_ids[:, [-1, 0]]:
            warn_string = (
                "We strongly recommend passing in an `attention_mask` since your input_ids may be padded. See "
                "https://huggingface.co/docs/MEROAI/troubleshooting"
                "#incorrect-output-when-padding-tokens-arent-masked."
            )
            if (
                (self.config.bos_token_id is not None and self.config.bos_token_id == self.config.pad_token_id)
                or (self.config.eos_token_id is not None and self.config.eos_token_id == self.config.pad_token_id)
                or (self.config.sep_token_id is not None and self.config.sep_token_id == self.config.pad_token_id)
            ):
                warn_string += (
                    f"\nYou may ignore this warning if your `pad_token_id` ({self.config.pad_token_id}) is identical "
                    f"to the `bos_token_id` ({self.config.bos_token_id}), `eos_token_id` ({self.config.eos_token_id}), "
                    f"or the `sep_token_id` ({self.config.sep_token_id}), and your input is not padded."
                )
            logger.warning_once(warn_string)
    @property
    def supports_tp_plan(self):
        if self._tp_plan is not None:
            return True
        if getattr(self.base_model, "_tp_plan", None) is not None:
            return True
        if self.config.base_model_tp_plan is not None:
            return True
        return False
    @property
    def tp_size(self):
        return self._tp_size
    @property
    def supports_pp_plan(self):
        if self._pp_plan is not None:
            return True
        if getattr(self.base_model, "_pp_plan", None) is not None:
            return True
        return False
    @property
    def loss_function(self):
        if hasattr(self, "_loss_function"):
            return self._loss_function
        loss_type = getattr(self, "loss_type", None)
        if loss_type is None or loss_type not in LOSS_MAPPING:
            logger.warning_once(
                f"`loss_type={loss_type}` was set in the config but it is unrecognized. "
                f"Using the default loss: `ForCausalLMLoss`."
            )
            loss_type = "ForCausalLM"
        return LOSS_MAPPING[loss_type]
    @loss_function.setter
    def loss_function(self, value):
        self._loss_function = value
    def kernelize(self):
        if not is_kernels_available():
            raise ValueError(
                "Kernels are not available. To use kernels, please install kernels using `pip install kernels`"
            )
        from kernels import Device, Mode, kernelize
        mode = Mode.INFERENCE if not self.training else Mode.TRAINING
        kernelize(self, device=Device(type=self.device.type), mode=mode)
        self._use_kernels = True
    @property
    def use_kernels(self) -> bool:
        return getattr(self, "_use_kernels", False)
    @use_kernels.setter
    def use_kernels(self, value: bool) -> None:
        if bool(value) and getattr(self, "_use_kernels", False):
            return
        if value:
            self.kernelize()
        else:
            if getattr(self, "_use_kernels", False):
                logger.warning_once(
                    "Disabling kernels at runtime is a no-op as there is no 'unkernelize' routine; keeping current kernels active."
                )
            self._use_kernels = False
    def get_compiled_call(self, compile_config: Optional[CompileConfig]) -> Callable:
        if "llama4" in self.config.model_type:
            return self.__call__
        compile_config = compile_config or CompileConfig()
        default_config = getattr(self.generation_config, "compile_config", None) or CompileConfig()
        if (
            not hasattr(self, "_compiled_call")
            or getattr(self, "_last_compile_config", default_config) != compile_config
        ):
            self._last_compile_config = compile_config
            self._compiled_call = torch.compile(self.__call__, **compile_config.to_dict())
        return self._compiled_call
    @classmethod
    def is_backend_compatible(cls):
        return cls._supports_attention_backend
    def _move_missing_keys_from_meta_to_cpu(
        self, missing_keys: list[str], dtype: torch.dtype, hf_quantizer: Optional[HfQuantizer]
    ) -> None:
        is_quantized = hf_quantizer is not None
        if is_fsdp_enabled() and not is_local_dist_rank_0() and not is_quantized:
            for key, param in self.named_parameters():
                value = torch.empty_like(param, dtype=dtype, device="cpu")
                _load_parameter_into_model(self, key, value)
            return
        model_state_dict = self.state_dict()
        for key in missing_keys:
            param = model_state_dict[key]
            if param.device == torch.device("meta"):
                value = torch.empty_like(param, dtype=dtype, device="cpu")
                if not is_quantized or not hf_quantizer.param_needs_quantization(self, key):
                    _load_parameter_into_model(self, key, value)
                else:
                    hf_quantizer.create_quantized_param(self, value, key, "cpu")
    def _initialize_missing_keys(self, missing_keys: list[str], is_quantized: bool) -> None:
        for key in self.state_dict():
            if key not in missing_keys:
                param_or_buffer = self.get_parameter_or_buffer(key)
                param_or_buffer._is_hf_initialized = True
        def set_is_initialized_for_modules(module):
            if (
                all(getattr(child, "_is_hf_initialized", False) for child in module.children())
                and all(getattr(param, "_is_hf_initialized", False) for param in module.parameters(recurse=False))
                and all(
                    getattr(buffer, "_is_hf_initialized", False)
                    for buffer in module.buffers(recurse=False)
                    if buffer not in module._non_persistent_buffers_set
                )
            ):
                module._is_hf_initialized = True
        self.apply(set_is_initialized_for_modules)
        if is_deepspeed_zero3_enabled() and not is_quantized:
            import deepspeed
            not_initialized_parameters = list(
                {v for v in self.state_dict().values() if not getattr(v, "_is_hf_initialized", False)}
            )
            with deepspeed.zero.GatheredParameters(not_initialized_parameters, modifier_rank=0):
                self.initialize_weights()
        else:
            self.initialize_weights()
    def _adjust_missing_and_unexpected_keys(
        self, missing_keys: list[str], unexpected_keys: list[str], loading_task_model_from_base_state_dict: bool
    ) -> tuple[list[str], list[str]]:
        has_inv_freq_buffers = any(buffer.endswith("rotary_emb.inv_freq") for buffer, _ in self.named_buffers())
        additional_unexpected_patterns = [r"rotary_emb\.inv_freq"] if has_inv_freq_buffers else []
        missing_patterns = self._keys_to_ignore_on_load_missing or []
        unexpected_patterns = (self._keys_to_ignore_on_load_unexpected or []) + additional_unexpected_patterns
        ignore_missing_regex, ignore_unexpected_regex = None, None
        if len(missing_patterns) > 0:
            ignore_missing_regex = re.compile("|".join(rf"({pattern})" for pattern in missing_patterns))
        if len(unexpected_patterns) > 0:
            ignore_unexpected_regex = re.compile("|".join(rf"({pattern})" for pattern in unexpected_patterns))
        if ignore_missing_regex is not None:
            missing_keys = [key for key in missing_keys if ignore_missing_regex.search(key) is None]
        if ignore_unexpected_regex is not None:
            unexpected_keys = [key for key in unexpected_keys if ignore_unexpected_regex.search(key) is None]
        if loading_task_model_from_base_state_dict:
            _prefix = f"{self.base_model_prefix}."
            unexpected_keys = [k.removeprefix(_prefix) for k in unexpected_keys]
        return missing_keys, unexpected_keys
    def get_parameter_or_buffer(self, target: str):
        try:
            return self.get_parameter(target)
        except AttributeError:
            pass
        try:
            return self.get_buffer(target)
        except AttributeError:
            pass
        module, param_name = get_module_from_name(self, target)
        if (
            param_name == "_extra_state"
            and getattr(module.__class__, "get_extra_state", torch.nn.Module.get_extra_state)
            is not torch.nn.Module.get_extra_state
        ):
            return module.get_extra_state()
        raise AttributeError(f"`{target}` is neither a parameter, buffer, nor extra state.")
    def train(self, mode: bool = True):
        out = super().train(mode)
        if self.use_kernels:
            self.kernelize()
        return out
    def eval(self):
        return self.train(False)
PreTrainedModel.push_to_hub = copy_func(PreTrainedModel.push_to_hub)
if PreTrainedModel.push_to_hub.__doc__ is not None:
    PreTrainedModel.push_to_hub.__doc__ = PreTrainedModel.push_to_hub.__doc__.format(
        object="model", object_class="AutoModel", object_files="model file"
    )
def unwrap_model(model: nn.Module, recursive: bool = False) -> nn.Module:
    if is_accelerate_available():
        kwargs = {}
        if recursive:
            if not is_accelerate_available("0.29.0"):
                raise RuntimeError(
                    "Setting `recursive=True` to `unwrap_model` requires `accelerate` v0.29.0. Please upgrade your version of accelerate"
                )
            else:
                kwargs["recursive"] = recursive
        return extract_model_from_parallel(model, **kwargs)
    else:
        if hasattr(model, "module"):
            return unwrap_model(model.module)
        else:
            return model
def expand_device_map(device_map, param_names):
    new_device_map = {}
    for module, device in device_map.items():
        new_device_map.update(
            {p: device for p in param_names if p == module or p.startswith(f"{module}.") or module == ""}
        )
    return new_device_map
def is_accelerator_device(device: Union[str, int, torch.device]) -> bool:
    if device == "disk":
        return False
    else:
        return torch.device(device).type not in ["meta", "cpu"]
def caching_allocator_warmup(model: PreTrainedModel, expanded_device_map: dict, hf_quantizer: Optional[HfQuantizer]):
    factor = 2 if hf_quantizer is None else hf_quantizer.get_accelerator_warm_up_factor()
    accelerator_device_map = {
        param: torch.device(device) for param, device in expanded_device_map.items() if is_accelerator_device(device)
    }
    if not accelerator_device_map:
        return
    tp_plan = getattr(model, "_tp_plan", []) or []
    tp_plan_regex = (
        re.compile("|".join([re.escape(plan) for plan in tp_plan]))
        if _torch_distributed_available and torch.distributed.is_initialized()
        else None
    )
    total_byte_count = defaultdict(lambda: 0)
    tied_param_names = _get_tied_weight_keys(model)
    for param_name, device in accelerator_device_map.items():
        if param_name in tied_param_names:
            continue
        if hf_quantizer is not None:
            param_name = hf_quantizer.get_param_name(param_name)
        try:
            param = model.get_parameter_or_buffer(param_name)
        except AttributeError:
            raise AttributeError(f"Parameter {param_name} not found in model")
        param_byte_count = param.numel() * param.element_size()
        if tp_plan_regex is not None:
            generic_name = re.sub(r"\.\d+\.", ".*.", param_name)
            param_byte_count //= torch.distributed.get_world_size() if tp_plan_regex.search(generic_name) else 1
        total_byte_count[device] += param_byte_count
    for device, byte_count in total_byte_count.items():
        if device.type in ["cuda", "xpu"]:
            torch_accelerator_module = getattr(torch, device.type)
            index = device.index if device.index is not None else torch_accelerator_module.current_device()
            device_memory = torch_accelerator_module.mem_get_info(index)[0]
            byte_count = min(byte_count, max(0, int(device_memory - 1.2 * 1024**3)))
            unused_memory = torch_accelerator_module.memory_reserved(
                index
            ) - torch_accelerator_module.memory_allocated(index)
            byte_count = max(0, byte_count - unused_memory)
        _ = torch.empty(byte_count // factor, dtype=torch.float16, device=device, requires_grad=False)
def get_disk_only_shard_files(device_map, weight_map):
    files_content = collections.defaultdict(list)
    for weight_name, filename in weight_map.items():
        while len(weight_name) > 0 and weight_name not in device_map:
            weight_name = ".".join(weight_name.split(".")[:-1])
        files_content[filename].append(device_map[weight_name])
    return [fname for fname, devices in files_content.items() if set(devices) == {"disk"}]
class AttentionInterface(GeneralInterface):
    _global_mapping = {
        "flash_attention_3": flash_attention_forward,
        "flash_attention_2": flash_attention_forward,
        "flex_attention": flex_attention_forward,
        "paged_attention": paged_attention_forward,
        "sdpa": sdpa_attention_forward,
        "sdpa_paged": sdpa_attention_paged_forward,
        "eager_paged": eager_paged_attention_forward,
    }
ALL_ATTENTION_FUNCTIONS: AttentionInterface = AttentionInterface()
class PreTrainedAudioTokenizerBase(PreTrainedModel):
    @abstractmethod
    def encode(self, input_values: torch.Tensor, *args, **kwargs):
        pass
    @abstractmethod
    def decode(self, audio_codes: torch.Tensor, *args, **kwargs):
        pass