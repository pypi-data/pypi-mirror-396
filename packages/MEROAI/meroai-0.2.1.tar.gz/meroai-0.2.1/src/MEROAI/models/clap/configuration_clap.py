from ...configuration_utils import PretrainedConfig
from ...utils import logging
logger = logging.get_logger(__name__)
class ClapTextConfig(PretrainedConfig):
    model_type = "clap_text_model"
    base_config_key = "text_config"
    def __init__(
        self,
        vocab_size=50265,
        hidden_size=768,
        num_hidden_layers=12,
        num_attention_heads=12,
        intermediate_size=3072,
        hidden_act="gelu",
        hidden_dropout_prob=0.1,
        attention_probs_dropout_prob=0.1,
        max_position_embeddings=514,
        type_vocab_size=1,
        initializer_factor=1.0,
        layer_norm_eps=1e-12,
        projection_dim=512,
        pad_token_id=1,
        bos_token_id=0,
        eos_token_id=2,
        position_embedding_type="absolute",
        use_cache=True,
        projection_hidden_act="relu",
        **kwargs,
    ):
        super().__init__(pad_token_id=pad_token_id, bos_token_id=bos_token_id, eos_token_id=eos_token_id, **kwargs)
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.hidden_act = hidden_act
        self.intermediate_size = intermediate_size
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.max_position_embeddings = max_position_embeddings
        self.type_vocab_size = type_vocab_size
        self.initializer_factor = initializer_factor
        self.layer_norm_eps = layer_norm_eps
        self.position_embedding_type = position_embedding_type
        self.use_cache = use_cache
        self.projection_hidden_act = projection_hidden_act
        self.projection_dim = projection_dim
class ClapAudioConfig(PretrainedConfig):
    model_type = "clap_audio_model"
    base_config_key = "audio_config"
    def __init__(
        self,
        window_size=8,
        num_mel_bins=64,
        spec_size=256,
        hidden_act="gelu",
        patch_size=4,
        patch_stride=[4, 4],
        num_classes=527,
        hidden_size=768,
        projection_dim=512,
        depths=[2, 2, 6, 2],
        num_attention_heads=[4, 8, 16, 32],
        enable_fusion=False,
        hidden_dropout_prob=0.1,
        fusion_type=None,
        patch_embed_input_channels=1,
        flatten_patch_embeds=True,
        patch_embeds_hidden_size=96,
        enable_patch_layer_norm=True,
        drop_path_rate=0.0,
        attention_probs_dropout_prob=0.0,
        qkv_bias=True,
        mlp_ratio=4.0,
        aff_block_r=4,
        num_hidden_layers=4,
        projection_hidden_act="relu",
        layer_norm_eps=1e-5,
        initializer_factor=1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.window_size = window_size
        self.num_mel_bins = num_mel_bins
        self.spec_size = spec_size
        self.patch_size = patch_size
        self.patch_stride = patch_stride
        self.num_classes = num_classes
        self.hidden_size = hidden_size
        self.depths = depths
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.window_size = window_size
        self.enable_fusion = enable_fusion
        self.fusion_type = fusion_type
        self.hidden_act = hidden_act
        self.hidden_dropout_prob = hidden_dropout_prob
        self.projection_dim = projection_dim
        self.flatten_patch_embeds = flatten_patch_embeds
        self.patch_embeds_hidden_size = patch_embeds_hidden_size
        self.enable_patch_layer_norm = enable_patch_layer_norm
        self.drop_path_rate = drop_path_rate
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.qkv_bias = qkv_bias
        self.mlp_ratio = mlp_ratio
        self.patch_embed_input_channels = patch_embed_input_channels
        self.aff_block_r = aff_block_r
        self.layer_norm_eps = layer_norm_eps
        self.initializer_factor = initializer_factor
        self.projection_hidden_act = projection_hidden_act
class ClapConfig(PretrainedConfig):
    model_type = "clap"
    sub_configs = {"text_config": ClapTextConfig, "audio_config": ClapAudioConfig}
    def __init__(
        self,
        text_config=None,
        audio_config=None,
        logit_scale_init_value=(1 / 0.07),
        projection_dim=512,
        projection_hidden_act="relu",
        initializer_factor=1.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("text_config is None. Initializing the ClapTextConfig with default values.")
        if audio_config is None:
            audio_config = {}
            logger.info("audio_config is None. initializing the ClapAudioConfig with default values.")
        self.text_config = ClapTextConfig(**text_config)
        self.audio_config = ClapAudioConfig(**audio_config)
        self.text_config.projection_dim = projection_dim
        self.audio_config.projection_dim = projection_dim
        self.text_config.projection_hidden_act = projection_hidden_act
        self.audio_config.projection_hidden_act = projection_hidden_act
        self.projection_dim = projection_dim
        self.projection_hidden_act = projection_hidden_act
        self.hidden_size = self.text_config.hidden_size
        self.logit_scale_init_value = logit_scale_init_value
        self.initializer_factor = initializer_factor
        self.num_hidden_layers = self.text_config.num_hidden_layers + len(self.audio_config.depths)
__all__ = ["ClapAudioConfig", "ClapConfig", "ClapTextConfig"]