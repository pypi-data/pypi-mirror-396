from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class BltLocalEncoderConfig(PretrainedConfig):
    model_type = "blt_local_encoder"
    def __init__(
        self,
        vocab_size=260,
        cross_attn_all_layers=False,
        cross_attn_k=2,
        hidden_size_global=2048,
        hidden_size=1024,
        num_attention_heads=16,
        num_key_value_heads=None,
        num_hidden_layers=1,
        rms_norm_eps=1e-5,
        dropout=0.0,
        max_position_embeddings=24576,
        rope_theta=500000.0,
        rope_scaling=None,
        hidden_act="silu",
        intermediate_size=2816,
        initializer_range=0.02,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.cross_attn_all_layers = cross_attn_all_layers
        self.cross_attn_k = cross_attn_k
        self.hidden_size_global = hidden_size_global
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads or num_attention_heads
        self.head_dim = hidden_size // num_attention_heads
        self.intermediate_size = intermediate_size or int(8 * hidden_size / 3)
        self.num_hidden_layers = num_hidden_layers
        self.rms_norm_eps = rms_norm_eps
        self.dropout = dropout
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        kwargs.pop("tie_word_embeddings", None)
        super().__init__(**kwargs, tie_word_embeddings=False)
class BltLocalDecoderConfig(PretrainedConfig):
    model_type = "blt_local_decoder"
    def __init__(
        self,
        vocab_size=260,
        cross_attn_all_layers=True,
        cross_attn_k=2,
        hidden_size_global=2048,
        hidden_size=1024,
        num_attention_heads=16,
        num_key_value_heads=None,
        num_hidden_layers=9,
        rms_norm_eps=1e-5,
        dropout=0.0,
        max_position_embeddings=24576,
        rope_theta=500000.0,
        rope_scaling=None,
        hidden_act="silu",
        intermediate_size=2816,
        initializer_range=0.02,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.cross_attn_all_layers = cross_attn_all_layers
        self.cross_attn_k = cross_attn_k
        self.hidden_size_global = hidden_size_global
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads or num_attention_heads
        self.head_dim = hidden_size // num_attention_heads
        self.intermediate_size = intermediate_size or int(8 * hidden_size / 3)
        self.num_hidden_layers = num_hidden_layers
        self.rms_norm_eps = rms_norm_eps
        self.dropout = dropout
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        kwargs.pop("tie_word_embeddings", None)
        super().__init__(**kwargs, tie_word_embeddings=False)
class BltGlobalTransformerConfig(PretrainedConfig):
    model_type = "blt_global_transformer"
    def __init__(
        self,
        hidden_size=2048,
        num_attention_heads=16,
        num_key_value_heads=None,
        num_hidden_layers=25,
        rms_norm_eps=1e-5,
        dropout=0.0,
        max_position_embeddings=4096,
        rope_theta=500000.0,
        rope_scaling=None,
        hidden_act="silu",
        intermediate_size=5632,
        initializer_range=0.02,
        **kwargs,
    ):
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads or num_attention_heads
        self.head_dim = hidden_size // num_attention_heads
        self.intermediate_size = intermediate_size or int(8 * hidden_size / 3)
        self.num_hidden_layers = num_hidden_layers
        self.rms_norm_eps = rms_norm_eps
        self.dropout = dropout
        self.max_position_embeddings = max_position_embeddings
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.hidden_act = hidden_act
        self.initializer_range = initializer_range
        kwargs.pop("tie_word_embeddings", None)
        super().__init__(**kwargs, tie_word_embeddings=False)
class BltPatcherConfig(PretrainedConfig):
    model_type = "blt_patcher"
    def __init__(
        self,
        vocab_size=260,
        hidden_size=768,
        num_hidden_layers=14,
        num_attention_heads=12,
        num_key_value_heads=None,
        max_position_embeddings=8192,
        rms_norm_eps=1e-5,
        dropout=0.0,
        rope_theta=10000.0,
        intermediate_size=2048,
        rope_scaling=None,
        initializer_range=0.02,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.head_dim = hidden_size // num_attention_heads
        self.num_key_value_heads = num_key_value_heads if num_key_value_heads is not None else num_attention_heads
        self.max_position_embeddings = max_position_embeddings
        self.rms_norm_eps = rms_norm_eps
        self.dropout = dropout
        self.rope_theta = rope_theta
        self.hidden_act = "silu"
        self.intermediate_size = intermediate_size or int(8 * self.hidden_size / 3)
        self.rope_scaling = rope_scaling
        self.initializer_range = initializer_range
        kwargs.pop("tie_word_embeddings", None)
        super().__init__(**kwargs, tie_word_embeddings=False)
class BltConfig(PretrainedConfig):
    model_type = "blt"
    keys_to_ignore_at_inference = ["past_key_values"]
    sub_configs = {
        "patcher_config": BltPatcherConfig,
        "encoder_config": BltLocalEncoderConfig,
        "decoder_config": BltLocalDecoderConfig,
        "global_config": BltGlobalTransformerConfig,
    }
    def __init__(
        self,
        vocab_size=260,
        max_position_embeddings=4096,
        patch_in_forward=True,
        patch_size=4,
        patching_mode="entropy",
        patching_threshold=1.335442066192627,
        patching_batch_size=1,
        max_patch_length=None,
        cross_attn_k=2,
        encoder_hash_byte_group_size=None,
        encoder_hash_byte_group_vocab=500002,
        encoder_hash_byte_group_nb_functions=1,
        patcher_config=None,
        encoder_config=None,
        decoder_config=None,
        global_config=None,
        tie_word_embeddings=False,
        initializer_range=0.02,
        rope_theta=500000.0,
        rope_scaling=None,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.initializer_range = initializer_range
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.patch_in_forward = patch_in_forward
        self.patch_size = patch_size
        self.patching_mode = patching_mode
        self.patching_threshold = patching_threshold
        self.patching_batch_size = patching_batch_size
        self.max_patch_length = max_patch_length
        self.patching_device = kwargs.get("patching_device", "cuda")
        self.realtime_patching = kwargs.get("realtime_patching", True)
        self.patching_threshold_add = kwargs.get("patching_threshold_add")
        self.monotonicity = kwargs.get("monotonicity", False)
        self.cross_attn_k = cross_attn_k
        self.encoder_hash_byte_group_size = encoder_hash_byte_group_size or [3, 4, 5, 6, 7, 8]
        self.encoder_hash_byte_group_vocab = encoder_hash_byte_group_vocab
        self.encoder_hash_byte_group_nb_functions = encoder_hash_byte_group_nb_functions
        if patcher_config is None:
            self.patcher_config = BltPatcherConfig(initializer_range=initializer_range)
            logger.info("patcher_config is None, using default Blt patcher config")
        elif isinstance(patcher_config, dict):
            patcher_config.setdefault("initializer_range", initializer_range)
            self.patcher_config = BltPatcherConfig(**patcher_config)
        elif isinstance(patcher_config, BltPatcherConfig):
            self.patcher_config = patcher_config
        if encoder_config is None:
            self.encoder_config = BltLocalEncoderConfig(initializer_range=initializer_range)
            logger.info("encoder_config is None, using default Blt encoder config")
        elif isinstance(encoder_config, dict):
            encoder_config.setdefault("initializer_range", initializer_range)
            self.encoder_config = BltLocalEncoderConfig(**encoder_config)
        elif isinstance(encoder_config, BltLocalEncoderConfig):
            self.encoder_config = encoder_config
        if decoder_config is None:
            self.decoder_config = BltLocalDecoderConfig(initializer_range=initializer_range)
            logger.info("decoder_config is None, using default Blt decoder config")
        elif isinstance(decoder_config, dict):
            decoder_config.setdefault("initializer_range", initializer_range)
            self.decoder_config = BltLocalDecoderConfig(**decoder_config)
        elif isinstance(decoder_config, BltLocalDecoderConfig):
            self.decoder_config = decoder_config
        if global_config is None:
            self.global_config = BltGlobalTransformerConfig(initializer_range=initializer_range)
            logger.info("global_config is None, using default Blt global config")
        elif isinstance(global_config, dict):
            global_config.setdefault("initializer_range", initializer_range)
            self.global_config = BltGlobalTransformerConfig(**global_config)
        elif isinstance(global_config, BltGlobalTransformerConfig):
            self.global_config = global_config
        encoder_cross_output_size = self.encoder_config.hidden_size * self.cross_attn_k
        self.global_config.encoder_cross_output_size = (
            encoder_cross_output_size if encoder_cross_output_size != self.global_config.hidden_size else None
        )
        kwargs.pop("tie_word_embeddings", None)
        super().__init__(tie_word_embeddings=tie_word_embeddings, **kwargs)
__all__ = [
    "BltConfig",
    "BltPatcherConfig",
    "BltLocalEncoderConfig",
    "BltLocalDecoderConfig",
    "BltGlobalTransformerConfig",
]