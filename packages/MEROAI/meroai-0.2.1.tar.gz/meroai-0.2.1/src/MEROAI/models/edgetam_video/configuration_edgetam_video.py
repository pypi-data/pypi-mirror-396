from ...configuration_utils import PretrainedConfig
from ..auto import CONFIG_MAPPING, AutoConfig
class EdgeTamVideoPromptEncoderConfig(PretrainedConfig):
    base_config_key = "prompt_encoder_config"
    def __init__(
        self,
        hidden_size=256,
        image_size=1024,
        patch_size=16,
        mask_input_channels=16,
        num_point_embeddings=4,
        hidden_act="gelu",
        layer_norm_eps=1e-6,
        scale=1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.image_size = image_size
        self.patch_size = patch_size
        self.mask_input_channels = mask_input_channels
        self.num_point_embeddings = num_point_embeddings
        self.hidden_act = hidden_act
        self.layer_norm_eps = layer_norm_eps
        self.scale = scale
class EdgeTamVideoMaskDecoderConfig(PretrainedConfig):
    base_config_key = "mask_decoder_config"
    def __init__(
        self,
        hidden_size=256,
        hidden_act="gelu",
        mlp_dim=2048,
        num_hidden_layers=2,
        num_attention_heads=8,
        attention_downsample_rate=2,
        num_multimask_outputs=3,
        iou_head_depth=3,
        iou_head_hidden_dim=256,
        dynamic_multimask_via_stability=True,
        dynamic_multimask_stability_delta=0.05,
        dynamic_multimask_stability_thresh=0.98,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.hidden_size = hidden_size
        self.num_multimask_outputs = num_multimask_outputs
        self.hidden_act = hidden_act
        self.iou_head_depth = iou_head_depth
        self.iou_head_hidden_dim = iou_head_hidden_dim
        self.dynamic_multimask_via_stability = dynamic_multimask_via_stability
        self.dynamic_multimask_stability_delta = dynamic_multimask_stability_delta
        self.dynamic_multimask_stability_thresh = dynamic_multimask_stability_thresh
        self.num_hidden_layers = num_hidden_layers
        self.hidden_size = hidden_size
        self.num_attention_heads = num_attention_heads
        self.mlp_dim = mlp_dim
        self.attention_downsample_rate = attention_downsample_rate
class EdgeTamVideoConfig(PretrainedConfig):
    model_type = "edgetam_video"
    sub_configs = {
        "vision_config": AutoConfig,
        "prompt_encoder_config": EdgeTamVideoPromptEncoderConfig,
        "mask_decoder_config": EdgeTamVideoMaskDecoderConfig,
    }
    def __init__(
        self,
        vision_config=None,
        prompt_encoder_config=None,
        mask_decoder_config=None,
        initializer_range=0.02,
        num_maskmem=7,
        image_size=1024,
        sigmoid_scale_for_mem_enc=20.0,
        sigmoid_bias_for_mem_enc=-10.0,
        enable_occlusion_spatial_embedding=True,
        multimask_output_in_sam=True,
        multimask_min_pt_num=0,
        multimask_max_pt_num=1,
        multimask_output_for_tracking=True,
        max_object_pointers_in_encoder=16,
        enable_temporal_pos_encoding_for_object_pointers=True,
        memory_attention_hidden_size=256,
        memory_attention_num_layers=2,
        memory_attention_num_attention_heads=1,
        memory_attention_downsample_rate=1,
        memory_attention_mlp_hidden_size=2048,
        memory_attention_mlp_hidden_act="relu",
        memory_attention_dropout=0.1,
        memory_attention_rope_theta=10000,
        memory_attention_rope_feat_sizes=None,
        memory_attention_rope_k_sizes=None,
        memory_attention_rope_dropout=0.1,
        perceiver_resampler_num_latents=256,
        perceiver_resampler_num_latents_2d=256,
        perceiver_resampler_hidden_size=64,
        perceiver_resampler_mlp_intermediate_size=256,
        perceiver_resampler_num_attention_heads=1,
        perceiver_resampler_attention_head_dim=64,
        perceiver_resampler_num_layers=2,
        perceiver_resampler_hidden_dropout=0.0,
        perceiver_resampler_attention_dropout=0.0,
        memory_encoder_hidden_size=256,
        memory_encoder_output_channels=64,
        mask_downsampler_embed_dim=256,
        memory_fuser_intermediate_dim=1024,
        mask_downsampler_kernel_size=3,
        mask_downsampler_stride=2,
        mask_downsampler_padding=1,
        mask_downsampler_total_stride=16,
        mask_downsampler_hidden_act="gelu",
        memory_fuser_num_layers=2,
        memory_fuser_embed_dim=256,
        memory_fuser_kernel_size=7,
        memory_fuser_padding=3,
        memory_fuser_layer_scale_init_value=1e-6,
        memory_fuser_hidden_act="gelu",
        **kwargs,
    ):
        super().__init__(**kwargs)
        vision_config = vision_config if vision_config is not None else {}
        prompt_encoder_config = prompt_encoder_config if prompt_encoder_config is not None else {}
        mask_decoder_config = mask_decoder_config if mask_decoder_config is not None else {}
        memory_attention_rope_feat_sizes = (
            [64, 64] if memory_attention_rope_feat_sizes is None else memory_attention_rope_feat_sizes
        )
        memory_attention_rope_k_sizes = (
            [16, 16] if memory_attention_rope_k_sizes is None else memory_attention_rope_k_sizes
        )
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "sam2_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        if isinstance(prompt_encoder_config, EdgeTamVideoPromptEncoderConfig):
            prompt_encoder_config = prompt_encoder_config.to_dict()
        if isinstance(mask_decoder_config, EdgeTamVideoMaskDecoderConfig):
            mask_decoder_config = mask_decoder_config.to_dict()
        self.vision_config = vision_config
        self.prompt_encoder_config = EdgeTamVideoPromptEncoderConfig(**prompt_encoder_config)
        self.mask_decoder_config = EdgeTamVideoMaskDecoderConfig(**mask_decoder_config)
        self.initializer_range = initializer_range
        self.num_maskmem = num_maskmem
        self.image_size = image_size
        self.sigmoid_scale_for_mem_enc = sigmoid_scale_for_mem_enc
        self.sigmoid_bias_for_mem_enc = sigmoid_bias_for_mem_enc
        self.enable_occlusion_spatial_embedding = enable_occlusion_spatial_embedding
        self.multimask_output_in_sam = multimask_output_in_sam
        self.multimask_min_pt_num = multimask_min_pt_num
        self.multimask_max_pt_num = multimask_max_pt_num
        self.multimask_output_for_tracking = multimask_output_for_tracking
        self.max_object_pointers_in_encoder = max_object_pointers_in_encoder
        self.enable_temporal_pos_encoding_for_object_pointers = enable_temporal_pos_encoding_for_object_pointers
        self.memory_attention_hidden_size = memory_attention_hidden_size
        self.memory_attention_num_layers = memory_attention_num_layers
        self.memory_attention_num_attention_heads = memory_attention_num_attention_heads
        self.memory_attention_downsample_rate = memory_attention_downsample_rate
        self.memory_attention_mlp_hidden_size = memory_attention_mlp_hidden_size
        self.memory_attention_mlp_hidden_act = memory_attention_mlp_hidden_act
        self.memory_attention_dropout = memory_attention_dropout
        self.memory_attention_rope_theta = memory_attention_rope_theta
        self.memory_attention_rope_feat_sizes = memory_attention_rope_feat_sizes
        self.memory_attention_rope_k_sizes = memory_attention_rope_k_sizes
        self.memory_attention_rope_dropout = memory_attention_rope_dropout
        self.perceiver_resampler_num_latents = perceiver_resampler_num_latents
        self.perceiver_resampler_num_latents_2d = perceiver_resampler_num_latents_2d
        self.perceiver_resampler_hidden_size = perceiver_resampler_hidden_size
        self.perceiver_resampler_mlp_intermediate_size = perceiver_resampler_mlp_intermediate_size
        self.perceiver_resampler_attention_head_dim = perceiver_resampler_attention_head_dim
        self.perceiver_resampler_num_attention_heads = perceiver_resampler_num_attention_heads
        self.perceiver_resampler_num_layers = perceiver_resampler_num_layers
        self.perceiver_resampler_hidden_dropout = perceiver_resampler_hidden_dropout
        self.perceiver_resampler_attention_dropout = perceiver_resampler_attention_dropout
        self.memory_encoder_hidden_size = memory_encoder_hidden_size
        self.memory_encoder_output_channels = memory_encoder_output_channels
        self.mask_downsampler_embed_dim = mask_downsampler_embed_dim
        self.mask_downsampler_kernel_size = mask_downsampler_kernel_size
        self.mask_downsampler_stride = mask_downsampler_stride
        self.mask_downsampler_padding = mask_downsampler_padding
        self.mask_downsampler_total_stride = mask_downsampler_total_stride
        self.mask_downsampler_hidden_act = mask_downsampler_hidden_act
        self.memory_fuser_num_layers = memory_fuser_num_layers
        self.memory_fuser_embed_dim = memory_fuser_embed_dim
        self.memory_fuser_intermediate_dim = memory_fuser_intermediate_dim
        self.memory_fuser_kernel_size = memory_fuser_kernel_size
        self.memory_fuser_padding = memory_fuser_padding
        self.memory_fuser_layer_scale_init_value = memory_fuser_layer_scale_init_value
        self.memory_fuser_hidden_act = memory_fuser_hidden_act
__all__ = ["EdgeTamVideoMaskDecoderConfig", "EdgeTamVideoPromptEncoderConfig", "EdgeTamVideoConfig"]