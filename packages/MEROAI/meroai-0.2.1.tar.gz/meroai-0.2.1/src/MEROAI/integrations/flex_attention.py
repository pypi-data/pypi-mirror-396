from typing import Optional, Union
import torch
from packaging import version
from ..utils import is_torch_flex_attn_available, logging
from ..utils.import_utils import _torch_version, is_torch_less_or_equal, is_torchdynamo_compiling
if is_torch_flex_attn_available():
    from torch.nn.attention.flex_attention import _DEFAULT_SPARSE_BLOCK_SIZE as flex_default_block_size
    from torch.nn.attention.flex_attention import BlockMask, create_block_mask, flex_attention
logger = logging.get_logger(__name__)
class WrappedFlexAttention:
    _instance = None
    _is_flex_compiled = False
    _compiled_flex_attention = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    @torch.compiler.disable(recursive=False)
    def __init__(self, training):
        if not self._is_flex_compiled or training != self.training:
            self.training = training
            if is_torch_less_or_equal("2.5.1"):
                self._compiled_flex_attention = torch.compile(flex_attention, dynamic=False)
            elif version.parse(_torch_version).base_version == "2.6.0" and training:
                self._compiled_flex_attention = torch.compile(
                    flex_attention, dynamic=False, mode="max-autotune-no-cudagraphs"
                )
            else:
                self._compiled_flex_attention = torch.compile(flex_attention)
            self._is_flex_compiled = True
    def __call__(self):
        return self._compiled_flex_attention
def compile_friendly_flex_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    training=False,
    **kwargs,
) -> Union[torch.Tensor, tuple[torch.Tensor, torch.Tensor]]:
    flex_attention_compiled = WrappedFlexAttention(training)() if not is_torchdynamo_compiling() else flex_attention
    return flex_attention_compiled(
        query,
        key,
        value,
        **kwargs,
    )
Offset = Union[torch.Tensor, int]
def make_flex_block_causal_mask(
    attention_mask_2d: torch.Tensor,
    attention_chunk_size: Optional[int] = None,
    query_length=None,
    key_length=None,
    offsets: Optional[tuple[Offset, Offset]] = None,
    is_causal: Optional[bool] = True,
) -> "BlockMask":
    batch_size, total_seq_len = attention_mask_2d.shape
    if not key_length:
        key_length = total_seq_len
    if not query_length:
        query_length = total_seq_len
    pad_len = ((key_length // flex_default_block_size) + 1) * flex_default_block_size
    attention_mask_2d = torch.nn.functional.pad(attention_mask_2d, value=0, pad=(0, pad_len - key_length))
    device = attention_mask_2d.device
    document_ids = attention_mask_2d.clone()
    if attention_chunk_size is not None:
        chunk_idxs = (document_ids.clone().fill_(1).cumsum(-1) - 1) // (attention_chunk_size)
    def causal_mask_mod(batch_idx, head_idx, q_idx, kv_idx):
        causal_mask = q_idx >= kv_idx
        document_mask = document_ids[batch_idx, q_idx] == document_ids[batch_idx, kv_idx]
        padding_mask = attention_mask_2d[batch_idx, q_idx] > 0
        final_mask = causal_mask & padding_mask & document_mask
        return final_mask
    def chunk_causal_mask_mod(batch_idx, head_idx, q_idx, kv_idx):
        chunk_mask = chunk_idxs[batch_idx, q_idx] == chunk_idxs[batch_idx, kv_idx]
        causal_doc_mask = causal_mask_mod(batch_idx, head_idx, q_idx, kv_idx)
        return chunk_mask & causal_doc_mask
    def default_mask_mod(batch_idx, head_idx, q_idx, kv_idx):
        document_mask = document_ids[batch_idx, q_idx] == document_ids[batch_idx, kv_idx]
        padding_mask = attention_mask_2d[batch_idx, kv_idx] > 0
        final_mask = padding_mask & document_mask
        return final_mask
    if not is_causal:
        mask_mod_maybe_combined = default_mask_mod
    else:
        mask_mod_maybe_combined = causal_mask_mod if attention_chunk_size is None else chunk_causal_mask_mod
    if offsets is not None:
        q_offset = offsets[0].to(device)
        kv_offset = offsets[1].to(device)
        def mask_mod(batch_idx, head_idx, q_idx, kv_idx):
            offset_q = q_idx + q_offset
            offset_kv = kv_idx + kv_offset
            return mask_mod_maybe_combined(batch_idx, head_idx, offset_q, offset_kv)
    else:
        mask_mod = mask_mod_maybe_combined
    return create_block_mask(
        mask_mod=mask_mod,
        B=batch_size,
        H=None,
        Q_LEN=query_length,
        KV_LEN=key_length,
        device=device,
        _compile=not is_torch_less_or_equal("2.5.1"),
    )
def repeat_kv(hidden_states: torch.Tensor, n_rep: int) -> torch.Tensor:
    batch, num_key_value_heads, slen, head_dim = hidden_states.shape
    if n_rep == 1:
        return hidden_states
    hidden_states = hidden_states[:, :, None, :, :].expand(batch, num_key_value_heads, n_rep, slen, head_dim)
    return hidden_states.reshape(batch, num_key_value_heads * n_rep, slen, head_dim)
def flex_attention_forward(
    module: torch.nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Union[torch.Tensor, "BlockMask"],
    scaling: Optional[float] = None,
    softcap: Optional[float] = None,
    head_mask: Optional[torch.Tensor] = None,
    s_aux: Optional[torch.Tensor] = None,
    **kwargs,
) -> tuple[torch.Tensor, Optional[torch.Tensor]]:
    if head_mask is not None:
        logger.warning_once(
            "`flex_attention` does not support `head_mask`. Please set your attention to `eager` if you want this feature."
        )
    if kwargs.get("dropout", 0.0) > 0:
        raise ValueError(
            "`flex_attention` does not support `dropout`. Please use it with inference"
            " only (`model.eval()`) or turn off the attention dropout in the respective config."
        )
    block_mask = None
    score_mask = None
    if isinstance(attention_mask, BlockMask):
        block_mask = attention_mask
    else:
        score_mask = attention_mask
    if score_mask is not None:
        score_mask = score_mask[:, :, :, : key.shape[-2]]
    def score_mod(score, batch_idx, head_idx, q_idx, kv_idx):
        if softcap is not None:
            score = softcap * torch.tanh(score / softcap)
        if score_mask is not None:
            score = score + score_mask[batch_idx][0][q_idx][kv_idx]
        if head_mask is not None:
            score = score + head_mask[batch_idx][head_idx][0][0]
        return score
    enable_gqa = True
    num_local_query_heads = query.shape[1]
    if (num_local_query_heads & (num_local_query_heads - 1)) != 0:
        key = repeat_kv(key, query.shape[1] // key.shape[1])
        value = repeat_kv(value, query.shape[1] // value.shape[1])
        enable_gqa = False
    kernel_options = kwargs.get("kernel_options")
    return_lse = query.device.type != "cpu"
    if not return_lse and s_aux is not None:
        raise ValueError(
            "Attention sinks cannot be run on CPU with flex attention. Please switch to a different device, e.g. CUDA"
        )
    flex_attention_output = compile_friendly_flex_attention(
        query,
        key,
        value,
        score_mod=score_mod,
        block_mask=block_mask,
        enable_gqa=enable_gqa,
        scale=scaling,
        kernel_options=kernel_options,
        return_lse=return_lse,
        training=module.training,
    )
    if return_lse:
        attention_output, lse = flex_attention_output
        lse = lse.to(value.dtype)
        if s_aux is not None:
            batch_size, num_heads, seq_len_q, _ = attention_output.shape
            sinks = s_aux.view(1, -1, 1, 1).expand(batch_size, num_heads, seq_len_q, 1)
            lse_expanded = lse.unsqueeze(-1)
            combined_lse = torch.logsumexp(torch.cat([lse_expanded, sinks], dim=-1), dim=-1, keepdim=True)
            renorm_factor = torch.exp(lse_expanded - combined_lse)
            attention_output = attention_output * renorm_factor
    else:
        attention_output = flex_attention_output
        lse = None
    attention_output = attention_output.transpose(1, 2).contiguous()
    return attention_output, lse