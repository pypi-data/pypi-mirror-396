from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class BambaConfig(PretrainedConfig):
    model_type = "bamba"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(
        self,
        vocab_size=128000,
        tie_word_embeddings=False,
        hidden_size=4096,
        intermediate_size=14336,
        num_hidden_layers=32,
        num_attention_heads=32,
        num_key_value_heads=8,
        hidden_act="silu",
        initializer_range=0.02,
        rms_norm_eps=1e-5,
        use_cache=True,
        num_logits_to_keep=1,
        pad_token_id=0,
        bos_token_id=1,
        eos_token_id=2,
        max_position_embeddings=262144,
        attention_dropout=0.0,
        attn_layer_indices=None,
        mamba_n_heads=128,
        mamba_d_head="auto",
        mamba_n_groups=1,
        mamba_d_state=256,
        mamba_d_conv=4,
        mamba_expand=2,
        mamba_chunk_size=256,
        mamba_conv_bias=True,
        mamba_proj_bias=False,
        z_loss_coefficient=0.0,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.tie_word_embeddings = tie_word_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.attention_dropout = attention_dropout
        self.attention_bias = False
        self.mlp_bias = False
        if num_key_value_heads is None:
            num_key_value_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.num_logits_to_keep = num_logits_to_keep
        self.attn_layer_indices = attn_layer_indices
        self.rope_theta = 10000.0
        self.rope_scaling = None
        self.partial_rotary_factor = 0.5
        mamba_intermediate = mamba_expand * hidden_size
        if mamba_intermediate % mamba_n_heads != 0:
            raise ValueError("mamba_n_heads must divide mamba_expand * hidden_size")
        if mamba_d_head == "auto":
            mamba_d_head = mamba_intermediate // mamba_n_heads
        if mamba_d_head * mamba_n_heads != mamba_intermediate:
            raise ValueError("The dimensions for the Mamba head state do not match the model intermediate_size")
        self.mamba_n_heads = mamba_n_heads
        self.mamba_d_head = mamba_d_head
        self.mamba_n_groups = mamba_n_groups
        self.mamba_d_state = mamba_d_state
        self.mamba_d_conv = mamba_d_conv
        self.mamba_expand = mamba_expand
        self.mamba_chunk_size = mamba_chunk_size
        self.mamba_conv_bias = mamba_conv_bias
        self.mamba_proj_bias = mamba_proj_bias
        self.z_loss_coefficient = z_loss_coefficient
        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )
    @property
    def layers_block_type(self):
        return [
            "attention" if (self.attn_layer_indices and i in self.attn_layer_indices) else "mamba"
            for i in range(self.num_hidden_layers)
        ]
__all__ = ["BambaConfig"]