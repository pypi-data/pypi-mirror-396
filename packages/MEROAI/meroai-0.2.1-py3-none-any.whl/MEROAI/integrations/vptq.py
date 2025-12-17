"VPTQ (Vector Post-Training Quantization) integration file"
import torch.nn as nn
from accelerate import init_empty_weights
from vptq import VQuantLinear
def replace_with_vptq_linear(
    model,
    quantization_config=None,
    modules_to_not_convert=None,
    current_key_name=None,
    has_been_replaced=False,
):
    modules_to_not_convert = modules_to_not_convert if modules_to_not_convert else ["lm_head"]
    for name, module in model.named_children():
        if current_key_name is None:
            current_key_name = []
        current_key_name.append(name)
        layer_name = ".".join(current_key_name)
        shared_layer_config = quantization_config.shared_layer_config
        config_for_layers = quantization_config.config_for_layers
        if (
            isinstance(module, nn.Linear)
            and layer_name not in modules_to_not_convert
            and ((layer_name in config_for_layers) or (current_key_name[-1] in shared_layer_config))
        ):
            layer_params = config_for_layers.get(layer_name, None) or shared_layer_config.get(
                current_key_name[-1], None
            )
            with init_empty_weights():
                in_features = module.in_features
                out_features = module.out_features
                model._modules[name] = VQuantLinear(
                    in_features,
                    out_features,
                    vector_lens=layer_params["vector_lens"],
                    num_centroids=layer_params["num_centroids"],
                    num_res_centroids=layer_params["num_res_centroids"],
                    group_num=layer_params["group_num"],
                    group_size=layer_params["group_size"],
                    outlier_size=layer_params["outlier_size"],
                    indices_as_float=layer_params["indices_as_float"],
                    enable_norm=layer_params["enable_norm"],
                    enable_perm=layer_params["enable_perm"],
                    is_indice_packed=True,
                    enable_proxy_error=False,
                    bias=module.bias is not None,
                )
                has_been_replaced = True
                model._modules[name].requires_grad_(False)
        if len(list(module.children())) > 0:
            _, has_been_replaced = replace_with_vptq_linear(
                module,
                quantization_config=quantization_config,
                modules_to_not_convert=modules_to_not_convert,
                current_key_name=current_key_name,
                has_been_replaced=has_been_replaced,
            )
        current_key_name.pop(-1)
    return model, has_been_replaced