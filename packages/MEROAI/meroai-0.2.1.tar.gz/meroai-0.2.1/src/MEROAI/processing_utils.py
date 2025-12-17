import bisect
import copy
import inspect
import json
import os
import sys
import typing
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, TypedDict, TypeVar, Union
import numpy as np
import typing_extensions
from huggingface_hub.errors import EntryNotFoundError
from .audio_utils import AudioInput, load_audio
from .dynamic_module_utils import custom_object_save
from .feature_extraction_utils import BatchFeature
from .image_utils import ChannelDimension, ImageInput, is_vision_available
from .utils.chat_template_utils import render_jinja_template
from .video_utils import VideoInput, VideoMetadata
if is_vision_available():
    from .image_utils import PILImageResampling
from .tokenization_utils_base import (
    PaddingStrategy,
    PreTokenizedInput,
    PreTrainedTokenizerBase,
    TextInput,
    TruncationStrategy,
)
from .utils import (
    AUDIO_TOKENIZER_NAME,
    CHAT_TEMPLATE_DIR,
    CHAT_TEMPLATE_FILE,
    LEGACY_PROCESSOR_CHAT_TEMPLATE_FILE,
    PROCESSOR_NAME,
    PushToHubMixin,
    TensorType,
    cached_file,
    copy_func,
    direct_MEROAI_import,
    download_url,
    is_offline_mode,
    is_remote_url,
    is_torch_available,
    list_repo_templates,
    logging,
)
from .utils.deprecation import deprecate_kwarg
if is_torch_available():
    from .modeling_utils import PreTrainedAudioTokenizerBase
logger = logging.get_logger(__name__)
SpecificProcessorType = TypeVar("SpecificProcessorType", bound="ProcessorMixin")
MEROAI_module = direct_MEROAI_import(Path(__file__).parent)
AUTO_TO_BASE_CLASS_MAPPING = {
    "AutoTokenizer": "PreTrainedTokenizerBase",
    "AutoFeatureExtractor": "FeatureExtractionMixin",
    "AutoImageProcessor": "ImageProcessingMixin",
    "AutoVideoProcessor": "BaseVideoProcessor",
}
if sys.version_info >= (3, 11):
    Unpack = typing.Unpack
else:
    Unpack = typing_extensions.Unpack
class TextKwargs(TypedDict, total=False):
    text_pair: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]]
    text_target: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]
    text_pair_target: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]]
    add_special_tokens: Optional[bool]
    padding: Union[bool, str, PaddingStrategy]
    truncation: Union[bool, str, TruncationStrategy]
    max_length: Optional[int]
    stride: Optional[int]
    is_split_into_words: Optional[bool]
    pad_to_multiple_of: Optional[int]
    return_token_type_ids: Optional[bool]
    return_attention_mask: Optional[bool]
    return_overflowing_tokens: Optional[bool]
    return_special_tokens_mask: Optional[bool]
    return_offsets_mapping: Optional[bool]
    return_length: Optional[bool]
    verbose: Optional[bool]
    padding_side: Optional[str]
    return_mm_token_type_ids: Optional[bool]
class ImagesKwargs(TypedDict, total=False):
    do_resize: Optional[bool]
    size: Optional[dict[str, int]]
    crop_size: Optional[dict[str, int]]
    resample: Optional[Union["PILImageResampling", int]]
    do_rescale: Optional[bool]
    rescale_factor: Optional[float]
    do_normalize: Optional[bool]
    image_mean: Optional[Union[float, list[float]]]
    image_std: Optional[Union[float, list[float]]]
    do_pad: Optional[bool]
    pad_size: Optional[dict[str, int]]
    do_center_crop: Optional[bool]
    data_format: Optional[ChannelDimension]
    input_data_format: Optional[Union[str, ChannelDimension]]
    device: Optional[str]
class VideosKwargs(TypedDict, total=False):
    do_convert_rgb: Optional[bool]
    do_resize: Optional[bool]
    size: Optional[dict[str, int]]
    default_to_square: Optional[bool]
    resample: Optional["PILImageResampling"]
    do_rescale: Optional[bool]
    rescale_factor: Optional[float]
    do_normalize: Optional[bool]
    image_mean: Optional[Union[float, list[float]]]
    image_std: Optional[Union[float, list[float]]]
    do_center_crop: Optional[bool]
    crop_size: Optional[dict[str, int]]
    data_format: Optional[ChannelDimension]
    input_data_format: Optional[Union[str, ChannelDimension]]
    device: Optional[str]
    do_sample_frames: Optional[bool]
    video_metadata: Optional[Union[VideoMetadata, dict]]
    fps: Optional[Union[int, float]]
    num_frames: Optional[int]
    return_metadata: Optional[bool]
class AudioKwargs(TypedDict, total=False):
    sampling_rate: Optional[int]
    raw_speech: Optional[Union[np.ndarray, list[float], list[np.ndarray], list[list[float]]]]
    padding: Optional[Union[bool, str, PaddingStrategy]]
    max_length: Optional[int]
    truncation: Optional[bool]
    pad_to_multiple_of: Optional[int]
    return_attention_mask: Optional[bool]
class CommonKwargs(TypedDict, total=False):
    return_tensors: Optional[Union[str, TensorType]]
class ProcessingKwargs(TypedDict, total=False):
    _defaults = {}
    common_kwargs: CommonKwargs = {
        **CommonKwargs.__annotations__,
    }
    text_kwargs: TextKwargs = {
        **TextKwargs.__annotations__,
    }
    images_kwargs: ImagesKwargs = {
        **ImagesKwargs.__annotations__,
    }
    videos_kwargs: VideosKwargs = {
        **VideosKwargs.__annotations__,
    }
    audio_kwargs: AudioKwargs = {
        **AudioKwargs.__annotations__,
    }
class TokenizerChatTemplateKwargs(TypedDict, total=False):
    tools: Optional[list[dict]] = None
    documents: Optional[list[dict[str, str]]] = None
    add_generation_prompt: Optional[bool] = False
    continue_final_message: Optional[bool] = False
    return_assistant_tokens_mask: Optional[bool] = False
class ChatTemplateLoadKwargs(TypedDict, total=False):
    sampling_rate: Optional[int] = 16_000
    load_audio_from_video: Optional[bool] = False
class ProcessorChatTemplateKwargs(ChatTemplateLoadKwargs, TokenizerChatTemplateKwargs, total=False):
    tokenize: Optional[bool] = False
    return_dict: Optional[bool] = False
class AllKwargsForChatTemplate(TypedDict, total=False):
    processor_kwargs: ProcessingKwargs
    mm_load_kwargs: ChatTemplateLoadKwargs
    template_kwargs: ProcessorChatTemplateKwargs
@dataclass
class MultiModalData:
    num_image_tokens: Optional[list[int]] = None
    num_video_tokens: Optional[list[int]] = None
    num_audio_tokens: Optional[list[int]] = None
    num_image_patches: Optional[list[int]] = None
    def __contains__(self, key):
        return hasattr(self, key) and getattr(self, key) is not None
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise AttributeError(f"{self.__class__.__name__} has no attribute {key}")
class ProcessorMixin(PushToHubMixin):
    attributes = ["feature_extractor", "tokenizer"]
    optional_attributes = ["chat_template", "audio_tokenizer"]
    optional_call_args: list[str] = []
    feature_extractor_class = None
    tokenizer_class = None
    _auto_class = None
    valid_processor_kwargs = ProcessingKwargs
    def __init__(self, *args, **kwargs):
        for optional_attribute in self.optional_attributes:
            optional_attribute_value = kwargs.pop(optional_attribute, None)
            setattr(self, optional_attribute, optional_attribute_value)
            if optional_attribute == "audio_tokenizer" and optional_attribute_value is not None:
                proper_class = self.check_argument_for_proper_class(optional_attribute, optional_attribute_value)
                if not (is_torch_available() and isinstance(optional_attribute_value, PreTrainedAudioTokenizerBase)):
                    raise ValueError(
                        f"Tried to use `{proper_class}` for audio tokenization. However, this class is not"
                        " registered for audio tokenization."
                    )
        for key in kwargs:
            if key not in self.attributes:
                raise TypeError(f"Unexpected keyword argument {key}.")
        for arg, attribute_name in zip(args, self.attributes):
            if attribute_name in kwargs:
                raise TypeError(f"Got multiple values for argument {attribute_name}.")
            else:
                kwargs[attribute_name] = arg
        if len(kwargs) != len(self.attributes):
            raise ValueError(
                f"This processor requires {len(self.attributes)} arguments: {', '.join(self.attributes)}. Got "
                f"{len(args)} arguments instead."
            )
        for attribute_name, arg in kwargs.items():
            self.check_argument_for_proper_class(attribute_name, arg)
            setattr(self, attribute_name, arg)
    def __call__(
        self,
        images: Optional[ImageInput] = None,
        text: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]] = None,
        videos: Optional[VideoInput] = None,
        audio: Optional[AudioInput] = None,
        **kwargs: Unpack[ProcessingKwargs],
    ):
        if images is None and text is None and videos is None and audio is None:
            raise ValueError(f"You need to provide at least one input to call {self.__class__.__name__}")
        kwargs = self._merge_kwargs(
            self.valid_processor_kwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs if hasattr(self, "tokenizer") else {},
            **kwargs,
        )
        attribute_to_kwargs = {
            "tokenizer": (text, "text_kwargs"),
            "image_processor": (images, "images_kwargs"),
            "video_processor": (videos, "videos_kwargs"),
            "feature_extractor": (audio, "audio_kwargs"),
        }
        outputs = {}
        for attribute_name in self.attributes:
            attribute = getattr(self, attribute_name, None)
            input_data, input_kwargs = attribute_to_kwargs[attribute_name]
            if input_data is not None and attribute is not None:
                attribute_output = attribute(input_data, **kwargs[input_kwargs])
                outputs.update(attribute_output)
        return BatchFeature(outputs)
    def check_argument_for_proper_class(self, argument_name, argument):
        class_name = getattr(self, f"{argument_name}_class")
        class_name = AUTO_TO_BASE_CLASS_MAPPING.get(class_name, class_name)
        if isinstance(class_name, tuple):
            proper_class = tuple(self.get_possibly_dynamic_module(n) for n in class_name if n is not None)
        else:
            proper_class = self.get_possibly_dynamic_module(class_name)
        if not isinstance(argument, proper_class):
            raise TypeError(
                f"Received a {type(argument).__name__} for argument {argument_name}, but a {class_name} was expected."
            )
        return proper_class
    def to_dict(self, legacy_serialization=True) -> dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        sig = inspect.signature(self.__init__)
        attrs_to_save = list(sig.parameters)
        attrs_to_save += ["auto_map"]
        if legacy_serialization:
            attrs_to_save = [x for x in attrs_to_save if x not in self.__class__.attributes]
        if "tokenizer" in output:
            del output["tokenizer"]
        if "qformer_tokenizer" in output:
            del output["qformer_tokenizer"]
        if "protein_tokenizer" in output:
            del output["protein_tokenizer"]
        if "chat_template" in output:
            del output["chat_template"]
        def cast_array_to_list(dictionary):
            for key, value in dictionary.items():
                if isinstance(value, np.ndarray):
                    dictionary[key] = value.tolist()
                elif isinstance(value, dict):
                    dictionary[key] = cast_array_to_list(value)
            return dictionary
        output = {
            k: v.to_dict() if isinstance(v, PushToHubMixin) else v
            for k, v in output.items()
            if (
                k in attrs_to_save
                and v.__class__.__name__ != "BeamSearchDecoderCTC"
                and (
                    (legacy_serialization and not isinstance(v, PushToHubMixin)) or not legacy_serialization
                )
            )
        }
        output = cast_array_to_list(output)
        if not legacy_serialization and "audio_tokenizer" in output:
            audio_tokenizer_dict = {
                "audio_tokenizer_class": self.audio_tokenizer.__class__.__name__,
                "audio_tokenizer_name_or_path": self.audio_tokenizer.name_or_path,
            }
            output["audio_tokenizer"] = audio_tokenizer_dict
        output["processor_class"] = self.__class__.__name__
        return output
    def to_json_string(self, legacy_serialization=True) -> str:
        dictionary = self.to_dict(legacy_serialization=legacy_serialization)
        return json.dumps(dictionary, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike], legacy_serialization=True):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            writer.write(self.to_json_string(legacy_serialization=legacy_serialization))
    def __repr__(self):
        attributes_repr = [f"- {name}: {repr(getattr(self, name))}" for name in self.attributes]
        attributes_repr = "\n".join(attributes_repr)
        return f"{self.__class__.__name__}:\n{attributes_repr}\n\n{self.to_json_string()}"
    def save_pretrained(self, save_directory, push_to_hub: bool = False, legacy_serialization: bool = True, **kwargs):
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
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if self._auto_class is not None:
            attrs = [getattr(self, attribute_name) for attribute_name in self.attributes]
            configs = [(a.init_kwargs if isinstance(a, PreTrainedTokenizerBase) else a) for a in attrs]
            configs.append(self)
            custom_object_save(self, save_directory, config=configs)
        save_jinja_files = kwargs.get("save_jinja_files", True)
        for attribute_name in self.attributes:
            if attribute_name == "tokenizer":
                attribute = getattr(self, attribute_name)
                if hasattr(attribute, "_set_processor_class"):
                    attribute._set_processor_class(self.__class__.__name__)
                attribute.save_pretrained(save_directory, save_jinja_files=save_jinja_files)
            elif legacy_serialization:
                attribute = getattr(self, attribute_name)
                if hasattr(attribute, "_set_processor_class"):
                    attribute._set_processor_class(self.__class__.__name__)
                attribute.save_pretrained(save_directory)
        if self._auto_class is not None:
            for attribute_name in self.attributes:
                attribute = getattr(self, attribute_name)
                if isinstance(attribute, PreTrainedTokenizerBase):
                    del attribute.init_kwargs["auto_map"]
        output_processor_file = os.path.join(save_directory, PROCESSOR_NAME)
        output_chat_template_file_jinja = os.path.join(save_directory, CHAT_TEMPLATE_FILE)
        output_chat_template_file_legacy = os.path.join(
            save_directory, LEGACY_PROCESSOR_CHAT_TEMPLATE_FILE
        )
        chat_template_dir = os.path.join(save_directory, CHAT_TEMPLATE_DIR)
        if self.chat_template is not None:
            save_jinja_files = kwargs.get("save_jinja_files", True)
            is_single_template = isinstance(self.chat_template, str)
            if save_jinja_files and is_single_template:
                with open(output_chat_template_file_jinja, "w", encoding="utf-8") as f:
                    f.write(self.chat_template)
                logger.info(f"chat template saved in {output_chat_template_file_jinja}")
            elif save_jinja_files and not is_single_template:
                for template_name, template in self.chat_template.items():
                    if template_name == "default":
                        with open(output_chat_template_file_jinja, "w", encoding="utf-8") as f:
                            f.write(self.chat_template["default"])
                        logger.info(f"chat template saved in {output_chat_template_file_jinja}")
                    else:
                        os.makedirs(chat_template_dir, exist_ok=True)
                        template_filepath = os.path.join(chat_template_dir, f"{template_name}.jinja")
                        with open(template_filepath, "w", encoding="utf-8") as f:
                            f.write(template)
                        logger.info(f"chat template saved in {template_filepath}")
            elif is_single_template:
                chat_template_json_string = (
                    json.dumps({"chat_template": self.chat_template}, indent=2, sort_keys=True) + "\n"
                )
                with open(output_chat_template_file_legacy, "w", encoding="utf-8") as writer:
                    writer.write(chat_template_json_string)
                logger.info(f"chat template saved in {output_chat_template_file_legacy}")
            elif self.chat_template is not None:
                raise ValueError(
                    "Multiple chat templates are not supported in the legacy format. Please save them as "
                    "separate files using the `save_jinja_files` argument."
                )
        if legacy_serialization:
            output_audio_tokenizer_file = os.path.join(save_directory, AUDIO_TOKENIZER_NAME)
            processor_dict = self.to_dict()
            if set(processor_dict.keys()) != {"processor_class"}:
                self.to_json_file(output_processor_file)
                logger.info(f"processor saved in {output_processor_file}")
            if set(processor_dict.keys()) == {"processor_class"}:
                return_files = []
            else:
                return_files = [output_processor_file]
            if self.audio_tokenizer is not None:
                audio_tokenizer_class = self.audio_tokenizer.__class__.__name__
                audio_tokenizer_name_or_path = self.audio_tokenizer.name_or_path
                audio_tokenizer_dict = {
                    "audio_tokenizer_class": audio_tokenizer_class,
                    "audio_tokenizer_name_or_path": audio_tokenizer_name_or_path,
                }
                audio_tokenizer_json = json.dumps(audio_tokenizer_dict, indent=2, sort_keys=True) + "\n"
                with open(output_audio_tokenizer_file, "w", encoding="utf-8") as writer:
                    writer.write(audio_tokenizer_json)
        else:
            self.to_json_file(output_processor_file, legacy_serialization=False)
            logger.info(f"processor saved in {output_processor_file}")
            return_files = [output_processor_file]
        if push_to_hub:
            self._upload_modified_files(
                save_directory,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=kwargs.get("token"),
            )
        return return_files
    @classmethod
    def get_processor_dict(
        cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        audio_tokenizer_kwargs = copy.deepcopy(kwargs)
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        user_agent = {"file_type": "processor", "from_auto_class": from_auto_class}
        if from_pipeline is not None:
            user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isdir(pretrained_model_name_or_path):
            processor_file = os.path.join(pretrained_model_name_or_path, PROCESSOR_NAME)
        additional_chat_template_files = {}
        resolved_additional_chat_template_files = {}
        if os.path.isfile(pretrained_model_name_or_path):
            resolved_processor_file = pretrained_model_name_or_path
            resolved_chat_template_file = None
            resolved_raw_chat_template_file = None
            resolved_audio_tokenizer_file = None
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            processor_file = pretrained_model_name_or_path
            resolved_processor_file = download_url(pretrained_model_name_or_path)
            resolved_chat_template_file = None
            resolved_raw_chat_template_file = None
            resolved_audio_tokenizer_file = None
        else:
            if is_local:
                template_dir = Path(pretrained_model_name_or_path, CHAT_TEMPLATE_DIR)
                if template_dir.is_dir():
                    for template_file in template_dir.glob("*.jinja"):
                        template_name = template_file.stem
                        additional_chat_template_files[template_name] = f"{CHAT_TEMPLATE_DIR}/{template_file.name}"
            else:
                try:
                    for template in list_repo_templates(
                        pretrained_model_name_or_path,
                        local_files_only=local_files_only,
                        revision=revision,
                        cache_dir=cache_dir,
                        token=token,
                    ):
                        additional_chat_template_files[template] = f"{CHAT_TEMPLATE_DIR}/{template}.jinja"
                except EntryNotFoundError:
                    pass
            processor_file = PROCESSOR_NAME
            try:
                resolved_processor_file = cached_file(
                    pretrained_model_name_or_path,
                    processor_file,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    local_files_only=local_files_only,
                    token=token,
                    user_agent=user_agent,
                    revision=revision,
                    subfolder=subfolder,
                    _raise_exceptions_for_missing_entries=False,
                )
                resolved_chat_template_file = cached_file(
                    pretrained_model_name_or_path,
                    LEGACY_PROCESSOR_CHAT_TEMPLATE_FILE,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    local_files_only=local_files_only,
                    token=token,
                    user_agent=user_agent,
                    revision=revision,
                    subfolder=subfolder,
                    _raise_exceptions_for_missing_entries=False,
                )
                resolved_raw_chat_template_file = cached_file(
                    pretrained_model_name_or_path,
                    CHAT_TEMPLATE_FILE,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    local_files_only=local_files_only,
                    token=token,
                    user_agent=user_agent,
                    revision=revision,
                    subfolder=subfolder,
                    _raise_exceptions_for_missing_entries=False,
                )
                resolved_additional_chat_template_files = {
                    template_name: cached_file(
                        pretrained_model_name_or_path,
                        template_file,
                        cache_dir=cache_dir,
                        force_download=force_download,
                        proxies=proxies,
                        resume_download=resume_download,
                        local_files_only=local_files_only,
                        token=token,
                        user_agent=user_agent,
                        revision=revision,
                        subfolder=subfolder,
                        _raise_exceptions_for_missing_entries=False,
                    )
                    for template_name, template_file in additional_chat_template_files.items()
                }
                resolved_audio_tokenizer_file = cached_file(
                    pretrained_model_name_or_path,
                    AUDIO_TOKENIZER_NAME,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    local_files_only=local_files_only,
                    token=token,
                    user_agent=user_agent,
                    revision=revision,
                    subfolder=subfolder,
                    _raise_exceptions_for_missing_entries=False,
                )
            except OSError:
                raise
            except Exception:
                raise OSError(
                    f"Can't load processor for '{pretrained_model_name_or_path}'. If you were trying to load"
                    " it from 'https://huggingface.co/models', make sure you don't have a local directory with the"
                    f" same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a"
                    f" directory containing a {PROCESSOR_NAME} file"
                )
        if resolved_chat_template_file is not None:
            with open(resolved_chat_template_file, encoding="utf-8") as reader:
                chat_template_json = json.loads(reader.read())
                chat_templates = {"default": chat_template_json["chat_template"]}
                if resolved_additional_chat_template_files:
                    raise ValueError(
                        "Cannot load chat template due to conflicting files - this checkpoint combines "
                        "a legacy chat_template.json file with separate template files, which is not "
                        "supported. To resolve this error, replace the legacy chat_template.json file "
                        "with a modern chat_template.jinja file."
                    )
        else:
            chat_templates = {
                template_name: open(template_file, "r", encoding="utf-8").read()
                for template_name, template_file in resolved_additional_chat_template_files.items()
            }
            if resolved_raw_chat_template_file is not None:
                with open(resolved_raw_chat_template_file, "r", encoding="utf-8") as reader:
                    chat_templates["default"] = reader.read()
        if isinstance(chat_templates, dict) and "default" in chat_templates and len(chat_templates) == 1:
            chat_templates = chat_templates["default"]
        if chat_templates:
            kwargs["chat_template"] = chat_templates
        if resolved_processor_file is None:
            processor_dict = {}
        else:
            try:
                with open(resolved_processor_file, encoding="utf-8") as reader:
                    text = reader.read()
                processor_dict = json.loads(text)
            except json.JSONDecodeError:
                raise OSError(
                    f"It looks like the config file at '{resolved_processor_file}' is not a valid JSON file."
                )
        if is_local:
            logger.info(f"loading configuration file {resolved_processor_file}")
        else:
            logger.info(f"loading configuration file {processor_file} from cache at {resolved_processor_file}")
        if "chat_template" in processor_dict and processor_dict["chat_template"] is not None:
            logger.warning_once(
                "Chat templates should be in a 'chat_template.jinja' file but found key='chat_template' "
                "in the processor's config. Make sure to move your template to its own file."
            )
        if "chat_template" in kwargs:
            processor_dict["chat_template"] = kwargs.pop("chat_template")
        if resolved_audio_tokenizer_file is not None or "audio_tokenizer" in processor_dict:
            if resolved_audio_tokenizer_file is not None:
                reader = open(resolved_audio_tokenizer_file, "r", encoding="utf-8")
                audio_tokenizer_dict = reader.read()
                audio_tokenizer_dict = json.loads(audio_tokenizer_dict)
            else:
                audio_tokenizer_dict = processor_dict["audio_tokenizer"]
            audio_tokenizer_class = cls.get_possibly_dynamic_module(audio_tokenizer_dict["audio_tokenizer_class"])
            audio_tokenizer_path = audio_tokenizer_dict["audio_tokenizer_name_or_path"]
            processor_dict["audio_tokenizer"] = audio_tokenizer_class.from_pretrained(
                audio_tokenizer_path, **audio_tokenizer_kwargs
            )
        for attribute in cls.attributes:
            processor_dict.pop(attribute, None)
        return processor_dict, kwargs
    @classmethod
    def from_args_and_dict(cls, args, processor_dict: dict[str, Any], **kwargs):
        processor_dict = processor_dict.copy()
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        if "processor_class" in processor_dict:
            del processor_dict["processor_class"]
        if "auto_map" in processor_dict:
            del processor_dict["auto_map"]
        processor_dict.update(kwargs)
        accepted_args_and_kwargs = cls.__init__.__code__.co_varnames[: cls.__init__.__code__.co_argcount][1:]
        unused_kwargs, valid_kwargs = cls.validate_init_kwargs(
            processor_config=processor_dict, valid_kwargs=accepted_args_and_kwargs
        )
        args_to_update = {
            i: valid_kwargs.pop(arg)
            for i, arg in enumerate(accepted_args_and_kwargs)
            if (arg in valid_kwargs and i < len(args))
        }
        args = [args_to_update.get(i, arg) for i, arg in enumerate(args)]
        processor = cls(*args, **valid_kwargs)
        logger.info(f"Processor {processor}")
        if return_unused_kwargs:
            return processor, unused_kwargs
        else:
            return processor
    def _merge_kwargs(
        self,
        ModelProcessorKwargs: ProcessingKwargs,
        tokenizer_init_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> dict[str, dict]:
        output_kwargs = {
            "text_kwargs": {},
            "images_kwargs": {},
            "audio_kwargs": {},
            "videos_kwargs": {},
            "common_kwargs": {},
        }
        default_kwargs = {
            "text_kwargs": {},
            "images_kwargs": {},
            "audio_kwargs": {},
            "videos_kwargs": {},
            "common_kwargs": {},
        }
        possible_modality_keywords = {"text", "audio", "videos", "images"}
        used_keys = set()
        for modality in default_kwargs:
            default_kwargs[modality] = ModelProcessorKwargs._defaults.get(modality, {}).copy()
            for modality_key in ModelProcessorKwargs.__annotations__[modality].__annotations__:
                if tokenizer_init_kwargs is not None and modality_key in tokenizer_init_kwargs:
                    value = (
                        getattr(self.tokenizer, modality_key)
                        if hasattr(self.tokenizer, modality_key)
                        else tokenizer_init_kwargs[modality_key]
                    )
                    default_kwargs[modality][modality_key] = value
        output_kwargs.update(default_kwargs)
        non_modality_kwargs = set(kwargs) - set(output_kwargs)
        for modality, output_kwarg in output_kwargs.items():
            for modality_key in ModelProcessorKwargs.__annotations__[modality].__annotations__:
                if modality in kwargs:
                    kwarg_value = kwargs[modality].pop(modality_key, "__empty__")
                    if kwarg_value != "__empty__" and modality_key in non_modality_kwargs:
                        raise ValueError(
                            f"Keyword argument {modality_key} was passed two times:\n"
                            f"in a dictionary for {modality} and as a **kwarg."
                        )
                elif modality_key in kwargs:
                    kwarg_value = kwargs.get(modality_key, "__empty__")
                else:
                    kwarg_value = "__empty__"
                if not isinstance(kwarg_value, str) or kwarg_value != "__empty__":
                    output_kwarg[modality_key] = kwarg_value
                    used_keys.add(modality_key)
        if any(key in default_kwargs for key in kwargs):
            for modality, subdict in kwargs.items():
                if modality in default_kwargs:
                    for subkey, subvalue in subdict.items():
                        if subkey not in used_keys:
                            output_kwargs[modality][subkey] = subvalue
                            used_keys.add(subkey)
        else:
            for key, kwarg in kwargs.items():
                if key not in used_keys:
                    if key in ModelProcessorKwargs.__annotations__["common_kwargs"].__annotations__:
                        output_kwargs["common_kwargs"][key] = kwarg
                    elif key not in possible_modality_keywords:
                        logger.warning_once(
                            f"Keyword argument `{key}` is not a valid argument for this processor and will be ignored."
                        )
        for kwarg in output_kwargs.values():
            kwarg.update(output_kwargs["common_kwargs"])
        return output_kwargs
    @classmethod
    def from_pretrained(
        cls: type[SpecificProcessorType],
        pretrained_model_name_or_path: Union[str, os.PathLike],
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        **kwargs,
    ) -> SpecificProcessorType:
        kwargs["cache_dir"] = cache_dir
        kwargs["force_download"] = force_download
        kwargs["local_files_only"] = local_files_only
        kwargs["revision"] = revision
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if token is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            token = use_auth_token
        if token is not None:
            kwargs["token"] = token
        args = cls._get_arguments_from_pretrained(pretrained_model_name_or_path, **kwargs)
        processor_dict, kwargs = cls.get_processor_dict(pretrained_model_name_or_path, **kwargs)
        return cls.from_args_and_dict(args, processor_dict, **kwargs)
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoProcessor"):
        if not isinstance(auto_class, str):
            auto_class = auto_class.__name__
        import MEROAI.models.auto as auto_module
        if not hasattr(auto_module, auto_class):
            raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    @classmethod
    def _get_arguments_from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        args = []
        for attribute_name in cls.attributes:
            class_name = getattr(cls, f"{attribute_name}_class")
            if isinstance(class_name, tuple):
                classes = tuple(cls.get_possibly_dynamic_module(n) if n is not None else None for n in class_name)
                if attribute_name == "image_processor":
                    use_fast = kwargs.get("use_fast")
                    if use_fast is None:
                        logger.warning_once(
                            "Using a slow image processor as `use_fast` is unset and a slow processor was saved with this model. "
                            "`use_fast=True` will be the default behavior in v4.52, even if the model was saved with a slow processor. "
                            "This will result in minor differences in outputs. You'll still be able to use a slow processor with `use_fast=False`."
                        )
                else:
                    use_fast = kwargs.get("use_fast", True)
                if use_fast and classes[1] is not None:
                    attribute_class = classes[1]
                else:
                    attribute_class = classes[0]
            else:
                attribute_class = cls.get_possibly_dynamic_module(class_name)
            args.append(attribute_class.from_pretrained(pretrained_model_name_or_path, **kwargs))
        return args
    @staticmethod
    def get_possibly_dynamic_module(module_name):
        if hasattr(MEROAI_module, module_name):
            return getattr(MEROAI_module, module_name)
        lookup_locations = [
            MEROAI_module.IMAGE_PROCESSOR_MAPPING,
            MEROAI_module.VIDEO_PROCESSOR_MAPPING,
            MEROAI_module.TOKENIZER_MAPPING,
            MEROAI_module.FEATURE_EXTRACTOR_MAPPING,
            MEROAI_module.MODEL_FOR_AUDIO_TOKENIZATION_MAPPING,
        ]
        for lookup_location in lookup_locations:
            for custom_class in lookup_location._extra_content.values():
                if isinstance(custom_class, tuple):
                    for custom_subclass in custom_class:
                        if custom_subclass is not None and custom_subclass.__name__ == module_name:
                            return custom_subclass
                elif custom_class is not None and custom_class.__name__ == module_name:
                    return custom_class
        raise ValueError(
            f"Could not find module {module_name} in `MEROAI`. If this is a custom class, "
            f"it should be registered using the relevant `AutoClass.register()` function so that "
            f"other functions can find it!"
        )
    def batch_decode(self, *args, **kwargs):
        if not hasattr(self, "tokenizer"):
            raise ValueError(f"Cannot batch decode text: {self.__class__.__name__} has no tokenizer.")
        return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs):
        if not hasattr(self, "tokenizer"):
            raise ValueError(f"Cannot decode text: {self.__class__.__name__} has no tokenizer.")
        return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        model_input_names = []
        for attribute_name in self.attributes:
            attribute = getattr(self, attribute_name, None)
            attr_input_names = getattr(attribute, "model_input_names")
            model_input_names.extend(attr_input_names)
        return model_input_names
    @staticmethod
    def validate_init_kwargs(processor_config, valid_kwargs):
        kwargs_from_config = set(processor_config.keys())
        valid_kwargs_set = set(valid_kwargs)
        unused_keys = kwargs_from_config - valid_kwargs_set
        valid_keys = kwargs_from_config & valid_kwargs_set
        unused_kwargs = {k: processor_config[k] for k in unused_keys} if unused_keys else {}
        valid_kwargs = {k: processor_config[k] for k in valid_keys} if valid_keys else {}
        return unused_kwargs, valid_kwargs
    @deprecate_kwarg("video_fps", version="4.58", new_name="fps")
    @deprecate_kwarg(
        "video_load_backend",
        version="4.59",
        additional_message=". This function will use `torchcodec` by default, or `torchvision` if `torchcodec` is not installed.",
    )
    def apply_chat_template(
        self,
        conversation: Union[list[dict[str, str]], list[list[dict[str, str]]]],
        chat_template: Optional[str] = None,
        **kwargs: Unpack[AllKwargsForChatTemplate],
    ) -> str:
        if chat_template is None:
            if isinstance(self.chat_template, dict) and "default" in self.chat_template:
                chat_template = self.chat_template["default"]
            elif isinstance(self.chat_template, dict):
                raise ValueError(
                    'The processor has multiple chat templates but none of them are named "default". You need to specify'
                    " which one to use by passing the `chat_template` argument. Available templates are: "
                    f"{', '.join(self.chat_template.keys())}"
                )
            elif self.chat_template is not None:
                chat_template = self.chat_template
            else:
                raise ValueError(
                    "Cannot use apply_chat_template because this processor does not have a chat template."
                )
        else:
            if isinstance(self.chat_template, dict) and chat_template in self.chat_template:
                chat_template = self.chat_template[chat_template]
            else:
                pass
        is_tokenizers_fast = hasattr(self, "tokenizer") and self.tokenizer.__class__.__name__.endswith("Fast")
        if kwargs.get("continue_final_message", False):
            if kwargs.get("add_generation_prompt", False):
                raise ValueError(
                    "continue_final_message and add_generation_prompt are not compatible. Use continue_final_message when you want the model to continue the final message, and add_generation_prompt when you want to add a header that will prompt it to start a new assistant message instead."
                )
            if kwargs.get("return_assistant_tokens_mask", False):
                raise ValueError("continue_final_message is not compatible with return_assistant_tokens_mask.")
        if kwargs.get("return_assistant_tokens_mask", False):
            if not is_tokenizers_fast:
                raise ValueError(
                    "`return_assistant_tokens_mask` is not possible with slow tokenizers. Make sure you have `tokenizers` installed. "
                    "If the error persists, open an issue to support a Fast tokenizer for your model."
                )
            else:
                kwargs["return_offsets_mapping"] = True
        processed_kwargs = {
            "mm_load_kwargs": {},
            "template_kwargs": {},
        }
        for kwarg_type in processed_kwargs:
            for key in AllKwargsForChatTemplate.__annotations__[kwarg_type].__annotations__:
                kwarg_type_defaults = AllKwargsForChatTemplate.__annotations__[kwarg_type]
                default_value = getattr(kwarg_type_defaults, key, None)
                value = kwargs.pop(key, default_value)
                if value is not None and not isinstance(value, dict):
                    processed_kwargs[kwarg_type][key] = value
        kwargs.pop("video_load_backend", None)
        processed_kwargs["template_kwargs"].update(kwargs)
        if isinstance(conversation, (list, tuple)) and (
            isinstance(conversation[0], (list, tuple)) or hasattr(conversation[0], "content")
        ):
            is_batched = True
            conversations = conversation
        else:
            is_batched = False
            conversations = [conversation]
        tokenize = processed_kwargs["template_kwargs"].pop("tokenize", False)
        return_dict = processed_kwargs["template_kwargs"].pop("return_dict", False)
        mm_load_kwargs = processed_kwargs["mm_load_kwargs"]
        if tokenize:
            batch_images, batch_videos = [], []
            batch_audios = []
            for conversation in conversations:
                images, videos = [], []
                for message in conversation:
                    visuals = [content for content in message["content"] if content["type"] in ["image", "video"]]
                    audio_fnames = [
                        content[key]
                        for content in message["content"]
                        for key in ["audio", "url", "path"]
                        if key in content and content["type"] == "audio"
                    ]
                    image_fnames = [
                        vision_info[key]
                        for vision_info in visuals
                        for key in ["image", "url", "path", "base64"]
                        if key in vision_info and vision_info["type"] == "image"
                    ]
                    images.extend(image_fnames)
                    video_fnames = [
                        vision_info[key]
                        for vision_info in visuals
                        for key in ["video", "url", "path"]
                        if key in vision_info and vision_info["type"] == "video"
                    ]
                    videos.extend(video_fnames)
                    if not mm_load_kwargs["load_audio_from_video"]:
                        for fname in audio_fnames:
                            batch_audios.append(load_audio(fname, sampling_rate=mm_load_kwargs["sampling_rate"]))
                    else:
                        for fname in video_fnames:
                            batch_audios.append(load_audio(fname, sampling_rate=mm_load_kwargs["sampling_rate"]))
                batch_images.append(images)
                batch_videos.append(videos)
        prompt, generation_indices = render_jinja_template(
            conversations=conversations,
            chat_template=chat_template,
            **processed_kwargs["template_kwargs"],
            **self.tokenizer.special_tokens_map,
        )
        if not is_batched:
            prompt = prompt[0]
        if tokenize:
            single_prompt = prompt[0] if is_batched else prompt
            if self.tokenizer.bos_token is not None and single_prompt.startswith(self.tokenizer.bos_token):
                kwargs["add_special_tokens"] = False
            if "do_sample_frames" not in kwargs and (
                kwargs.get("fps") is not None or kwargs.get("num_frames") is not None
            ):
                kwargs["do_sample_frames"] = True
            images_exist = any((im is not None) for im_list in batch_images for im in im_list)
            videos_exist = any((vid is not None) for vid_list in batch_videos for vid in vid_list)
            out = self(
                text=prompt,
                images=batch_images if images_exist else None,
                videos=batch_videos if videos_exist else None,
                audio=batch_audios if batch_audios else None,
                **kwargs,
            )
            if return_dict:
                if processed_kwargs["template_kwargs"].get("return_assistant_tokens_mask", False):
                    assistant_masks = []
                    offset_mapping = out.pop("offset_mapping")
                    input_ids = out["input_ids"]
                    for i in range(len(input_ids)):
                        current_mask = [0] * len(input_ids[i])
                        offsets = offset_mapping[i]
                        offset_starts = [start for start, end in offsets]
                        for assistant_start_char, assistant_end_char in generation_indices[i]:
                            start_pos = bisect.bisect_left(offset_starts, assistant_start_char)
                            end_pos = bisect.bisect_left(offset_starts, assistant_end_char)
                            if not (
                                start_pos >= 0
                                and offsets[start_pos][0] <= assistant_start_char < offsets[start_pos][1]
                            ):
                                continue
                            for token_id in range(start_pos, end_pos if end_pos else len(input_ids[i])):
                                current_mask[token_id] = 1
                        assistant_masks.append(current_mask)
                    out["assistant_masks"] = assistant_masks
                    out.convert_to_tensors(tensor_type=kwargs.get("return_tensors"))
                return out
            else:
                return out["input_ids"]
        return prompt
    def post_process_image_text_to_text(self, generated_outputs, skip_special_tokens=True, **kwargs):
        return self.tokenizer.batch_decode(generated_outputs, skip_special_tokens=skip_special_tokens, **kwargs)
    def _check_special_mm_tokens(self, text: list[str], text_inputs: "BatchFeature", modalities: list[str]):
        for modality in modalities:
            token_str = getattr(self, f"{modality}_token")
            token_id = getattr(self, f"{modality}_token_id")
            ids_count = [list(ids).count(token_id) for ids in text_inputs["input_ids"]]
            text_count = [sample.count(token_str) for sample in text]
            if ids_count != text_count:
                raise ValueError(
                    f"Mismatch in `{modality}` token count between text and `input_ids`. Got ids={ids_count} and text={text_count}. "
                    "Likely due to `truncation='max_length'`. Please disable truncation or increase `max_length`."
                )
ProcessorMixin.push_to_hub = copy_func(ProcessorMixin.push_to_hub)
if ProcessorMixin.push_to_hub.__doc__ is not None:
    ProcessorMixin.push_to_hub.__doc__ = ProcessorMixin.push_to_hub.__doc__.format(
        object="processor", object_class="AutoProcessor", object_files="processor files"
    )