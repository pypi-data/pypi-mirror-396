from typing import Optional, Union
import torch
from torchvision.transforms.v2 import functional as F
from ...image_processing_utils import BatchFeature
from ...image_processing_utils_fast import (
    BaseImageProcessorFast,
    DefaultFastImageProcessorKwargs,
    group_images_by_shape,
    reorder_images,
)
from ...image_transforms import get_resize_output_image_size
from ...image_utils import (
    IMAGENET_STANDARD_MEAN,
    IMAGENET_STANDARD_STD,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
)
from ...processing_utils import Unpack
from ...utils import (
    TensorType,
    auto_docstring,
)
class ConvNextFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    crop_pct: Optional[float]
@auto_docstring
class ConvNextImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BILINEAR
    image_mean = IMAGENET_STANDARD_MEAN
    image_std = IMAGENET_STANDARD_STD
    size = {"shortest_edge": 384}
    default_to_square = False
    do_resize = True
    do_rescale = True
    do_normalize = True
    crop_pct = 224 / 256
    valid_kwargs = ConvNextFastImageProcessorKwargs
    def __init__(self, **kwargs: Unpack[ConvNextFastImageProcessorKwargs]):
        super().__init__(**kwargs)
    @auto_docstring
    def preprocess(self, images: ImageInput, **kwargs: Unpack[ConvNextFastImageProcessorKwargs]) -> BatchFeature:
        return super().preprocess(images, **kwargs)
    def resize(
        self,
        image: "torch.Tensor",
        size: dict[str, int],
        crop_pct: float,
        interpolation: PILImageResampling = PILImageResampling.BICUBIC,
        **kwargs,
    ) -> "torch.Tensor":
        if not size.shortest_edge:
            raise ValueError(f"Size dictionary must contain 'shortest_edge' key. Got {size.keys()}")
        shortest_edge = size["shortest_edge"]
        if shortest_edge < 384:
            resize_shortest_edge = int(shortest_edge / crop_pct)
            resize_size = get_resize_output_image_size(
                image, size=resize_shortest_edge, default_to_square=False, input_data_format=ChannelDimension.FIRST
            )
            image = F.resize(
                image,
                resize_size,
                interpolation=interpolation,
                **kwargs,
            )
            return F.center_crop(
                image,
                (shortest_edge, shortest_edge),
                **kwargs,
            )
        else:
            return F.resize(
                image,
                (shortest_edge, shortest_edge),
                interpolation=interpolation,
                **kwargs,
            )
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        do_resize: bool,
        size: dict[str, int],
        crop_pct: float,
        interpolation: Optional["F.InterpolationMode"],
        do_center_crop: bool,
        crop_size: int,
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
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
                stacked_images = self.resize(
                    image=stacked_images, size=size, crop_pct=crop_pct, interpolation=interpolation
                )
            resized_images_grouped[shape] = stacked_images
        resized_images = reorder_images(resized_images_grouped, grouped_images_index)
        grouped_images, grouped_images_index = group_images_by_shape(resized_images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_center_crop:
                stacked_images = self.center_crop(stacked_images, crop_size)
            stacked_images = self.rescale_and_normalize(
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images}, tensor_type=return_tensors)
__all__ = ["ConvNextImageProcessorFast"]