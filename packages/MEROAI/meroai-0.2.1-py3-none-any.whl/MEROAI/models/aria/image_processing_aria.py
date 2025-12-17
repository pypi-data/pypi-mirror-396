from collections.abc import Iterable
from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_patch_output_size, select_best_resolution
from ...image_transforms import PaddingMode, convert_to_rgb, pad, resize, to_channel_dimension_format
from ...image_utils import (
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    get_image_size,
    infer_channel_dimension_format,
    is_scaled_image,
    make_flat_list_of_images,
    to_numpy_array,
    valid_images,
    validate_preprocess_arguments,
)
from ...utils import TensorType, logging
logger = logging.get_logger(__name__)
def divide_to_patches(image: np.ndarray, patch_size: int, input_data_format) -> list[np.ndarray]:
    patches = []
    height, width = get_image_size(image, channel_dim=input_data_format)
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size):
            if input_data_format == ChannelDimension.LAST:
                patch = image[i : i + patch_size, j : j + patch_size]
            else:
                patch = image[:, i : i + patch_size, j : j + patch_size]
            patches.append(patch)
    return patches
class AriaImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "pixel_mask", "num_crops"]
    def __init__(
        self,
        image_mean: Optional[list[float]] = None,
        image_std: Optional[list[float]] = None,
        max_image_size: int = 980,
        min_image_size: int = 336,
        split_resolutions: Optional[list[tuple[int, int]]] = None,
        split_image: Optional[bool] = False,
        do_convert_rgb: Optional[bool] = True,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: Optional[bool] = True,
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if image_mean is None:
            image_mean = [0.5, 0.5, 0.5]
        if image_std is None:
            image_std = [0.5, 0.5, 0.5]
        self.max_image_size = max_image_size
        self.min_image_size = min_image_size
        self.image_mean = image_mean
        self.image_std = image_std
        self.split_image = split_image
        if split_resolutions is None:
            split_resolutions = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 4), (2, 3), (2, 2), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (6, 1), (7, 1), (8, 1)]
            split_resolutions = [(el[0] * 490, el[1] * 490) for el in split_resolutions]
        self.split_resolutions = split_resolutions
        self.do_convert_rgb = do_convert_rgb
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.resample = resample
    def preprocess(
        self,
        images: Union[ImageInput, list[ImageInput]],
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        max_image_size: Optional[int] = None,
        min_image_size: Optional[int] = None,
        split_image: Optional[bool] = None,
        do_convert_rgb: Optional[bool] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        resample: Optional[PILImageResampling] = None,
        return_tensors: Optional[Union[str, TensorType]] = "pt",
        data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        max_image_size = max_image_size if max_image_size is not None else self.max_image_size
        min_image_size = min_image_size if min_image_size is not None else self.min_image_size
        split_image = split_image if split_image is not None else self.split_image
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        resample = resample if resample is not None else self.resample
        if max_image_size not in [490, 980]:
            raise ValueError("max_image_size must be either 490 or 980")
        images = self.fetch_images(images)
        images = make_flat_list_of_images(images)
        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )
        validate_preprocess_arguments(
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            resample=resample,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
        )
        if do_convert_rgb:
            images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if do_rescale and is_scaled_image(images[0]):
            logger.warning_once(
                "It looks like you are trying to rescale already rescaled images. If the input"
                " images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again."
            )
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(images[0])
        pixel_values = []
        pixel_masks = []
        num_crops = None
        for image in images:
            if split_image:
                crop_images = self.get_image_patches(
                    image,
                    self.split_resolutions,
                    max_image_size,
                    resample,
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
            else:
                crop_images = [image]
            if num_crops is None or len(crop_images) > num_crops:
                num_crops = len(crop_images)
            for crop_image in crop_images:
                h, w = get_image_size(crop_image)
                scale = max_image_size / max(h, w)
                if w >= h:
                    new_size = (max(int(h * scale), min_image_size), max_image_size)
                else:
                    new_size = (max_image_size, max(int(w * scale), min_image_size))
                crop_image_resized = resize(
                    crop_image,
                    new_size,
                    resample=resample,
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
                padding_bottom, padding_right = max_image_size - new_size[0], max_image_size - new_size[1]
                crop_image_padded = pad(
                    crop_image_resized,
                    ((0, padding_bottom), (0, padding_right)),
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
                pixel_mask = np.zeros((max_image_size, max_image_size), dtype=bool)
                pixel_mask[: new_size[0], : new_size[1]] = 1
                pixel_masks.append(pixel_mask)
                if do_rescale:
                    crop_image_padded = self.rescale(
                        image=crop_image_padded, scale=rescale_factor, input_data_format=input_data_format
                    )
                if do_normalize:
                    crop_image_padded = self.normalize(
                        crop_image_padded,
                        self.image_mean,
                        self.image_std,
                        data_format=input_data_format,
                        input_data_format=input_data_format,
                    )
                    crop_image_padded = (
                        to_channel_dimension_format(crop_image_padded, data_format, input_data_format)
                        if data_format is not None
                        else crop_image_padded
                    )
                pixel_values.append(crop_image_padded)
        return BatchFeature(
            data={
                "pixel_values": np.stack(pixel_values, axis=0),
                "pixel_mask": np.stack(pixel_masks, axis=0),
                "num_crops": num_crops,
            },
            tensor_type=return_tensors,
        )
    def _resize_for_patching(
        self, image: np.ndarray, target_resolution: tuple, resample, input_data_format: ChannelDimension
    ) -> np.ndarray:
        new_height, new_width = get_patch_output_size(image, target_resolution, input_data_format)
        resized_image = resize(image, (new_height, new_width), resample=resample, input_data_format=input_data_format)
        return resized_image
    def _get_padding_size(self, original_resolution: tuple, target_resolution: tuple):
        original_height, original_width = original_resolution
        target_height, target_width = target_resolution
        paste_x, r_x = divmod(target_width - original_width, 2)
        paste_y, r_y = divmod(target_height - original_height, 2)
        return (paste_y, paste_y + r_y), (paste_x, paste_x + r_x)
    def _pad_for_patching(
        self, image: np.ndarray, target_resolution: tuple, input_data_format: ChannelDimension
    ) -> np.ndarray:
        new_resolution = get_patch_output_size(image, target_resolution, input_data_format)
        padding = self._get_padding_size(new_resolution, target_resolution)
        padded_image = self.pad(image, padding=padding)
        return padded_image
    def pad(
        self,
        image: np.ndarray,
        padding: Union[int, tuple[int, int], Iterable[tuple[int, int]]],
        mode: PaddingMode = PaddingMode.CONSTANT,
        constant_values: Union[float, Iterable[float]] = 0.0,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> np.ndarray:
        if isinstance(padding, int) or len(padding) != 4:
            return pad(image, padding, mode, constant_values, data_format, input_data_format)
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        padding_mode_mapping = {
            PaddingMode.CONSTANT: "constant",
            PaddingMode.REFLECT: "reflect",
            PaddingMode.REPLICATE: "edge",
            PaddingMode.SYMMETRIC: "symmetric",
        }
        image = np.pad(image, padding, mode=padding_mode_mapping[mode], constant_values=constant_values)
        image = (
            to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image
        )
        return image
    def get_image_patches(
        self,
        image: np.ndarray,
        grid_pinpoints: list[tuple[int, int]],
        patch_size: int,
        resample: PILImageResampling,
        data_format: ChannelDimension,
        input_data_format: ChannelDimension,
    ) -> list[np.ndarray]:
        if not isinstance(grid_pinpoints, list):
            raise TypeError("grid_pinpoints must be a list of possible resolutions.")
        possible_resolutions = grid_pinpoints
        image_size = get_image_size(image, channel_dim=input_data_format)
        best_resolution = select_best_resolution(image_size, possible_resolutions)
        resized_image = self._resize_for_patching(
            image, best_resolution, resample=resample, input_data_format=input_data_format
        )
        padded_image = self._pad_for_patching(resized_image, best_resolution, input_data_format=input_data_format)
        patches = divide_to_patches(padded_image, patch_size=patch_size, input_data_format=input_data_format)
        patches = [
            to_channel_dimension_format(patch, channel_dim=data_format, input_channel_dim=input_data_format)
            for patch in patches
        ]
        return patches
    def get_number_of_image_patches(self, height: int, width: int, images_kwargs=None):
        split_image = images_kwargs.get("split_image", self.split_image)
        max_image_size = images_kwargs.get("max_image_size", self.max_image_size)
        resized_height, resized_width = select_best_resolution((height, width), self.split_resolutions)
        num_patches = 1 if not split_image else resized_height // max_image_size * resized_width // max_image_size
        return num_patches
__all__ = ["AriaImageProcessor"]