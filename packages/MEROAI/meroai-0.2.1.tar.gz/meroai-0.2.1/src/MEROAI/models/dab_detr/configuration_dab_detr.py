from ...configuration_utils import PretrainedConfig
from ...utils import logging
from ...utils.backbone_utils import verify_backbone_config_arguments
from ..auto import CONFIG_MAPPING
logger = logging.get_logger(__name__)
class DabDetrConfig(PretrainedConfig):
    model_type = "dab-detr"
    keys_to_ignore_at_inference = ["past_key_values"]
    attribute_map = {
        "num_attention_heads": "encoder_attention_heads",
    }
    def __init__(
        self,
        use_timm_backbone=True,
        backbone_config=None,
        backbone="resnet50",
        use_pretrained_backbone=True,
        backbone_kwargs=None,
        num_queries=300,
        encoder_layers=6,
        encoder_ffn_dim=2048,
        encoder_attention_heads=8,
        decoder_layers=6,
        decoder_ffn_dim=2048,
        decoder_attention_heads=8,
        is_encoder_decoder=True,
        activation_function="prelu",
        hidden_size=256,
        dropout=0.1,
        attention_dropout=0.0,
        activation_dropout=0.0,
        init_std=0.02,
        init_xavier_std=1.0,
        auxiliary_loss=False,
        dilation=False,
        class_cost=2,
        bbox_cost=5,
        giou_cost=2,
        cls_loss_coefficient=2,
        bbox_loss_coefficient=5,
        giou_loss_coefficient=2,
        focal_alpha=0.25,
        temperature_height=20,
        temperature_width=20,
        query_dim=4,
        random_refpoints_xy=False,
        keep_query_pos=False,
        num_patterns=0,
        normalize_before=False,
        sine_position_embedding_scale=None,
        initializer_bias_prior_prob=None,
        **kwargs,
    ):
        if query_dim != 4:
            raise ValueError("The query dimensions has to be 4.")
        if use_timm_backbone and backbone_kwargs is None:
            backbone_kwargs = {}
            if dilation:
                backbone_kwargs["output_stride"] = 16
            backbone_kwargs["out_indices"] = [1, 2, 3, 4]
            backbone_kwargs["in_chans"] = 3
        elif not use_timm_backbone and backbone in (None, "resnet50"):
            if backbone_config is None:
                logger.info("`backbone_config` is `None`. Initializing the config with the default `ResNet` backbone.")
                backbone_config = CONFIG_MAPPING["resnet"](out_features=["stage4"])
            elif isinstance(backbone_config, dict):
                backbone_model_type = backbone_config.get("model_type")
                config_class = CONFIG_MAPPING[backbone_model_type]
                backbone_config = config_class.from_dict(backbone_config)
            backbone = None
            dilation = None
        verify_backbone_config_arguments(
            use_timm_backbone=use_timm_backbone,
            use_pretrained_backbone=use_pretrained_backbone,
            backbone=backbone,
            backbone_config=backbone_config,
            backbone_kwargs=backbone_kwargs,
        )
        self.use_timm_backbone = use_timm_backbone
        self.backbone_config = backbone_config
        self.num_queries = num_queries
        self.hidden_size = hidden_size
        self.encoder_ffn_dim = encoder_ffn_dim
        self.encoder_layers = encoder_layers
        self.encoder_attention_heads = encoder_attention_heads
        self.decoder_ffn_dim = decoder_ffn_dim
        self.decoder_layers = decoder_layers
        self.decoder_attention_heads = decoder_attention_heads
        self.dropout = dropout
        self.attention_dropout = attention_dropout
        self.activation_dropout = activation_dropout
        self.activation_function = activation_function
        self.init_std = init_std
        self.init_xavier_std = init_xavier_std
        self.num_hidden_layers = encoder_layers
        self.auxiliary_loss = auxiliary_loss
        self.backbone = backbone
        self.use_pretrained_backbone = use_pretrained_backbone
        self.backbone_kwargs = backbone_kwargs
        self.class_cost = class_cost
        self.bbox_cost = bbox_cost
        self.giou_cost = giou_cost
        self.cls_loss_coefficient = cls_loss_coefficient
        self.bbox_loss_coefficient = bbox_loss_coefficient
        self.giou_loss_coefficient = giou_loss_coefficient
        self.focal_alpha = focal_alpha
        self.query_dim = query_dim
        self.random_refpoints_xy = random_refpoints_xy
        self.keep_query_pos = keep_query_pos
        self.num_patterns = num_patterns
        self.normalize_before = normalize_before
        self.temperature_width = temperature_width
        self.temperature_height = temperature_height
        self.sine_position_embedding_scale = sine_position_embedding_scale
        self.initializer_bias_prior_prob = initializer_bias_prior_prob
        super().__init__(is_encoder_decoder=is_encoder_decoder, **kwargs)
    @property
    def sub_configs(self):
        return (
            {"backbone_config": type(self.backbone_config)}
            if getattr(self, "backbone_config", None) is not None
            else {}
        )
__all__ = ["DabDetrConfig"]