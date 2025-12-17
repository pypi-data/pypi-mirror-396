import importlib
import inspect
import json
import warnings
from collections import OrderedDict
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...feature_extraction_utils import FeatureExtractionMixin
from ...image_processing_utils import ImageProcessingMixin
from ...processing_utils import ProcessorMixin
from ...tokenization_utils import TOKENIZER_CONFIG_FILE
from ...utils import FEATURE_EXTRACTOR_NAME, PROCESSOR_NAME, VIDEO_PROCESSOR_NAME, cached_file, logging
from ...video_processing_utils import BaseVideoProcessor
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (
    CONFIG_MAPPING_NAMES,
    AutoConfig,
    model_type_to_module_name,
    replace_list_option_in_docstrings,
)
from .feature_extraction_auto import AutoFeatureExtractor
from .image_processing_auto import AutoImageProcessor
from .tokenization_auto import AutoTokenizer
logger = logging.get_logger(__name__)
PROCESSOR_MAPPING_NAMES = OrderedDict(
    [
        ("aimv2", "CLIPProcessor"),
        ("align", "AlignProcessor"),
        ("altclip", "AltCLIPProcessor"),
        ("aria", "AriaProcessor"),
        ("aya_vision", "AyaVisionProcessor"),
        ("bark", "BarkProcessor"),
        ("blip", "BlipProcessor"),
        ("blip-2", "Blip2Processor"),
        ("bridgetower", "BridgeTowerProcessor"),
        ("chameleon", "ChameleonProcessor"),
        ("chinese_clip", "ChineseCLIPProcessor"),
        ("clap", "ClapProcessor"),
        ("clip", "CLIPProcessor"),
        ("clipseg", "CLIPSegProcessor"),
        ("clvp", "ClvpProcessor"),
        ("cohere2_vision", "Cohere2VisionProcessor"),
        ("colpali", "ColPaliProcessor"),
        ("colqwen2", "ColQwen2Processor"),
        ("deepseek_vl", "DeepseekVLProcessor"),
        ("deepseek_vl_hybrid", "DeepseekVLHybridProcessor"),
        ("dia", "DiaProcessor"),
        ("edgetam", "Sam2Processor"),
        ("emu3", "Emu3Processor"),
        ("evolla", "EvollaProcessor"),
        ("flava", "FlavaProcessor"),
        ("florence2", "Florence2Processor"),
        ("fuyu", "FuyuProcessor"),
        ("gemma3", "Gemma3Processor"),
        ("gemma3n", "Gemma3nProcessor"),
        ("git", "GitProcessor"),
        ("glm4v", "Glm4vProcessor"),
        ("glm4v_moe", "Glm4vProcessor"),
        ("got_ocr2", "GotOcr2Processor"),
        ("granite_speech", "GraniteSpeechProcessor"),
        ("grounding-dino", "GroundingDinoProcessor"),
        ("groupvit", "CLIPProcessor"),
        ("hubert", "Wav2Vec2Processor"),
        ("idefics", "IdeficsProcessor"),
        ("idefics2", "Idefics2Processor"),
        ("idefics3", "Idefics3Processor"),
        ("instructblip", "InstructBlipProcessor"),
        ("instructblipvideo", "InstructBlipVideoProcessor"),
        ("internvl", "InternVLProcessor"),
        ("janus", "JanusProcessor"),
        ("kosmos-2", "Kosmos2Processor"),
        ("kosmos-2.5", "Kosmos2_5Processor"),
        ("kyutai_speech_to_text", "KyutaiSpeechToTextProcessor"),
        ("layoutlmv2", "LayoutLMv2Processor"),
        ("layoutlmv3", "LayoutLMv3Processor"),
        ("lfm2_vl", "Lfm2VlProcessor"),
        ("llama4", "Llama4Processor"),
        ("llava", "LlavaProcessor"),
        ("llava_next", "LlavaNextProcessor"),
        ("llava_next_video", "LlavaNextVideoProcessor"),
        ("llava_onevision", "LlavaOnevisionProcessor"),
        ("markuplm", "MarkupLMProcessor"),
        ("mctct", "MCTCTProcessor"),
        ("metaclip_2", "CLIPProcessor"),
        ("mgp-str", "MgpstrProcessor"),
        ("mistral3", "PixtralProcessor"),
        ("mllama", "MllamaProcessor"),
        ("mm-grounding-dino", "GroundingDinoProcessor"),
        ("moonshine", "Wav2Vec2Processor"),
        ("oneformer", "OneFormerProcessor"),
        ("ovis2", "Ovis2Processor"),
        ("owlv2", "Owlv2Processor"),
        ("owlvit", "OwlViTProcessor"),
        ("paligemma", "PaliGemmaProcessor"),
        ("perception_lm", "PerceptionLMProcessor"),
        ("phi4_multimodal", "Phi4MultimodalProcessor"),
        ("pix2struct", "Pix2StructProcessor"),
        ("pixtral", "PixtralProcessor"),
        ("pop2piano", "Pop2PianoProcessor"),
        ("qwen2_5_omni", "Qwen2_5OmniProcessor"),
        ("qwen2_5_vl", "Qwen2_5_VLProcessor"),
        ("qwen2_audio", "Qwen2AudioProcessor"),
        ("qwen2_vl", "Qwen2VLProcessor"),
        ("qwen3_omni_moe", "Qwen3OmniMoeProcessor"),
        ("qwen3_vl", "Qwen3VLProcessor"),
        ("qwen3_vl_moe", "Qwen3VLProcessor"),
        ("sam", "SamProcessor"),
        ("sam2", "Sam2Processor"),
        ("sam_hq", "SamHQProcessor"),
        ("seamless_m4t", "SeamlessM4TProcessor"),
        ("sew", "Wav2Vec2Processor"),
        ("sew-d", "Wav2Vec2Processor"),
        ("shieldgemma2", "ShieldGemma2Processor"),
        ("siglip", "SiglipProcessor"),
        ("siglip2", "Siglip2Processor"),
        ("smolvlm", "SmolVLMProcessor"),
        ("speech_to_text", "Speech2TextProcessor"),
        ("speech_to_text_2", "Speech2Text2Processor"),
        ("speecht5", "SpeechT5Processor"),
        ("trocr", "TrOCRProcessor"),
        ("tvlt", "TvltProcessor"),
        ("tvp", "TvpProcessor"),
        ("udop", "UdopProcessor"),
        ("unispeech", "Wav2Vec2Processor"),
        ("unispeech-sat", "Wav2Vec2Processor"),
        ("video_llava", "VideoLlavaProcessor"),
        ("vilt", "ViltProcessor"),
        ("vipllava", "LlavaProcessor"),
        ("vision-text-dual-encoder", "VisionTextDualEncoderProcessor"),
        ("voxtral", "VoxtralProcessor"),
        ("wav2vec2", "Wav2Vec2Processor"),
        ("wav2vec2-bert", "Wav2Vec2Processor"),
        ("wav2vec2-conformer", "Wav2Vec2Processor"),
        ("wavlm", "Wav2Vec2Processor"),
        ("whisper", "WhisperProcessor"),
        ("xclip", "XCLIPProcessor"),
    ]
)
PROCESSOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, PROCESSOR_MAPPING_NAMES)
def processor_class_from_name(class_name: str):
    for module_name, processors in PROCESSOR_MAPPING_NAMES.items():
        if class_name in processors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "MEROAI.models")
            try:
                return getattr(module, class_name)
            except AttributeError:
                continue
    for processor in PROCESSOR_MAPPING._extra_content.values():
        if getattr(processor, "__name__", None) == class_name:
            return processor
    main_module = importlib.import_module("MEROAI")
    if hasattr(main_module, class_name):
        return getattr(main_module, class_name)
    return None
class AutoProcessor:
    def __init__(self):
        raise OSError(
            "AutoProcessor is designed to be instantiated "
            "using the `AutoProcessor.from_pretrained(pretrained_model_name_or_path)` method."
        )
    @classmethod
    @replace_list_option_in_docstrings(PROCESSOR_MAPPING_NAMES)
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
        processor_class = None
        processor_auto_map = None
        cached_file_kwargs = {key: kwargs[key] for key in inspect.signature(cached_file).parameters if key in kwargs}
        cached_file_kwargs.update(
            {
                "_raise_exceptions_for_gated_repo": False,
                "_raise_exceptions_for_missing_entries": False,
                "_raise_exceptions_for_connection_errors": False,
            }
        )
        processor_config_file = cached_file(pretrained_model_name_or_path, PROCESSOR_NAME, **cached_file_kwargs)
        if processor_config_file is not None:
            config_dict, _ = ProcessorMixin.get_processor_dict(pretrained_model_name_or_path, **kwargs)
            processor_class = config_dict.get("processor_class", None)
            if "AutoProcessor" in config_dict.get("auto_map", {}):
                processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            preprocessor_config_file = cached_file(
                pretrained_model_name_or_path, FEATURE_EXTRACTOR_NAME, **cached_file_kwargs
            )
            if preprocessor_config_file is not None:
                config_dict, _ = ImageProcessingMixin.get_image_processor_dict(pretrained_model_name_or_path, **kwargs)
                processor_class = config_dict.get("processor_class", None)
                if "AutoProcessor" in config_dict.get("auto_map", {}):
                    processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
            if preprocessor_config_file is None:
                preprocessor_config_file = cached_file(
                    pretrained_model_name_or_path, VIDEO_PROCESSOR_NAME, **cached_file_kwargs
                )
                if preprocessor_config_file is not None:
                    config_dict, _ = BaseVideoProcessor.get_video_processor_dict(
                        pretrained_model_name_or_path, **kwargs
                    )
                    processor_class = config_dict.get("processor_class", None)
                    if "AutoProcessor" in config_dict.get("auto_map", {}):
                        processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
            if preprocessor_config_file is None:
                preprocessor_config_file = cached_file(
                    pretrained_model_name_or_path, FEATURE_EXTRACTOR_NAME, **cached_file_kwargs
                )
                if preprocessor_config_file is not None and processor_class is None:
                    config_dict, _ = FeatureExtractionMixin.get_feature_extractor_dict(
                        pretrained_model_name_or_path, **kwargs
                    )
                    processor_class = config_dict.get("processor_class", None)
                    if "AutoProcessor" in config_dict.get("auto_map", {}):
                        processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            tokenizer_config_file = cached_file(
                pretrained_model_name_or_path, TOKENIZER_CONFIG_FILE, **cached_file_kwargs
            )
            if tokenizer_config_file is not None:
                with open(tokenizer_config_file, encoding="utf-8") as reader:
                    config_dict = json.load(reader)
                processor_class = config_dict.get("processor_class", None)
                if "AutoProcessor" in config_dict.get("auto_map", {}):
                    processor_auto_map = config_dict["auto_map"]["AutoProcessor"]
        if processor_class is None:
            if not isinstance(config, PretrainedConfig):
                config = AutoConfig.from_pretrained(
                    pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
                )
            processor_class = getattr(config, "processor_class", None)
            if hasattr(config, "auto_map") and "AutoProcessor" in config.auto_map:
                processor_auto_map = config.auto_map["AutoProcessor"]
        if processor_class is not None:
            processor_class = processor_class_from_name(processor_class)
        has_remote_code = processor_auto_map is not None
        has_local_code = processor_class is not None or type(config) in PROCESSOR_MAPPING
        if has_remote_code:
            if "--" in processor_auto_map:
                upstream_repo = processor_auto_map.split("--")[0]
            else:
                upstream_repo = None
            trust_remote_code = resolve_trust_remote_code(
                trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code, upstream_repo
            )
        if has_remote_code and trust_remote_code:
            processor_class = get_class_from_dynamic_module(
                processor_auto_map, pretrained_model_name_or_path, **kwargs
            )
            _ = kwargs.pop("code_revision", None)
            processor_class.register_for_auto_class()
            return processor_class.from_pretrained(
                pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
            )
        elif processor_class is not None:
            return processor_class.from_pretrained(
                pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
            )
        elif type(config) in PROCESSOR_MAPPING:
            return PROCESSOR_MAPPING[type(config)].from_pretrained(pretrained_model_name_or_path, **kwargs)
        try:
            return AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
            )
        except Exception:
            try:
                return AutoImageProcessor.from_pretrained(
                    pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
                )
            except Exception:
                pass
            try:
                return AutoFeatureExtractor.from_pretrained(
                    pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
                )
            except Exception:
                pass
        raise ValueError(
            f"Unrecognized processing class in {pretrained_model_name_or_path}. Can't instantiate a processor, a "
            "tokenizer, an image processor or a feature extractor for this model. Make sure the repository contains "
            "the files of at least one of those processing classes."
        )
    @staticmethod
    def register(config_class, processor_class, exist_ok=False):
        PROCESSOR_MAPPING.register(config_class, processor_class, exist_ok=exist_ok)
__all__ = ["PROCESSOR_MAPPING", "AutoProcessor"]