import importlib
import json
import os
import warnings
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...utils import CONFIG_NAME, VIDEO_PROCESSOR_NAME, cached_file, is_torchvision_available, logging
from ...utils.import_utils import requires
from ...video_processing_utils import BaseVideoProcessor
from .auto_factory import _LazyAutoMapping
from .configuration_auto import (
    CONFIG_MAPPING_NAMES,
    AutoConfig,
    model_type_to_module_name,
    replace_list_option_in_docstrings,
)
logger = logging.get_logger(__name__)
if TYPE_CHECKING:
    VIDEO_PROCESSOR_MAPPING_NAMES: OrderedDict[str, tuple[Optional[str], Optional[str]]] = OrderedDict()
else:
    VIDEO_PROCESSOR_MAPPING_NAMES = OrderedDict(
        [
            ("glm4v", "Glm4vVideoProcessor"),
            ("instructblip", "InstructBlipVideoVideoProcessor"),
            ("instructblipvideo", "InstructBlipVideoVideoProcessor"),
            ("internvl", "InternVLVideoProcessor"),
            ("llava_next_video", "LlavaNextVideoVideoProcessor"),
            ("llava_onevision", "LlavaOnevisionVideoProcessor"),
            ("perception_lm", "PerceptionLMVideoProcessor"),
            ("qwen2_5_omni", "Qwen2VLVideoProcessor"),
            ("qwen2_5_vl", "Qwen2VLVideoProcessor"),
            ("qwen2_vl", "Qwen2VLVideoProcessor"),
            ("qwen3_omni_moe", "Qwen2VLVideoProcessor"),
            ("qwen3_vl", "Qwen3VLVideoProcessor"),
            ("qwen3_vl_moe", "Qwen3VLVideoProcessor"),
            ("sam2_video", "Sam2VideoVideoProcessor"),
            ("smolvlm", "SmolVLMVideoProcessor"),
            ("video_llava", "VideoLlavaVideoProcessor"),
            ("vjepa2", "VJEPA2VideoProcessor"),
        ]
    )
for model_type, video_processors in VIDEO_PROCESSOR_MAPPING_NAMES.items():
    fast_video_processor_class = video_processors
    if not is_torchvision_available():
        fast_video_processor_class = None
    VIDEO_PROCESSOR_MAPPING_NAMES[model_type] = fast_video_processor_class
VIDEO_PROCESSOR_MAPPING = _LazyAutoMapping(CONFIG_MAPPING_NAMES, VIDEO_PROCESSOR_MAPPING_NAMES)
def video_processor_class_from_name(class_name: str):
    for module_name, extractors in VIDEO_PROCESSOR_MAPPING_NAMES.items():
        if class_name in extractors:
            module_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{module_name}", "MEROAI.models")
            try:
                return getattr(module, class_name)
            except AttributeError:
                continue
    for extractor in VIDEO_PROCESSOR_MAPPING._extra_content.values():
        if getattr(extractor, "__name__", None) == class_name:
            return extractor
    main_module = importlib.import_module("MEROAI")
    if hasattr(main_module, class_name):
        return getattr(main_module, class_name)
    return None
def get_video_processor_config(
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
        VIDEO_PROCESSOR_NAME,
        cache_dir=cache_dir,
        force_download=force_download,
        resume_download=resume_download,
        proxies=proxies,
        token=token,
        revision=revision,
        local_files_only=local_files_only,
    )
    if resolved_config_file is None:
        logger.info(
            "Could not locate the video processor configuration file, will try to use the model config instead."
        )
        return {}
    with open(resolved_config_file, encoding="utf-8") as reader:
        return json.load(reader)
@requires(backends=("vision", "torchvision"))
class AutoVideoProcessor:
    def __init__(self):
        raise OSError(
            "AutoVideoProcessor is designed to be instantiated "
            "using the `AutoVideoProcessor.from_pretrained(pretrained_model_name_or_path)` method."
        )
    @classmethod
    @replace_list_option_in_docstrings(VIDEO_PROCESSOR_MAPPING_NAMES)
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
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        kwargs["_from_auto"] = True
        config_dict, _ = BaseVideoProcessor.get_video_processor_dict(pretrained_model_name_or_path, **kwargs)
        video_processor_class = config_dict.get("video_processor_type", None)
        video_processor_auto_map = None
        if "AutoVideoProcessor" in config_dict.get("auto_map", {}):
            video_processor_auto_map = config_dict["auto_map"]["AutoVideoProcessor"]
        if video_processor_class is None and video_processor_auto_map is None:
            image_processor_class = config_dict.pop("image_processor_type", None)
            if image_processor_class is not None:
                video_processor_class_inferred = image_processor_class.replace("ImageProcessor", "VideoProcessor")
                if video_processor_class_inferred in VIDEO_PROCESSOR_MAPPING_NAMES.values():
                    video_processor_class = video_processor_class_inferred
            if "AutoImageProcessor" in config_dict.get("auto_map", {}):
                image_processor_auto_map = config_dict["auto_map"]["AutoImageProcessor"]
                video_processor_auto_map = image_processor_auto_map.replace("ImageProcessor", "VideoProcessor")
        if video_processor_class is None and video_processor_auto_map is None:
            if not isinstance(config, PretrainedConfig):
                config = AutoConfig.from_pretrained(
                    pretrained_model_name_or_path, trust_remote_code=trust_remote_code, **kwargs
                )
            video_processor_class = getattr(config, "video_processor_type", None)
            if hasattr(config, "auto_map") and "AutoVideoProcessor" in config.auto_map:
                video_processor_auto_map = config.auto_map["AutoVideoProcessor"]
        if video_processor_class is not None:
            video_processor_class = video_processor_class_from_name(video_processor_class)
        has_remote_code = video_processor_auto_map is not None
        has_local_code = video_processor_class is not None or type(config) in VIDEO_PROCESSOR_MAPPING
        trust_remote_code = resolve_trust_remote_code(
            trust_remote_code, pretrained_model_name_or_path, has_local_code, has_remote_code
        )
        if has_remote_code and trust_remote_code:
            class_ref = video_processor_auto_map
            video_processor_class = get_class_from_dynamic_module(class_ref, pretrained_model_name_or_path, **kwargs)
            _ = kwargs.pop("code_revision", None)
            video_processor_class.register_for_auto_class()
            return video_processor_class.from_dict(config_dict, **kwargs)
        elif video_processor_class is not None:
            return video_processor_class.from_dict(config_dict, **kwargs)
        elif type(config) in VIDEO_PROCESSOR_MAPPING:
            video_processor_class = VIDEO_PROCESSOR_MAPPING[type(config)]
            if video_processor_class is not None:
                return video_processor_class.from_pretrained(pretrained_model_name_or_path, *inputs, **kwargs)
            else:
                raise ValueError(
                    "This video processor cannot be instantiated. Please make sure you have `torchvision` installed."
                )
        raise ValueError(
            f"Unrecognized video processor in {pretrained_model_name_or_path}. Should have a "
            f"`video_processor_type` key in its {VIDEO_PROCESSOR_NAME} of {CONFIG_NAME}, or one of the following "
            f"`model_type` keys in its {CONFIG_NAME}: {', '.join(c for c in VIDEO_PROCESSOR_MAPPING_NAMES)}"
        )
    @staticmethod
    def register(
        config_class,
        video_processor_class,
        exist_ok=False,
    ):
        VIDEO_PROCESSOR_MAPPING.register(config_class, video_processor_class, exist_ok=exist_ok)
__all__ = ["VIDEO_PROCESSOR_MAPPING", "AutoVideoProcessor"]