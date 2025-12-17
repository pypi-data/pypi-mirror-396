import importlib
import json
import os
import warnings
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...image_processing_utils import ImageProcessingMixin
from ...image_processing_utils_fast import BaseImageProcessorFast
from ...utils import (
    CONFIG_NAME,
    IMAGE_PROCESSOR_NAME,
    cached_file,
    is_timm_config_dict,
    is_timm_local_checkpoint,
    is_torchvision_available,
    is_vision_available,
    logging,
)
from ...utils.import_utils import requires
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (
    CONFIG_MAPPING_NAMES,
    AutoConfig,
    model_type_to_module_name,
    replace_list_option_in_docstrings,
)
logger = logging.get_logger(__name__)
FORCE_FAST_IMAGE_PROCESSOR = ["Qwen2VLImageProcessor"]
if TYPE_CHECKING:
    IMAGE_PROCESSOR_MAPPING_NAMES: OrderedDict[str, tuple[Optional[str], Optional[str]]] = OrderedDict()
else:
    IMAGE_PROCESSOR_MAPPING_NAMES = OrderedDict(
        [
            ("aimv2", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("aimv2_vision_model", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("align", ("EfficientNetImageProcessor", "EfficientNetImageProcessorFast")),
            ("aria", ("AriaImageProcessor", None)),
            ("beit", ("BeitImageProcessor", "BeitImageProcessorFast")),
            ("bit", ("BitImageProcessor", "BitImageProcessorFast")),
            ("blip", ("BlipImageProcessor", "BlipImageProcessorFast")),
            ("blip-2", ("BlipImageProcessor", "BlipImageProcessorFast")),
            ("bridgetower", ("BridgeTowerImageProcessor", "BridgeTowerImageProcessorFast")),
            ("chameleon", ("ChameleonImageProcessor", "ChameleonImageProcessorFast")),
            ("chinese_clip", ("ChineseCLIPImageProcessor", "ChineseCLIPImageProcessorFast")),
            ("clip", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("clipseg", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("cohere2_vision", (None, "Cohere2VisionImageProcessorFast")),
            ("conditional_detr", ("ConditionalDetrImageProcessor", "ConditionalDetrImageProcessorFast")),
            ("convnext", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("convnextv2", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("cvt", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("data2vec-vision", ("BeitImageProcessor", "BeitImageProcessorFast")),
            ("deepseek_vl", ("DeepseekVLImageProcessor", "DeepseekVLImageProcessorFast")),
            ("deepseek_vl_hybrid", ("DeepseekVLHybridImageProcessor", "DeepseekVLHybridImageProcessorFast")),
            ("deformable_detr", ("DeformableDetrImageProcessor", "DeformableDetrImageProcessorFast")),
            ("deit", ("DeiTImageProcessor", "DeiTImageProcessorFast")),
            ("depth_anything", ("DPTImageProcessor", "DPTImageProcessorFast")),
            ("depth_pro", ("DepthProImageProcessor", "DepthProImageProcessorFast")),
            ("deta", ("DetaImageProcessor", None)),
            ("detr", ("DetrImageProcessor", "DetrImageProcessorFast")),
            ("dinat", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("dinov2", ("BitImageProcessor", "BitImageProcessorFast")),
            ("dinov3_vit", (None, "DINOv3ViTImageProcessorFast")),
            ("donut-swin", ("DonutImageProcessor", "DonutImageProcessorFast")),
            ("dpt", ("DPTImageProcessor", "DPTImageProcessorFast")),
            ("edgetam", (None, "Sam2ImageProcessorFast")),
            ("efficientformer", ("EfficientFormerImageProcessor", None)),
            ("efficientloftr", ("EfficientLoFTRImageProcessor", "EfficientLoFTRImageProcessorFast")),
            ("efficientnet", ("EfficientNetImageProcessor", "EfficientNetImageProcessorFast")),
            ("eomt", ("EomtImageProcessor", "EomtImageProcessorFast")),
            ("flava", ("FlavaImageProcessor", "FlavaImageProcessorFast")),
            ("focalnet", ("BitImageProcessor", "BitImageProcessorFast")),
            ("fuyu", ("FuyuImageProcessor", None)),
            ("gemma3", ("Gemma3ImageProcessor", "Gemma3ImageProcessorFast")),
            ("gemma3n", ("SiglipImageProcessor", "SiglipImageProcessorFast")),
            ("git", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("glm4v", ("Glm4vImageProcessor", "Glm4vImageProcessorFast")),
            ("glpn", ("GLPNImageProcessor", None)),
            ("got_ocr2", ("GotOcr2ImageProcessor", "GotOcr2ImageProcessorFast")),
            ("grounding-dino", ("GroundingDinoImageProcessor", "GroundingDinoImageProcessorFast")),
            ("groupvit", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("hiera", ("BitImageProcessor", "BitImageProcessorFast")),
            ("idefics", ("IdeficsImageProcessor", None)),
            ("idefics2", ("Idefics2ImageProcessor", "Idefics2ImageProcessorFast")),
            ("idefics3", ("Idefics3ImageProcessor", "Idefics3ImageProcessorFast")),
            ("ijepa", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("imagegpt", ("ImageGPTImageProcessor", "ImageGPTImageProcessorFast")),
            ("instructblip", ("BlipImageProcessor", "BlipImageProcessorFast")),
            ("instructblipvideo", ("InstructBlipVideoImageProcessor", None)),
            ("janus", ("JanusImageProcessor", "JanusImageProcessorFast")),
            ("kosmos-2", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("kosmos-2.5", ("Kosmos2_5ImageProcessor", "Kosmos2_5ImageProcessorFast")),
            ("layoutlmv2", ("LayoutLMv2ImageProcessor", "LayoutLMv2ImageProcessorFast")),
            ("layoutlmv3", ("LayoutLMv3ImageProcessor", "LayoutLMv3ImageProcessorFast")),
            ("levit", ("LevitImageProcessor", "LevitImageProcessorFast")),
            ("lfm2_vl", (None, "Lfm2VlImageProcessorFast")),
            ("lightglue", ("LightGlueImageProcessor", None)),
            ("llama4", ("Llama4ImageProcessor", "Llama4ImageProcessorFast")),
            ("llava", ("LlavaImageProcessor", "LlavaImageProcessorFast")),
            ("llava_next", ("LlavaNextImageProcessor", "LlavaNextImageProcessorFast")),
            ("llava_next_video", ("LlavaNextVideoImageProcessor", None)),
            ("llava_onevision", ("LlavaOnevisionImageProcessor", "LlavaOnevisionImageProcessorFast")),
            ("mask2former", ("Mask2FormerImageProcessor", "Mask2FormerImageProcessorFast")),
            ("maskformer", ("MaskFormerImageProcessor", "MaskFormerImageProcessorFast")),
            ("metaclip_2", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("mgp-str", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("mistral3", ("PixtralImageProcessor", "PixtralImageProcessorFast")),
            ("mlcd", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("mllama", ("MllamaImageProcessor", None)),
            ("mm-grounding-dino", ("GroundingDinoImageProcessor", "GroundingDinoImageProcessorFast")),
            ("mobilenet_v1", ("MobileNetV1ImageProcessor", "MobileNetV1ImageProcessorFast")),
            ("mobilenet_v2", ("MobileNetV2ImageProcessor", "MobileNetV2ImageProcessorFast")),
            ("mobilevit", ("MobileViTImageProcessor", "MobileViTImageProcessorFast")),
            ("mobilevitv2", ("MobileViTImageProcessor", "MobileViTImageProcessorFast")),
            ("nat", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("nougat", ("NougatImageProcessor", "NougatImageProcessorFast")),
            ("oneformer", ("OneFormerImageProcessor", "OneFormerImageProcessorFast")),
            ("ovis2", ("Ovis2ImageProcessor", "Ovis2ImageProcessorFast")),
            ("owlv2", ("Owlv2ImageProcessor", "Owlv2ImageProcessorFast")),
            ("owlvit", ("OwlViTImageProcessor", "OwlViTImageProcessorFast")),
            ("paligemma", ("SiglipImageProcessor", "SiglipImageProcessorFast")),
            ("perceiver", ("PerceiverImageProcessor", "PerceiverImageProcessorFast")),
            ("perception_lm", (None, "PerceptionLMImageProcessorFast")),
            ("phi4_multimodal", (None, "Phi4MultimodalImageProcessorFast")),
            ("pix2struct", ("Pix2StructImageProcessor", None)),
            ("pixtral", ("PixtralImageProcessor", "PixtralImageProcessorFast")),
            ("poolformer", ("PoolFormerImageProcessor", "PoolFormerImageProcessorFast")),
            ("prompt_depth_anything", ("PromptDepthAnythingImageProcessor", "PromptDepthAnythingImageProcessorFast")),
            ("pvt", ("PvtImageProcessor", "PvtImageProcessorFast")),
            ("pvt_v2", ("PvtImageProcessor", "PvtImageProcessorFast")),
            ("qwen2_5_vl", ("Qwen2VLImageProcessor", "Qwen2VLImageProcessorFast")),
            ("qwen2_vl", ("Qwen2VLImageProcessor", "Qwen2VLImageProcessorFast")),
            ("qwen3_vl", ("Qwen2VLImageProcessor", "Qwen2VLImageProcessorFast")),
            ("regnet", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("resnet", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("rt_detr", ("RTDetrImageProcessor", "RTDetrImageProcessorFast")),
            ("sam", ("SamImageProcessor", "SamImageProcessorFast")),
            ("sam2", (None, "Sam2ImageProcessorFast")),
            ("sam_hq", ("SamImageProcessor", "SamImageProcessorFast")),
            ("segformer", ("SegformerImageProcessor", "SegformerImageProcessorFast")),
            ("seggpt", ("SegGptImageProcessor", None)),
            ("shieldgemma2", ("Gemma3ImageProcessor", "Gemma3ImageProcessorFast")),
            ("siglip", ("SiglipImageProcessor", "SiglipImageProcessorFast")),
            ("siglip2", ("Siglip2ImageProcessor", "Siglip2ImageProcessorFast")),
            ("smolvlm", ("SmolVLMImageProcessor", "SmolVLMImageProcessorFast")),
            ("superglue", ("SuperGlueImageProcessor", None)),
            ("superpoint", ("SuperPointImageProcessor", "SuperPointImageProcessorFast")),
            ("swiftformer", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("swin", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("swin2sr", ("Swin2SRImageProcessor", "Swin2SRImageProcessorFast")),
            ("swinv2", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("table-transformer", ("DetrImageProcessor", "DetrImageProcessorFast")),
            ("textnet", ("TextNetImageProcessor", "TextNetImageProcessorFast")),
            ("timesformer", ("VideoMAEImageProcessor", None)),
            ("timm_wrapper", ("TimmWrapperImageProcessor", None)),
            ("tvlt", ("TvltImageProcessor", None)),
            ("tvp", ("TvpImageProcessor", "TvpImageProcessorFast")),
            ("udop", ("LayoutLMv3ImageProcessor", "LayoutLMv3ImageProcessorFast")),
            ("upernet", ("SegformerImageProcessor", "SegformerImageProcessorFast")),
            ("van", ("ConvNextImageProcessor", "ConvNextImageProcessorFast")),
            ("videomae", ("VideoMAEImageProcessor", None)),
            ("vilt", ("ViltImageProcessor", "ViltImageProcessorFast")),
            ("vipllava", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("vit", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("vit_hybrid", ("ViTHybridImageProcessor", None)),
            ("vit_mae", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("vit_msn", ("ViTImageProcessor", "ViTImageProcessorFast")),
            ("vitmatte", ("VitMatteImageProcessor", "VitMatteImageProcessorFast")),
            ("xclip", ("CLIPImageProcessor", "CLIPImageProcessorFast")),
            ("yolos", ("YolosImageProcessor", "YolosImageProcessorFast")),
            ("zoedepth", ("ZoeDepthImageProcessor", "ZoeDepthImageProcessorFast")),
        ]
    )
for model_type, (slow_class, fast_class) in IMAGE_PROCESSOR_MAPPING_NAMES.items():
    if not is_vision_available():
        slow_class = None
    if not is_torchvision_available():
        fast_class = None
    IMAGE_PROCESSOR_MAPPING_NAMES[model_type] = (slow_class, fast_class)
IMAGE_PROCESSOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, IMAGE_PROCESSOR_MAPPING_NAMES)
def get_image_processor_class_from_name(class_name: str):
    if class_name == "BaseImageProcessorFast":
        return BaseImageProcessorFast
    for module_name, extractors in IMAGE_PROCESSOR_MAPPING_NAMES.items():
        if class_name in extractors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "MEROAI.models")
            try:
                return getattr(module, class_name)
            except AttributeError:
                continue
    for extractors in IMAGE_PROCESSOR_MAPPING._extra_content.values():
        for extractor in extractors:
            if getattr(extractor, "__name__", None) == class_name:
                return extractor
    main_module = importlib.import_module("MEROAI")
    if hasattr(main_module, class_name):
        return getattr(main_module, class_name)
    return None
def get_image_processor_config(
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
        IMAGE_PROCESSOR_NAME,
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
            "Could not locate the image processor configuration file, will try to use the model config instead."
        )
        return {}
    with open(resolved_config_file, encoding="utf-8") as reader:
        return json.load(reader)
def _warning_fast_image_processor_available(fast_class):
    logger.warning(
        f"Fast image processor class {fast_class} is available for this model. "
        "Using slow image processor class. To use the fast image processor class set `use_fast=True`."
    )
@requires(backends=("vision",))
class AutoImageProcessor:
    def __init__(self):
        raise OSError(
            "AutoImageProcessor is designed to be instantiated "
            "using the `AutoImageProcessor.from_pretrained(pretrained_model_name_or_path)` method."
        )
    @classmethod
    @replace_list_option_in_docstrings(IMAGE_PROCESSOR_MAPPING_NAMES)
    def from_pretrained(cls, pretrained_model_name_or_path, *inputs, **kwargs):
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
        use_fast = kwargs.pop("use_fast", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        if "image_processor_filename" in kwargs:
            image_processor_filename = kwargs.pop("image_processor_filename")
        elif is_timm_local_checkpoint(pretrained_model_name_or_path):
            image_processor_filename = CONFIG_NAME
        else:
            image_processor_filename = IMAGE_PROCESSOR_NAME
        try:
            config_dict, _ = ImageProcessingMixin.get_image_processor_dict(
                pretrained_model_name_or_path, image_processor_filename=image_processor_filename, **kwargs
            )
        except Exception as initial_exception:
            try:
                config_dict, _ = ImageProcessingMixin.get_image_processor_dict(
                    pretrained_model_name_or_path, image_processor_filename=CONFIG_NAME, **kwargs
                )
            except Exception:
                raise initial_exception
            if not is_timm_config_dict(config_dict):
                raise initial_exception
        image_processor_type = config_dict.get("image_processor_type", None)
        image_processor_auto_map = None
        if "AutoImageProcessor" in config_dict.get("auto_map", {}):
            image_processor_auto_map = config_dict["auto_map"]["AutoImageProcessor"]
        if image_processor_type is None and image_processor_auto_map is None:
            feature_extractor_class = config_dict.pop("feature_extractor_type", None)
            if feature_extractor_class is not None:
                image_processor_type = feature_extractor_class.replace("FeatureExtractor", "ImageProcessor")
            if "AutoFeatureExtractor" in config_dict.get("auto_map", {}):
                feature_extractor_auto_map = config_dict["auto_map"]["AutoFeatureExtractor"]
                image_processor_auto_map = feature_extractor_auto_map.replace("FeatureExtractor", "ImageProcessor")
        if image_processor_type is None and image_processor_auto_map is None:
            if not isinstance(config, PretrainedConfig):
                config = AutoConfig.from_pretrained(
                    pretrained_model_name_or_path,
                    trust_remote_code=trust_remote_code,
                    **kwargs,
                )
            image_processor_type = getattr(config, "image_processor_type", None)
            if hasattr(config, "auto_map") and "AutoImageProcessor" in config.auto_map:
                image_processor_auto_map = config.auto_map["AutoImageProcessor"]
        image_processor_class = None
        if image_processor_type is not None:
            if use_fast is None:
                use_fast = image_processor_type.endswith("Fast")
                if not use_fast and image_processor_type in FORCE_FAST_IMAGE_PROCESSOR and is_torchvision_available():
                    use_fast = True
                    logger.warning_once(
                        f"The image processor of type `{image_processor_type}` is now loaded as a fast processor by default, even if the model checkpoint was saved with a slow processor. "
                        "This is a breaking change and may produce slightly different outputs. To continue using the slow processor, instantiate this class with `use_fast=False`. "
                        "Note that this behavior will be extended to all models in a future release."
                    )
                if not use_fast:
                    logger.warning_once(
                        "Using a slow image processor as `use_fast` is unset and a slow processor was saved with this model. "
                        "`use_fast=True` will be the default behavior in v4.52, even if the model was saved with a slow processor. "
                        "This will result in minor differences in outputs. You'll still be able to use a slow processor with `use_fast=False`."
                    )
            if use_fast and not image_processor_type.endswith("Fast"):
                image_processor_type += "Fast"
            if use_fast and not is_torchvision_available():
                image_processor_class = get_image_processor_class_from_name(image_processor_type[:-4])
                if image_processor_class is None:
                    raise ValueError(
                        f"`{image_processor_type}` requires `torchvision` to be installed. Please install `torchvision` and try again."
                    )
                logger.warning_once(
                    "Using `use_fast=True` but `torchvision` is not available. Falling back to the slow image processor."
                )
                use_fast = False
            if use_fast:
                for image_processors in IMAGE_PROCESSOR_MAPPING_NAMES.values():
                    if image_processor_type in image_processors:
                        break
                else:
                    image_processor_type = image_processor_type[:-4]
                    use_fast = False
                    logger.warning_once(
                        "`use_fast` is set to `True` but the image processor class does not have a fast version. "
                        " Falling back to the slow version."
                    )
                image_processor_class = get_image_processor_class_from_name(image_processor_type)
            else:
                image_processor_type_slow = image_processor_type.removesuffix("Fast")
                image_processor_class = get_image_processor_class_from_name(image_processor_type_slow)
                if image_processor_class is None and image_processor_type.endswith("Fast"):
                    raise ValueError(
                        f"`{image_processor_type}` does not have a slow version. Please set `use_fast=True` when instantiating the processor."
                    )
        has_remote_code = image_processor_auto_map is not None
        has_local_code = image_processor_class is not None or type(config) in IMAGE_PROCESSOR_MAPPING
        if has_remote_code:
            if image_processor_auto_map is not None and not isinstance(image_processor_auto_map, tuple):
                image_processor_auto_map = (image_processor_auto_map, None)
            if use_fast and image_processor_auto_map[1] is not None:
                class_ref = image_processor_auto_map[1]
            else:
                class_ref = image_processor_auto_map[0]
            if "--" in class_ref:
                upstream_repo = class_ref.split("--")[0]
            else:
                upstream_repo = None
            trust_remote_code = resolve_trust_remote_code(
                trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code, upstream_repo
            )
        if has_remote_code and trust_remote_code:
            if not use_fast and image_processor_auto_map[1] is not None:
                _warning_fast_image_processor_available(image_processor_auto_map[1])
            image_processor_class = get_class_from_dynamic_module(class_ref, pretrained_model_name_or_path, **kwargs)
            _ = kwargs.pop("code_revision", None)
            image_processor_class.register_for_auto_class()
            return image_processor_class.from_dict(config_dict, **kwargs)
        elif image_processor_class is not None:
            return image_processor_class.from_dict(config_dict, **kwargs)
        elif type(config) in IMAGE_PROCESSOR_MAPPING:
            image_processor_tuple = IMAGE_PROCESSOR_MAPPING[type(config)]
            image_processor_class_py, image_processor_class_fast = image_processor_tuple
            if not use_fast and image_processor_class_fast is not None:
                _warning_fast_image_processor_available(image_processor_class_fast)
            if image_processor_class_fast and (use_fast or image_processor_class_py is None):
                return image_processor_class_fast.from_pretrained(pretrained_model_name_or_path, *inputs, **kwargs)
            else:
                if image_processor_class_py is not None:
                    return image_processor_class_py.from_pretrained(pretrained_model_name_or_path, *inputs, **kwargs)
                else:
                    raise ValueError(
                        "This image processor cannot be instantiated. Please make sure you have `Pillow` installed."
                    )
        raise ValueError(
            f"Unrecognized image processor in {pretrained_model_name_or_path}. Should have a "
            f"`image_processor_type` key in its {IMAGE_PROCESSOR_NAME} of {CONFIG_NAME}, or one of the following "
            f"`model_type` keys in its {CONFIG_NAME}: {', '.join(c for c in IMAGE_PROCESSOR_MAPPING_NAMES)}"
        )
    @staticmethod
    def register(
        config_class,
        image_processor_class=None,
        slow_image_processor_class=None,
        fast_image_processor_class=None,
        exist_ok=False,
    ):
        if image_processor_class is not None:
            if slow_image_processor_class is not None:
                raise ValueError("Cannot specify both image_processor_class and slow_image_processor_class")
            warnings.warn(
                "The image_processor_class argument is deprecated and will be removed in v4.42. Please use `slow_image_processor_class`, or `fast_image_processor_class` instead",
                FutureWarning,
            )
            slow_image_processor_class = image_processor_class
        if slow_image_processor_class is None and fast_image_processor_class is None:
            raise ValueError("You need to specify either slow_image_processor_class or fast_image_processor_class")
        if slow_image_processor_class is not None and issubclass(slow_image_processor_class, BaseImageProcessorFast):
            raise ValueError("You passed a fast image processor in as the `slow_image_processor_class`.")
        if fast_image_processor_class is not None and not issubclass(
            fast_image_processor_class, BaseImageProcessorFast
        ):
            raise ValueError("The `fast_image_processor_class` should inherit from `BaseImageProcessorFast`.")
        if (
            slow_image_processor_class is not None
            and fast_image_processor_class is not None
            and issubclass(fast_image_processor_class, BaseImageProcessorFast)
            and fast_image_processor_class.slow_image_processor_class != slow_image_processor_class
        ):
            raise ValueError(
                "The fast processor class you are passing has a `slow_image_processor_class` attribute that is not "
                "consistent with the slow processor class you passed (fast tokenizer has "
                f"{fast_image_processor_class.slow_image_processor_class} and you passed {slow_image_processor_class}. Fix one of those "
                "so they match!"
            )
        if config_class in IMAGE_PROCESSOR_MAPPING._extra_content:
            existing_slow, existing_fast = IMAGE_PROCESSOR_MAPPING[config_class]
            if slow_image_processor_class is None:
                slow_image_processor_class = existing_slow
            if fast_image_processor_class is None:
                fast_image_processor_class = existing_fast
        IMAGE_PROCESSOR_MAPPING.register(
            config_class, (slow_image_processor_class, fast_image_processor_class), exist_ok=exist_ok
        )
__all__ = ["IMAGE_PROCESSOR_MAPPING", "AutoImageProcessor"]