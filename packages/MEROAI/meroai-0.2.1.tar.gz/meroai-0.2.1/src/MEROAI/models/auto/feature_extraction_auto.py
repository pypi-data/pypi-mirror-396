import importlib
import json
import os
import warnings
from collections import OrderedDict
from typing import Optional, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...feature_extraction_utils import FeatureExtractionMixin
from ...utils import CONFIG_NAME, FEATURE_EXTRACTOR_NAME, cached_file, logging
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (
    CONFIG_MAPPING_NAMES,
    AutoConfig,
    model_type_to_module_name,
    replace_list_option_in_docstrings,
)
logger = logging.get_logger(__name__)
FEATURE_EXTRACTOR_MAPPING_NAMES = OrderedDict(
    [
        ("audio-spectrogram-transformer", "ASTFeatureExtractor"),
        ("beit", "BeitFeatureExtractor"),
        ("chinese_clip", "ChineseCLIPFeatureExtractor"),
        ("clap", "ClapFeatureExtractor"),
        ("clip", "CLIPFeatureExtractor"),
        ("clipseg", "ViTFeatureExtractor"),
        ("clvp", "ClvpFeatureExtractor"),
        ("conditional_detr", "ConditionalDetrFeatureExtractor"),
        ("convnext", "ConvNextFeatureExtractor"),
        ("cvt", "ConvNextFeatureExtractor"),
        ("dac", "DacFeatureExtractor"),
        ("data2vec-audio", "Wav2Vec2FeatureExtractor"),
        ("data2vec-vision", "BeitFeatureExtractor"),
        ("deformable_detr", "DeformableDetrFeatureExtractor"),
        ("deit", "DeiTFeatureExtractor"),
        ("detr", "DetrFeatureExtractor"),
        ("dia", "DiaFeatureExtractor"),
        ("dinat", "ViTFeatureExtractor"),
        ("donut-swin", "DonutFeatureExtractor"),
        ("dpt", "DPTFeatureExtractor"),
        ("encodec", "EncodecFeatureExtractor"),
        ("flava", "FlavaFeatureExtractor"),
        ("gemma3n", "Gemma3nAudioFeatureExtractor"),
        ("glpn", "GLPNFeatureExtractor"),
        ("granite_speech", "GraniteSpeechFeatureExtractor"),
        ("groupvit", "CLIPFeatureExtractor"),
        ("hubert", "Wav2Vec2FeatureExtractor"),
        ("imagegpt", "ImageGPTFeatureExtractor"),
        ("kyutai_speech_to_text", "KyutaiSpeechToTextFeatureExtractor"),
        ("layoutlmv2", "LayoutLMv2FeatureExtractor"),
        ("layoutlmv3", "LayoutLMv3FeatureExtractor"),
        ("levit", "LevitFeatureExtractor"),
        ("maskformer", "MaskFormerFeatureExtractor"),
        ("mctct", "MCTCTFeatureExtractor"),
        ("mimi", "EncodecFeatureExtractor"),
        ("mobilenet_v1", "MobileNetV1FeatureExtractor"),
        ("mobilenet_v2", "MobileNetV2FeatureExtractor"),
        ("mobilevit", "MobileViTFeatureExtractor"),
        ("moonshine", "Wav2Vec2FeatureExtractor"),
        ("moshi", "EncodecFeatureExtractor"),
        ("nat", "ViTFeatureExtractor"),
        ("owlvit", "OwlViTFeatureExtractor"),
        ("parakeet_ctc", "ParakeetFeatureExtractor"),
        ("parakeet_encoder", "ParakeetFeatureExtractor"),
        ("perceiver", "PerceiverFeatureExtractor"),
        ("phi4_multimodal", "Phi4MultimodalFeatureExtractor"),
        ("poolformer", "PoolFormerFeatureExtractor"),
        ("pop2piano", "Pop2PianoFeatureExtractor"),
        ("regnet", "ConvNextFeatureExtractor"),
        ("resnet", "ConvNextFeatureExtractor"),
        ("seamless_m4t", "SeamlessM4TFeatureExtractor"),
        ("seamless_m4t_v2", "SeamlessM4TFeatureExtractor"),
        ("segformer", "SegformerFeatureExtractor"),
        ("sew", "Wav2Vec2FeatureExtractor"),
        ("sew-d", "Wav2Vec2FeatureExtractor"),
        ("speech_to_text", "Speech2TextFeatureExtractor"),
        ("speecht5", "SpeechT5FeatureExtractor"),
        ("swiftformer", "ViTFeatureExtractor"),
        ("swin", "ViTFeatureExtractor"),
        ("swinv2", "ViTFeatureExtractor"),
        ("table-transformer", "DetrFeatureExtractor"),
        ("timesformer", "VideoMAEFeatureExtractor"),
        ("tvlt", "TvltFeatureExtractor"),
        ("unispeech", "Wav2Vec2FeatureExtractor"),
        ("unispeech-sat", "Wav2Vec2FeatureExtractor"),
        ("univnet", "UnivNetFeatureExtractor"),
        ("van", "ConvNextFeatureExtractor"),
        ("videomae", "VideoMAEFeatureExtractor"),
        ("vilt", "ViltFeatureExtractor"),
        ("vit", "ViTFeatureExtractor"),
        ("vit_mae", "ViTFeatureExtractor"),
        ("vit_msn", "ViTFeatureExtractor"),
        ("wav2vec2", "Wav2Vec2FeatureExtractor"),
        ("wav2vec2-bert", "Wav2Vec2FeatureExtractor"),
        ("wav2vec2-conformer", "Wav2Vec2FeatureExtractor"),
        ("wavlm", "Wav2Vec2FeatureExtractor"),
        ("whisper", "WhisperFeatureExtractor"),
        ("xclip", "CLIPFeatureExtractor"),
        ("xcodec", "DacFeatureExtractor"),
        ("yolos", "YolosFeatureExtractor"),
    ]
)
FEATURE_EXTRACTOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, FEATURE_EXTRACTOR_MAPPING_NAMES)
def feature_extractor_class_from_name(class_name: str):
    for module_name, extractors in FEATURE_EXTRACTOR_MAPPING_NAMES.items():
        if class_name in extractors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "MEROAI.models")
            try:
                return getattr(module, class_name)
            except AttributeError:
                continue
    for extractor in FEATURE_EXTRACTOR_MAPPING._extra_content.values():
        if getattr(extractor, "__name__", None) == class_name:
            return extractor
    main_module = importlib.import_module("MEROAI")
    if hasattr(main_module, class_name):
        return getattr(main_module, class_name)
    return None
def get_feature_extractor_config(
    pretrained_model_name_or_path: Union[str, os.PathLike],
    cache_dir: Optional[Union[str, os.PathLike]] = None,
    force_download: bool = False,
    resume_download: Optional[bool] = None,
    proxies: Optional[dict[str, str]] = None,
    token: Optional[Union[bool, str]] = None,
    revision: Optional[str] = None,
    local_files_only: bool = False,
    **kwargs,
):
    use_auth_token = kwargs.pop("use_auth_token", None)
    if use_auth_token is not None:
        warnings.warn(
            "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
            FutureWarning,
        )
        if token is not None:
            raise ValueError("`token` and `use_auth_token` are both specified. Please set only the argument `token`.")
        token = use_auth_token
    resolved_config_file = cached_file(
        pretrained_model_name_or_path,
        FEATURE_EXTRACTOR_NAME,
        cache_dir=cache_dir,
        force_download=force_download,
        resume_download=resume_download,
        proxies=proxies,
        token=token,
        revision=revision,
        local_files_only=local_files_only,
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _raise_exceptions_for_connection_errors=False,
    )
    if resolved_config_file is None:
        logger.info(
            "Could not locate the feature extractor configuration file, will try to use the model config instead."
        )
        return {}
    with open(resolved_config_file, encoding="utf-8") as reader:
        return json.load(reader)
class AutoFeatureExtractor:
    def __init__(self):
        raise OSError(
            "AutoFeatureExtractor is designed to be instantiated "
            "using the `AutoFeatureExtractor.from_pretrained(pretrained_model_name_or_path)` method."
        )
    @classmethod
    @replace_list_option_in_docstrings(FEATURE_EXTRACTOR_MAPPING_NAMES)
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if kwargs.get("token") is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            kwargs["token"] = use_auth_token
        config = kwargs.pop("config", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        config_dict, _ = FeatureExtractionMixin.get_feature_extractor_dict(pretrained_model_name_or_path, **kwargs)
        feature_extractor_class = config_dict.get("feature_extractor_type", None)
        feature_extractor_auto_map = None
        if "AutoFeatureExtractor" in config_dict.get("auto_map", {}):
            feature_extractor_auto_map = config_dict["auto_map"]["AutoFeatureExtractor"]
        if feature_extractor_class is None and feature_extractor_auto_map is None:
            if not isinstance(config, PretrainedConfig):
                config = AutoConfig.from_pretrained(
                    pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
                )
            feature_extractor_class = getattr(config, "feature_extractor_type", None)
            if hasattr(config, "auto_map") and "AutoFeatureExtractor" in config.auto_map:
                feature_extractor_auto_map = config.auto_map["AutoFeatureExtractor"]
        if feature_extractor_class is not None:
            feature_extractor_class = feature_extractor_class_from_name(feature_extractor_class)
        has_remote_code = feature_extractor_auto_map is not None
        has_local_code = feature_extractor_class is not None or type(config) in FEATURE_EXTRACTOR_MAPPING
        if has_remote_code:
            if "--" in feature_extractor_auto_map:
                upstream_repo = feature_extractor_auto_map.split("--")[0]
            else:
                upstream_repo = None
            trust_remote_code = resolve_trust_remote_code(
                trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code, upstream_repo
            )
        if has_remote_code and trust_remote_code:
            feature_extractor_class = get_class_from_dynamic_module(
                feature_extractor_auto_map, pretrained_model_name_or_path, **kwargs
            )
            _ = kwargs.pop("code_revision", None)
            feature_extractor_class.register_for_auto_class()
            return feature_extractor_class.from_dict(config_dict, **kwargs)
        elif feature_extractor_class is not None:
            return feature_extractor_class.from_dict(config_dict, **kwargs)
        elif type(config) in FEATURE_EXTRACTOR_MAPPING:
            feature_extractor_class = FEATURE_EXTRACTOR_MAPPING[type(config)]
            return feature_extractor_class.from_dict(config_dict, **kwargs)
        raise ValueError(
            f"Unrecognized feature extractor in {pretrained_model_name_or_path}. Should have a "
            f"`feature_extractor_type` key in its {FEATURE_EXTRACTOR_NAME} of {CONFIG_NAME}, or one of the following "
            f"`model_type` keys in its {CONFIG_NAME}: {', '.join(c for c in FEATURE_EXTRACTOR_MAPPING_NAMES)}"
        )
    @staticmethod
    def register(config_class, feature_extractor_class, exist_ok=False):
        FEATURE_EXTRACTOR_MAPPING.register(config_class, feature_extractor_class, exist_ok=exist_ok)
__all__ = ["FEATURE_EXTRACTOR_MAPPING", "AutoFeatureExtractor"]