import functools
import json
import os
import re
from contextlib import contextmanager, redirect_stdout
from io import StringIO
from typing import Optional
from .utils import logging
from .utils.import_utils import is_torch_available, requires
if is_torch_available():
    import torch
    from safetensors.torch import save_file
    _torch_distributed_available = False
    if torch.distributed.is_available():
        import torch.distributed.tensor
        _torch_distributed_available = True
else:
    _torch_distributed_available = False
logger = logging.get_logger(__name__)
def _is_rank_zero():
    if not (_torch_distributed_available and torch.distributed.is_initialized()):
        return True
    return torch.distributed.get_rank() == 0
MEMORY_ADDRESS_REGEX = re.compile(r"object at 0x[0-9A-Fa-f]+")
def _sanitize_repr_for_diff(x_str: str) -> str:
    return MEMORY_ADDRESS_REGEX.sub("object at 0xXXXXXXXX", x_str)
def _dtensor_repr(x):
    if _is_rank_zero():
        return f"DTensor (rank0) -> {repr(x._local_tensor)}"
    return "DTensor(non-rank0)"
def _serialize_tensor_like_io(
    value, debug_path: Optional[str] = None, use_repr: bool = True, path_to_value: Optional[str] = None
):
    torch.set_printoptions(sci_mode=True)
    if use_repr:
        value_out = _repr_to_list(value)
    elif path_to_value:
        if not path_to_value.endswith(".safetensors"):
            path_to_value += ".safetensors"
        filepath = os.path.join(debug_path, path_to_value) if debug_path else path_to_value
        save_file({"data": value.contiguous().detach().cpu()}, filepath)
        value_out = f"./{path_to_value}"
    else:
        raise ValueError(f"{use_repr=} and {path_to_value=} cannot both be falsy.")
    out = {
        "shape": repr(value.shape),
        "dtype": repr(value.dtype),
        "value": value_out,
    }
    if value.dtype in {torch.float16, torch.float32, torch.bfloat16}:
        out.update(
            {
                "mean": _sanitize_repr_for_diff(repr(value.mean())),
                "std": _sanitize_repr_for_diff(repr(value.std())),
                "min": _sanitize_repr_for_diff(repr(value.min())),
                "max": _sanitize_repr_for_diff(repr(value.max())),
            }
        )
    return out
def _serialize_io(value, debug_path: Optional[str] = None, use_repr: bool = True, path_to_value: Optional[str] = None):
    if isinstance(value, (list, tuple)):
        return [
            _serialize_io(v, debug_path=debug_path, use_repr=use_repr, path_to_value=f"{path_to_value}_{i}")
            for i, v in enumerate(value)
        ]
    if isinstance(value, dict):
        return {
            k: _serialize_io(v, debug_path=debug_path, use_repr=use_repr, path_to_value=f"{path_to_value}_{k}")
            for k, v in value.items()
        }
    if hasattr(value, "_local_tensor"):
        return _serialize_tensor_like_io(
            value._local_tensor, debug_path=debug_path, use_repr=use_repr, path_to_value=path_to_value
        )
    if isinstance(value, torch.Tensor):
        return _serialize_tensor_like_io(value, debug_path=debug_path, use_repr=use_repr, path_to_value=path_to_value)
    return _sanitize_repr_for_diff(repr(value))
def _repr_to_list(value: torch.Tensor):
    torch.set_printoptions(sci_mode=True, linewidth=120)
    with StringIO() as buf, redirect_stdout(buf):
        print(value)
        raw = buf.getvalue()
    return _sanitize_repr_for_diff(raw).splitlines()
def prune_outputs_if_children(node):
    if node.get("children"):
        node.pop("outputs", None)
        for child in node["children"]:
            prune_outputs_if_children(child)
LAYER_SUFFIX_RE = re.compile(r"(.*)\.(\d+)$")
def is_layer_block(node):
    match = LAYER_SUFFIX_RE.match(node.get("module_path", ""))
    if not match or not node.get("children"):
        return False
    number = match.group(2)
    return any(f".{number}." in child.get("module_path", "") for child in node["children"])
def prune_intermediate_layers(node):
    if not node.get("children"):
        return
    layer_blocks = [(i, child) for i, child in enumerate(node["children"]) if is_layer_block(child)]
    if len(layer_blocks) > 2:
        to_remove = [i for i, _ in layer_blocks[1:-1]]
        node["children"] = [child for i, child in enumerate(node["children"]) if i not in to_remove]
    for child in node["children"]:
        prune_intermediate_layers(child)
def log_model_debug_trace(debug_path: Optional[str], model):
    if debug_path:
        try:
            os.makedirs(debug_path, exist_ok=True)
            base = os.path.join(debug_path, model._debugger_module_dump_name + "_debug_tree")
        except Exception as e:
            raise ValueError(f"Unexpected or existing debug_path={debug_path}.") from e
    else:
        base = model._debugger_module_dump_name + "_debug_tree"
    logger.info(f"Writing model trace at {base}.json")
    full_path = base + "_FULL_TENSORS.json"
    summary_path = base + "_SUMMARY.json"
    prune_outputs_if_children(model._call_tree)
    with open(full_path, "w") as f:
        json.dump(model._call_tree, f, indent=2)
    def strip_values(node):
        def clean(val):
            if isinstance(val, dict):
                val.pop("value", None)
                for v in val.values():
                    clean(v)
            elif isinstance(val, list):
                for item in val:
                    clean(item)
        clean(node.get("inputs", {}))
        clean(node.get("outputs", {}))
        for child in node.get("children", []):
            strip_values(child)
    tree_copy = json.loads(json.dumps(model._call_tree))
    strip_values(tree_copy)
    with open(summary_path, "w") as f:
        json.dump(tree_copy, f, indent=2)
def _attach_debugger_logic(
    model,
    debug_path: str = ".",
    do_prune_layers: bool = True,
    use_repr: bool = True,
):
    class_name = model.__class__.__name__
    model._call_tree = {"module_path": class_name, "inputs": None, "outputs": None, "children": []}
    model._debugger_model_call_stack = []
    model._debugger_module_dump_name = class_name
    if debug_path:
        try:
            os.makedirs(debug_path, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Unexpected or existing debug_path={debug_path}.") from e
    def wrap_forward(module, full_path):
        orig_forward = module.forward
        @functools.wraps(orig_forward)
        def wrapped_forward(*inps, **kws):
            if _is_rank_zero():
                dict_inputs = {"args": inps, "kwargs": kws}
                dict_inputs = {k: dict_inputs[k] for k in dict_inputs if len(dict_inputs[k]) > 0}
                node = {
                    "module_path": full_path,
                    "inputs": _serialize_io(
                        dict_inputs,
                        debug_path=debug_path,
                        use_repr=use_repr,
                        path_to_value=f"{full_path}_inputs",
                    ),
                    "outputs": None,
                    "children": [],
                }
                model._debugger_model_call_stack.append(node)
            with torch.no_grad():
                out = orig_forward(*inps, **kws)
            if _is_rank_zero():
                if sum(1 for _ in module.named_children()) > 0:
                    node["outputs"] = None
                else:
                    node["outputs"] = _serialize_io(
                        out,
                        debug_path=debug_path,
                        use_repr=use_repr,
                        path_to_value=f"{full_path}_outputs",
                    )
                finished = model._debugger_model_call_stack.pop()
                if not finished["children"]:
                    finished.pop("children")
                if model._debugger_model_call_stack:
                    model._debugger_model_call_stack[-1]["children"].append(finished)
            return out
        module.forward = wrapped_forward
    for name, submodule in model.named_modules():
        if name == "":
            continue
        wrap_forward(submodule, f"{class_name}.{name}")
    real_top_forward = model.forward
    @functools.wraps(real_top_forward)
    def top_wrapped_forward(*inps, **kws):
        if _is_rank_zero():
            top_node = {
                "module_path": f"{class_name} (top-level)",
                "inputs": _serialize_io(
                    {"args": inps, "kwargs": kws},
                    debug_path=debug_path,
                    use_repr=use_repr,
                    path_to_value=f"{class_name}_inputs",
                ),
                "outputs": None,
                "children": [],
            }
            model._debugger_model_call_stack.append(top_node)
        out = real_top_forward(*inps, **kws)
        if _is_rank_zero() and model._debugger_model_call_stack:
            top_node["outputs"] = _serialize_io(
                out,
                debug_path=debug_path,
                use_repr=use_repr,
                path_to_value=f"{class_name}_outputs",
            )
            finished = model._debugger_model_call_stack.pop()
            model._call_tree["inputs"] = finished["inputs"]
            model._call_tree["outputs"] = finished["outputs"]
            model._call_tree["children"] = finished["children"]
            [model._call_tree.pop(k, None) for k in list(model._call_tree.keys()) if not model._call_tree[k]]
            if do_prune_layers:
                prune_intermediate_layers(model._call_tree)
            log_model_debug_trace(debug_path=debug_path, model=model)
        return out
    model.forward = top_wrapped_forward
@requires(backends=("torch",))
@contextmanager
def model_addition_debugger_context(
    model,
    debug_path: Optional[str] = None,
    do_prune_layers: bool = True,
    use_repr: bool = True,
):
    orig_forwards = {m: m.forward for _, m in model.named_modules()}
    orig_forwards[model] = model.forward
    _attach_debugger_logic(model, debug_path, do_prune_layers, use_repr)
    try:
        yield model
    finally:
        for module_instance, forward_method in orig_forwards.items():
            module_instance.forward = forward_method