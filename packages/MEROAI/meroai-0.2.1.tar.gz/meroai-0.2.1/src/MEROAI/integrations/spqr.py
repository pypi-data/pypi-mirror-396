"SpQR (Sparse-Quantized Representation) integration file"
from ..utils import is_accelerate_available, is_spqr_available, is_torch_available
if is_torch_available():
    import torch.nn as nn
def replace_with_spqr_linear(
    model,
    quantization_config=None,
    modules_to_not_convert=None,
    current_key_name=None,
    has_been_replaced=False,
):
    if modules_to_not_convert is None:
        modules_to_not_convert = []
    if is_accelerate_available():
        from accelerate import init_empty_weights
    if is_spqr_available():
        from spqr_quant import QuantizedLinear
    for name, module in model.named_children():
        if current_key_name is None:
            current_key_name = []
        current_key_name.append(name)
        if isinstance(module, nn.Linear):
            if ".".join(current_key_name) + ".weight" not in modules_to_not_convert:
                with init_empty_weights():
                    tensor_name = ".".join(current_key_name)
                    shapes = quantization_config.shapes
                    shapes_keys = shapes.keys()
                    shapes_valid = (
                        f"{tensor_name}.dense_weights.shape" in shapes_keys
                        and f"{tensor_name}.row_offsets.shape" in shapes_keys
                        and f"{tensor_name}.col_vals.shape" in shapes_keys
                        and f"{tensor_name}.in_perm.shape" in shapes_keys
                    )
                    if not shapes_valid:
                        raise ValueError(
                            f"The SpQR quantization config does not contain the shape "
                            f"configuration for {tensor_name}. This indicates that the "
                            f"configuration is either invalid or corrupted."
                        )
                    dense_weights_shape = shapes[f"{tensor_name}.dense_weights.shape"]
                    row_offsets_shape = shapes[f"{tensor_name}.row_offsets.shape"]
                    col_vals_shape = shapes[f"{tensor_name}.col_vals.shape"]
                    in_perm_shape = shapes[f"{tensor_name}.in_perm.shape"]
                    in_features = module.in_features
                    out_features = module.out_features
                    model._modules[name] = QuantizedLinear.create_placehodler(
                        rows=out_features,
                        cols=in_features,
                        bits=quantization_config.bits,
                        beta1=quantization_config.beta1,
                        beta2=quantization_config.beta2,
                        dense_weights_shape=dense_weights_shape,
                        row_offsets_shape=row_offsets_shape,
                        col_vals_shape=col_vals_shape,
                        in_perm_shape=in_perm_shape,
                    )
                    has_been_replaced = True
                    model._modules[name].source_cls = type(module)
                    model._modules[name].requires_grad_(False)
            else:
                pass
        if len(list(module.children())) > 0:
            _, has_been_replaced = replace_with_spqr_linear(
                module,
                quantization_config=quantization_config,
                modules_to_not_convert=modules_to_not_convert,
                current_key_name=current_key_name,
                has_been_replaced=has_been_replaced,
            )
        current_key_name.pop(-1)
    return model, has_been_replaced