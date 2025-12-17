import inspect
import os
from functools import partial
from typing import Optional, TypedDict
import torch
import torch.nn.functional as F
from .utils import (
    is_flash_attn_2_available,
    is_flash_attn_3_available,
    is_flash_attn_greater_or_equal_2_10,
    is_torch_npu_available,
    logging,
)
logger = logging.get_logger(__name__)
def flash_attn_supports_top_left_mask():
    if is_flash_attn_3_available():
        return False
    if is_flash_attn_2_available():
        return not is_flash_attn_greater_or_equal_2_10()
    from .integrations.npu_flash_attention import is_npu_fa2_top_left_aligned_causal_mask
    return is_npu_fa2_top_left_aligned_causal_mask()
def is_flash_attn_available():
    return is_flash_attn_3_available() or is_flash_attn_2_available() or is_torch_npu_available()
_flash_fn = None
_flash_varlen_fn = None
_pad_fn = None
_unpad_fn = None
_process_flash_kwargs_fn = None
_hf_api_to_flash_mapping = {
    "dropout": "dropout_p",
    "sliding_window": "window_size",
}
def _lazy_imports(implementation: Optional[str]):
    is_fa2 = is_flash_attn_2_available()
    is_fa3 = is_flash_attn_3_available()
    pad_input, unpad_input = _pad_input, _unpad_input
    if (implementation == "flash_attention_2" and is_fa2) or (implementation is None and is_fa2 and not is_fa3):
        from flash_attn import flash_attn_func, flash_attn_varlen_func
        from flash_attn.bert_padding import pad_input, unpad_input
    elif is_torch_npu_available():
        from .integrations.npu_flash_attention import npu_flash_attn_func as flash_attn_func
        from .integrations.npu_flash_attention import npu_flash_attn_varlen_func as flash_attn_varlen_func
    else:
        if implementation == "flash_attention_3" or (implementation is None and is_fa3):
            from flash_attn_interface import flash_attn_func, flash_attn_varlen_func
        else:
            flash_attn_func = getattr(implementation, "flash_attn_func", None)
            flash_attn_varlen_func = getattr(implementation, "flash_attn_varlen_func", None)
            if flash_attn_varlen_func is None or flash_attn_func is None:
                raise ValueError(
                    f"Could not find the currently requested flash attention implementation at `{implementation}`."
                    f"Make sure that you request a valid kernel from the hub, e.g. `kernels-community/flash-attn`."
                )
    return flash_attn_func, flash_attn_varlen_func, pad_input, unpad_input
def _lazy_define_process_function(flash_function):
    flash_parameters = inspect.signature(flash_function).parameters
    process_parameters = inspect.signature(_process_flash_attention_kwargs).parameters
    supports_mapping = {}
    for param in process_parameters:
        fa_param = _hf_api_to_flash_mapping.get(param, param)
        supports_mapping[fa_param] = fa_param in flash_parameters
    return partial(_process_flash_attention_kwargs, supports_mapping=supports_mapping)
def lazy_import_flash_attention(implementation: Optional[str], force_import: Optional[bool] = False):
    global _flash_fn, _flash_varlen_fn, _pad_fn, _unpad_fn
    if force_import or any(k is None for k in [_flash_fn, _flash_varlen_fn, _pad_fn, _unpad_fn]):
        _flash_fn, _flash_varlen_fn, _pad_fn, _unpad_fn = _lazy_imports(implementation)
    global _process_flash_kwargs_fn
    if force_import or _process_flash_kwargs_fn is None:
        _process_flash_kwargs_fn = _lazy_define_process_function(_flash_varlen_fn)
    return (_flash_fn, _flash_varlen_fn, _pad_fn, _unpad_fn), _process_flash_kwargs_fn
def _index_first_axis(tensor, indices):
    reshaped_tensor = tensor.reshape(-1, *tensor.shape[2:])
    return reshaped_tensor[indices]
def _unpad_input(hidden_states, attention_mask, unused_mask=None):
    all_masks = (attention_mask + unused_mask) if unused_mask is not None else attention_mask
    seqlens_in_batch = all_masks.sum(dim=-1, dtype=torch.int32)
    used_seqlens_in_batch = attention_mask.sum(dim=-1, dtype=torch.int32)
    indices = torch.nonzero(all_masks.flatten(), as_tuple=False).flatten()
    max_seqlen_in_batch = seqlens_in_batch.max().item()
    cu_seqlens = F.pad(torch.cumsum(seqlens_in_batch, dim=0, dtype=torch.int32), (1, 0))
    return (
        _index_first_axis(hidden_states, indices),
        indices,
        cu_seqlens,
        max_seqlen_in_batch,
        used_seqlens_in_batch,
    )
def _pad_input(hidden_states, indices, batch, seqlen):
    dim = hidden_states.shape[1:]
    output = torch.zeros((batch * seqlen), *dim, device=hidden_states.device, dtype=hidden_states.dtype)
    output[indices] = hidden_states
    return output.view(batch, seqlen, *dim)
def _get_unpad_data(attention_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, int]:
    seqlens_in_batch = attention_mask.sum(dim=-1, dtype=torch.int32)
    indices = torch.nonzero(attention_mask.flatten(), as_tuple=False).flatten()
    max_seqlen_in_batch = seqlens_in_batch.max().item()
    cu_seqlens = F.pad(torch.cumsum(seqlens_in_batch, dim=0, dtype=torch.int32), (1, 0))
    return (
        indices,
        cu_seqlens,
        max_seqlen_in_batch,
    )
def _upad_input(
    query_layer: torch.Tensor,
    key_layer: torch.Tensor,
    value_layer: torch.Tensor,
    attention_mask: torch.Tensor,
    query_length: int,
    unpad_input_func,
):
    indices_k, cu_seqlens_k, max_seqlen_in_batch_k = _get_unpad_data(attention_mask)
    if key_layer.shape[1] > (seq_len := attention_mask.shape[-1]):
        key_layer, value_layer = key_layer[:, :seq_len, :, :], value_layer[:, :seq_len, :, :]
    batch_size, kv_seq_len, num_key_value_heads, head_dim = key_layer.shape
    key_layer = _index_first_axis(key_layer, indices_k)
    value_layer = _index_first_axis(value_layer, indices_k)
    if query_length == kv_seq_len:
        query_layer = _index_first_axis(query_layer, indices_k)
        cu_seqlens_q = cu_seqlens_k
        max_seqlen_in_batch_q = max_seqlen_in_batch_k
        indices_q = indices_k
    elif query_length == 1:
        max_seqlen_in_batch_q = 1
        cu_seqlens_q = torch.arange(
            batch_size + 1, dtype=torch.int32, device=query_layer.device
        )
        indices_q = cu_seqlens_q[:-1]
        query_layer = query_layer.squeeze(1)
    else:
        attention_mask = attention_mask[:, -query_length:]
        query_layer, indices_q, cu_seqlens_q, max_seqlen_in_batch_q, *_ = unpad_input_func(query_layer, attention_mask)
    return (
        query_layer,
        key_layer,
        value_layer,
        indices_q,
        (cu_seqlens_q, cu_seqlens_k),
        (max_seqlen_in_batch_q, max_seqlen_in_batch_k),
    )
def prepare_fa_kwargs_from_position_ids(position_ids):
    tensor_kwargs = {"dtype": torch.int32, "device": position_ids.device}
    position_ids = position_ids.view(-1)
    indices_q = (position_ids == 0).nonzero().view(-1)
    cu_seq_lens_q = torch.cat(
        (
            indices_q.to(**tensor_kwargs),
            torch.tensor(position_ids.size(), **tensor_kwargs),
        )
    )
    cu_seq_lens_k = cu_seq_lens_q
    max_length_q = cu_seq_lens_q.diff().max()
    max_length_q = max_length_q.item()
    max_length_k = max_length_q
    return (cu_seq_lens_q, cu_seq_lens_k), (max_length_q, max_length_k)
def _prepare_from_posids(query, key, value, position_ids):
    query = query.contiguous().view(-1, query.size(-2), query.size(-1))
    key = key.contiguous().view(-1, key.size(-2), key.size(-1))
    value = value.contiguous().view(-1, value.size(-2), value.size(-1))
    (cu_seq_lens_q, cu_seq_lens_k), (max_length_q, max_length_k) = prepare_fa_kwargs_from_position_ids(position_ids)
    return (query, key, value, (cu_seq_lens_q, cu_seq_lens_k), (max_length_q, max_length_k))
def _is_packed_sequence(position_ids, batch_size):
    if position_ids is None:
        return False
    increasing_position_sequences = (
        torch.arange(position_ids.shape[1], device=position_ids.device) + position_ids.min()
    )
    return batch_size == 1 and (increasing_position_sequences - position_ids).abs().sum().bool()
def fa_peft_integration_check(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    target_dtype: Optional[torch.dtype] = None,
):
    if target_dtype and q.dtype == torch.float32:
        logger.warning_once(f"Casting fp32 inputs back to {target_dtype} for flash-attn compatibility.")
        q, k, v = q.to(target_dtype), k.to(target_dtype), v.to(target_dtype)
    return q, k, v
class FlashAttentionKwargs(TypedDict, total=False):
    cu_seq_lens_q: Optional[torch.LongTensor]
    cu_seq_lens_k: Optional[torch.LongTensor]
    max_length_q: Optional[int]
    max_length_k: Optional[int]
def _process_flash_attention_kwargs(
    query_length: int,
    key_length: int,
    is_causal: bool,
    dropout: float = 0.0,
    softmax_scale: Optional[float] = None,
    sliding_window: Optional[int] = None,
    use_top_left_mask: bool = False,
    softcap: Optional[float] = None,
    deterministic: Optional[bool] = None,
    s_aux: Optional[torch.Tensor] = None,
    supports_mapping: Optional[dict[str, bool]] = None,
    **kwargs,
):
    flash_kwargs = {
        "causal": is_causal and not (use_top_left_mask and query_length == 1),
        "softmax_scale": softmax_scale,
    }
    if supports_mapping["dropout_p"]:
        flash_kwargs["dropout_p"] = dropout
    if supports_mapping["window_size"] and sliding_window is not None and key_length > sliding_window:
        flash_kwargs["window_size"] = (sliding_window - 1, sliding_window - 1)
    if supports_mapping["deterministic"]:
        flash_kwargs["deterministic"] = (
            deterministic if deterministic is not None else os.getenv("FLASH_ATTENTION_DETERMINISTIC", "0") == "1"
        )
    if supports_mapping["softcap"] and softcap is not None:
        flash_kwargs["softcap"] = softcap
    if supports_mapping["s_aux"] and s_aux is not None:
        flash_kwargs["s_aux"] = s_aux
    return flash_kwargs
def _flash_attention_forward(
    query_states: torch.Tensor,
    key_states: torch.Tensor,
    value_states: torch.Tensor,
    attention_mask: Optional[torch.Tensor],
    query_length: int,
    is_causal: bool,
    dropout: float = 0.0,
    position_ids: Optional[torch.Tensor] = None,
    softmax_scale: Optional[float] = None,
    sliding_window: Optional[int] = None,
    use_top_left_mask: bool = False,
    softcap: Optional[float] = None,
    deterministic: Optional[bool] = None,
    cu_seq_lens_q: Optional[torch.LongTensor] = None,
    cu_seq_lens_k: Optional[torch.LongTensor] = None,
    max_length_q: Optional[int] = None,
    max_length_k: Optional[int] = None,
    target_dtype: Optional[torch.dtype] = None,
    implementation: Optional[str] = None,
    **kwargs,
):
    (flash_fn, flash_varlen_fn, pad_fn, unpad_fn), process_flash_kwargs_fn = lazy_import_flash_attention(
        implementation
    )
    query_states, key_states, value_states = fa_peft_integration_check(
        query_states, key_states, value_states, target_dtype
    )
    flash_kwargs = process_flash_kwargs_fn(
        query_length=query_length,
        key_length=key_states.size(1),
        is_causal=is_causal,
        dropout=dropout,
        softmax_scale=softmax_scale,
        sliding_window=sliding_window,
        use_top_left_mask=use_top_left_mask,
        softcap=softcap,
        deterministic=deterministic,
        **kwargs,
    )
    is_fa_with_position_ids = _is_packed_sequence(position_ids, batch_size=query_states.size(0))
    is_fa_with_varlen_kwargs = all(
        kwarg is not None for kwarg in (cu_seq_lens_q, cu_seq_lens_k, max_length_q, max_length_k)
    )
    if attention_mask is not None:
        q, k, v, indices_q, (cu_seq_lens_q, cu_seq_lens_k), (max_length_q, max_length_k) = _upad_input(
            query_states, key_states, value_states, attention_mask, query_length, unpad_fn
        )
        if "mps" in str(q.device):
            cu_seq_lens_k = cu_seq_lens_k.clone()
        out_unpad = flash_varlen_fn(
            q,
            k,
            v,
            cu_seqlens_q=cu_seq_lens_q,
            cu_seqlens_k=cu_seq_lens_k,
            max_seqlen_q=max_length_q,
            max_seqlen_k=max_length_k,
            **flash_kwargs,
        )
        if isinstance(out_unpad, tuple):
            out_unpad = out_unpad[0]
        out = pad_fn(out_unpad, indices_q, query_states.size(0), query_length)
    elif is_fa_with_varlen_kwargs or is_fa_with_position_ids:
        if cu_seq_lens_q is None or cu_seq_lens_k is None:
            q, k, v, (cu_seq_lens_q, cu_seq_lens_k), (max_length_q, max_length_k) = _prepare_from_posids(
                query_states, key_states, value_states, position_ids
            )
        else:
            q = query_states.reshape(-1, query_states.size(-2), query_states.size(-1))
            k = key_states.reshape(-1, key_states.size(-2), key_states.size(-1))
            v = value_states.reshape(-1, value_states.size(-2), value_states.size(-1))
        if "mps" in str(q.device):
            cu_seq_lens_k = cu_seq_lens_k.clone()
        out = flash_varlen_fn(
            q,
            k,
            v,
            cu_seqlens_q=cu_seq_lens_q,
            cu_seqlens_k=cu_seq_lens_k,
            max_seqlen_q=max_length_q,
            max_seqlen_k=max_length_k,
            **flash_kwargs,
        )
        if isinstance(out, tuple):
            out = out[0]
        out = out.view(query_states.size(0), -1, out.size(-2), out.size(-1))
    else:
        out = flash_fn(query_states, key_states, value_states, **flash_kwargs)
        if isinstance(out, tuple):
            out = out[0]
    return out