from typing import Any, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...modeling_rope_utils import rope_config_validation
class Emu3VQVAEConfig(PretrainedConfig):
    model_type = "emu3_vqgan"
    base_config_key = "vq_config"
    def __init__(
        self,
        codebook_size: int = 32768,
        embed_dim: int = 4,
        latent_channels: int = 4,
        double_latent: bool = False,
        in_channels: int = 3,
        out_channels: int = 3,
        temporal_downsample_factor: int = 4,
        base_channels: int = 256,
        channel_multiplier: list[int] = [1, 2, 2, 4],
        num_res_blocks: int = 2,
        attn_resolutions: list[int] = [3],
        hidden_size: int = 1024,
        num_attention_heads: int = 1,
        attention_dropout: float = 0.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.codebook_size = codebook_size
        self.embed_dim = embed_dim
        self.latent_channels = latent_channels
        self.double_latent = double_latent
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.temporal_downsample_factor = temporal_downsample_factor
        self.base_channels = base_channels
        self.channel_multiplier = channel_multiplier
        self.num_res_blocks = num_res_blocks
        self.attn_resolutions = attn_resolutions
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.attention_dropout = attention_dropout
class Emu3TextConfig(PretrainedConfig):
    model_type = "emu3_text_model"
    base_config_key = "text_config"
    keys_to_ignore_at_inference = ["past_key_values"]
    def __init__(
        self,
        vocab_size: int = 184622,
        hidden_size: int = 4096,
        intermediate_size: int = 14336,
        num_hidden_layers: int = 32,
        num_attention_heads: int = 32,
        num_key_value_heads: Optional[int] = 8,
        hidden_act: str = "silu",
        max_position_embeddings: int = 9216,
        rms_norm_eps: float = 1e-5,
        use_cache: bool = True,
        pad_token_id: int = 151643,
        bos_token_id: int = 151849,
        eos_token_id: int = 151850,
        tie_word_embeddings: bool = False,
        rope_theta: float = 1000000.0,
        rope_scaling: Optional[dict[str, Any]] = None,
        mlp_bias=False,
        attention_bias=False,
        attention_dropout: float = 0.1,
        initializer_range: float = 0.02,
        **kwargs,
    ):
        self.vocab_size = vocab_size
        self.max_position_embeddings = max_position_embeddings
        self.hidden_size = hidden_size
        self.intermediate_size = intermediate_size
        self.num_hidden_layers = num_hidden_layers
        self.num_attention_heads = num_attention_heads
        self.num_key_value_heads = num_key_value_heads
        self.hidden_act = hidden_act
        self.rms_norm_eps = rms_norm_eps
        self.use_cache = use_cache
        self.rope_theta = rope_theta
        self.rope_scaling = rope_scaling
        self.mlp_bias = mlp_bias
        self.attention_bias = attention_bias
        self.initializer_range = initializer_range
        rope_config_validation(self)
        self.attention_dropout = attention_dropout
        super().__init__(
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            tie_word_embeddings=tie_word_embeddings,
            **kwargs,
        )
class Emu3Config(PretrainedConfig):
    model_type = "emu3"
    keys_to_ignore_at_inference = ["past_key_values"]
    sub_configs = {"text_config": Emu3TextConfig, "vq_config": Emu3VQVAEConfig}
    def __init__(
        self,
        vq_config: Union[dict, Emu3VQVAEConfig] = None,
        text_config: Union[dict, Emu3TextConfig] = None,
        vocabulary_map: Optional[dict[int, int]] = None,
        **kwargs,
    ):
        if vq_config is None:
            vq_config = Emu3VQVAEConfig()
        elif isinstance(vq_config, dict):
            vq_config = Emu3VQVAEConfig(**vq_config)
        if text_config is None:
            text_config = Emu3TextConfig()
        elif isinstance(text_config, dict):
            text_config = Emu3TextConfig(**text_config)
        self.vq_config = vq_config
        self.text_config = text_config
        self.vocabulary_map = vocabulary_map
        self.image_token_id = vocabulary_map.get("<image>") if vocabulary_map is not None else None
        super().__init__(**kwargs)
__all__ = ["Emu3Config", "Emu3TextConfig", "Emu3VQVAEConfig"]