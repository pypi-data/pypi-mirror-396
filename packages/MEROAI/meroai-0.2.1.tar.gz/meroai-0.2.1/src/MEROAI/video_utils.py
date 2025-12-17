import os
import warnings
from collections.abc import Iterable, Mapping
from contextlib import redirect_stdout
from dataclasses import dataclass, fields
from io import BytesIO
from typing import Callable, NewType, Optional, Union
from urllib.parse import urlparse
import numpy as np
import requests
from .image_transforms import PaddingMode, to_channel_dimension_format
from .image_utils import ChannelDimension, infer_channel_dimension_format, is_valid_image
from .utils import (
    is_av_available,
    is_cv2_available,
    is_decord_available,
    is_numpy_array,
    is_torch_available,
    is_torch_tensor,
    is_torchcodec_available,
    is_torchvision_available,
    is_vision_available,
    is_yt_dlp_available,
    logging,
    requires_backends,
)
if is_vision_available():
    import PIL.Image
    import PIL.ImageOps
    if is_torchvision_available():
        from torchvision import io as torchvision_io
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
URL = NewType("URL", str)
Path = NewType("Path", str)
VideoInput = Union[
    list["PIL.Image.Image"],
    np.ndarray,
    "torch.Tensor",
    list[np.ndarray],
    list["torch.Tensor"],
    list[list["PIL.Image.Image"]],
    list[list[np.ndarray]],
    list[list["torch.Tensor"]],
    URL,
    list[URL],
    list[list[URL]],
    Path,
    list[Path],
    list[list[Path]],
]
@dataclass
class VideoMetadata(Mapping):
    total_num_frames: int
    fps: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    video_backend: Optional[str] = None
    frames_indices: Optional[list[int]] = None
    def __iter__(self):
        return (f.name for f in fields(self))
    def __len__(self):
        return len(fields(self))
    def __getitem__(self, item):
        return getattr(self, item)
    def __setitem__(self, key, value):
        return setattr(self, key, value)
    @property
    def timestamps(self) -> list[float]:
        "Timestamps of the sampled frames in seconds."
        if self.fps is None or self.frames_indices is None:
            raise ValueError("Cannot infer video `timestamps` when `fps` or `frames_indices` is None.")
        return [frame_idx / self.fps for frame_idx in self.frames_indices]
    def update(self, dictionary):
        for key, value in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)
def is_valid_video_frame(frame):
    return isinstance(frame, PIL.Image.Image) or (
        (is_numpy_array(frame) or is_torch_tensor(frame)) and frame.ndim == 3
    )
def is_valid_video(video):
    if not isinstance(video, (list, tuple)):
        return (is_numpy_array(video) or is_torch_tensor(video)) and video.ndim == 4
    return video and all(is_valid_video_frame(frame) for frame in video)
def valid_videos(videos):
    if isinstance(videos, (list, tuple)):
        for video_or_frame in videos:
            if not (is_valid_video(video_or_frame) or is_valid_video_frame(video_or_frame)):
                return False
    elif not is_valid_video(videos) or videos.ndim == 5:
        return False
    return True
def is_batched_video(videos):
    if isinstance(videos, (list, tuple)):
        return is_valid_video(videos[0])
    elif (is_numpy_array(videos) or is_torch_tensor(videos)) and videos.ndim == 5:
        return True
    return False
def is_scaled_video(video: np.ndarray) -> bool:
    return np.min(video) >= 0 and np.max(video) <= 1
def convert_pil_frames_to_video(videos: list[VideoInput]) -> list[Union[np.ndarray, "torch.Tensor"]]:
    if not (isinstance(videos[0], (list, tuple)) and is_valid_image(videos[0][0])):
        return videos
    video_converted = []
    for video in videos:
        video = [np.array(frame) for frame in video]
        video = np.stack(video)
        video_converted.append(video)
    return video_converted
def make_batched_videos(videos) -> list[Union[np.ndarray, "torch.Tensor", "URL", "Path"]]:
    try:
        if isinstance(videos[0][0], list) and isinstance(videos[0][0][0], str):
            return [image_paths for sublist in videos for image_paths in sublist]
    except (IndexError, TypeError):
        pass
    if isinstance(videos, str) or is_valid_video(videos):
        return convert_pil_frames_to_video([videos])
    elif is_valid_image(videos):
        if isinstance(videos, PIL.Image.Image):
            videos = np.array(videos)
        return [videos[None, ...]]
    elif not isinstance(videos, list):
        raise ValueError(
            f"Invalid video input. Expected either a list of video frames or an input of 4 or 5 dimensions, but got"
            f" type {type(videos)}."
        )
    flat_videos_list = []
    for item in videos:
        if isinstance(item, str) or is_valid_video(item):
            flat_videos_list.append(item)
        elif isinstance(item, list) and item:
            flat_videos_list.extend(make_batched_videos(item))
    flat_videos_list = convert_pil_frames_to_video(flat_videos_list)
    return flat_videos_list
def make_batched_metadata(videos: VideoInput, video_metadata: Union[VideoMetadata, dict]):
    if video_metadata is None:
        video_metadata = [
            {
                "total_num_frames": len(video),
                "fps": None,
                "duration": None,
                "frames_indices": list(range(len(video))),
                "height": get_video_size(video)[0] if is_valid_video(video) else None,
                "width": get_video_size(video)[1] if is_valid_video(video) else None,
            }
            for video in videos
        ]
    if isinstance(video_metadata, list):
        if isinstance(video_metadata[0], list):
            video_metadata = [
                VideoMetadata(**metadata) for metadata_list in video_metadata for metadata in metadata_list
            ]
        elif isinstance(video_metadata[0], dict):
            video_metadata = [VideoMetadata(**metadata) for metadata in video_metadata]
    else:
        video_metadata = [VideoMetadata(**video_metadata)]
    return video_metadata
def get_video_size(video: np.ndarray, channel_dim: Optional[ChannelDimension] = None) -> tuple[int, int]:
    if channel_dim is None:
        channel_dim = infer_channel_dimension_format(video, num_channels=(1, 3, 4))
    if channel_dim == ChannelDimension.FIRST:
        return video.shape[-2], video.shape[-1]
    elif channel_dim == ChannelDimension.LAST:
        return video.shape[-3], video.shape[-2]
    else:
        raise ValueError(f"Unsupported data format: {channel_dim}")
def get_uniform_frame_indices(total_num_frames: int, num_frames: Optional[int] = None):
    if num_frames is not None:
        indices = np.arange(0, total_num_frames, total_num_frames / num_frames).astype(int)
    else:
        indices = np.arange(0, total_num_frames).astype(int)
    return indices
def default_sample_indices_fn(metadata: VideoMetadata, num_frames=None, fps=None, **kwargs):
    total_num_frames = metadata.total_num_frames
    video_fps = metadata.fps
    if num_frames is None and fps is not None:
        num_frames = int(total_num_frames / video_fps * fps)
        if num_frames > total_num_frames:
            raise ValueError(
                f"When loading the video with fps={fps}, we computed num_frames={num_frames} "
                f"which exceeds total_num_frames={total_num_frames}. Check fps or video metadata."
            )
    if num_frames is not None:
        indices = np.arange(0, total_num_frames, total_num_frames / num_frames, dtype=int)
    else:
        indices = np.arange(0, total_num_frames, dtype=int)
    return indices
def read_video_opencv(
    video_path: Union["URL", "Path"],
    sample_indices_fn: Callable,
    **kwargs,
) -> tuple[np.ndarray, VideoMetadata]:
    requires_backends(read_video_opencv, ["cv2"])
    import cv2
    video = cv2.VideoCapture(video_path)
    total_num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    video_fps = video.get(cv2.CAP_PROP_FPS)
    duration = total_num_frames / video_fps if video_fps else 0
    metadata = VideoMetadata(
        total_num_frames=int(total_num_frames),
        fps=float(video_fps),
        duration=float(duration),
        video_backend="opencv",
        height=int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        width=int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
    )
    indices = sample_indices_fn(metadata=metadata, **kwargs)
    index = 0
    frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        if index in indices:
            height, width, channel = frame.shape
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame[0:height, 0:width, 0:channel])
        if success:
            index += 1
        if index >= total_num_frames:
            break
    video.release()
    metadata.frames_indices = indices
    return np.stack(frames), metadata
def read_video_decord(
    video_path: Union["URL", "Path"],
    sample_indices_fn: Callable,
    **kwargs,
):
    requires_backends(read_video_decord, ["decord"])
    from decord import VideoReader, cpu
    vr = VideoReader(uri=video_path, ctx=cpu(0))
    video_fps = vr.get_avg_fps()
    total_num_frames = len(vr)
    duration = total_num_frames / video_fps if video_fps else 0
    metadata = VideoMetadata(
        total_num_frames=int(total_num_frames),
        fps=float(video_fps),
        duration=float(duration),
        video_backend="decord",
    )
    indices = sample_indices_fn(metadata=metadata, **kwargs)
    video = vr.get_batch(indices).asnumpy()
    metadata.update(
        {
            "frames_indices": indices,
            "height": video.shape[1],
            "width": video.shape[2],
        }
    )
    return video, metadata
def read_video_pyav(
    video_path: Union["URL", "Path"],
    sample_indices_fn: Callable,
    **kwargs,
):
    requires_backends(read_video_pyav, ["av"])
    import av
    container = av.open(video_path)
    total_num_frames = container.streams.video[0].frames
    video_fps = container.streams.video[0].average_rate
    duration = total_num_frames / video_fps if video_fps else 0
    metadata = VideoMetadata(
        total_num_frames=int(total_num_frames),
        fps=float(video_fps),
        duration=float(duration),
        video_backend="pyav",
        height=container.streams.video[0].height,
        width=container.streams.video[0].width,
    )
    indices = sample_indices_fn(metadata=metadata, **kwargs)
    frames = []
    container.seek(0)
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= 0 and i in indices:
            frames.append(frame)
    video = np.stack([x.to_ndarray(format="rgb24") for x in frames])
    metadata.frames_indices = indices
    return video, metadata
def read_video_torchvision(
    video_path: Union["URL", "Path"],
    sample_indices_fn: Callable,
    **kwargs,
):
    warnings.warn(
        "Using `torchvision` for video decoding is deprecated and will be removed in future versions. "
        "Please use `torchcodec` instead."
    )
    video, _, info = torchvision_io.read_video(
        video_path,
        start_pts=0.0,
        end_pts=None,
        pts_unit="sec",
        output_format="TCHW",
    )
    video_fps = info["video_fps"]
    total_num_frames = video.size(0)
    duration = total_num_frames / video_fps if video_fps else 0
    metadata = VideoMetadata(
        total_num_frames=int(total_num_frames),
        fps=float(video_fps),
        duration=float(duration),
        video_backend="torchvision",
    )
    indices = sample_indices_fn(metadata=metadata, **kwargs)
    video = video[indices].contiguous()
    metadata.update(
        {
            "frames_indices": indices,
            "height": video.shape[2],
            "width": video.shape[3],
        }
    )
    return video, metadata
def read_video_torchcodec(
    video_path: Union["URL", "Path"],
    sample_indices_fn: Callable,
    **kwargs,
):
    requires_backends(read_video_torchcodec, ["torchcodec"])
    from torchcodec.decoders import VideoDecoder
    decoder = VideoDecoder(
        video_path,
        seek_mode="exact",
        num_ffmpeg_threads=0,
        device=kwargs.get("device"),
    )
    metadata = VideoMetadata(
        total_num_frames=decoder.metadata.num_frames,
        fps=decoder.metadata.average_fps,
        duration=decoder.metadata.duration_seconds,
        video_backend="torchcodec",
        height=decoder.metadata.height,
        width=decoder.metadata.width,
    )
    indices = sample_indices_fn(metadata=metadata, **kwargs)
    video = decoder.get_frames_at(indices=indices).data.contiguous()
    metadata.frames_indices = indices
    return video, metadata
VIDEO_DECODERS = {
    "decord": read_video_decord,
    "opencv": read_video_opencv,
    "pyav": read_video_pyav,
    "torchvision": read_video_torchvision,
    "torchcodec": read_video_torchcodec,
}
def load_video(
    video: VideoInput,
    num_frames: Optional[int] = None,
    fps: Optional[Union[int, float]] = None,
    backend: str = "pyav",
    sample_indices_fn: Optional[Callable] = None,
    **kwargs,
) -> np.ndarray:
    if fps is not None and num_frames is not None and sample_indices_fn is None:
        raise ValueError(
            "`num_frames`, `fps`, and `sample_indices_fn` are mutually exclusive arguments, please use only one!"
        )
    if sample_indices_fn is None:
        def sample_indices_fn_func(metadata, **fn_kwargs):
            return default_sample_indices_fn(metadata, num_frames=num_frames, fps=fps, **fn_kwargs)
        sample_indices_fn = sample_indices_fn_func
    if not isinstance(video, str):
        metadata = [None] * len(video)
        return video, metadata
    if urlparse(video).netloc in ["www.youtube.com", "youtube.com"]:
        if not is_yt_dlp_available():
            raise ImportError("To load a video from YouTube url you have  to install `yt_dlp` first.")
        requires_backends(load_video, ["yt_dlp"])
        from yt_dlp import YoutubeDL
        buffer = BytesIO()
        with redirect_stdout(buffer), YoutubeDL() as f:
            f.download([video])
        bytes_obj = buffer.getvalue()
        file_obj = BytesIO(bytes_obj)
    elif video.startswith("http://") or video.startswith("https://"):
        file_obj = BytesIO(requests.get(video).content)
    elif os.path.isfile(video):
        file_obj = video
    else:
        raise TypeError("Incorrect format used for video. Should be an url linking to an video or a local path.")
    video_is_url = video.startswith("http://") or video.startswith("https://")
    if video_is_url and backend == "opencv":
        raise ValueError("If you are trying to load a video from URL, you cannot use 'opencv' as backend")
    if (
        (not is_decord_available() and backend == "decord")
        or (not is_av_available() and backend == "pyav")
        or (not is_cv2_available() and backend == "opencv")
        or (not is_torchvision_available() and backend == "torchvision")
        or (not is_torchcodec_available() and backend == "torchcodec")
    ):
        raise ImportError(
            f"You chose backend={backend} for loading the video but the required library is not found in your environment "
            f"Make sure to install {backend} before loading the video."
        )
    video_decoder = VIDEO_DECODERS[backend]
    video, metadata = video_decoder(file_obj, sample_indices_fn, **kwargs)
    return video, metadata
def convert_to_rgb(
    video: np.ndarray,
    input_data_format: Optional[Union[str, ChannelDimension]] = None,
) -> np.ndarray:
    if not isinstance(video, np.ndarray):
        raise TypeError(f"Video has to be a numpy array to convert to RGB format, but found {type(video)}")
    if input_data_format is None:
        input_data_format = infer_channel_dimension_format(video)
    video = to_channel_dimension_format(video, ChannelDimension.FIRST, input_channel_dim=input_data_format)
    if video.shape[-3] == 3:
        return video
    if video.shape[-3] == 1:
        return video.repeat(3, -3)
    if not (video[..., 3, :, :] < 255).any():
        return video
    alpha = video[..., 3, :, :] / 255.0
    video = (1 - alpha[..., None, :, :]) * 255 + alpha[..., None, :, :] * video[..., 3, :, :]
    return video
def pad(
    video: np.ndarray,
    padding: Union[int, tuple[int, int], Iterable[tuple[int, int]]],
    mode: PaddingMode = PaddingMode.CONSTANT,
    constant_values: Union[float, Iterable[float]] = 0.0,
    data_format: Optional[Union[str, ChannelDimension]] = None,
    input_data_format: Optional[Union[str, ChannelDimension]] = None,
) -> np.ndarray:
    if input_data_format is None:
        input_data_format = infer_channel_dimension_format(video)
    def _expand_for_data_format(values):
        if isinstance(values, (int, float)):
            values = ((values, values), (values, values))
        elif isinstance(values, tuple) and len(values) == 1:
            values = ((values[0], values[0]), (values[0], values[0]))
        elif isinstance(values, tuple) and len(values) == 2 and isinstance(values[0], int):
            values = (values, values)
        elif isinstance(values, tuple) and len(values) == 2 and isinstance(values[0], tuple):
            pass
        else:
            raise ValueError(f"Unsupported format: {values}")
        values = (
            ((0, 0), (0, 0), *values) if input_data_format == ChannelDimension.FIRST else ((0, 0), *values, (0, 0))
        )
        values = (0, *values) if video.ndim == 5 else values
        return values
    padding_map = {
        PaddingMode.CONSTANT: "constant",
        PaddingMode.REFLECT: "reflect",
        PaddingMode.REPLICATE: "replicate",
        PaddingMode.SYMMETRIC: "symmetric",
    }
    padding = _expand_for_data_format(padding)
    pad_kwargs = {}
    if mode not in padding_map:
        raise ValueError(f"Invalid padding mode: {mode}")
    elif mode == PaddingMode.CONSTANT:
        pad_kwargs["constant_values"] = _expand_for_data_format(constant_values)
    video = np.pad(video, padding, mode=padding_map[mode], **pad_kwargs)
    video = to_channel_dimension_format(video, data_format, input_data_format) if data_format is not None else video
    return video
def group_videos_by_shape(
    videos: list["torch.Tensor"],
) -> tuple[dict[tuple[int, int], "torch.Tensor"], dict[int, tuple[tuple[int, int], int]]]:
    grouped_videos = {}
    grouped_videos_index = {}
    for i, video in enumerate(videos):
        shape = video.shape[-2::]
        num_frames = video.shape[-4]
        shape = (num_frames, *shape)
        if shape not in grouped_videos:
            grouped_videos[shape] = []
        grouped_videos[shape].append(video)
        grouped_videos_index[i] = (shape, len(grouped_videos[shape]) - 1)
    grouped_videos = {shape: torch.stack(videos, dim=0) for shape, videos in grouped_videos.items()}
    return grouped_videos, grouped_videos_index
def reorder_videos(
    processed_videos: dict[tuple[int, int], "torch.Tensor"],
    grouped_videos_index: dict[int, tuple[tuple[int, int], int]],
) -> list["torch.Tensor"]:
    return [
        processed_videos[grouped_videos_index[i][0]][grouped_videos_index[i][1]]
        for i in range(len(grouped_videos_index))
    ]