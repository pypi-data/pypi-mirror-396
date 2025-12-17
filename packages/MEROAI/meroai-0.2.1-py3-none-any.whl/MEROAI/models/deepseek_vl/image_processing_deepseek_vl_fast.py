from typing import Optional, Union
import torch
import torch.nn.functional as F
from ...image_processing_utils import BatchFeature
from ...image_processing_utils_fast import (
    BaseImageProcessorFast,
    DefaultFastImageProcessorKwargs,
    group_images_by_shape,
    reorder_images,
)
from ...image_utils import OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, PILImageResampling, SizeDict
from ...processing_utils import Unpack
from ...utils import TensorType, auto_docstring
class DeepseekVLFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    min_size: int
@auto_docstring
class DeepseekVLImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BICUBIC
    image_mean = OPENAI_CLIP_MEAN
    image_std = OPENAI_CLIP_STD
    size = {"height": 384, "width": 384}
    min_size = 14
    do_resize = True
    do_rescale = True
    do_normalize = True
    do_pad = True
    valid_kwargs = DeepseekVLFastImageProcessorKwargs
    def __init__(self, **kwargs: Unpack[DeepseekVLFastImageProcessorKwargs]):
        super().__init__(**kwargs)
        if kwargs.get("image_mean") is None:
            background_color = (127, 127, 127)
        else:
            background_color = tuple(int(x * 255) for x in kwargs.get("image_mean"))
        self.background_color = tuple(background_color)
    def resize(
        self,
        image: "torch.Tensor",
        size: SizeDict,
        min_size: int,
        interpolation: Optional["F.InterpolationMode"] = None,
        antialias: bool = True,
        **kwargs,
    ) -> "torch.Tensor":
        if size.height is None or size.width is None or size.height != size.width:
            raise ValueError(
                f"Output height and width must be the same. Got height={size['height']} and width={size['width']}"
            )
        size = size.height
        height, width = image.shape[-2:]
        max_size = max(height, width)
        delta = size / max_size
        output_size_nonpadded = SizeDict(
            height=max(int(height * delta), min_size),
            width=max(int(width * delta), min_size),
        )
        return super().resize(image, size=output_size_nonpadded, interpolation=interpolation, antialias=antialias)
    def pad_to_square(
        self,
        images: "torch.Tensor",
        background_color: Union[int, tuple[int, int, int]] = 0,
    ) -> "torch.Tensor":
        height, width = images.shape[-2:]
        num_channels = images.shape[1]
        batch_size = images.shape[0]
        if height == width:
            return images
        max_dim = max(height, width)
        if isinstance(background_color, int):
            background_color = [background_color]
        elif len(background_color) != num_channels:
            raise ValueError(
                f"background_color must have no more than {num_channels} elements to match the number of channels"
            )
        padded_images = torch.zeros(
            (batch_size, num_channels, max_dim, max_dim), dtype=images.dtype, device=images.device
        )
        for i, color in enumerate(background_color):
            padded_images[:, i, :, :] = color
        if width > height:
            start = (max_dim - height) // 2
            padded_images[:, :, start : start + height, :] = images
        else:
            start = (max_dim - width) // 2
            padded_images[:, :, :, start : start + width] = images
        return padded_images
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        do_resize: bool,
        size: SizeDict,
        min_size: int,
        interpolation: Optional["F.InterpolationMode"],
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
        image_mean: Optional[Union[float, list[float]]],
        image_std: Optional[Union[float, list[float]]],
        disable_grouping: Optional[bool],
        return_tensors: Optional[Union[str, TensorType]],
        do_pad: bool = True,
        **kwargs,
    ) -> BatchFeature:
        grouped_images, grouped_images_index = group_images_by_shape(images, disable_grouping=disable_grouping)
        resized_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_resize:
                stacked_images = self.resize(
                    image=stacked_images, size=size, min_size=min_size, interpolation=interpolation
                )
            resized_images_grouped[shape] = stacked_images
        resized_images = reorder_images(resized_images_grouped, grouped_images_index)
        grouped_images, grouped_images_index = group_images_by_shape(resized_images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_pad:
                stacked_images = self.pad_to_square(stacked_images, background_color=self.background_color)
            stacked_images = self.rescale_and_normalize(
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images}, tensor_type=return_tensors)
__all__ = ["DeepseekVLImageProcessorFast"]