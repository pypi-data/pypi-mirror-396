import math
from collections.abc import Iterable
from typing import TYPE_CHECKING, Optional, Union
import torch
from torchvision.transforms.v2 import functional as F
from ...image_processing_base import BatchFeature
from ...image_processing_utils_fast import BaseImageProcessorFast, DefaultFastImageProcessorKwargs
from ...image_transforms import group_images_by_shape, reorder_images
from ...image_utils import (
    IMAGENET_STANDARD_MEAN,
    IMAGENET_STANDARD_STD,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    SizeDict,
    is_torch_tensor,
)
from ...processing_utils import Unpack
from ...utils import TensorType, auto_docstring, requires_backends
if TYPE_CHECKING:
    from ...modeling_outputs import DepthEstimatorOutput
class DPTFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    ensure_multiple_of: Optional[int]
    size_divisor: Optional[int]
    keep_aspect_ratio: Optional[bool]
    do_reduce_labels: Optional[bool]
def get_resize_output_image_size(
    input_image: "torch.Tensor",
    output_size: Union[int, Iterable[int]],
    keep_aspect_ratio: bool,
    multiple: int,
) -> SizeDict:
    def constrain_to_multiple_of(val, multiple, min_val=0, max_val=None):
        x = round(val / multiple) * multiple
        if max_val is not None and x > max_val:
            x = math.floor(val / multiple) * multiple
        if x < min_val:
            x = math.ceil(val / multiple) * multiple
        return x
    input_height, input_width = input_image.shape[-2:]
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
    return SizeDict(height=new_height, width=new_width)
@auto_docstring
class DPTImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BICUBIC
    image_mean = IMAGENET_STANDARD_MEAN
    image_std = IMAGENET_STANDARD_STD
    size = {"height": 384, "width": 384}
    default_to_square = True
    crop_size = None
    do_resize = True
    do_center_crop = None
    do_rescale = True
    do_normalize = True
    do_reduce_labels = None
    valid_kwargs = DPTFastImageProcessorKwargs
    do_pad = False
    rescale_factor = 1 / 255
    ensure_multiple_of = 1
    keep_aspect_ratio = False
    def __init__(self, **kwargs: Unpack[DPTFastImageProcessorKwargs]):
        super().__init__(**kwargs)
    def reduce_label(self, labels: list["torch.Tensor"]):
        for idx in range(len(labels)):
            label = labels[idx]
            label = torch.where(label == 0, torch.tensor(255, dtype=label.dtype), label)
            label = label - 1
            label = torch.where(label == 254, torch.tensor(255, dtype=label.dtype), label)
            labels[idx] = label
        return label
    @auto_docstring
    def preprocess(
        self,
        images: ImageInput,
        segmentation_maps: Optional[ImageInput] = None,
        **kwargs: Unpack[DPTFastImageProcessorKwargs],
    ) -> BatchFeature:
        return super().preprocess(images, segmentation_maps, **kwargs)
    def _preprocess_image_like_inputs(
        self,
        images: ImageInput,
        segmentation_maps: Optional[ImageInput],
        do_convert_rgb: bool,
        input_data_format: ChannelDimension,
        device: Optional[Union[str, "torch.device"]] = None,
        **kwargs: Unpack[DPTFastImageProcessorKwargs],
    ) -> BatchFeature:
        images = self._prepare_image_like_inputs(
            images=images, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format, device=device
        )
        images_kwargs = kwargs.copy()
        images_kwargs["do_reduce_labels"] = False
        batch_feature = self._preprocess(images, **images_kwargs)
        if segmentation_maps is not None:
            processed_segmentation_maps = self._prepare_image_like_inputs(
                images=segmentation_maps,
                expected_ndims=2,
                do_convert_rgb=False,
                input_data_format=ChannelDimension.FIRST,
            )
            segmentation_maps_kwargs = kwargs.copy()
            segmentation_maps_kwargs.update({"do_normalize": False, "do_rescale": False})
            processed_segmentation_maps = self._preprocess(
                images=processed_segmentation_maps, **segmentation_maps_kwargs
            ).pixel_values
            batch_feature["labels"] = processed_segmentation_maps.squeeze(1).to(torch.int64)
        return batch_feature
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        do_reduce_labels: bool,
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
        keep_aspect_ratio: bool,
        ensure_multiple_of: Optional[int],
        do_pad: bool,
        size_divisor: Optional[int],
        disable_grouping: Optional[bool],
        return_tensors: Optional[Union[str, TensorType]],
        **kwargs,
    ) -> BatchFeature:
        if do_reduce_labels:
            images = self.reduce_label(images)
        grouped_images, grouped_images_index = group_images_by_shape(images, disable_grouping=disable_grouping)
        resized_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_resize:
                stacked_images = self.resize(
                    image=stacked_images,
                    size=size,
                    interpolation=interpolation,
                    ensure_multiple_of=ensure_multiple_of,
                    keep_aspect_ratio=keep_aspect_ratio,
                )
            resized_images_grouped[shape] = stacked_images
        resized_images = reorder_images(resized_images_grouped, grouped_images_index)
        grouped_images, grouped_images_index = group_images_by_shape(resized_images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        for shape, stacked_images in grouped_images.items():
            if do_center_crop:
                stacked_images = self.center_crop(stacked_images, crop_size)
            if do_pad:
                stacked_images = self.pad_image(stacked_images, size_divisor)
            stacked_images = self.rescale_and_normalize(
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images})
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
    def resize(
        self,
        image: "torch.Tensor",
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"] = None,
        antialias: bool = True,
        ensure_multiple_of: Optional[int] = 1,
        keep_aspect_ratio: bool = False,
    ) -> "torch.Tensor":
        if not size.height or not size.width:
            raise ValueError(f"The size dictionary must contain the keys 'height' and 'width'. Got {size.keys()}")
        output_size = get_resize_output_image_size(
            image,
            output_size=(size.height, size.width),
            keep_aspect_ratio=keep_aspect_ratio,
            multiple=ensure_multiple_of,
        )
        return super().resize(image, output_size, interpolation=interpolation, antialias=antialias)
    def pad_image(
        self,
        image: "torch.Tensor",
        size_divisor: int = 1,
    ) -> "torch.Tensor":
        height, width = image.shape[-2:]
        def _get_pad(size, size_divisor):
            new_size = math.ceil(size / size_divisor) * size_divisor
            pad_size = new_size - size
            pad_size_left = pad_size // 2
            pad_size_right = pad_size - pad_size_left
            return pad_size_left, pad_size_right
        pad_top, pad_bottom = _get_pad(height, size_divisor)
        pad_left, pad_right = _get_pad(width, size_divisor)
        padding = (pad_left, pad_top, pad_right, pad_bottom)
        return F.pad(image, padding)
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
__all__ = ["DPTImageProcessorFast"]