import json
import os
import warnings
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Optional, Union
import numpy as np
from .dynamic_module_utils import custom_object_save
from .image_processing_utils import (
    BatchFeature,
    get_size_dict,
)
from .image_processing_utils_fast import BaseImageProcessorFast
from .image_utils import (
    ChannelDimension,
    SizeDict,
    validate_kwargs,
)
from .processing_utils import Unpack, VideosKwargs
from .utils import (
    IMAGE_PROCESSOR_NAME,
    PROCESSOR_NAME,
    VIDEO_PROCESSOR_NAME,
    TensorType,
    add_start_docstrings,
    copy_func,
    download_url,
    is_offline_mode,
    is_remote_url,
    is_torch_available,
    is_torchcodec_available,
    is_torchvision_v2_available,
    logging,
)
from .utils.hub import cached_file
from .utils.import_utils import requires
from .video_utils import (
    VideoInput,
    VideoMetadata,
    group_videos_by_shape,
    is_valid_video,
    load_video,
    make_batched_metadata,
    make_batched_videos,
    reorder_videos,
    to_channel_dimension_format,
)
if is_torch_available():
    import torch
if is_torchvision_v2_available():
    from torchvision.transforms.v2 import functional as F
logger = logging.get_logger(__name__)
@add_start_docstrings(
    "Constructs a base VideoProcessor.",
    BASE_VIDEO_PROCESSOR_DOCSTRING,
)
@requires(backends=("vision", "torchvision"))
class BaseVideoProcessor(BaseImageProcessorFast):
    _auto_class = None
    resample = None
    image_mean = None
    image_std = None
    size = None
    size_divisor = None
    default_to_square = True
    crop_size = None
    do_resize = None
    do_center_crop = None
    do_rescale = None
    rescale_factor = 1 / 255
    do_normalize = None
    do_convert_rgb = None
    do_sample_frames = None
    fps = None
    num_frames = None
    video_metadata = None
    return_metadata = False
    valid_kwargs = VideosKwargs
    model_input_names = ["pixel_values_videos"]
    def __init__(self, **kwargs: Unpack[VideosKwargs]) -> None:
        super().__init__()
        self._processor_class = kwargs.pop("processor_class", None)
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err
        size = kwargs.pop("size", self.size)
        self.size = (
            get_size_dict(size=size, default_to_square=kwargs.pop("default_to_square", self.default_to_square))
            if size is not None
            else None
        )
        crop_size = kwargs.pop("crop_size", self.crop_size)
        self.crop_size = get_size_dict(crop_size, param_name="crop_size") if crop_size is not None else None
        self.model_valid_processing_keys = list(self.valid_kwargs.__annotations__.keys())
        for key in self.model_valid_processing_keys:
            if kwargs.get(key) is not None:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, deepcopy(getattr(self, key, None)))
    def __call__(self, videos, **kwargs) -> BatchFeature:
        return self.preprocess(videos, **kwargs)
    def convert_to_rgb(
        self,
        video: "torch.Tensor",
    ) -> VideoInput:
        video = F.grayscale_to_rgb(video)
        if video.shape[-3] == 3 or not (video[..., 3, :, :] < 255).any():
            return video
        alpha = video[..., 3, :, :] / 255.0
        video = (1 - alpha[..., None, :, :]) * 255 + alpha[..., None, :, :] * video[..., :3, :, :]
        return video
    def sample_frames(
        self,
        metadata: VideoMetadata,
        num_frames: Optional[int] = None,
        fps: Optional[Union[int, float]] = None,
        **kwargs,
    ):
        if fps is not None and num_frames is not None:
            raise ValueError(
                "`num_frames`, `fps`, and `sample_indices_fn` are mutually exclusive arguments, please use only one!"
            )
        num_frames = num_frames if num_frames is not None else self.num_frames
        fps = fps if fps is not None else self.fps
        total_num_frames = metadata.total_num_frames
        if num_frames is None and fps is not None:
            if metadata is None or metadata.fps is None:
                raise ValueError(
                    "Asked to sample `fps` frames per second but no video metadata was provided which is required when sampling with `fps`. "
                    "Please pass in `VideoMetadata` object or use a fixed `num_frames` per input video"
                )
            num_frames = int(total_num_frames / metadata.fps * fps)
        if num_frames > total_num_frames:
            raise ValueError(
                f"Video can't be sampled. The `num_frames={num_frames}` exceeds `total_num_frames={total_num_frames}`. "
            )
        if num_frames is not None:
            indices = torch.arange(0, total_num_frames, total_num_frames / num_frames).int()
        else:
            indices = torch.arange(0, total_num_frames).int()
        return indices
    def _decode_and_sample_videos(
        self,
        videos: VideoInput,
        video_metadata: Union[VideoMetadata, dict],
        do_sample_frames: Optional[bool] = None,
        sample_indices_fn: Optional[Callable] = None,
    ) -> list["torch.Tensor"]:
        videos = make_batched_videos(videos)
        video_metadata = make_batched_metadata(videos, video_metadata=video_metadata)
        if is_valid_video(videos[0]) and do_sample_frames:
            sampled_videos = []
            sampled_metadata = []
            for video, metadata in zip(videos, video_metadata):
                indices = sample_indices_fn(metadata=metadata)
                metadata.frames_indices = indices
                sampled_videos.append(video[indices])
                sampled_metadata.append(metadata)
            videos = sampled_videos
            video_metadata = sampled_metadata
        elif not is_valid_video(videos[0]):
            if isinstance(videos[0], list):
                videos = [
                    torch.stack([F.pil_to_tensor(image) for image in images], dim=0)
                    for images in self.fetch_images(videos)
                ]
                if do_sample_frames:
                    raise ValueError(
                        "Sampling frames from a list of images is not supported! Set `do_sample_frames=False`."
                    )
            else:
                videos, video_metadata = self.fetch_videos(videos, sample_indices_fn=sample_indices_fn)
        return videos, video_metadata
    def _prepare_input_videos(
        self,
        videos: VideoInput,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        device: Optional[str] = None,
    ) -> list["torch.Tensor"]:
        processed_videos = []
        for video in videos:
            if isinstance(video, np.ndarray):
                video = to_channel_dimension_format(video, ChannelDimension.FIRST, input_data_format)
                video = torch.from_numpy(video).contiguous()
            if device is not None:
                video = video.to(device)
            processed_videos.append(video)
        return processed_videos
    @add_start_docstrings(
        BASE_VIDEO_PROCESSOR_DOCSTRING,
    )
    def preprocess(
        self,
        videos: VideoInput,
        **kwargs: Unpack[VideosKwargs],
    ) -> BatchFeature:
        validate_kwargs(
            captured_kwargs=kwargs.keys(),
            valid_processor_keys=list(self.valid_kwargs.__annotations__.keys()) + ["return_tensors"],
        )
        for kwarg_name in self.valid_kwargs.__annotations__:
            kwargs.setdefault(kwarg_name, getattr(self, kwarg_name, None))
        input_data_format = kwargs.pop("input_data_format")
        do_sample_frames = kwargs.pop("do_sample_frames")
        device = kwargs.pop("device")
        video_metadata = kwargs.pop("video_metadata")
        sample_indices_fn = partial(self.sample_frames, **kwargs) if do_sample_frames else None
        videos, video_metadata = self._decode_and_sample_videos(
            videos,
            video_metadata=video_metadata,
            do_sample_frames=do_sample_frames,
            sample_indices_fn=sample_indices_fn,
        )
        videos = self._prepare_input_videos(videos=videos, input_data_format=input_data_format, device=device)
        kwargs = self._further_process_kwargs(**kwargs)
        self._validate_preprocess_kwargs(**kwargs)
        kwargs.pop("data_format")
        return_metadata = kwargs.pop("return_metadata")
        preprocessed_videos = self._preprocess(videos=videos, **kwargs)
        if return_metadata:
            preprocessed_videos["video_metadata"] = video_metadata
        return preprocessed_videos
    def _preprocess(
        self,
        videos: list["torch.Tensor"],
        do_convert_rgb: bool,
        do_resize: bool,
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"],
        do_center_crop: bool,
        crop_size: SizeDict,
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
        image_mean: Optional[Union[float, list[float]]],
        image_std: Optional[Union[float, list[float]]],
        return_tensors: Optional[Union[str, TensorType]] = None,
        **kwargs,
    ) -> BatchFeature:
        grouped_videos, grouped_videos_index = group_videos_by_shape(videos)
        resized_videos_grouped = {}
        for shape, stacked_videos in grouped_videos.items():
            if do_convert_rgb:
                stacked_videos = self.convert_to_rgb(stacked_videos)
            if do_resize:
                stacked_videos = self.resize(stacked_videos, size=size, interpolation=interpolation)
            resized_videos_grouped[shape] = stacked_videos
        resized_videos = reorder_videos(resized_videos_grouped, grouped_videos_index)
        grouped_videos, grouped_videos_index = group_videos_by_shape(resized_videos)
        processed_videos_grouped = {}
        for shape, stacked_videos in grouped_videos.items():
            if do_center_crop:
                stacked_videos = self.center_crop(stacked_videos, crop_size)
            stacked_videos = self.rescale_and_normalize(
                stacked_videos, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_videos_grouped[shape] = stacked_videos
        processed_videos = reorder_videos(processed_videos_grouped, grouped_videos_index)
        processed_videos = torch.stack(processed_videos, dim=0) if return_tensors else processed_videos
        return BatchFeature(data={"pixel_values_videos": processed_videos}, tensor_type=return_tensors)
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: Union[str, os.PathLike],
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        **kwargs,
    ):
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
        video_processor_dict, kwargs = cls.get_video_processor_dict(pretrained_model_name_or_path, **kwargs)
        return cls.from_dict(video_processor_dict, **kwargs)
    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool = False, **kwargs):
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
        if os.path.isfile(save_directory):
            raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if self._auto_class is not None:
            custom_object_save(self, save_directory, config=self)
        output_video_processor_file = os.path.join(save_directory, VIDEO_PROCESSOR_NAME)
        self.to_json_file(output_video_processor_file)
        logger.info(f"Video processor saved in {output_video_processor_file}")
        if push_to_hub:
            self._upload_modified_files(
                save_directory,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=kwargs.get("token"),
            )
        return [output_video_processor_file]
    @classmethod
    def get_video_processor_dict(
        cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
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
        user_agent = {"file_type": "video processor", "from_auto_class": from_auto_class}
        if from_pipeline is not None:
            user_agent["using_pipeline"] = from_pipeline
        if is_offline_mode() and not local_files_only:
            logger.info("Offline mode: forcing local_files_only=True")
            local_files_only = True
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isfile(pretrained_model_name_or_path):
            resolved_video_processor_file = pretrained_model_name_or_path
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            video_processor_file = pretrained_model_name_or_path
            resolved_video_processor_file = download_url(pretrained_model_name_or_path)
        else:
            video_processor_file = VIDEO_PROCESSOR_NAME
            try:
                resolved_video_processor_files = [
                    resolved_file
                    for filename in [VIDEO_PROCESSOR_NAME, IMAGE_PROCESSOR_NAME, PROCESSOR_NAME]
                    if (
                        resolved_file := cached_file(
                            pretrained_model_name_or_path,
                            filename=filename,
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
                    )
                    is not None
                ]
                resolved_video_processor_file = resolved_video_processor_files[0]
            except OSError:
                raise
            except Exception:
                raise OSError(
                    f"Can't load video processor for '{pretrained_model_name_or_path}'. If you were trying to load"
                    " it from 'https://huggingface.co/models', make sure you don't have a local directory with the"
                    f" same name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a"
                    f" directory containing a {VIDEO_PROCESSOR_NAME} file"
                )
        try:
            with open(resolved_video_processor_file, "r", encoding="utf-8") as reader:
                text = reader.read()
            video_processor_dict = json.loads(text)
            video_processor_dict = video_processor_dict.get("video_processor", video_processor_dict)
        except json.JSONDecodeError:
            raise OSError(
                f"It looks like the config file at '{resolved_video_processor_file}' is not a valid JSON file."
            )
        if is_local:
            logger.info(f"loading configuration file {resolved_video_processor_file}")
        else:
            logger.info(
                f"loading configuration file {video_processor_file} from cache at {resolved_video_processor_file}"
            )
        return video_processor_dict, kwargs
    @classmethod
    def from_dict(cls, video_processor_dict: dict[str, Any], **kwargs):
        video_processor_dict = video_processor_dict.copy()
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        if "size" in kwargs and "size" in video_processor_dict:
            video_processor_dict["size"] = kwargs.pop("size")
        if "crop_size" in kwargs and "crop_size" in video_processor_dict:
            video_processor_dict["crop_size"] = kwargs.pop("crop_size")
        video_processor = cls(**video_processor_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(video_processor, key):
                setattr(video_processor, key, value)
                to_remove.append(key)
        for key in to_remove:
            kwargs.pop(key, None)
        logger.info(f"Video processor {video_processor}")
        if return_unused_kwargs:
            return video_processor, kwargs
        else:
            return video_processor
    def to_dict(self) -> dict[str, Any]:
        output = deepcopy(self.__dict__)
        output.pop("model_valid_processing_keys", None)
        output.pop("_valid_kwargs_names", None)
        output["video_processor_type"] = self.__class__.__name__
        return output
    def to_json_string(self) -> str:
        dictionary = self.to_dict()
        for key, value in dictionary.items():
            if isinstance(value, np.ndarray):
                dictionary[key] = value.tolist()
        _processor_class = dictionary.pop("_processor_class", None)
        if _processor_class is not None:
            dictionary["processor_class"] = _processor_class
        return json.dumps(dictionary, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            writer.write(self.to_json_string())
    def __repr__(self):
        return f"{self.__class__.__name__} {self.to_json_string()}"
    @classmethod
    def from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, "r", encoding="utf-8") as reader:
            text = reader.read()
        video_processor_dict = json.loads(text)
        return cls(**video_processor_dict)
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoVideoProcessor"):
        if not isinstance(auto_class, str):
            auto_class = auto_class.__name__
        import MEROAI.models.auto as auto_module
        if not hasattr(auto_module, auto_class):
            raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    def fetch_videos(self, video_url_or_urls: Union[str, list[str], list[list[str]]], sample_indices_fn=None):
        backend = "torchcodec"
        if not is_torchcodec_available():
            warnings.warn(
                "`torchcodec` is not installed and cannot be used to decode the video by default. "
                "Falling back to `torchvision`. Note that `torchvision` decoding is deprecated and will be removed in future versions. "
            )
            backend = "torchvision"
        if isinstance(video_url_or_urls, list):
            return list(zip(*[self.fetch_videos(x, sample_indices_fn=sample_indices_fn) for x in video_url_or_urls]))
        else:
            return load_video(video_url_or_urls, backend=backend, sample_indices_fn=sample_indices_fn)
BaseVideoProcessor.push_to_hub = copy_func(BaseVideoProcessor.push_to_hub)
if BaseVideoProcessor.push_to_hub.__doc__ is not None:
    BaseVideoProcessor.push_to_hub.__doc__ = BaseVideoProcessor.push_to_hub.__doc__.format(
        object="video processor", object_class="AutoVideoProcessor", object_files="video processor file"
    )