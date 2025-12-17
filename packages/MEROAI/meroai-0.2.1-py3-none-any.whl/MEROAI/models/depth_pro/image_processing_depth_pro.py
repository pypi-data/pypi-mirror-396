from typing import TYPE_CHECKING, Optional, Union
import numpy as np
from ...utils.import_utils import requires
if TYPE_CHECKING:
    from .modeling_depth_pro import DepthProDepthEstimatorOutput
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import to_channel_dimension_format
from ...image_utils import (
    IMAGENET_STANDARD_MEAN,
    IMAGENET_STANDARD_STD,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    infer_channel_dimension_format,
    is_scaled_image,
    is_torch_available,
    make_flat_list_of_images,
    to_numpy_array,
    valid_images,
)
from ...utils import TensorType, filter_out_non_signature_kwargs, is_torchvision_available, logging, requires_backends
if is_torch_available():
    import torch
if is_torchvision_available():
    from ...image_utils import pil_torch_interpolation_mapping
logger = logging.get_logger(__name__)
@requires(backends=("torchvision", "torch"))
class DepthProImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(
        self,
        do_resize: bool = True,
        size: Optional[dict[str, int]] = None,
        resample: PILImageResampling = PILImageResampling.BILINEAR,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: bool = True,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 1536, "width": 1536}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.do_rescale = do_rescale
        self.do_normalize = do_normalize
        self.size = size
        self.resample = resample
        self.rescale_factor = rescale_factor
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
    def resize(
        self,
        image: np.ndarray,
        size: dict[str, int],
        resample: PILImageResampling = PILImageResampling.BILINEAR,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        requires_backends(self, "torch")
        size = get_size_dict(size)
        if "height" not in size or "width" not in size:
            raise ValueError(f"The `size` dictionary must contain the keys `height` and `width`. Got {size.keys()}")
        output_size = (size["height"], size["width"])
        image_tensor = torch.from_numpy(image).unsqueeze(0)
        resized_image = torch.nn.functional.interpolate(
            input=image_tensor,
            size=output_size,
            mode=pil_torch_interpolation_mapping[resample].value,
        )
        resized_image = resized_image.squeeze(0).numpy()
        return resized_image
    def _validate_input_arguments(
        self,
        do_resize: bool,
        size: dict[str, int],
        resample: PILImageResampling,
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
        image_mean: Union[float, list[float]],
        image_std: Union[float, list[float]],
        data_format: Union[str, ChannelDimension],
    ):
        if do_resize and None in (size, resample):
            raise ValueError("Size and resample must be specified if do_resize is True.")
        if do_rescale and rescale_factor is None:
            raise ValueError("Rescale factor must be specified if do_rescale is True.")
        if do_normalize and None in (image_mean, image_std):
            raise ValueError("Image mean and standard deviation must be specified if do_normalize is True.")
    @filter_out_non_signature_kwargs()
    def preprocess(
        self,
        images: ImageInput,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: Union[str, ChannelDimension] = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        do_resize = do_resize if do_resize is not None else self.do_resize
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        resample = resample if resample is not None else self.resample
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        size = size if size is not None else self.size
        images = make_flat_list_of_images(images)
        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )
        self._validate_input_arguments(
            do_resize=do_resize,
            size=size,
            resample=resample,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            data_format=data_format,
        )
        images = [to_numpy_array(image) for image in images]
        if is_scaled_image(images[0]) and do_rescale:
            logger.warning_once(
                "It looks like you are trying to rescale already rescaled images. If the input"
                " images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again."
            )
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(images[0])
        all_images = []
        for image in images:
            if do_rescale:
                image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
            if do_normalize:
                image = self.normalize(
                    image=image, mean=image_mean, std=image_std, input_data_format=input_data_format
                )
            if do_resize:
                image = to_channel_dimension_format(image, ChannelDimension.FIRST, input_channel_dim=input_data_format)
                image = self.resize(image=image, size=size, resample=resample)
                image = to_channel_dimension_format(image, data_format, input_channel_dim=ChannelDimension.FIRST)
            else:
                image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
            all_images.append(image)
        data = {"pixel_values": all_images}
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_depth_estimation(
        self,
        outputs: "DepthProDepthEstimatorOutput",
        target_sizes: Optional[Union[TensorType, list[tuple[int, int]], None]] = None,
    ) -> list[dict[str, TensorType]]:
        requires_backends(self, "torch")
        predicted_depth = outputs.predicted_depth
        fov = outputs.field_of_view
        batch_size = len(predicted_depth)
        if target_sizes is not None and batch_size != len(target_sizes):
            raise ValueError(
                "Make sure that you pass in as many fov values as the batch dimension of the predicted depth"
            )
        results = []
        fov = [None] * batch_size if fov is None else fov
        target_sizes = [None] * batch_size if target_sizes is None else target_sizes
        for depth, fov_value, target_size in zip(predicted_depth, fov, target_sizes):
            focal_length = None
            if target_size is not None:
                if fov_value is not None:
                    width = target_size[1]
                    focal_length = 0.5 * width / torch.tan(0.5 * torch.deg2rad(fov_value))
                    depth = depth * width / focal_length
                depth = torch.nn.functional.interpolate(
                    input=depth.unsqueeze(0).unsqueeze(1),
                    size=target_size,
                    mode=pil_torch_interpolation_mapping[self.resample].value,
                ).squeeze()
            depth = 1.0 / torch.clamp(depth, min=1e-4, max=1e4)
            results.append(
                {
                    "predicted_depth": depth,
                    "field_of_view": fov_value,
                    "focal_length": focal_length,
                }
            )
        return results
__all__ = ["DepthProImageProcessor"]