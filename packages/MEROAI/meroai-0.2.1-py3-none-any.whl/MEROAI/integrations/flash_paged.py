from typing import Optional
import torch
from ..generation.continuous_batching import PagedAttentionCache
from ..utils import is_flash_attn_2_available
try:
    if is_flash_attn_2_available():
        from flash_attn import flash_attn_varlen_func
        FLASH_ATTN_VARLEN_FUNC = flash_attn_varlen_func
    else:
        raise RuntimeError(
            "Flash Attention 2 is not installed. Please refer to https://huggingface.co/docs/MEROAI/perf_infer_gpu_one#flashattention-2 to install it"
        )
except Exception as e:
    msg = repr(e)
    def FLASH_ATTN_VARLEN_FUNC(*args, **kwargs):
        raise Exception(f"flash_attn_varlen_func is not available: {msg}")
def paged_attention_forward(
    module: torch.nn.Module,
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    attention_mask: Optional[torch.Tensor] = None,
    cache: PagedAttentionCache = None,
    cu_seq_lens_q=None,
    cu_seq_lens_k=None,
    max_seqlen_q=None,
    max_seqlen_k=None,
    implementation=None,
    **kwargs,
) -> torch.Tensor:
    sliding_window = (-1, -1) if not getattr(module, "sliding_window", False) else (module.sliding_window - 1, 0)
    layer_type = "full_attention" if sliding_window == (-1, -1) else "sliding_attention"
    if cache is not None:
        k, v = cache.update(k, v, module.layer_idx, **kwargs)
    if isinstance(cu_seq_lens_k, dict):
        cu_seq_lens_k = cu_seq_lens_k[layer_type]
        max_seqlen_k = max_seqlen_k[layer_type]
    if implementation is not None and hasattr(implementation, "flash_attn_varlen_func"):
        flash_attn_varlen_func = implementation.flash_attn_varlen_func
    else:
        flash_attn_varlen_func = FLASH_ATTN_VARLEN_FUNC
    custom_kwargs = {"s_aux": kwargs.get("s_aux")} if "s_aux" in kwargs else {}
    attn_output = flash_attn_varlen_func(
        q.transpose(1, 2).squeeze(0).contiguous(),
        k.contiguous(),
        v.contiguous(),
        cu_seq_lens_q.to(torch.int32),
        cu_seq_lens_k.to(torch.int32).clone(),
        max_seqlen_q,
        max_seqlen_k,
        softmax_scale=module.scaling,
        causal=True,
        window_size=sliding_window,
        **custom_kwargs,
    )
    if isinstance(attn_output, tuple):
        attn_output = attn_output[0]
    return attn_output, None