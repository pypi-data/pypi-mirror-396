from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BaseImageProcessor
from ...image_processing_utils_fast import BatchFeature, get_size_dict
from ...image_transforms import convert_to_rgb, resize, to_channel_dimension_format
from ...image_utils import (
    OPENAI_CLIP_MEAN,
    OPENAI_CLIP_STD,
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
from ...utils import TensorType, filter_out_non_signature_kwargs, is_vision_available, logging
if is_vision_available():
    import PIL
logger = logging.get_logger(__name__)
class DeepseekVLHybridImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "high_res_pixel_values"]
    def __init__(
        self,
        do_resize: bool = True,
        size: Optional[dict[str, int]] = None,
        high_res_size: Optional[dict[str, int]] = None,
        min_size: int = 14,
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        high_res_resample: PILImageResampling = PILImageResampling.BICUBIC,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: bool = True,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        high_res_image_mean: Optional[Union[float, list[float]]] = None,
        high_res_image_std: Optional[Union[float, list[float]]] = None,
        do_convert_rgb: Optional[bool] = None,
        do_pad: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        high_res_size = high_res_size if high_res_size is not None else {"height": 1024, "width": 1024}
        high_res_size = get_size_dict(high_res_size, default_to_square=True)
        self.high_res_size = high_res_size
        self.high_res_image_mean = high_res_image_mean if high_res_image_mean is not None else OPENAI_CLIP_MEAN
        self.high_res_image_std = high_res_image_std if high_res_image_std is not None else OPENAI_CLIP_STD
        self.resample = resample
        self.high_res_resample = high_res_resample
        size = size if size is not None else {"height": 384, "width": 384}
        size = get_size_dict(size, default_to_square=True)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else OPENAI_CLIP_MEAN
        self.image_std = image_std if image_std is not None else OPENAI_CLIP_STD
        self.do_convert_rgb = do_convert_rgb
        self.do_pad = do_pad
        self.min_size = min_size
        if image_mean is None:
            self.background_color = (127, 127, 127)
        else:
            self.background_color = tuple(int(x * 255) for x in image_mean)
        if high_res_image_mean is None:
            self.high_res_background_color = (127, 127, 127)
        else:
            self.high_res_background_color = tuple(int(x * 255) for x in high_res_image_mean)
    def resize(
        self,
        image: np.ndarray,
        size: Union[dict[str, int], int],
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        height, width = get_image_size(image, input_data_format)
        max_size = max(height, width)
        size = get_size_dict(size, default_to_square=True)
        if size["height"] != size["width"]:
            raise ValueError(
                f"Output height and width must be the same. Got height={size['height']} and width={size['width']}"
            )
        size = size["height"]
        delta = size / max_size
        output_size_nonpadded = [
            max(int(height * delta), self.min_size),
            max(int(width * delta), self.min_size),
        ]
        image = resize(
            image,
            size=output_size_nonpadded,
            resample=resample,
            data_format=data_format,
            input_data_format=input_data_format,
            **kwargs,
        )
        return image
    @filter_out_non_signature_kwargs()
    def preprocess(
        self,
        images: ImageInput,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        high_res_size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        high_res_resample: Optional[PILImageResampling] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        high_res_image_mean: Optional[Union[float, list[float]]] = None,
        high_res_image_std: Optional[Union[float, list[float]]] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        do_convert_rgb: Optional[bool] = None,
        do_pad: Optional[bool] = None,
        background_color: Optional[tuple[int, int, int]] = None,
    ) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        resample = resample if resample is not None else self.resample
        high_res_resample = high_res_resample if high_res_resample is not None else self.high_res_resample
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        high_res_image_mean = high_res_image_mean if high_res_image_mean is not None else self.high_res_image_mean
        high_res_image_std = high_res_image_std if high_res_image_std is not None else self.high_res_image_std
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_pad = do_pad if do_pad is not None else self.do_pad
        background_color = background_color if background_color is not None else self.background_color
        size = size if size is not None else self.size
        size_dict = get_size_dict(size)
        high_res_size = high_res_size if high_res_size is not None else self.high_res_size
        high_res_size_dict = get_size_dict(high_res_size)
        images = self.fetch_images(images)
        images = make_flat_list_of_images(images)
        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )
        validate_preprocess_arguments(
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            do_resize=do_resize,
            size=size,
            resample=resample,
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
        all_images = []
        all_high_res_images = []
        for image in images:
            high_res_image = image
            if do_resize:
                high_res_image = self.resize(
                    image=high_res_image,
                    size=high_res_size_dict,
                    resample=high_res_resample,
                    input_data_format=input_data_format,
                )
                if do_pad:
                    high_res_image = self.pad_to_square(
                        image=high_res_image,
                        background_color=background_color,
                        input_data_format=input_data_format,
                    )
                image = self.resize(
                    image=high_res_image,
                    size=size_dict,
                    resample=resample,
                    input_data_format=input_data_format,
                )
                if do_pad:
                    image = self.pad_to_square(
                        image=image,
                        background_color=background_color,
                        input_data_format=input_data_format,
                    )
            if do_rescale:
                image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
                high_res_image = self.rescale(
                    image=high_res_image, scale=rescale_factor, input_data_format=input_data_format
                )
            if do_normalize:
                image = self.normalize(
                    image=image, mean=image_mean, std=image_std, input_data_format=input_data_format
                )
                high_res_image = self.normalize(
                    image=high_res_image,
                    mean=high_res_image_mean,
                    std=high_res_image_std,
                    input_data_format=input_data_format,
                )
            image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
            high_res_image = to_channel_dimension_format(
                high_res_image, data_format, input_channel_dim=input_data_format
            )
            all_images.append(image)
            all_high_res_images.append(high_res_image)
        data = {"pixel_values": all_images, "high_res_pixel_values": all_high_res_images}
        return BatchFeature(data=data, tensor_type=return_tensors)
    def pad_to_square(
        self,
        image: np.ndarray,
        background_color: Union[int, tuple[int, int, int]] = 0,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> np.ndarray:
        height, width = get_image_size(image, input_data_format)
        num_channels = image.shape[0] if input_data_format == ChannelDimension.FIRST else image.shape[-1]
        if height == width:
            image = (
                to_channel_dimension_format(image, data_format, input_data_format)
                if data_format is not None
                else image
            )
            return image
        max_dim = max(height, width)
        if isinstance(background_color, int):
            background_color = [background_color]
        elif len(background_color) != num_channels:
            raise ValueError(
                f"background_color must have no more than {num_channels} elements to match the number of channels"
            )
        if input_data_format == ChannelDimension.FIRST:
            result = np.zeros((num_channels, max_dim, max_dim), dtype=image.dtype)
            for i, color in enumerate(background_color):
                result[i, :, :] = color
            if width > height:
                start = (max_dim - height) // 2
                result[:, start : start + height, :] = image
            else:
                start = (max_dim - width) // 2
                result[:, :, start : start + width] = image
        else:
            result = np.zeros((max_dim, max_dim, num_channels), dtype=image.dtype)
            for i, color in enumerate(background_color):
                result[:, :, i] = color
            if width > height:
                start = (max_dim - height) // 2
                result[start : start + height, :, :] = image
            else:
                start = (max_dim - width) // 2
                result[:, start : start + width, :] = image
        return result
__all__ = ["DeepseekVLHybridImageProcessor"]