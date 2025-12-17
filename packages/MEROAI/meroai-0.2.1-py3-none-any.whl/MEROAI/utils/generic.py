import inspect
import json
import os
import tempfile
import warnings
from collections import OrderedDict, UserDict, defaultdict
from collections.abc import Iterable, MutableMapping
from contextlib import AbstractContextManager, ExitStack, contextmanager
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from functools import partial, wraps
from typing import Any, Callable, Optional, TypedDict
import numpy as np
from ..utils import logging
from .import_utils import (
    is_flax_available,
    is_mlx_available,
    is_tf_available,
    is_torch_available,
    is_torch_fx_proxy,
    requires,
)
_CAN_RECORD_REGISTRY = {}
logger = logging.get_logger(__name__)
if is_torch_available():
    import torch
    from ..model_debugging_utils import model_addition_debugger_context
def strtobool(val):
    val = val.lower()
    if val in {"y", "yes", "t", "true", "on", "1"}:
        return 1
    if val in {"n", "no", "f", "false", "off", "0"}:
        return 0
    raise ValueError(f"invalid truth value {val!r}")
def infer_framework_from_repr(x):
    representation = str(type(x))
    if representation.startswith("<class 'torch."):
        return "pt"
    elif representation.startswith("<class 'tensorflow."):
        return "tf"
    elif representation.startswith("<class 'jax"):
        return "jax"
    elif representation.startswith("<class 'numpy."):
        return "np"
    elif representation.startswith("<class 'mlx."):
        return "mlx"
def _get_frameworks_and_test_func(x):
    framework_to_test = {
        "pt": is_torch_tensor,
        "tf": is_tf_tensor,
        "jax": is_jax_tensor,
        "np": is_numpy_array,
        "mlx": is_mlx_array,
    }
    preferred_framework = infer_framework_from_repr(x)
    frameworks = [] if preferred_framework is None else [preferred_framework]
    if preferred_framework != "np":
        frameworks.append("np")
    frameworks.extend([f for f in framework_to_test if f not in [preferred_framework, "np"]])
    return {f: framework_to_test[f] for f in frameworks}
def is_tensor(x):
    framework_to_test_func = _get_frameworks_and_test_func(x)
    for test_func in framework_to_test_func.values():
        if test_func(x):
            return True
    if is_torch_fx_proxy(x):
        return True
    if is_flax_available():
        from jax.core import Tracer
        if isinstance(x, Tracer):
            return True
    return False
def _is_numpy(x):
    return isinstance(x, np.ndarray)
def is_numpy_array(x):
    return _is_numpy(x)
def _is_torch(x):
    import torch
    return isinstance(x, torch.Tensor)
def is_torch_tensor(x):
    return False if not is_torch_available() else _is_torch(x)
def _is_torch_device(x):
    import torch
    return isinstance(x, torch.device)
def is_torch_device(x):
    return False if not is_torch_available() else _is_torch_device(x)
def _is_torch_dtype(x):
    import torch
    if isinstance(x, str):
        if hasattr(torch, x):
            x = getattr(torch, x)
        else:
            return False
    return isinstance(x, torch.dtype)
def is_torch_dtype(x):
    return False if not is_torch_available() else _is_torch_dtype(x)
def _is_tensorflow(x):
    import tensorflow as tf
    return isinstance(x, tf.Tensor)
def is_tf_tensor(x):
    return False if not is_tf_available() else _is_tensorflow(x)
def _is_tf_symbolic_tensor(x):
    import tensorflow as tf
    if hasattr(tf, "is_symbolic_tensor"):
        return tf.is_symbolic_tensor(x)
    return isinstance(x, tf.Tensor)
def is_tf_symbolic_tensor(x):
    return False if not is_tf_available() else _is_tf_symbolic_tensor(x)
def _is_jax(x):
    import jax.numpy as jnp
    return isinstance(x, jnp.ndarray)
def is_jax_tensor(x):
    return False if not is_flax_available() else _is_jax(x)
def _is_mlx(x):
    import mlx.core as mx
    return isinstance(x, mx.array)
def is_mlx_array(x):
    return False if not is_mlx_available() else _is_mlx(x)
def to_py_obj(obj):
    if isinstance(obj, (int, float)):
        return obj
    elif isinstance(obj, (dict, UserDict)):
        return {k: to_py_obj(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        try:
            arr = np.array(obj)
            if np.issubdtype(arr.dtype, np.integer) or np.issubdtype(arr.dtype, np.floating):
                return arr.tolist()
        except Exception:
            pass
        return [to_py_obj(o) for o in obj]
    framework_to_py_obj = {
        "pt": lambda obj: obj.tolist(),
        "tf": lambda obj: obj.numpy().tolist(),
        "jax": lambda obj: np.asarray(obj).tolist(),
        "np": lambda obj: obj.tolist(),
    }
    framework_to_test_func = _get_frameworks_and_test_func(obj)
    for framework, test_func in framework_to_test_func.items():
        if test_func(obj):
            return framework_to_py_obj[framework](obj)
    if isinstance(obj, np.number):
        return obj.tolist()
    else:
        return obj
def to_numpy(obj):
    framework_to_numpy = {
        "pt": lambda obj: obj.detach().cpu().numpy(),
        "tf": lambda obj: obj.numpy(),
        "jax": lambda obj: np.asarray(obj),
        "np": lambda obj: obj,
    }
    if isinstance(obj, (dict, UserDict)):
        return {k: to_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return np.array(obj)
    framework_to_test_func = _get_frameworks_and_test_func(obj)
    for framework, test_func in framework_to_test_func.items():
        if test_func(obj):
            return framework_to_numpy[framework](obj)
    return obj
class ModelOutput(OrderedDict):
    def __init_subclass__(cls) -> None:
        if is_torch_available():
            from torch.utils._pytree import register_pytree_node
            register_pytree_node(
                cls,
                _model_output_flatten,
                partial(_model_output_unflatten, output_type=cls),
                serialized_type_name=f"{cls.__module__}.{cls.__name__}",
            )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_modeloutput_subclass = self.__class__ != ModelOutput
        if is_modeloutput_subclass and not is_dataclass(self):
            raise TypeError(
                f"{self.__module__}.{self.__class__.__name__} is not a dataclass."
                " This is a subclass of ModelOutput and so must use the @dataclass decorator."
            )
    def __post_init__(self):
        class_fields = fields(self)
        if not len(class_fields):
            raise ValueError(f"{self.__class__.__name__} has no fields.")
        if not all(field.default is None for field in class_fields[1:]):
            raise ValueError(f"{self.__class__.__name__} should not have more than one required field.")
        first_field = getattr(self, class_fields[0].name)
        other_fields_are_none = all(getattr(self, field.name) is None for field in class_fields[1:])
        if other_fields_are_none and not is_tensor(first_field):
            if isinstance(first_field, dict):
                iterator = first_field.items()
                first_field_iterator = True
            else:
                try:
                    iterator = iter(first_field)
                    first_field_iterator = True
                except TypeError:
                    first_field_iterator = False
            if first_field_iterator:
                setattr(self, class_fields[0].name, None)
                for idx, element in enumerate(iterator):
                    if not isinstance(element, (list, tuple)) or len(element) != 2 or not isinstance(element[0], str):
                        if idx == 0:
                            self[class_fields[0].name] = first_field
                        else:
                            raise ValueError(
                                f"Cannot set key/value for {element}. It needs to be a tuple (key, value)."
                            )
                        break
                    setattr(self, element[0], element[1])
                    if element[1] is not None:
                        self[element[0]] = element[1]
            elif first_field is not None:
                self[class_fields[0].name] = first_field
        else:
            for field in class_fields:
                v = getattr(self, field.name)
                if v is not None:
                    self[field.name] = v
    def __delitem__(self, *args, **kwargs):
        raise Exception(f"You cannot use ``__delitem__`` on a {self.__class__.__name__} instance.")
    def setdefault(self, *args, **kwargs):
        raise Exception(f"You cannot use ``setdefault`` on a {self.__class__.__name__} instance.")
    def pop(self, *args, **kwargs):
        raise Exception(f"You cannot use ``pop`` on a {self.__class__.__name__} instance.")
    def update(self, *args, **kwargs):
        raise Exception(f"You cannot use ``update`` on a {self.__class__.__name__} instance.")
    def __getitem__(self, k):
        if isinstance(k, str):
            inner_dict = dict(self.items())
            return inner_dict[k]
        else:
            return self.to_tuple()[k]
    def __setattr__(self, name, value):
        if name in self.keys() and value is not None:
            super().__setitem__(name, value)
        super().__setattr__(name, value)
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        super().__setattr__(key, value)
    def __reduce__(self):
        if not is_dataclass(self):
            return super().__reduce__()
        callable, _args, *remaining = super().__reduce__()
        args = tuple(getattr(self, field.name) for field in fields(self))
        return callable, args, *remaining
    def to_tuple(self) -> tuple:
        return tuple(self[k] for k in self.keys())
if is_torch_available():
    import torch.utils._pytree as _torch_pytree
    def _model_output_flatten(output: ModelOutput) -> tuple[list[Any], "_torch_pytree.Context"]:
        return list(output.values()), list(output.keys())
    def _model_output_unflatten(
        values: Iterable[Any],
        context: "_torch_pytree.Context",
        output_type=None,
    ) -> ModelOutput:
        return output_type(**dict(zip(context, values)))
    _torch_pytree.register_pytree_node(
        ModelOutput,
        _model_output_flatten,
        partial(_model_output_unflatten, output_type=ModelOutput),
        serialized_type_name=f"{ModelOutput.__module__}.{ModelOutput.__name__}",
    )
class ExplicitEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        raise ValueError(
            f"{value} is not a valid {cls.__name__}, please select one of {list(cls._value2member_map_.keys())}"
        )
class PaddingStrategy(ExplicitEnum):
    LONGEST = "longest"
    MAX_LENGTH = "max_length"
    DO_NOT_PAD = "do_not_pad"
class TensorType(ExplicitEnum):
    PYTORCH = "pt"
    TENSORFLOW = "tf"
    NUMPY = "np"
    JAX = "jax"
    MLX = "mlx"
class ContextManagers:
    def __init__(self, context_managers: list[AbstractContextManager]):
        self.context_managers = context_managers
        self.stack = ExitStack()
    def __enter__(self):
        for context_manager in self.context_managers:
            self.stack.enter_context(context_manager)
    def __exit__(self, *args, **kwargs):
        self.stack.__exit__(*args, **kwargs)
def can_return_loss(model_class):
    framework = infer_framework(model_class)
    if framework == "tf":
        signature = inspect.signature(model_class.call)
    elif framework == "pt":
        signature = inspect.signature(model_class.forward)
    else:
        signature = inspect.signature(model_class.__call__)
    for p in signature.parameters:
        if p == "return_loss" and signature.parameters[p].default is True:
            return True
    return False
def find_labels(model_class):
    model_name = model_class.__name__
    framework = infer_framework(model_class)
    if framework == "tf":
        signature = inspect.signature(model_class.call)
    elif framework == "pt":
        signature = inspect.signature(model_class.forward)
    else:
        signature = inspect.signature(model_class.__call__)
    if "QuestionAnswering" in model_name:
        return [p for p in signature.parameters if "label" in p or p in ("start_positions", "end_positions")]
    else:
        return [p for p in signature.parameters if "label" in p]
def flatten_dict(d: MutableMapping, parent_key: str = "", delimiter: str = "."):
    def _flatten_dict(d, parent_key="", delimiter="."):
        for k, v in d.items():
            key = str(parent_key) + delimiter + str(k) if parent_key else k
            if v and isinstance(v, MutableMapping):
                yield from flatten_dict(v, key, delimiter=delimiter).items()
            else:
                yield key, v
    return dict(_flatten_dict(d, parent_key, delimiter))
@contextmanager
def working_or_temp_dir(working_dir, use_temp_dir: bool = False):
    if use_temp_dir:
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    else:
        yield working_dir
def transpose(array, axes=None):
    if is_numpy_array(array):
        return np.transpose(array, axes=axes)
    elif is_torch_tensor(array):
        return array.T if axes is None else array.permute(*axes)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.transpose(array, perm=axes)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.transpose(array, axes=axes)
    else:
        raise ValueError(f"Type not supported for transpose: {type(array)}.")
def reshape(array, newshape):
    if is_numpy_array(array):
        return np.reshape(array, newshape)
    elif is_torch_tensor(array):
        return array.reshape(*newshape)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.reshape(array, newshape)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.reshape(array, newshape)
    else:
        raise ValueError(f"Type not supported for reshape: {type(array)}.")
def squeeze(array, axis=None):
    if is_numpy_array(array):
        return np.squeeze(array, axis=axis)
    elif is_torch_tensor(array):
        return array.squeeze() if axis is None else array.squeeze(dim=axis)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.squeeze(array, axis=axis)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.squeeze(array, axis=axis)
    else:
        raise ValueError(f"Type not supported for squeeze: {type(array)}.")
def expand_dims(array, axis):
    if is_numpy_array(array):
        return np.expand_dims(array, axis)
    elif is_torch_tensor(array):
        return array.unsqueeze(dim=axis)
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.expand_dims(array, axis=axis)
    elif is_jax_tensor(array):
        import jax.numpy as jnp
        return jnp.expand_dims(array, axis=axis)
    else:
        raise ValueError(f"Type not supported for expand_dims: {type(array)}.")
def tensor_size(array):
    if is_numpy_array(array):
        return np.size(array)
    elif is_torch_tensor(array):
        return array.numel()
    elif is_tf_tensor(array):
        import tensorflow as tf
        return tf.size(array)
    elif is_jax_tensor(array):
        return array.size
    else:
        raise ValueError(f"Type not supported for tensor_size: {type(array)}.")
def infer_framework(model_class):
    for base_class in inspect.getmro(model_class):
        module = base_class.__module__
        name = base_class.__name__
        if module.startswith("tensorflow") or module.startswith("keras") or name == "TFPreTrainedModel":
            return "tf"
        elif module.startswith("torch") or name == "PreTrainedModel":
            return "pt"
        elif module.startswith("flax") or module.startswith("jax") or name == "FlaxPreTrainedModel":
            return "flax"
    raise TypeError(f"Could not infer framework from class {model_class}.")
def torch_int(x):
    if not is_torch_available():
        return int(x)
    import torch
    return x.to(torch.int64) if torch.jit.is_tracing() and isinstance(x, torch.Tensor) else int(x)
def torch_float(x):
    if not is_torch_available():
        return int(x)
    import torch
    return x.to(torch.float32) if torch.jit.is_tracing() and isinstance(x, torch.Tensor) else int(x)
def filter_out_non_signature_kwargs(extra: Optional[list] = None):
    extra = extra or []
    extra_params_to_pass = set(extra)
    def decorator(func):
        sig = inspect.signature(func)
        function_named_args = set(sig.parameters.keys())
        valid_kwargs_to_pass = function_named_args.union(extra_params_to_pass)
        is_instance_method = "self" in function_named_args
        is_class_method = "cls" in function_named_args
        func._filter_out_non_signature_kwargs = True
        @wraps(func)
        def wrapper(*args, **kwargs):
            valid_kwargs = {}
            invalid_kwargs = {}
            for k, v in kwargs.items():
                if k in valid_kwargs_to_pass:
                    valid_kwargs[k] = v
                else:
                    invalid_kwargs[k] = v
            if invalid_kwargs:
                invalid_kwargs_names = [f"'{k}'" for k in invalid_kwargs]
                invalid_kwargs_names = ", ".join(invalid_kwargs_names)
                if is_instance_method:
                    cls_prefix = args[0].__class__.__name__ + "."
                elif is_class_method:
                    cls_prefix = args[0].__name__ + "."
                else:
                    cls_prefix = ""
                warnings.warn(
                    f"The following named arguments are not valid for `{cls_prefix}{func.__name__}`"
                    f" and were ignored: {invalid_kwargs_names}",
                    UserWarning,
                    stacklevel=2,
                )
            return func(*args, **valid_kwargs)
        return wrapper
    return decorator
class MEROAIKwargs(TypedDict, total=False):
    num_items_in_batch: Optional["torch.Tensor"]
    output_hidden_states: Optional[bool]
    output_attentions: Optional[bool]
    output_router_logits: Optional[bool]
    cu_seq_lens_q: Optional["torch.LongTensor"]
    cu_seq_lens_k: Optional["torch.LongTensor"]
    max_length_q: Optional[int]
    max_length_k: Optional[int]
def is_timm_config_dict(config_dict: dict[str, Any]) -> bool:
    return "pretrained_cfg" in config_dict
def is_timm_local_checkpoint(pretrained_model_path: str) -> bool:
    if pretrained_model_path is None:
        return False
    pretrained_model_path = str(pretrained_model_path)
    is_file = os.path.isfile(pretrained_model_path)
    is_dir = os.path.isdir(pretrained_model_path)
    if is_file and pretrained_model_path.endswith(".json"):
        with open(pretrained_model_path) as f:
            config_dict = json.load(f)
        return is_timm_config_dict(config_dict)
    if is_dir and os.path.exists(os.path.join(pretrained_model_path, "config.json")):
        with open(os.path.join(pretrained_model_path, "config.json")) as f:
            config_dict = json.load(f)
        return is_timm_config_dict(config_dict)
    return False
def set_attribute_for_modules(module: "torch.nn.Module", key: str, value: Any):
    setattr(module, key, value)
    for submodule in module.children():
        set_attribute_for_modules(submodule, key, value)
def del_attribute_from_modules(module: "torch.nn.Module", key: str):
    if hasattr(module, key):
        delattr(module, key)
    for submodule in module.children():
        del_attribute_from_modules(submodule, key)
def can_return_tuple(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return_dict = self.config.return_dict if hasattr(self, "config") else True
        return_dict_passed = kwargs.pop("return_dict", return_dict)
        if return_dict_passed is not None:
            return_dict = return_dict_passed
        output = func(self, *args, **kwargs)
        if not return_dict and not isinstance(output, tuple):
            output = output.to_tuple()
        return output
    return wrapper
@dataclass
@requires(backends=("torch",))
class OutputRecorder:
    target_class: "type[torch.nn.Module]"
    index: int = 0
    layer_name: Optional[str] = None
    class_name: Optional[str] = None
def check_model_inputs(tie_last_hidden_states=True):
    def wrapped_fn(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            use_cache = (
                kwargs["use_cache"] if kwargs.get("use_cache") is not None else getattr(self.config, "use_cache", None)
            )
            if use_cache is not None:
                if getattr(self, "gradient_checkpointing", False) and self.training and use_cache:
                    logger.warning_once(
                        "`use_cache=True` is incompatible with gradient checkpointing. Setting `use_cache=False`."
                    )
                    use_cache = False
                kwargs["use_cache"] = use_cache
            return_dict = kwargs.pop("return_dict", None)
            if return_dict is None:
                return_dict = getattr(self.config, "return_dict", True)
            all_args = kwargs.copy()
            if "kwargs" in all_args:
                for k, v in all_args["kwargs"].items():
                    all_args[k] = v
            capture_flags = _CAN_RECORD_REGISTRY.get(str(self.__class__), {})
            recordable_keys = {
                f"output_{k}": all_args.get(
                    f"output_{k}",
                    getattr(
                        self.config,
                        f"output_{k}",
                        all_args.get("output_attentions", getattr(self.config, "output_attentions", False)),
                    ),
                )
                for k in capture_flags
            }
            if "output_attentions" in recordable_keys:
                recordable_keys["output_cross_attentions"] = recordable_keys["output_attentions"]
            collected_outputs = defaultdict(tuple)
            monkey_patched_layers = []
            if recordable_keys.get("output_attentions", False):
                supported_attn = ["eager", "eager_paged", "flex_attention"]
                config_attn = getattr(self.config, "_attn_implementation", None)
                sub_configs = [getattr(self.config, key, None) for key in self.config.sub_configs]
                sub_configs_attn = [
                    getattr(config, "_attn_implementation", None) for config in sub_configs if config is not None
                ]
                if config_attn not in supported_attn or any(attn not in supported_attn for attn in sub_configs_attn):
                    warnings.warn(
                        f"`output_attentions=True` is not supported with `attn_implementation` other than {supported_attn}. "
                        "Please use `model.set_attn_implementation('eager')` to enable capturing attention outputs.",
                        UserWarning,
                    )
            def make_capture_wrapper(module, orig_forward, key, index):
                @wraps(orig_forward)
                def wrapped_forward(*args, **kwargs):
                    if key == "hidden_states" and len(collected_outputs[key]) == 0:
                        collected_outputs[key] += (args[0],)
                    if kwargs.get("debug_io", False):
                        with model_addition_debugger_context(
                            module, kwargs.get("debug_io_dir", "~/model_debug"), kwargs.get("prune_layers")
                        ):
                            output = orig_forward(*args, **kwargs)
                    else:
                        output = orig_forward(*args, **kwargs)
                    if not isinstance(output, tuple):
                        collected_outputs[key] += (output,)
                    elif output[index] is not None:
                        if key not in collected_outputs:
                            collected_outputs[key] = (output[index],)
                        else:
                            collected_outputs[key] += (output[index],)
                    return output
                return wrapped_forward
            if any(recordable_keys.values()):
                capture_tasks = []
                for key, layer_specs in capture_flags.items():
                    if not recordable_keys.get(f"output_{key}", False):
                        continue
                    if not isinstance(layer_specs, list):
                        layer_specs = [layer_specs]
                    for specs in layer_specs:
                        if not isinstance(specs, OutputRecorder):
                            index = 0 if "hidden_states" in key else 1
                            class_name = None if not isinstance(specs, str) else specs
                            target_class = specs if not isinstance(specs, str) else None
                            specs = OutputRecorder(target_class=target_class, index=index, class_name=class_name)
                        capture_tasks.append((key, specs))
                for name, module in self.named_modules():
                    for key, specs in capture_tasks:
                        if (specs.target_class is not None and isinstance(module, specs.target_class)) or (
                            specs.class_name is not None and name.endswith(specs.class_name)
                        ):
                            if specs.layer_name is not None and specs.layer_name not in name:
                                continue
                            original_forward = module.forward
                            module.forward = make_capture_wrapper(module, original_forward, key, specs.index)
                            monkey_patched_layers.append((module, original_forward))
            try:
                outputs = func(self, *args, **kwargs)
            except TypeError as original_exception:
                kwargs_without_recordable = {k: v for k, v in kwargs.items() if k not in recordable_keys}
                try:
                    outputs = func(self, *args, **kwargs_without_recordable)
                except TypeError:
                    raise original_exception
                raise TypeError(
                    "Missing `**kwargs` in the signature of the `@check_model_inputs`-decorated function "
                    f"({func.__qualname__})"
                )
            for module, original_forward in monkey_patched_layers:
                module.forward = original_forward
            for key in collected_outputs:
                if key == "hidden_states":
                    if not tie_last_hidden_states:
                        pass
                    elif hasattr(outputs, "vision_hidden_states"):
                        collected_outputs[key] = collected_outputs[key][:-1]
                        collected_outputs[key] += (outputs.vision_hidden_states,)
                    elif hasattr(outputs, "last_hidden_state"):
                        collected_outputs[key] = collected_outputs[key][:-1]
                        collected_outputs[key] += (outputs.last_hidden_state,)
                    outputs[key] = collected_outputs[key]
                elif key == "attentions":
                    if isinstance(capture_flags[key], list) and len(capture_flags[key]) == 2:
                        outputs[key] = collected_outputs[key][0::2]
                        outputs["cross_" + key] = collected_outputs[key][1::2]
                    else:
                        outputs[key] = collected_outputs[key]
                else:
                    outputs[key] = collected_outputs[key]
            if return_dict is False:
                outputs = outputs.to_tuple()
            return outputs
        return wrapper
    return wrapped_fn
class GeneralInterface(MutableMapping):
    _global_mapping = {}
    def __init__(self):
        self._local_mapping = {}
    def __getitem__(self, key):
        if key in self._local_mapping:
            return self._local_mapping[key]
        return self._global_mapping[key]
    def __setitem__(self, key, value):
        self._local_mapping.update({key: value})
    def __delitem__(self, key):
        del self._local_mapping[key]
    def __iter__(self):
        return iter({**self._global_mapping, **self._local_mapping})
    def __len__(self):
        return len(self._global_mapping.keys() | self._local_mapping.keys())
    @classmethod
    def register(cls, key: str, value: Callable):
        cls._global_mapping.update({key: value})
    def valid_keys(self) -> list[str]:
        return list(self.keys())