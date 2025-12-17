import math
from typing import Callable, Optional, Union
import torch
import torch.nn.functional as F
from torch import nn
from ...activations import ACT2FN
from ...cache_utils import Cache
from ...configuration_utils import PretrainedConfig
from ...integrations.flex_attention import compile_friendly_flex_attention
from ...modeling_layers import GradientCheckpointingLayer
from ...modeling_outputs import MoeCausalLMOutputWithPast, MoeModelOutputWithPast
from ...modeling_rope_utils import rope_config_validation
from ...modeling_utils import AttentionInterface, PreTrainedModel
from ...processing_utils import Unpack
from ...utils import MEROAIKwargs, is_torch_flex_attn_available
from ...utils.deprecation import deprecate_kwarg
from ...utils.generic import OutputRecorder
from ..llama.modeling_llama import (
    LlamaForSequenceClassification,
    LlamaMLP,
    LlamaPreTrainedModel,
    LlamaRMSNorm,
    LlamaRotaryEmbedding,
    apply_rotary_pos_emb,
    eager_attention_forward,
    repeat_kv,
)
from ..mixtral.modeling_mixtral import MixtralForCausalLM, MixtralModel
if is_torch_flex_attn_available():
    from torch.nn.attention.flex_attention import BlockMask
class DogeConfig(PretrainedConfig):
    model_type = "doge"
    keys_to_ignore_at_inference = ["past_key_values"]
    base_model_tp_plan = {
        "layers.*.self_attn.q_proj": "colwise",
        "layers.*.self_attn.k_proj": "colwise",
        "layers.*.self_attn.v_proj": "colwise",
        "layers.*.self_attn.dt_proj": "rowwise",
        "layers.*.self_attn.o_proj": "rowwise",
        "layers.*.input_layernorm.weight": "sequence_parallel",
        "layers.*.input_residual.weight": "sequence_parallel",
        "layers.*.post_attention_layernorm.weight": "sequence_parallel",
        "layers.*.post_attention_residual.weight": "sequence_parallel",
        "norm.weight": "sequence_parallel",
        "layers.*.mlp.gate_proj": "colwise",
        "layers.*.mlp.up_proj": "colwise",
        "layers.*.mlp.down_proj": "rowwise",
        "layers.*.mlp.router_gate": "colwise_rep",
        "layers.*.mlp.down_embed": "rowwise_rep",
        "layers.*.mlp.up_embed": "rowwise_rep",
    }
    base_model_pp_plan = {
        "embed_tokens": (["input_ids"], ["inputs_embeds"]),
        "layers": (["hidden_states", "attention_mask"], ["hidden_states"]),
        "norm": (["hidden_states"], ["hidden_states"]),
    }
    def __init__(
        self,
        vocab_size=32768,
        hidden_size=1024,
        intermediate_size=2048,
        num_hidden_layers=32,
        hidden_dropout=0.0,
        hidden_act="silu",
        initializer_range=0.02,
        rms_norm_eps=1e-06,
        use_cache=True,
        tie_word_embeddings=False,
        max_position_embeddings=2048,
        rope_theta=10000.0,
        rope_scaling=None,
        num_attention_heads=8,
        num_key_value_heads=None,
        attention_bias=False,
        attention_dropout=0.0,
        mlp_bias=False,
        sliding_window=None,
        keep_window_size=2048,
        is_moe=False,
        num_experts=16384,
        num_experts_per_tok=64,
        norm_topk_prob=False,
        output_router_logits=False,
        router_aux_loss_coef=0.001,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.hidden_dropout = hidden_dropout
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.attention_bias = attention_bias
        self.attention_dropout = attention_dropout
        self.mlp_bias = mlp_bias
        self.sliding_window = sliding_window
        self.keep_window_size = keep_window_size
        self.is_moe = is_moe
        self.num_experts = num_experts
        self.num_experts_per_tok = num_experts_per_tok
        self.norm_topk_prob = norm_topk_prob
        self.output_router_logits = output_router_logits
        self.router_aux_loss_coef = router_aux_loss_coef
        if self.rope_scaling is not None and "type" in self.rope_scaling:
            self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        rope_config_validation(self)
        if num_key_value_heads is None:
            self.num_key_value_heads = num_attention_heads
        super().__init__(
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )
class DogeRMSNorm(LlamaRMSNorm):
    pass
class DogeRotaryEmbedding(LlamaRotaryEmbedding):
    pass
def flex_attention_forward(
    module: nn.Module,
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attention_mask: Union[torch.Tensor, "BlockMask"],
    scaling: Optional[float] = None,
    softcap: Optional[float] = None,
    head_mask: Optional[torch.Tensor] = None,
    **kwargs,
) -> tuple[torch.Tensor, torch.Tensor]:
    block_mask = None
    causal_mask = None
    if isinstance(attention_mask, BlockMask):
        block_mask = attention_mask
    else:
        causal_mask = attention_mask
    if causal_mask is not None:
        causal_mask = causal_mask[:, :, :, : key.shape[-2]]
    def score_mod(score, batch_idx, head_idx, q_idx, kv_idx):
        if softcap is not None:
            score = softcap * torch.tanh(score / softcap)
        if causal_mask is not None:
            score = score + causal_mask[batch_idx][head_idx][q_idx][kv_idx]
        if head_mask is not None:
            score = score + head_mask[batch_idx][head_idx][0][0]
        return score
    attn_output, attention_weights = compile_friendly_flex_attention(
        query,
        key,
        value,
        score_mod=score_mod,
        block_mask=block_mask,
        enable_gqa=True,
        scale=scaling,
        return_lse=True,
    )
    attention_weights = attention_weights.to(value.dtype)
    attn_output = attn_output.transpose(1, 2).contiguous()
    return attn_output, attention_weights
ALL_ATTENTION_FUNCTIONS = AttentionInterface()
ALL_ATTENTION_FUNCTIONS["doge_flex_attention"] = flex_attention_forward
class DogeAttention(nn.Module):
    def __init__(self, config: DogeConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx
        self.head_dim = getattr(config, "head_dim", config.hidden_size // config.num_attention_heads)
        self.num_key_value_groups = config.num_attention_heads // config.num_key_value_heads
        self.scaling = self.head_dim**-0.5
        self.attention_dropout = config.attention_dropout
        self.keep_window_size = config.keep_window_size
        self.q_proj = nn.Linear(
            config.hidden_size, config.num_attention_heads * self.head_dim, bias=config.attention_bias
        )
        self.k_proj = nn.Linear(
            config.hidden_size, config.num_key_value_heads * self.head_dim, bias=config.attention_bias
        )
        self.v_proj = nn.Linear(
            config.hidden_size, config.num_key_value_heads * self.head_dim, bias=config.attention_bias
        )
        self.A = nn.Parameter(torch.zeros(config.num_key_value_heads))
        self.dt_proj = nn.Linear(
            config.num_key_value_heads * self.head_dim, config.num_key_value_heads, bias=config.attention_bias
        )
        self.o_proj = nn.Linear(
            config.num_attention_heads * self.head_dim, config.hidden_size, bias=config.attention_bias
        )
        self.q_norm = DogeRMSNorm(self.head_dim, eps=config.rms_norm_eps)
        self.k_norm = DogeRMSNorm(self.head_dim, eps=config.rms_norm_eps)
    @deprecate_kwarg("past_key_value", new_name="past_key_values", version="4.58")
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        attention_mask: Optional[torch.Tensor] = None,
        past_key_values: Optional[Cache] = None,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs,
    ) -> tuple[torch.Tensor, Optional[torch.Tensor], Optional[tuple[torch.Tensor]]]:
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self.head_dim)
        query_states = self.q_norm(self.q_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        key_states = self.k_norm(self.k_proj(hidden_states).view(hidden_shape)).transpose(1, 2)
        value_states = self.v_proj(hidden_states).view(hidden_shape).transpose(1, 2)
        cos, sin = position_embeddings
        query_states, key_states = apply_rotary_pos_emb(query_states, key_states, cos, sin)
        if past_key_values is not None:
            cache_kwargs = {"sin": sin, "cos": cos, "cache_position": cache_position}
            key_states, value_states = past_key_values.update(key_states, value_states, self.layer_idx, cache_kwargs)
        dt_states = self.dt_proj(
            value_states.transpose(1, 2).reshape(value_states.shape[0], value_states.shape[-2], -1)
        )
        dt_states = torch.exp(self.A * F.softplus(dt_states)).transpose(-1, -2)
        attn_mask = self.prepare_dynamic_mask(
            hidden_states=hidden_states,
            dt_states=dt_states,
            keep_window_size=self.keep_window_size,
            attention_mask=attention_mask,
        )
        attn_mask = repeat_kv(attn_mask, self.num_key_value_groups)
        attention_interface: Callable = eager_attention_forward
        if self.config._attn_implementation != "eager":
            attention_interface = ALL_ATTENTION_FUNCTIONS[self.config._attn_implementation]
        attn_output, attn_weights = attention_interface(
            self,
            query_states,
            key_states,
            value_states,
            attention_mask=attn_mask,
            dropout=0.0 if not self.training else self.attention_dropout,
            scaling=self.scaling,
            **kwargs,
        )
        attn_output = attn_output.reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)
        return attn_output, attn_weights
    def prepare_dynamic_mask(
        self,
        hidden_states: torch.Tensor,
        dt_states: torch.Tensor,
        keep_window_size: int = 2048,
        attention_mask: Optional[torch.Tensor] = None,
    ):
        min_dtype = torch.finfo(hidden_states.dtype).min
        dtype = hidden_states.dtype
        attn_mask = dt_states[:, :, None, :].expand(
            -1, -1, hidden_states.shape[1], -1
        )
        if attention_mask is not None and not isinstance(attention_mask, BlockMask):
            if attention_mask.dtype == torch.bool:
                dtype = hidden_states.dtype
                attention_mask = torch.where(
                    attention_mask, torch.tensor(0.0, device=attention_mask.device, dtype=dtype), min_dtype
                )
            attn_mask = attn_mask.masked_fill(attention_mask[:, :, :, : attn_mask.shape[-1]] != 0, min_dtype)
        if attn_mask.shape[-1] > keep_window_size:
            active_mask = torch.zeros_like(attn_mask, dtype=dtype, device=attn_mask.device)
            topk_indices = torch.topk(attn_mask, keep_window_size, dim=-1, largest=True, sorted=False).indices
            active_mask = active_mask.scatter(-1, topk_indices, 1.0)
            attn_mask = attn_mask.masked_fill(active_mask == 0.0, min_dtype)
        return attn_mask
class DogeMLP(LlamaMLP):
    pass
class DogeCDMoE(nn.Module):
    def __init__(self, config: DogeConfig):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size
        self.act_fn = ACT2FN[config.hidden_act]
        self.num_experts = config.num_experts
        self.num_keys = math.floor(math.sqrt(self.num_experts))
        self.top_k = config.num_experts_per_tok
        self.norm_topk_prob = config.norm_topk_prob
        self.gate_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=config.mlp_bias)
        self.up_proj = nn.Linear(self.hidden_size, self.intermediate_size, bias=config.mlp_bias)
        self.down_proj = nn.Linear(self.intermediate_size, self.hidden_size, bias=config.mlp_bias)
        self.router_gate = nn.Linear(self.hidden_size, self.num_keys * 2, bias=False)
        self.down_embed = nn.Embedding(self.num_experts, self.hidden_size)
        self.up_embed = nn.Embedding(self.num_experts, self.hidden_size)
    def forward(
        self,
        hidden_states: torch.Tensor,
        **kwargs,
    ) -> torch.Tensor:
        bsz, seq_len, _ = hidden_states.shape
        router_logits = self.router_gate(hidden_states).view(2, bsz * seq_len, -1)
        (scores_x, scores_y), (indices_x, indices_y) = router_logits.topk(self.num_keys, dim=-1)
        all_scores = scores_x.unsqueeze(-1) + scores_y.unsqueeze(-2)
        all_indices = indices_x.unsqueeze(-1) * self.num_keys + indices_y.unsqueeze(-2)
        all_scores = all_scores.view(*all_scores.shape[:-2], -1)
        all_indices = all_indices.view(*all_indices.shape[:-2], -1)
        scores, position_indices = all_scores.topk(self.top_k, dim=-1)
        indices = all_indices.gather(-1, position_indices)
        routing_weights = F.softmax(scores, dim=-1)
        if self.norm_topk_prob:
            routing_weights /= routing_weights.sum(dim=-1, keepdim=True)
        down_embed = self.down_embed(indices)
        up_embed = self.up_embed(indices)
        experts_weights = torch.matmul(down_embed, hidden_states.view(bsz * seq_len, -1, 1)).view(bsz * seq_len, -1)
        experts_weights = self.act_fn(experts_weights) * routing_weights
        experts_states = torch.matmul(experts_weights.view(bsz * seq_len, 1, -1), up_embed).view(bsz, seq_len, -1)
        hidden_states = self.down_proj(self.act_fn(self.gate_proj(hidden_states)) * self.up_proj(hidden_states))
        hidden_states = hidden_states + experts_states
        return hidden_states, router_logits
class DogeDecoderLayer(GradientCheckpointingLayer):
    def __init__(self, config: DogeConfig, layer_idx: Optional[int] = None):
        super().__init__()
        self.hidden_dropout = config.hidden_dropout
        self.input_layernorm = DogeRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.self_attn = DogeAttention(config=config, layer_idx=layer_idx)
        self.input_residual = nn.Parameter(torch.ones(config.hidden_size))
        self.post_attention_layernorm = DogeRMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.mlp = DogeMLP(config) if not config.is_moe else DogeCDMoE(config)
        self.post_attention_residual = nn.Parameter(torch.ones(config.hidden_size))
    @deprecate_kwarg("past_key_value", new_name="past_key_values", version="4.58")
    def forward(
        self,
        hidden_states: torch.Tensor,
        position_embeddings: tuple[torch.Tensor, torch.Tensor],
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        use_cache: Optional[bool] = False,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> tuple[torch.FloatTensor, Optional[tuple[torch.FloatTensor, torch.FloatTensor]]]:
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights = self.self_attn(
            hidden_states=hidden_states,
            position_embeddings=position_embeddings,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        hidden_states = F.dropout(hidden_states, p=self.hidden_dropout, training=self.training)
        hidden_states = self.input_residual * residual + hidden_states
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = F.dropout(hidden_states, p=self.hidden_dropout, training=self.training)
        hidden_states = self.post_attention_residual * residual + hidden_states
        return hidden_states
class DogePreTrainedModel(LlamaPreTrainedModel):
    _supports_flash_attn = False
    _can_compile_fullgraph = False
    _can_record_outputs = {
        "router_logits": OutputRecorder(DogeCDMoE, index=1),
        "hidden_states": DogeDecoderLayer,
        "attentions": DogeAttention,
    }
    def _init_weights(self, module):
        PreTrainedModel._init_weights(self, module)
        if isinstance(module, DogeAttention):
            if hasattr(module, "A"):
                module.A.data.zero_()
        elif isinstance(module, DogeDecoderLayer):
            if hasattr(module, "input_residual"):
                module.input_residual.data.fill_(1.0)
            if hasattr(module, "post_attention_residual"):
                module.post_attention_residual.data.fill_(1.0)
class DogeModel(MixtralModel):
    pass
def load_balancing_loss_func(
    gate_logits: Union[torch.Tensor, tuple[torch.Tensor], None],
    num_experts: Optional[int] = None,
    num_keys: Optional[int] = None,
    top_k: int = 2,
    attention_mask: Optional[torch.Tensor] = None,
) -> Union[torch.Tensor, int]:
    if gate_logits is None or not isinstance(gate_logits, tuple):
        return 0
    compute_dtype = gate_logits[0].dtype
    compute_device = gate_logits[0].device
    all_expert_indices = []
    all_routing_weights = []
    for layer_gate_logits in gate_logits:
        layer_gate_logits = layer_gate_logits.to(compute_device)
        (scores_x, scores_y), (indices_x, indices_y) = layer_gate_logits.topk(num_keys, dim=-1)
        all_scores = scores_x.unsqueeze(-1) + scores_y.unsqueeze(-2)
        all_indices = indices_x.unsqueeze(-1) * num_keys + indices_y.unsqueeze(-2)
        all_scores = all_scores.view(*all_scores.shape[:-2], -1)
        all_indices = all_indices.view(*all_indices.shape[:-2], -1)
        _, position_indices = all_scores.topk(top_k, dim=-1)
        expert_indices = all_indices.gather(-1, position_indices)
        routing_weights = F.softmax(all_scores, dim=-1)
        all_expert_indices.append(expert_indices)
        all_routing_weights.append(routing_weights)
    all_expert_indices = torch.cat(all_expert_indices, dim=0)
    all_routing_weights = torch.cat(all_routing_weights, dim=0)
    if attention_mask is None:
        all_expert_indices = all_expert_indices.view(-1)
        tokens_per_expert = torch.zeros(num_experts, dtype=compute_dtype, device=compute_device)
        pad = torch.ones_like(all_expert_indices, dtype=compute_dtype, device=compute_device)
        tokens_per_expert = tokens_per_expert.scatter_add_(0, all_expert_indices, pad) / all_expert_indices.shape[0]
        router_prob_per_expert = torch.mean(all_routing_weights, dim=0)
    else:
        batch_size, sequence_length = attention_mask.shape
        num_hidden_layers = len(gate_logits)
        expert_attention_mask = (
            attention_mask[None, :, :, None]
            .expand((num_hidden_layers, batch_size, sequence_length, top_k))
            .reshape(-1)
            .to(compute_device)
        )
        all_expert_indices = all_expert_indices.view(-1)[expert_attention_mask.bool()]
        tokens_per_expert = torch.zeros(num_experts, dtype=compute_dtype, device=compute_device)
        pad = torch.ones_like(all_expert_indices, dtype=compute_dtype, device=compute_device)
        tokens_per_expert = tokens_per_expert.scatter_add_(0, all_expert_indices, pad) / torch.sum(
            expert_attention_mask
        )
        router_per_expert_attention_mask = (
            attention_mask[None, :, :, None]
            .expand((num_hidden_layers, batch_size, sequence_length, num_experts))
            .reshape(-1, num_experts)
            .to(compute_device)
        )
        router_prob_per_expert = torch.sum(all_routing_weights * router_per_expert_attention_mask, dim=0) / torch.sum(
            router_per_expert_attention_mask, dim=0
        )
    overall_loss = torch.sum(tokens_per_expert * router_prob_per_expert)
    return overall_loss * num_experts
class DogeForCausalLM(MixtralForCausalLM):
    def __init__(self, config):
        super().__init__(config)
        self.model = DogeModel(config)
        self.num_experts = config.num_experts
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        logits_to_keep: Union[int, torch.Tensor] = 0,
        output_router_logits: Optional[bool] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> MoeCausalLMOutputWithPast:
        output_router_logits = (
            output_router_logits if output_router_logits is not None else self.config.output_router_logits
        )
        outputs: MoeModelOutputWithPast = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        hidden_states = outputs.last_hidden_state
        slice_indices = slice(-logits_to_keep, None) if isinstance(logits_to_keep, int) else logits_to_keep
        logits = self.lm_head(hidden_states[:, slice_indices, :])
        loss = None
        if labels is not None:
            loss = self.loss_function(logits, labels, self.vocab_size, **kwargs)
        aux_loss = None
        if output_router_logits:
            aux_loss = load_balancing_loss_func(
                outputs.router_logits,
                self.num_experts,
                math.floor(math.sqrt(self.num_experts)),
                self.num_experts_per_tok,
                attention_mask,
            )
            if labels is not None:
                loss += self.router_aux_loss_coef * aux_loss.to(loss.device)
        return MoeCausalLMOutputWithPast(
            loss=loss,
            aux_loss=aux_loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            router_logits=outputs.router_logits,
        )
class DogeForSequenceClassification(LlamaForSequenceClassification):
    pass
__all__ = [
    "DogeConfig",
    "DogeForCausalLM",
    "DogeModel",
    "DogePreTrainedModel",
    "DogeForSequenceClassification",
]