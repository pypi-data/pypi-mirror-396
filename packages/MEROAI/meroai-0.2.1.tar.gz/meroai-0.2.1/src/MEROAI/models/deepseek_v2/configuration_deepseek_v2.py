from ...configuration_utils import PretrainedConfig
from ...modeling_rope_utils import rope_config_validation
class DeepseekV2Config(PretrainedConfig):
    model_type = "deepseek_v2"
    keys_to_ignore_at_inference = ["past_key_values"]
    base_model_tp_plan = {
        "layers.*.self_attn.q_proj": "colwise",
        "layers.*.self_attn.q_a_proj": "colwise",
        "layers.*.self_attn.q_b_proj": "colwise",
        "layers.*.self_attn.kv_b_proj": "colwise",
        "layers.*.self_attn.o_proj": "rowwise",
        "layers.*.mlp.gate_proj": "colwise",
        "layers.*.mlp.up_proj": "colwise",
        "layers.*.mlp.down_proj": "rowwise",
    }
    base_model_pp_plan = {
        "embed_tokens": (["input_ids"], ["inputs_embeds"]),
        "layers": (["hidden_states", "attention_mask"], ["hidden_states"]),
        "norm": (["hidden_states"], ["hidden_states"]),
    }
    def __init__(
        self,
        vocab_size=32000,
        hidden_size=4096,
        intermediate_size=11008,
        num_hidden_layers=32,
        num_attention_heads=32,
        num_key_value_heads=None,
        hidden_act="silu",
        max_position_embeddings=2048,
        initializer_range=0.02,
        rms_norm_eps=1e-6,
        use_cache=True,
        pad_token_id=None,
        bos_token_id=1,
        eos_token_id=2,
        tie_word_embeddings=False,
        rope_theta=10000.0,
        rope_scaling=None,
        attention_bias=False,
        attention_dropout=0.0,
        mlp_bias=False,
        aux_loss_alpha=0.001,
        first_k_dense_replace=0,
        kv_lora_rank=512,
        q_lora_rank=1536,
        n_group=None,
        n_routed_experts=64,
        n_shared_experts=2,
        qk_nope_head_dim=128,
        qk_rope_head_dim=64,
        routed_scaling_factor=1.0,
        seq_aux=True,
        topk_group=None,
        topk_method="greedy",
        v_head_dim=128,
        num_experts_per_tok=None,
        norm_topk_prob=False,
        moe_intermediate_size=1407,
        **kwargs,
    ):
        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        if num_key_value_heads is None:
            num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.attention_bias = attention_bias
        self.attention_dropout = attention_dropout
        self.mlp_bias = mlp_bias
        self.head_dim = qk_rope_head_dim
        if self.rope_scaling is not None and "type" in self.rope_scaling:
            self.rope_scaling["rope_type"] = self.rope_scaling["type"]
        rope_config_validation(self)
        self.aux_loss_alpha = aux_loss_alpha
        self.first_k_dense_replace = first_k_dense_replace
        self.kv_lora_rank = kv_lora_rank
        self.q_lora_rank = q_lora_rank
        self.n_group = n_group
        self.n_routed_experts = n_routed_experts
        self.n_shared_experts = n_shared_experts
        self.qk_nope_head_dim = qk_nope_head_dim
        self.qk_rope_head_dim = qk_rope_head_dim
        self.routed_scaling_factor = routed_scaling_factor
        self.seq_aux = seq_aux
        self.topk_group = topk_group
        self.topk_method = topk_method
        self.v_head_dim = v_head_dim
        self.num_experts_per_tok = num_experts_per_tok
        self.norm_topk_prob = norm_topk_prob
        self.moe_intermediate_size = moe_intermediate_size
__all__ = ["DeepseekV2Config"]