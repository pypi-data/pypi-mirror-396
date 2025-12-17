from functools import lru_cache
from typing import Optional, Union
import torch
from torchvision.transforms.v2 import functional as F
from ...image_processing_utils_fast import BaseImageProcessorFast, BatchFeature, DefaultFastImageProcessorKwargs
from ...image_transforms import group_images_by_shape, reorder_images
from ...image_utils import IMAGENET_STANDARD_MEAN, IMAGENET_STANDARD_STD, ImageInput, PILImageResampling, SizeDict
from ...processing_utils import Unpack
from ...utils import (
    TensorType,
    auto_docstring,
)
class EfficientNetFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    rescale_offset: bool
    include_top: bool
@auto_docstring
class EfficientNetImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.NEAREST
    image_mean = IMAGENET_STANDARD_MEAN
    image_std = IMAGENET_STANDARD_STD
    size = {"height": 346, "width": 346}
    crop_size = {"height": 289, "width": 289}
    do_resize = True
    do_center_crop = False
    do_rescale = True
    rescale_factor = 1 / 255
    rescale_offset = False
    do_normalize = True
    include_top = True
    valid_kwargs = EfficientNetFastImageProcessorKwargs
    def __init__(self, **kwargs: Unpack[EfficientNetFastImageProcessorKwargs]):
        super().__init__(**kwargs)
    def rescale(
        self,
        image: "torch.Tensor",
        scale: float,
        offset: Optional[bool] = True,
        **kwargs,
    ) -> "torch.Tensor":
        rescaled_image = image * scale
        if offset:
            rescaled_image -= 1
        return rescaled_image
    @lru_cache(maxsize=10)
    def _fuse_mean_std_and_rescale_factor(
        self,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        device: Optional["torch.device"] = None,
        rescale_offset: Optional[bool] = False,
    ) -> tuple:
        if do_rescale and do_normalize and not rescale_offset:
            image_mean = torch.tensor(image_mean, device=device) * (1.0 / rescale_factor)
            image_std = torch.tensor(image_std, device=device) * (1.0 / rescale_factor)
            do_rescale = False
        return image_mean, image_std, do_rescale
    def rescale_and_normalize(
        self,
        images: "torch.Tensor",
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
        image_mean: Union[float, list[float]],
        image_std: Union[float, list[float]],
        rescale_offset: bool = False,
    ) -> "torch.Tensor":
        image_mean, image_std, do_rescale = self._fuse_mean_std_and_rescale_factor(
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            device=images.device,
            rescale_offset=rescale_offset,
        )
        if do_rescale:
            images = self.rescale(images, rescale_factor, rescale_offset)
        if do_normalize:
            images = self.normalize(images.to(dtype=torch.float32), image_mean, image_std)
        return images
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        do_resize: bool,
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"],
        do_center_crop: bool,
        crop_size: SizeDict,
        do_rescale: bool,
        rescale_factor: float,
        rescale_offset: bool,
        do_normalize: bool,
        include_top: bool,
        image_mean: Optional[Union[float, list[float]]],
        image_std: Optional[Union[float, list[float]]],
        disable_grouping: Optional[bool],
        return_tensors: Optional[Union[str, TensorType]],
        **kwargs,
    ) -> BatchFeature:
        grouped_images, grouped_images_index = group_images_by_shape(images, disable_grouping=disable_grouping)
        resized_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_resize:
                stacked_images = self.resize(image=stacked_images, size=size, interpolation=interpolation)
            resized_images_grouped[shape] = stacked_images
        resized_images = reorder_images(resized_images_grouped, grouped_images_index)
        grouped_images, grouped_images_index = group_images_by_shape(resized_images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_center_crop:
                stacked_images = self.center_crop(stacked_images, crop_size)
            stacked_images = self.rescale_and_normalize(
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std, rescale_offset
            )
            if include_top:
                stacked_images = self.normalize(stacked_images, 0, image_std)
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images}, tensor_type=return_tensors)
    @auto_docstring
    def preprocess(self, images: ImageInput, **kwargs: Unpack[EfficientNetFastImageProcessorKwargs]) -> BatchFeature:
        return super().preprocess(images, **kwargs)
__all__ = ["EfficientNetImageProcessorFast"]