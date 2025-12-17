from collections.abc import Iterable
from copy import deepcopy
from functools import lru_cache, partial
from typing import Any, Optional, TypedDict, Union
import numpy as np
from .image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from .image_transforms import (
    convert_to_rgb,
    get_resize_output_image_size,
    get_size_with_aspect_ratio,
    group_images_by_shape,
    reorder_images,
)
from .image_utils import (
    ChannelDimension,
    ImageInput,
    ImageType,
    SizeDict,
    get_image_size,
    get_image_size_for_max_height_width,
    get_image_type,
    infer_channel_dimension_format,
    make_flat_list_of_images,
    validate_kwargs,
    validate_preprocess_arguments,
)
from .processing_utils import Unpack
from .utils import (
    TensorType,
    auto_docstring,
    is_torch_available,
    is_torchvision_available,
    is_vision_available,
    logging,
)
from .utils.import_utils import is_rocm_platform
if is_vision_available():
    from .image_utils import PILImageResampling
if is_torch_available():
    import torch
if is_torchvision_available():
    from torchvision.transforms.v2 import functional as F
    from .image_utils import pil_torch_interpolation_mapping
else:
    pil_torch_interpolation_mapping = None
logger = logging.get_logger(__name__)
@lru_cache(maxsize=10)
def validate_fast_preprocess_arguments(
    do_rescale: Optional[bool] = None,
    rescale_factor: Optional[float] = None,
    do_normalize: Optional[bool] = None,
    image_mean: Optional[Union[float, list[float]]] = None,
    image_std: Optional[Union[float, list[float]]] = None,
    do_center_crop: Optional[bool] = None,
    crop_size: Optional[SizeDict] = None,
    do_resize: Optional[bool] = None,
    size: Optional[SizeDict] = None,
    interpolation: Optional["F.InterpolationMode"] = None,
    return_tensors: Optional[Union[str, TensorType]] = None,
    data_format: ChannelDimension = ChannelDimension.FIRST,
):
    validate_preprocess_arguments(
        do_rescale=do_rescale,
        rescale_factor=rescale_factor,
        do_normalize=do_normalize,
        image_mean=image_mean,
        image_std=image_std,
        do_center_crop=do_center_crop,
        crop_size=crop_size,
        do_resize=do_resize,
        size=size,
        interpolation=interpolation,
    )
    if return_tensors is not None and return_tensors != "pt":
        raise ValueError("Only returning PyTorch tensors is currently supported.")
    if data_format != ChannelDimension.FIRST:
        raise ValueError("Only channel first data format is currently supported.")
def safe_squeeze(tensor: "torch.Tensor", axis: Optional[int] = None) -> "torch.Tensor":
    if axis is None:
        return tensor.squeeze()
    try:
        return tensor.squeeze(axis=axis)
    except ValueError:
        return tensor
def max_across_indices(values: Iterable[Any]) -> list[Any]:
    return [max(values_i) for values_i in zip(*values)]
def get_max_height_width(images: list["torch.Tensor"]) -> tuple[int, ...]:
    _, max_height, max_width = max_across_indices([img.shape for img in images])
    return (max_height, max_width)
def divide_to_patches(
    image: Union[np.ndarray, "torch.Tensor"], patch_size: int
) -> list[Union[np.ndarray, "torch.Tensor"]]:
    patches = []
    height, width = get_image_size(image, channel_dim=ChannelDimension.FIRST)
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size):
            patch = image[:, i : i + patch_size, j : j + patch_size]
            patches.append(patch)
    return patches
class DefaultFastImageProcessorKwargs(TypedDict, total=False):
    do_resize: Optional[bool]
    size: Optional[dict[str, int]]
    default_to_square: Optional[bool]
    resample: Optional[Union["PILImageResampling", "F.InterpolationMode"]]
    do_center_crop: Optional[bool]
    crop_size: Optional[dict[str, int]]
    do_rescale: Optional[bool]
    rescale_factor: Optional[Union[int, float]]
    do_normalize: Optional[bool]
    image_mean: Optional[Union[float, list[float]]]
    image_std: Optional[Union[float, list[float]]]
    do_pad: Optional[bool]
    pad_size: Optional[dict[str, int]]
    do_convert_rgb: Optional[bool]
    return_tensors: Optional[Union[str, TensorType]]
    data_format: Optional[ChannelDimension]
    input_data_format: Optional[Union[str, ChannelDimension]]
    device: Optional["torch.device"]
    disable_grouping: Optional[bool]
@auto_docstring
class BaseImageProcessorFast(BaseImageProcessor):
    resample = None
    image_mean = None
    image_std = None
    size = None
    default_to_square = True
    crop_size = None
    do_resize = None
    do_center_crop = None
    do_pad = None
    pad_size = None
    do_rescale = None
    rescale_factor = 1 / 255
    do_normalize = None
    do_convert_rgb = None
    return_tensors = None
    data_format = ChannelDimension.FIRST
    input_data_format = None
    device = None
    model_input_names = ["pixel_values"]
    valid_kwargs = DefaultFastImageProcessorKwargs
    unused_kwargs = None
    def __init__(self, **kwargs: Unpack[DefaultFastImageProcessorKwargs]):
        super().__init__(**kwargs)
        kwargs = self.filter_out_unused_kwargs(kwargs)
        size = kwargs.pop("size", self.size)
        self.size = (
            get_size_dict(size=size, default_to_square=kwargs.pop("default_to_square", self.default_to_square))
            if size is not None
            else None
        )
        crop_size = kwargs.pop("crop_size", self.crop_size)
        self.crop_size = get_size_dict(crop_size, param_name="crop_size") if crop_size is not None else None
        pad_size = kwargs.pop("pad_size", self.pad_size)
        self.pad_size = get_size_dict(size=pad_size, param_name="pad_size") if pad_size is not None else None
        for key in self.valid_kwargs.__annotations__:
            kwarg = kwargs.pop(key, None)
            if kwarg is not None:
                setattr(self, key, kwarg)
            else:
                setattr(self, key, deepcopy(getattr(self, key, None)))
        self._valid_kwargs_names = list(self.valid_kwargs.__annotations__.keys())
    @property
    def is_fast(self) -> bool:
        return True
    def pad(
        self,
        images: "torch.Tensor",
        pad_size: SizeDict = None,
        fill_value: Optional[int] = 0,
        padding_mode: Optional[str] = "constant",
        return_mask: bool = False,
        disable_grouping: Optional[bool] = False,
        **kwargs,
    ) -> "torch.Tensor":
        if pad_size is not None:
            if not (pad_size.height and pad_size.width):
                raise ValueError(f"Pad size must contain 'height' and 'width' keys only. Got pad_size={pad_size}.")
            pad_size = (pad_size.height, pad_size.width)
        else:
            pad_size = get_max_height_width(images)
        grouped_images, grouped_images_index = group_images_by_shape(images, disable_grouping=disable_grouping)
        processed_images_grouped = {}
        processed_masks_grouped = {}
        for shape, stacked_images in grouped_images.items():
            image_size = stacked_images.shape[-2:]
            padding_height = pad_size[0] - image_size[0]
            padding_width = pad_size[1] - image_size[1]
            if padding_height < 0 or padding_width < 0:
                raise ValueError(
                    f"Padding dimensions are negative. Please make sure that the `pad_size` is larger than the "
                    f"image size. Got pad_size={pad_size}, image_size={image_size}."
                )
            if image_size != pad_size:
                padding = (0, 0, padding_width, padding_height)
                stacked_images = F.pad(stacked_images, padding, fill=fill_value, padding_mode=padding_mode)
            processed_images_grouped[shape] = stacked_images
            if return_mask:
                stacked_masks = torch.zeros_like(stacked_images, dtype=torch.int64)[..., 0, :, :]
                stacked_masks[..., : image_size[0], : image_size[1]] = 1
                processed_masks_grouped[shape] = stacked_masks
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        if return_mask:
            processed_masks = reorder_images(processed_masks_grouped, grouped_images_index)
            return processed_images, processed_masks
        return processed_images
    def resize(
        self,
        image: "torch.Tensor",
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"] = None,
        antialias: bool = True,
        **kwargs,
    ) -> "torch.Tensor":
        interpolation = interpolation if interpolation is not None else F.InterpolationMode.BILINEAR
        if size.shortest_edge and size.longest_edge:
            new_size = get_size_with_aspect_ratio(
                image.size()[-2:],
                size.shortest_edge,
                size.longest_edge,
            )
        elif size.shortest_edge:
            new_size = get_resize_output_image_size(
                image,
                size=size.shortest_edge,
                default_to_square=False,
                input_data_format=ChannelDimension.FIRST,
            )
        elif size.max_height and size.max_width:
            new_size = get_image_size_for_max_height_width(image.size()[-2:], size.max_height, size.max_width)
        elif size.height and size.width:
            new_size = (size.height, size.width)
        else:
            raise ValueError(
                "Size must contain 'height' and 'width' keys, or 'max_height' and 'max_width', or 'shortest_edge' key. Got"
                f" {size}."
            )
        if torch.compiler.is_compiling() and is_rocm_platform():
            return self.compile_friendly_resize(image, new_size, interpolation, antialias)
        return F.resize(image, new_size, interpolation=interpolation, antialias=antialias)
    @staticmethod
    def compile_friendly_resize(
        image: "torch.Tensor",
        new_size: tuple[int, int],
        interpolation: Optional["F.InterpolationMode"] = None,
        antialias: bool = True,
    ) -> "torch.Tensor":
        if image.dtype == torch.uint8:
            image = image.float() / 256
            image = F.resize(image, new_size, interpolation=interpolation, antialias=antialias)
            image = image * 256
            image = torch.where(image > 255, 255, image)
            image = torch.where(image < 0, 0, image)
            image = image.round().to(torch.uint8)
        else:
            image = F.resize(image, new_size, interpolation=interpolation, antialias=antialias)
        return image
    def rescale(
        self,
        image: "torch.Tensor",
        scale: float,
        **kwargs,
    ) -> "torch.Tensor":
        return image * scale
    def normalize(
        self,
        image: "torch.Tensor",
        mean: Union[float, Iterable[float]],
        std: Union[float, Iterable[float]],
        **kwargs,
    ) -> "torch.Tensor":
        return F.normalize(image, mean, std)
    @lru_cache(maxsize=10)
    def _fuse_mean_std_and_rescale_factor(
        self,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        device: Optional["torch.device"] = None,
    ) -> tuple:
        if do_rescale and do_normalize:
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
    ) -> "torch.Tensor":
        image_mean, image_std, do_rescale = self._fuse_mean_std_and_rescale_factor(
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            device=images.device,
        )
        if do_normalize:
            images = self.normalize(images.to(dtype=torch.float32), image_mean, image_std)
        elif do_rescale:
            images = self.rescale(images, rescale_factor)
        return images
    def center_crop(
        self,
        image: "torch.Tensor",
        size: SizeDict,
        **kwargs,
    ) -> "torch.Tensor":
        if size.height is None or size.width is None:
            raise ValueError(f"The size dictionary must have keys 'height' and 'width'. Got {size.keys()}")
        image_height, image_width = image.shape[-2:]
        crop_height, crop_width = size.height, size.width
        if crop_width > image_width or crop_height > image_height:
            padding_ltrb = [
                (crop_width - image_width) // 2 if crop_width > image_width else 0,
                (crop_height - image_height) // 2 if crop_height > image_height else 0,
                (crop_width - image_width + 1) // 2 if crop_width > image_width else 0,
                (crop_height - image_height + 1) // 2 if crop_height > image_height else 0,
            ]
            image = F.pad(image, padding_ltrb, fill=0)
            image_height, image_width = image.shape[-2:]
            if crop_width == image_width and crop_height == image_height:
                return image
        crop_top = int((image_height - crop_height) / 2.0)
        crop_left = int((image_width - crop_width) / 2.0)
        return F.crop(image, crop_top, crop_left, crop_height, crop_width)
    def convert_to_rgb(
        self,
        image: ImageInput,
    ) -> ImageInput:
        return convert_to_rgb(image)
    def filter_out_unused_kwargs(self, kwargs: dict):
        if self.unused_kwargs is None:
            return kwargs
        for kwarg_name in self.unused_kwargs:
            if kwarg_name in kwargs:
                logger.warning_once(f"This processor does not use the `{kwarg_name}` parameter. It will be ignored.")
                kwargs.pop(kwarg_name)
        return kwargs
    def _prepare_images_structure(
        self,
        images: ImageInput,
        expected_ndims: int = 3,
    ) -> ImageInput:
        images = self.fetch_images(images)
        return make_flat_list_of_images(images, expected_ndims=expected_ndims)
    def _process_image(
        self,
        image: ImageInput,
        do_convert_rgb: Optional[bool] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        device: Optional["torch.device"] = None,
    ) -> "torch.Tensor":
        image_type = get_image_type(image)
        if image_type not in [ImageType.PIL, ImageType.TORCH, ImageType.NUMPY]:
            raise ValueError(f"Unsupported input image type {image_type}")
        if do_convert_rgb:
            image = self.convert_to_rgb(image)
        if image_type == ImageType.PIL:
            image = F.pil_to_tensor(image)
        elif image_type == ImageType.NUMPY:
            image = torch.from_numpy(image).contiguous()
        if image.ndim == 2:
            image = image.unsqueeze(0)
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        if input_data_format == ChannelDimension.LAST:
            image = image.permute(2, 0, 1).contiguous()
        if device is not None:
            image = image.to(device)
        return image
    def _prepare_image_like_inputs(
        self,
        images: ImageInput,
        do_convert_rgb: Optional[bool] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        device: Optional["torch.device"] = None,
        expected_ndims: int = 3,
    ) -> list["torch.Tensor"]:
        images = self._prepare_images_structure(images, expected_ndims=expected_ndims)
        process_image_partial = partial(
            self._process_image, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format, device=device
        )
        has_nested_structure = len(images) > 0 and isinstance(images[0], (list, tuple))
        if has_nested_structure:
            processed_images = [[process_image_partial(img) for img in nested_list] for nested_list in images]
        else:
            processed_images = [process_image_partial(img) for img in images]
        return processed_images
    def _further_process_kwargs(
        self,
        size: Optional[SizeDict] = None,
        crop_size: Optional[SizeDict] = None,
        pad_size: Optional[SizeDict] = None,
        default_to_square: Optional[bool] = None,
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        data_format: Optional[ChannelDimension] = None,
        **kwargs,
    ) -> dict:
        if kwargs is None:
            kwargs = {}
        if size is not None:
            size = SizeDict(**get_size_dict(size=size, default_to_square=default_to_square))
        if crop_size is not None:
            crop_size = SizeDict(**get_size_dict(crop_size, param_name="crop_size"))
        if pad_size is not None:
            pad_size = SizeDict(**get_size_dict(size=pad_size, param_name="pad_size"))
        if isinstance(image_mean, list):
            image_mean = tuple(image_mean)
        if isinstance(image_std, list):
            image_std = tuple(image_std)
        if data_format is None:
            data_format = ChannelDimension.FIRST
        kwargs["size"] = size
        kwargs["crop_size"] = crop_size
        kwargs["pad_size"] = pad_size
        kwargs["image_mean"] = image_mean
        kwargs["image_std"] = image_std
        kwargs["data_format"] = data_format
        resample = kwargs.pop("resample")
        kwargs["interpolation"] = (
            pil_torch_interpolation_mapping[resample] if isinstance(resample, (PILImageResampling, int)) else resample
        )
        return kwargs
    def _validate_preprocess_kwargs(
        self,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        image_mean: Optional[Union[float, tuple[float]]] = None,
        image_std: Optional[Union[float, tuple[float]]] = None,
        do_resize: Optional[bool] = None,
        size: Optional[SizeDict] = None,
        do_center_crop: Optional[bool] = None,
        crop_size: Optional[SizeDict] = None,
        interpolation: Optional["F.InterpolationMode"] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: Optional[ChannelDimension] = None,
        **kwargs,
    ):
        validate_fast_preprocess_arguments(
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            do_resize=do_resize,
            size=size,
            do_center_crop=do_center_crop,
            crop_size=crop_size,
            interpolation=interpolation,
            return_tensors=return_tensors,
            data_format=data_format,
        )
    def __call__(self, images: ImageInput, *args, **kwargs: Unpack[DefaultFastImageProcessorKwargs]) -> BatchFeature:
        return self.preprocess(images, *args, **kwargs)
    @auto_docstring
    def preprocess(self, images: ImageInput, *args, **kwargs: Unpack[DefaultFastImageProcessorKwargs]) -> BatchFeature:
        validate_kwargs(captured_kwargs=kwargs.keys(), valid_processor_keys=self._valid_kwargs_names)
        for kwarg_name in self._valid_kwargs_names:
            kwargs.setdefault(kwarg_name, getattr(self, kwarg_name, None))
        do_convert_rgb = kwargs.pop("do_convert_rgb")
        input_data_format = kwargs.pop("input_data_format")
        device = kwargs.pop("device")
        kwargs = self._further_process_kwargs(**kwargs)
        self._validate_preprocess_kwargs(**kwargs)
        kwargs.pop("data_format")
        return self._preprocess_image_like_inputs(
            images, *args, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format, device=device, **kwargs
        )
    def _preprocess_image_like_inputs(
        self,
        images: ImageInput,
        *args,
        do_convert_rgb: bool,
        input_data_format: ChannelDimension,
        device: Optional[Union[str, "torch.device"]] = None,
        **kwargs: Unpack[DefaultFastImageProcessorKwargs],
    ) -> BatchFeature:
        images = self._prepare_image_like_inputs(
            images=images, do_convert_rgb=do_convert_rgb, input_data_format=input_data_format, device=device
        )
        return self._preprocess(images, *args, **kwargs)
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
        do_pad: Optional[bool],
        pad_size: Optional[SizeDict],
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
                stacked_images, do_rescale, rescale_factor, do_normalize, image_mean, image_std
            )
            processed_images_grouped[shape] = stacked_images
        processed_images = reorder_images(processed_images_grouped, grouped_images_index)
        if do_pad:
            processed_images = self.pad(processed_images, pad_size=pad_size, disable_grouping=disable_grouping)
        processed_images = torch.stack(processed_images, dim=0) if return_tensors else processed_images
        return BatchFeature(data={"pixel_values": processed_images}, tensor_type=return_tensors)
    def to_dict(self):
        encoder_dict = super().to_dict()
        encoder_dict.pop("_valid_processor_keys", None)
        encoder_dict.pop("_valid_kwargs_names", None)
        return encoder_dict