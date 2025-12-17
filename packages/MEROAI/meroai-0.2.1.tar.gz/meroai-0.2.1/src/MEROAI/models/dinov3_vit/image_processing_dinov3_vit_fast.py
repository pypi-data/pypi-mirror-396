from typing import Optional, Union
import torch
from torchvision.transforms.v2 import functional as F
from MEROAI.image_processing_base import BatchFeature
from MEROAI.image_processing_utils_fast import BaseImageProcessorFast, group_images_by_shape, reorder_images
from MEROAI.image_utils import IMAGENET_DEFAULT_MEAN, IMAGENET_DEFAULT_STD, PILImageResampling, SizeDict
from MEROAI.utils import (
    TensorType,
    auto_docstring,
    logging,
)
from MEROAI.utils.import_utils import requires
logger = logging.get_logger(__name__)
@auto_docstring
@requires(backends=("torchvision", "torch"))
class DINOv3ViTImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BILINEAR
    image_mean = IMAGENET_DEFAULT_MEAN
    image_std = IMAGENET_DEFAULT_STD
    size = {"height": 224, "width": 224}
    do_resize = True
    do_rescale = True
    do_normalize = True
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
            if do_rescale:
                stacked_images = self.rescale(stacked_images, rescale_factor)
            if do_resize:
                stacked_images = self.resize(
                    image=stacked_images, size=size, interpolation=interpolation, antialias=True
                )
            resized_images_grouped[shape] = stacked_images
        resized_images = reorder_images(resized_images_grouped, grouped_images_index)
        grouped_images, grouped_images_index = group_images_by_shape(resized_images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_center_crop:
                stacked_images = self.center_crop(stacked_images, crop_size)
            if do_normalize:
                stacked_images = self.normalize(stacked_images, image_mean, image_std)
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images}, tensor_type=return_tensors)
__all__ = ["DINOv3ViTImageProcessorFast"]