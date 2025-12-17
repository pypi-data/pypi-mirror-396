import math
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Union
from ...utils.import_utils import requires
if TYPE_CHECKING:
    from ...modeling_outputs import DepthEstimatorOutput
import numpy as np
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import pad, resize, to_channel_dimension_format
from ...image_utils import (
    IMAGENET_STANDARD_MEAN,
    IMAGENET_STANDARD_STD,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    get_image_size,
    infer_channel_dimension_format,
    is_scaled_image,
    is_torch_available,
    is_torch_tensor,
    make_flat_list_of_images,
    to_numpy_array,
    valid_images,
    validate_preprocess_arguments,
)
from ...utils import (
    TensorType,
    filter_out_non_signature_kwargs,
    is_vision_available,
    logging,
    requires_backends,
)
if is_torch_available():
    import torch
if is_vision_available():
    import PIL
logger = logging.get_logger(__name__)
def get_resize_output_image_size(
    input_image: np.ndarray,
    output_size: Union[int, Iterable[int]],
    keep_aspect_ratio: bool,
    multiple: int,
    input_data_format: Optional[Union[str, ChannelDimension]] = None,
) -> tuple[int, int]:
    def constrain_to_multiple_of(val, multiple, min_val=0, max_val=None):
        x = round(val / multiple) * multiple
        if max_val is not None and x > max_val:
            x = math.floor(val / multiple) * multiple
        if x < min_val:
            x = math.ceil(val / multiple) * multiple
        return x
    output_size = (output_size, output_size) if isinstance(output_size, int) else output_size
    input_height, input_width = get_image_size(input_image, input_data_format)
    output_height, output_width = output_size
    scale_height = output_height / input_height
    scale_width = output_width / input_width
    if keep_aspect_ratio:
        if abs(1 - scale_width) < abs(1 - scale_height):
            scale_height = scale_width
        else:
            scale_width = scale_height
    new_height = constrain_to_multiple_of(scale_height * input_height, multiple=multiple)
    new_width = constrain_to_multiple_of(scale_width * input_width, multiple=multiple)
    return (new_height, new_width)
@requires(backends=("vision",))
class DPTImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(
        self,
        do_resize: bool = True,
        size: Optional[dict[str, int]] = None,
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        keep_aspect_ratio: bool = False,
        ensure_multiple_of: int = 1,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: bool = True,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_pad: bool = False,
        size_divisor: Optional[int] = None,
        do_reduce_labels: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 384, "width": 384}
        size = get_size_dict(size)
        self.do_resize = do_resize
        self.size = size
        self.keep_aspect_ratio = keep_aspect_ratio
        self.ensure_multiple_of = ensure_multiple_of
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.image_mean = image_mean if image_mean is not None else IMAGENET_STANDARD_MEAN
        self.image_std = image_std if image_std is not None else IMAGENET_STANDARD_STD
        self.do_pad = do_pad
        self.size_divisor = size_divisor
        self.do_reduce_labels = do_reduce_labels
    def resize(
        self,
        image: np.ndarray,
        size: dict[str, int],
        keep_aspect_ratio: bool = False,
        ensure_multiple_of: int = 1,
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> np.ndarray:
        size = get_size_dict(size)
        if "height" not in size or "width" not in size:
            raise ValueError(f"The size dictionary must contain the keys 'height' and 'width'. Got {size.keys()}")
        output_size = get_resize_output_image_size(
            image,
            output_size=(size["height"], size["width"]),
            keep_aspect_ratio=keep_aspect_ratio,
            multiple=ensure_multiple_of,
            input_data_format=input_data_format,
        )
        return resize(
            image,
            size=output_size,
            resample=resample,
            data_format=data_format,
            input_data_format=input_data_format,
            **kwargs,
        )
    def pad_image(
        self,
        image: np.ndarray,
        size_divisor: int,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        def _get_pad(size, size_divisor):
            new_size = math.ceil(size / size_divisor) * size_divisor
            pad_size = new_size - size
            pad_size_left = pad_size // 2
            pad_size_right = pad_size - pad_size_left
            return pad_size_left, pad_size_right
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        height, width = get_image_size(image, input_data_format)
        pad_size_left, pad_size_right = _get_pad(height, size_divisor)
        pad_size_top, pad_size_bottom = _get_pad(width, size_divisor)
        return pad(image, ((pad_size_left, pad_size_right), (pad_size_top, pad_size_bottom)), data_format=data_format)
    def reduce_label(self, label: ImageInput) -> np.ndarray:
        label = to_numpy_array(label)
        label[label == 0] = 255
        label = label - 1
        label[label == 254] = 255
        return label
    def _preprocess(
        self,
        image: ImageInput,
        do_reduce_labels: Optional[bool] = None,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        keep_aspect_ratio: Optional[bool] = None,
        ensure_multiple_of: Optional[int] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_pad: Optional[bool] = None,
        size_divisor: Optional[int] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        if do_reduce_labels:
            image = self.reduce_label(image)
        if do_resize:
            image = self.resize(
                image=image,
                size=size,
                resample=resample,
                keep_aspect_ratio=keep_aspect_ratio,
                ensure_multiple_of=ensure_multiple_of,
                input_data_format=input_data_format,
            )
        if do_rescale:
            image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
        if do_normalize:
            image = self.normalize(image=image, mean=image_mean, std=image_std, input_data_format=input_data_format)
        if do_pad:
            image = self.pad_image(image=image, size_divisor=size_divisor, input_data_format=input_data_format)
        return image
    def _preprocess_image(
        self,
        image: ImageInput,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        keep_aspect_ratio: Optional[bool] = None,
        ensure_multiple_of: Optional[int] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_pad: Optional[bool] = None,
        size_divisor: Optional[int] = None,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> np.ndarray:
        image = to_numpy_array(image)
        if do_rescale and is_scaled_image(image):
            logger.warning_once(
                "It looks like you are trying to rescale already rescaled images. If the input"
                " images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again."
            )
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        image = self._preprocess(
            image,
            do_reduce_labels=False,
            do_resize=do_resize,
            size=size,
            resample=resample,
            keep_aspect_ratio=keep_aspect_ratio,
            ensure_multiple_of=ensure_multiple_of,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            do_pad=do_pad,
            size_divisor=size_divisor,
            input_data_format=input_data_format,
        )
        if data_format is not None:
            image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
        return image
    def _preprocess_segmentation_map(
        self,
        segmentation_map: ImageInput,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        keep_aspect_ratio: Optional[bool] = None,
        ensure_multiple_of: Optional[int] = None,
        do_reduce_labels: Optional[bool] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        segmentation_map = to_numpy_array(segmentation_map)
        if segmentation_map.ndim == 2:
            segmentation_map = segmentation_map[None, ...]
            added_dimension = True
            input_data_format = ChannelDimension.FIRST
        else:
            added_dimension = False
            if input_data_format is None:
                input_data_format = infer_channel_dimension_format(segmentation_map, num_channels=1)
        segmentation_map = self._preprocess(
            image=segmentation_map,
            do_reduce_labels=do_reduce_labels,
            do_resize=do_resize,
            size=size,
            resample=resample,
            keep_aspect_ratio=keep_aspect_ratio,
            ensure_multiple_of=ensure_multiple_of,
            do_normalize=False,
            do_rescale=False,
            input_data_format=input_data_format,
        )
        if added_dimension:
            segmentation_map = np.squeeze(segmentation_map, axis=0)
        segmentation_map = segmentation_map.astype(np.int64)
        return segmentation_map
    def __call__(self, images, segmentation_maps=None, **kwargs):
        return super().__call__(images, segmentation_maps=segmentation_maps, **kwargs)
    @filter_out_non_signature_kwargs()
    def preprocess(
        self,
        images: ImageInput,
        segmentation_maps: Optional[ImageInput] = None,
        do_resize: Optional[bool] = None,
        size: Optional[int] = None,
        keep_aspect_ratio: Optional[bool] = None,
        ensure_multiple_of: Optional[int] = None,
        resample: Optional[PILImageResampling] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_pad: Optional[bool] = None,
        size_divisor: Optional[int] = None,
        do_reduce_labels: Optional[bool] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: ChannelDimension = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> PIL.Image.Image:
        do_resize = do_resize if do_resize is not None else self.do_resize
        size = size if size is not None else self.size
        size = get_size_dict(size)
        keep_aspect_ratio = keep_aspect_ratio if keep_aspect_ratio is not None else self.keep_aspect_ratio
        ensure_multiple_of = ensure_multiple_of if ensure_multiple_of is not None else self.ensure_multiple_of
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        do_pad = do_pad if do_pad is not None else self.do_pad
        size_divisor = size_divisor if size_divisor is not None else self.size_divisor
        do_reduce_labels = do_reduce_labels if do_reduce_labels is not None else self.do_reduce_labels
        images = make_flat_list_of_images(images)
        if segmentation_maps is not None:
            segmentation_maps = make_flat_list_of_images(segmentation_maps, expected_ndims=2)
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
        images = [
            self._preprocess_image(
                image=img,
                do_resize=do_resize,
                do_rescale=do_rescale,
                do_normalize=do_normalize,
                do_pad=do_pad,
                size=size,
                resample=resample,
                keep_aspect_ratio=keep_aspect_ratio,
                ensure_multiple_of=ensure_multiple_of,
                rescale_factor=rescale_factor,
                image_mean=image_mean,
                image_std=image_std,
                size_divisor=size_divisor,
                data_format=data_format,
                input_data_format=input_data_format,
            )
            for img in images
        ]
        data = {"pixel_values": images}
        if segmentation_maps is not None:
            segmentation_maps = [
                self._preprocess_segmentation_map(
                    segmentation_map=segmentation_map,
                    do_reduce_labels=do_reduce_labels,
                    do_resize=do_resize,
                    size=size,
                    resample=resample,
                    keep_aspect_ratio=keep_aspect_ratio,
                    ensure_multiple_of=ensure_multiple_of,
                    input_data_format=input_data_format,
                )
                for segmentation_map in segmentation_maps
            ]
            data["labels"] = segmentation_maps
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_semantic_segmentation(self, outputs, target_sizes: Optional[list[tuple]] = None):
        logits = outputs.logits
        if target_sizes is not None:
            if len(logits) != len(target_sizes):
                raise ValueError(
                    "Make sure that you pass in as many target sizes as the batch dimension of the logits"
                )
            if is_torch_tensor(target_sizes):
                target_sizes = target_sizes.numpy()
            semantic_segmentation = []
            for idx in range(len(logits)):
                resized_logits = torch.nn.functional.interpolate(
                    logits[idx].unsqueeze(dim=0), size=target_sizes[idx], mode="bilinear", align_corners=False
                )
                semantic_map = resized_logits[0].argmax(dim=0)
                semantic_segmentation.append(semantic_map)
        else:
            semantic_segmentation = logits.argmax(dim=1)
            semantic_segmentation = [semantic_segmentation[i] for i in range(semantic_segmentation.shape[0])]
        return semantic_segmentation
    def post_process_depth_estimation(
        self,
        outputs: "DepthEstimatorOutput",
        target_sizes: Optional[Union[TensorType, list[tuple[int, int]], None]] = None,
    ) -> list[dict[str, TensorType]]:
        requires_backends(self, "torch")
        predicted_depth = outputs.predicted_depth
        if (target_sizes is not None) and (len(predicted_depth) != len(target_sizes)):
            raise ValueError(
                "Make sure that you pass in as many target sizes as the batch dimension of the predicted depth"
            )
        results = []
        target_sizes = [None] * len(predicted_depth) if target_sizes is None else target_sizes
        for depth, target_size in zip(predicted_depth, target_sizes):
            if target_size is not None:
                depth = torch.nn.functional.interpolate(
                    depth.unsqueeze(0).unsqueeze(1), size=target_size, mode="bicubic", align_corners=False
                ).squeeze()
            results.append({"predicted_depth": depth})
        return results
__all__ = ["DPTImageProcessor"]