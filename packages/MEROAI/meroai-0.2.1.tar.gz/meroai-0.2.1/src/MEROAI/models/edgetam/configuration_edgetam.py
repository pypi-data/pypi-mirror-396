from ...configuration_utils import PretrainedConfig
from ..auto import CONFIG_MAPPING, AutoConfig
class EdgeTamVisionConfig(PretrainedConfig):
    base_config_key = "vision_config"
    model_type = "edgetam_vision_model"
    sub_configs = {
        "backbone_config": AutoConfig,
    }
    def __init__(
        self,
        backbone_config=None,
        backbone_channel_list=None,
        backbone_feature_sizes=None,
        fpn_hidden_size=256,
        fpn_kernel_size=1,
        fpn_stride=1,
        fpn_padding=0,
        fpn_top_down_levels=None,
        num_feature_levels=3,
        hidden_act="gelu",
        layer_norm_eps=1e-6,
        initializer_range=0.02,
        **kwargs,
    ):
        super().__init__(**kwargs)
        backbone_channel_list = [384, 192, 96, 48] if backbone_channel_list is None else backbone_channel_list
        backbone_feature_sizes = (
            [[256, 256], [128, 128], [64, 64]] if backbone_feature_sizes is None else backbone_feature_sizes
        )
        fpn_top_down_levels = [2, 3] if fpn_top_down_levels is None else fpn_top_down_levels
        if isinstance(backbone_config, dict):
            backbone_config["model_type"] = backbone_config.get("model_type", "timm_wrapper")
            backbone_config = CONFIG_MAPPING[backbone_config["model_type"]](**backbone_config)
        elif isinstance(backbone_config, AutoConfig):
            backbone_config = backbone_config
        elif backbone_config is None:
            backbone_config = AutoConfig.from_pretrained(
                "timm/repvit_m1.dist_in1k",
                model_args={"in_chans": 3, "features_only": True, "out_indices": [0, 1, 2, 3]},
            )
        self.backbone_config = backbone_config
        self.backbone_channel_list = backbone_channel_list
        self.backbone_feature_sizes = backbone_feature_sizes
        self.fpn_hidden_size = fpn_hidden_size
        self.fpn_kernel_size = fpn_kernel_size
        self.fpn_stride = fpn_stride
        self.fpn_padding = fpn_padding
        self.fpn_top_down_levels = fpn_top_down_levels
        self.num_feature_levels = num_feature_levels
        self.hidden_act = hidden_act
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range
class EdgeTamPromptEncoderConfig(PretrainedConfig):
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
class EdgeTamMaskDecoderConfig(PretrainedConfig):
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
class EdgeTamConfig(PretrainedConfig):
    model_type = "edgetam"
    sub_configs = {
        "vision_config": AutoConfig,
        "prompt_encoder_config": EdgeTamPromptEncoderConfig,
        "mask_decoder_config": EdgeTamMaskDecoderConfig,
    }
    def __init__(
        self,
        vision_config=None,
        prompt_encoder_config=None,
        mask_decoder_config=None,
        initializer_range=0.02,
        **kwargs,
    ):
        super().__init__(**kwargs)
        vision_config = vision_config if vision_config is not None else {}
        prompt_encoder_config = prompt_encoder_config if prompt_encoder_config is not None else {}
        mask_decoder_config = mask_decoder_config if mask_decoder_config is not None else {}
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "edgetam_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        if isinstance(prompt_encoder_config, EdgeTamPromptEncoderConfig):
            prompt_encoder_config = prompt_encoder_config.to_dict()
        if isinstance(mask_decoder_config, EdgeTamMaskDecoderConfig):
            mask_decoder_config = mask_decoder_config.to_dict()
        self.vision_config = vision_config
        self.prompt_encoder_config = EdgeTamPromptEncoderConfig(**prompt_encoder_config)
        self.mask_decoder_config = EdgeTamMaskDecoderConfig(**mask_decoder_config)
        self.initializer_range = initializer_range
__all__ = ["EdgeTamConfig", "EdgeTamVisionConfig", "EdgeTamPromptEncoderConfig", "EdgeTamMaskDecoderConfig"]