from ..utils import is_accelerate_available, is_torch_available, logging
if is_accelerate_available():
    from accelerate import init_empty_weights
if is_torch_available():
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
logger = logging.get_logger(__name__)
VALUES_PER_ITEM = 4
def pack_weights(quantized_weights: torch.Tensor) -> torch.Tensor:
    original_shape = quantized_weights.shape
    row_dim = (original_shape[0] + VALUES_PER_ITEM - 1) // VALUES_PER_ITEM
    if len(original_shape) == 1:
        packed_tensor_shape = (row_dim,)
    else:
        packed_tensor_shape = (row_dim, *original_shape[1:])
    quantized_weights += 1
    packed = torch.zeros(packed_tensor_shape, device=quantized_weights.device, dtype=torch.uint8)
    unpacked = quantized_weights.to(torch.uint8)
    it = min(VALUES_PER_ITEM, (original_shape[0] // row_dim) + 1)
    for i in range(it):
        start = i * row_dim
        end = min(start + row_dim, original_shape[0])
        packed[: (end - start)] |= unpacked[start:end] << 2 * i
    return packed
@torch.compile
def unpack_weights(packed: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
    packed_shape = packed.shape
    if len(packed_shape) == 1:
        original_row_dim = packed_shape[0] * VALUES_PER_ITEM
        unpacked_shape = (original_row_dim,)
    else:
        original_row_dim = packed_shape[0] * VALUES_PER_ITEM
        unpacked_shape = (original_row_dim, *packed_shape[1:])
    unpacked = torch.zeros(unpacked_shape, device=packed.device, dtype=torch.uint8)
    for i in range(VALUES_PER_ITEM):
        start = i * packed_shape[0]
        end = start + packed_shape[0]
        mask = 3 << (2 * i)
        unpacked[start:end] = (packed & mask) >> (2 * i)
    return unpacked.to(dtype) - 1
class BitLinear(nn.Module):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool,
        device=None,
        dtype=None,
        use_rms_norm: bool = False,
        rms_norm_eps: float = 1e-6,
    ):
        super().__init__()
        self.dtype = dtype
        self.in_features = in_features
        self.out_features = out_features
        self.register_buffer(
            "weight",
            torch.zeros(
                (out_features // VALUES_PER_ITEM, in_features),
                dtype=torch.uint8,
                device=device,
            ),
        )
        self.register_buffer(
            "weight_scale",
            torch.ones(
                (1),
                dtype=dtype,
                device=device,
            ),
        )
        if bias:
            self.register_buffer("bias", torch.zeros((out_features), dtype=dtype, device=device))
        else:
            self.bias = None
        self.rms_norm = None
        if use_rms_norm:
            from ..models.llama.modeling_llama import LlamaRMSNorm
            self.rms_norm = LlamaRMSNorm(in_features, eps=rms_norm_eps)
    @torch.compile
    def activation_quant(self, input, num_bits=8):
        Qn = -(2 ** (num_bits - 1))
        Qp = 2 ** (num_bits - 1) - 1
        scale = Qp / input.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-5)
        result = (input * scale).round().clamp(Qn, Qp)
        return result.to(torch.int8), scale
    @torch.compile
    def post_quant_process(self, input, input_scale, weight_scale):
        out = input / (input_scale * weight_scale)
        return out
    def forward(self, input):
        if self.rms_norm is not None:
            input = self.rms_norm(input)
        w = self.weight
        w_quant = unpack_weights(w, dtype=self.dtype)
        input_quant, input_scale = self.activation_quant(input)
        y = F.linear(input_quant.to(self.dtype), w_quant)
        y = self.post_quant_process(y, self.weight_scale, input_scale)
        if self.bias is not None:
            y += self.bias.view(1, -1).expand_as(y)
        return y
class WeightQuant(torch.autograd.Function):
    @staticmethod
    @torch.compile
    def forward(ctx, weight):
        dtype = weight.dtype
        weight = weight.float()
        scale = 1.0 / weight.abs().mean().clamp_(min=1e-5)
        weight = (weight * scale).round().clamp(-1, 1) / scale
        return weight.to(dtype)
    @staticmethod
    def backward(ctx, grad_output):
        grad_input = grad_output.clone()
        return grad_input
class ActQuant(torch.autograd.Function):
    @staticmethod
    @torch.compile
    def forward(ctx, activation):
        dtype = activation.dtype
        activation = activation.float()
        scale = 127 / activation.abs().max(dim=-1, keepdim=True).values.clamp_(min=1e-5)
        activation = (activation * scale).round().clamp(-128, 127) / scale
        return activation.to(dtype)
    @staticmethod
    def backward(ctx, grad_output):
        grad_input = grad_output.clone()
        return grad_input
class AutoBitLinear(nn.Linear):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        device=None,
        dtype=None,
        online_quant: bool = False,
        use_rms_norm: bool = False,
        rms_norm_eps: float = 1e-6,
    ):
        super().__init__(in_features, out_features, bias)
        self.online_quant = online_quant
        self.rms_norm = None
        if use_rms_norm:
            from ..models.llama.modeling_llama import LlamaRMSNorm
            self.rms_norm = LlamaRMSNorm(in_features, eps=rms_norm_eps)
        if not online_quant:
            self.register_buffer(
                "weight_scale",
                torch.ones(
                    (1),
                    dtype=dtype,
                    device=device,
                ),
            )
            self._register_load_state_dict_pre_hook(self.load_hook)
    def load_hook(
        self,
        state_dict,
        prefix,
        *args,
        **kwargs,
    ):
        if (prefix + "weight") in state_dict and state_dict[prefix + "weight"].dtype != self.weight.dtype:
            state_dict[prefix + "weight"] = unpack_weights(state_dict[prefix + "weight"], dtype=self.weight.dtype)
        return state_dict
    def forward(self, input):
        if self.rms_norm is not None:
            input = self.rms_norm(input)
        if self.online_quant:
            weight = WeightQuant.apply(self.weight)
        else:
            weight = self.weight
        input = ActQuant.apply(input)
        output = F.linear(input, weight, self.bias)
        if not self.online_quant:
            output = output * self.weight_scale
        return output
def _replace_with_bitnet_linear(
    model,
    modules_to_not_convert=None,
    current_key_name=None,
    quantization_config=None,
    has_been_replaced=False,
    pre_quantized=False,
):
    if current_key_name is None:
        current_key_name = []
    for name, module in model.named_children():
        if current_key_name is None:
            current_key_name = []
        current_key_name.append(name)
        if not any(key in ".".join(current_key_name) for key in modules_to_not_convert):
            with init_empty_weights():
                if isinstance(module, nn.Linear) and name not in modules_to_not_convert:
                    in_features = module.in_features
                    out_features = module.out_features
                    if quantization_config and quantization_config.linear_class == "autobitlinear":
                        model._modules[name] = AutoBitLinear(
                            in_features=in_features,
                            out_features=out_features,
                            bias=module.bias is not None,
                            device=module.weight.device,
                            dtype=module.weight.dtype,
                            online_quant=(quantization_config.quantization_mode == "online"),
                            use_rms_norm=quantization_config.use_rms_norm,
                            rms_norm_eps=quantization_config.rms_norm_eps,
                        )
                        if quantization_config.quantization_mode == "offline":
                            model._modules[name].requires_grad_(False)
                    else:
                        model._modules[name] = BitLinear(
                            in_features=in_features,
                            out_features=out_features,
                            bias=module.bias is not None,
                            device=module.weight.device,
                            dtype=module.weight.dtype,
                            use_rms_norm=quantization_config.use_rms_norm if quantization_config else False,
                            rms_norm_eps=quantization_config.rms_norm_eps if quantization_config else 1e-6,
                        )
                        model._modules[name].requires_grad_(False)
                    has_been_replaced = True
        if len(list(module.children())) > 0:
            _, has_been_replaced = _replace_with_bitnet_linear(
                module,
                modules_to_not_convert=modules_to_not_convert,
                current_key_name=current_key_name,
                quantization_config=quantization_config,
                has_been_replaced=has_been_replaced,
            )
        current_key_name.pop(-1)
    return model, has_been_replaced
def replace_with_bitnet_linear(
    model,
    modules_to_not_convert=None,
    current_key_name=None,
    quantization_config=None,
    pre_quantized=False,
):
    modules_to_not_convert = ["lm_head"] if modules_to_not_convert is None else modules_to_not_convert
    if quantization_config and quantization_config.modules_to_not_convert is not None:
        modules_to_not_convert.extend(quantization_config.modules_to_not_convert)
    modules_to_not_convert = list(set(modules_to_not_convert))
    model, has_been_replaced = _replace_with_bitnet_linear(
        model,
        modules_to_not_convert,
        current_key_name,
        quantization_config,
        pre_quantized=pre_quantized,
    )
    if not has_been_replaced:
        logger.warning(
            "You are loading your model using bitnet but no linear modules were found in your model."
            " Please double check your model architecture, or submit an issue on github if you think this is"
            " a bug."
        )
    return model