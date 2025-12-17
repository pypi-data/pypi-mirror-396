from contextlib import contextmanager
from ..utils import is_torch_available, logging
if is_torch_available():
    import torch
    import torch.nn as nn
logger = logging.get_logger(__name__)
@contextmanager
def init_empty_weights(include_buffers: bool = False):
    with init_on_device(torch.device("meta"), include_buffers=include_buffers) as f:
        yield f
@contextmanager
def init_on_device(device: "torch.device", include_buffers: bool = False):
    if include_buffers:
        with device:
            yield
        return
    old_register_parameter = nn.Module.register_parameter
    if include_buffers:
        old_register_buffer = nn.Module.register_buffer
    def register_empty_parameter(module, name, param):
        old_register_parameter(module, name, param)
        if param is not None:
            param_cls = type(module._parameters[name])
            kwargs = module._parameters[name].__dict__
            kwargs["requires_grad"] = param.requires_grad
            module._parameters[name] = param_cls(module._parameters[name].to(device), **kwargs)
    def register_empty_buffer(module, name, buffer, persistent=True):
        old_register_buffer(module, name, buffer, persistent=persistent)
        if buffer is not None:
            module._buffers[name] = module._buffers[name].to(device)
    if include_buffers:
        tensor_constructors_to_patch = {
            torch_function_name: getattr(torch, torch_function_name)
            for torch_function_name in ["empty", "zeros", "ones", "full"]
        }
    else:
        tensor_constructors_to_patch = {}
    def patch_tensor_constructor(fn):
        def wrapper(*args, **kwargs):
            kwargs["device"] = device
            return fn(*args, **kwargs)
        return wrapper
    try:
        nn.Module.register_parameter = register_empty_parameter
        if include_buffers:
            nn.Module.register_buffer = register_empty_buffer
        for torch_function_name in tensor_constructors_to_patch:
            setattr(torch, torch_function_name, patch_tensor_constructor(getattr(torch, torch_function_name)))
        yield
    finally:
        nn.Module.register_parameter = old_register_parameter
        if include_buffers:
            nn.Module.register_buffer = old_register_buffer
        for torch_function_name, old_torch_function in tensor_constructors_to_patch.items():
            setattr(torch, torch_function_name, old_torch_function)
def find_tied_parameters(model: "nn.Module", **kwargs):
    all_named_parameters = dict(model.named_parameters(remove_duplicate=False))
    no_duplicate_named_parameters = dict(model.named_parameters(remove_duplicate=True))
    tied_param_names = set(all_named_parameters.keys()) - set(no_duplicate_named_parameters.keys())
    tied_param_groups = {}
    for tied_param_name in tied_param_names:
        tied_param = all_named_parameters[tied_param_name]
        for param_name, param in no_duplicate_named_parameters.items():
            if param is tied_param:
                if param_name not in tied_param_groups:
                    tied_param_groups[param_name] = []
                tied_param_groups[param_name].append(tied_param_name)
    return [sorted([weight] + list(set(tied))) for weight, tied in tied_param_groups.items()]