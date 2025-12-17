from functools import lru_cache
from typing import Optional, Union
import numpy as np
import torch
from torchvision.transforms.v2 import functional as F
from ...image_processing_utils import BatchFeature
from ...image_processing_utils_fast import (
    BaseImageProcessorFast,
    DefaultFastImageProcessorKwargs,
    group_images_by_shape,
    reorder_images,
)
from ...image_utils import OPENAI_CLIP_MEAN, OPENAI_CLIP_STD, ImageInput, PILImageResampling, SizeDict
from ...processing_utils import Unpack
from ...utils import TensorType, auto_docstring
class Cohere2VisionFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    crop_to_patches: Optional[bool]
    min_patches: Optional[int]
    max_patches: Optional[int]
@lru_cache(maxsize=10)
def get_all_supported_aspect_ratios(max_image_tiles: int) -> list[tuple[int, int]]:
    aspect_ratios = []
    for width in range(1, max_image_tiles + 1):
        for height in range(1, max_image_tiles + 1):
            if width * height <= max_image_tiles:
                aspect_ratios.append((width, height))
    return aspect_ratios
def get_optimal_tiled_canvas(
    original_image_size: tuple[int, int],
    target_tile_size: tuple[int, int],
    min_image_tiles: int,
    max_image_tiles: int,
) -> tuple[int, int]:
    possible_resolutions = get_all_supported_aspect_ratios(max_image_tiles)
    possible_resolutions = sorted(possible_resolutions, key=lambda x: x[0] * x[1])
    image_height, image_width = original_image_size
    patch_size_height, patch_size_width = target_tile_size
    candidate_resolutions = np.array(possible_resolutions) * patch_size_height
    original_size = np.stack([image_height, image_width])
    required_scales = candidate_resolutions / original_size
    required_scale = np.min(required_scales, axis=-1, keepdims=True)
    if np.all(required_scale < 1):
        best_grid = possible_resolutions[np.argmax(required_scale)]
    else:
        required_scale = np.where(required_scale < 1.0, 10e9, required_scale)
        best_grid = possible_resolutions[np.argmin(required_scale)]
    return best_grid
@auto_docstring
class Cohere2VisionImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BICUBIC
    image_mean = OPENAI_CLIP_MEAN
    image_std = OPENAI_CLIP_STD
    size = {"height": 512, "width": 512}
    do_resize = True
    do_rescale = True
    do_normalize = True
    do_convert_rgb = True
    crop_to_patches = True
    min_patches = 1
    max_patches = 12
    valid_kwargs = Cohere2VisionFastImageProcessorKwargs
    patch_size = 16
    def __init__(self, **kwargs: Unpack[Cohere2VisionFastImageProcessorKwargs]):
        super().__init__(**kwargs)
    @auto_docstring
    def preprocess(self, images: ImageInput, **kwargs: Unpack[Cohere2VisionFastImageProcessorKwargs]) -> BatchFeature:
        return super().preprocess(images, **kwargs)
    def crop_image_to_patches(
        self,
        images: "torch.Tensor",
        min_patches: int,
        max_patches: int,
        use_thumbnail: bool = True,
        patch_size: Optional[Union[tuple, int, dict]] = None,
        interpolation: Optional["F.InterpolationMode"] = None,
    ):
        patch_size_height, patch_size_width = patch_size.height, patch_size.width
        original_height, original_width = images.shape[-2:]
        num_columns, num_rows = get_optimal_tiled_canvas(
            (original_height, original_width), (patch_size_height, patch_size_width), min_patches, max_patches
        )
        target_width = patch_size_width * num_columns
        target_height = patch_size_height * num_rows
        num_blocks = num_columns * num_rows
        resized_image = self.resize(
            images, SizeDict(height=target_height, width=target_width), interpolation=interpolation
        )
        processed_images = []
        for i in range(num_blocks):
            column = i % num_columns
            row = i // num_columns
            box = (
                column * patch_size_width,
                row * patch_size_height,
                (column + 1) * patch_size_width,
                (row + 1) * patch_size_height,
            )
            patch_image = resized_image[..., box[1] : box[3], box[0] : box[2]]
            processed_images.append(patch_image)
        if use_thumbnail and len(processed_images) != 1:
            thumbnail_img = self.resize(images, patch_size, interpolation=interpolation)
            processed_images.append(thumbnail_img)
        processed_images = torch.stack(processed_images, dim=0).transpose(0, 1).contiguous()
        return processed_images
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        do_resize: bool,
        size: SizeDict,
        crop_to_patches: bool,
        min_patches: int,
        max_patches: int,
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
        if crop_to_patches:
            grouped_images, grouped_images_index = group_images_by_shape(images, disable_grouping=disable_grouping)
            processed_images_grouped = {}
            num_patches = {}
            for shape, stacked_images in grouped_images.items():
                stacked_images = self.crop_image_to_patches(
                    stacked_images,
                    min_patches,
                    max_patches,
                    patch_size=size,
                    interpolation=interpolation,
                )
                processed_images_grouped[shape] = stacked_images
                num_patches[shape] = [stacked_images.shape[1]] * stacked_images.shape[0]
            images = reorder_images(processed_images_grouped, grouped_images_index)
            images = [image for images_list in images for image in images_list]
            num_patches = reorder_images(num_patches, grouped_images_index)
        else:
            num_patches = [1] * len(images)
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
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(
            data={"pixel_values": processed_images, "num_patches": num_patches}, tensor_type=return_tensors
        )
    def get_number_of_image_patches(self, height: int, width: int, images_kwargs=None):
        min_patches = images_kwargs.get("min_patches", self.min_patches)
        max_patches = images_kwargs.get("max_patches", self.max_patches)
        patch_size = images_kwargs.get("patch_size", self.size)
        crop_to_patches = images_kwargs.get("crop_to_patches", self.crop_to_patches)
        num_patches = 1
        if crop_to_patches and max_patches > 1:
            num_columns, num_rows = get_optimal_tiled_canvas(
                (height, width), (patch_size["height"], patch_size["width"]), min_patches, max_patches
            )
            if num_columns * num_rows > 1:
                num_patches += num_columns * num_rows
        return num_patches
__all__ = ["Cohere2VisionImageProcessorFast"]