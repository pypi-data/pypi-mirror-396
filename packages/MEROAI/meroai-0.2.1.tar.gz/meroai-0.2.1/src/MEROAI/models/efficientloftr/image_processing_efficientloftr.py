from typing import Optional, Union
import numpy as np
from ... import is_torch_available, is_vision_available
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_size_dict
from ...image_transforms import resize, to_channel_dimension_format
from ...image_utils import (
    ChannelDimension,
    ImageInput,
    ImageType,
    PILImageResampling,
    get_image_type,
    infer_channel_dimension_format,
    is_pil_image,
    is_scaled_image,
    is_valid_image,
    to_numpy_array,
    valid_images,
    validate_preprocess_arguments,
)
from ...utils import TensorType, logging, requires_backends
if is_torch_available():
    import torch
if is_vision_available():
    import PIL
    from PIL import Image, ImageDraw
    from .modeling_efficientloftr import KeypointMatchingOutput
logger = logging.get_logger(__name__)
def is_grayscale(
    image: np.ndarray,
    input_data_format: Optional[Union[str, ChannelDimension]] = None,
):
    if input_data_format == ChannelDimension.FIRST:
        if image.shape[0] == 1:
            return True
        return np.all(image[0, ...] == image[1, ...]) and np.all(image[1, ...] == image[2, ...])
    elif input_data_format == ChannelDimension.LAST:
        if image.shape[-1] == 1:
            return True
        return np.all(image[..., 0] == image[..., 1]) and np.all(image[..., 1] == image[..., 2])
def convert_to_grayscale(
    image: ImageInput,
    input_data_format: Optional[Union[str, ChannelDimension]] = None,
) -> ImageInput:
    requires_backends(convert_to_grayscale, ["vision"])
    if isinstance(image, np.ndarray):
        if is_grayscale(image, input_data_format=input_data_format):
            return image
        if input_data_format == ChannelDimension.FIRST:
            gray_image = image[0, ...] * 0.2989 + image[1, ...] * 0.5870 + image[2, ...] * 0.1140
            gray_image = np.stack([gray_image] * 3, axis=0)
        elif input_data_format == ChannelDimension.LAST:
            gray_image = image[..., 0] * 0.2989 + image[..., 1] * 0.5870 + image[..., 2] * 0.1140
            gray_image = np.stack([gray_image] * 3, axis=-1)
        return gray_image
    if not isinstance(image, PIL.Image.Image):
        return image
    image = image.convert("L")
    return image
def validate_and_format_image_pairs(images: ImageInput):
    error_message = (
        "Input images must be a one of the following :",
        " - A pair of PIL images.",
        " - A pair of 3D arrays.",
        " - A list of pairs of PIL images.",
        " - A list of pairs of 3D arrays.",
    )
    def _is_valid_image(image):
        return is_pil_image(image) or (
            is_valid_image(image) and get_image_type(image) != ImageType.PIL and len(image.shape) == 3
        )
    if isinstance(images, list):
        if len(images) == 2 and all((_is_valid_image(image)) for image in images):
            return images
        if all(
            isinstance(image_pair, list)
            and len(image_pair) == 2
            and all(_is_valid_image(image) for image in image_pair)
            for image_pair in images
        ):
            return [image for image_pair in images for image in image_pair]
    raise ValueError(error_message)
class EfficientLoFTRImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values"]
    def __init__(
        self,
        do_resize: bool = True,
        size: Optional[dict[str, int]] = None,
        resample: PILImageResampling = PILImageResampling.BILINEAR,
        do_rescale: bool = True,
        rescale_factor: float = 1 / 255,
        do_grayscale: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        size = size if size is not None else {"height": 480, "width": 640}
        size = get_size_dict(size, default_to_square=False)
        self.do_resize = do_resize
        self.size = size
        self.resample = resample
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_grayscale = do_grayscale
    def resize(
        self,
        image: np.ndarray,
        size: dict[str, int],
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ):
        size = get_size_dict(size, default_to_square=False)
        return resize(
            image,
            size=(size["height"], size["width"]),
            data_format=data_format,
            input_data_format=input_data_format,
            **kwargs,
        )
    def preprocess(
        self,
        images,
        do_resize: Optional[bool] = None,
        size: Optional[dict[str, int]] = None,
        resample: Optional[PILImageResampling] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_grayscale: Optional[bool] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        data_format: ChannelDimension = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
        **kwargs,
    ) -> BatchFeature:
        do_resize = do_resize if do_resize is not None else self.do_resize
        resample = resample if resample is not None else self.resample
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_grayscale = do_grayscale if do_grayscale is not None else self.do_grayscale
        size = size if size is not None else self.size
        size = get_size_dict(size, default_to_square=False)
        images = validate_and_format_image_pairs(images)
        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )
        validate_preprocess_arguments(
            do_resize=do_resize,
            size=size,
            resample=resample,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
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
            if do_resize:
                image = self.resize(image=image, size=size, resample=resample, input_data_format=input_data_format)
            if do_rescale:
                image = self.rescale(image=image, scale=rescale_factor, input_data_format=input_data_format)
            if do_grayscale:
                image = convert_to_grayscale(image, input_data_format=input_data_format)
            image = to_channel_dimension_format(image, data_format, input_channel_dim=input_data_format)
            all_images.append(image)
        image_pairs = [all_images[i : i + 2] for i in range(0, len(all_images), 2)]
        data = {"pixel_values": image_pairs}
        return BatchFeature(data=data, tensor_type=return_tensors)
    def post_process_keypoint_matching(
        self,
        outputs: "KeypointMatchingOutput",
        target_sizes: Union[TensorType, list[tuple]],
        threshold: float = 0.0,
    ) -> list[dict[str, torch.Tensor]]:
        if outputs.matches.shape[0] != len(target_sizes):
            raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the mask")
        if not all(len(target_size) == 2 for target_size in target_sizes):
            raise ValueError("Each element of target_sizes must contain the size (h, w) of each image of the batch")
        if isinstance(target_sizes, list):
            image_pair_sizes = torch.tensor(target_sizes, device=outputs.matches.device)
        else:
            if target_sizes.shape[1] != 2 or target_sizes.shape[2] != 2:
                raise ValueError(
                    "Each element of target_sizes must contain the size (h, w) of each image of the batch"
                )
            image_pair_sizes = target_sizes
        keypoints = outputs.keypoints.clone()
        keypoints = keypoints * image_pair_sizes.flip(-1).reshape(-1, 2, 1, 2)
        keypoints = keypoints.to(torch.int32)
        results = []
        for keypoints_pair, matches, scores in zip(keypoints, outputs.matches, outputs.matching_scores):
            valid_matches = torch.logical_and(scores > threshold, matches > -1)
            matched_keypoints0 = keypoints_pair[0][valid_matches[0]]
            matched_keypoints1 = keypoints_pair[1][valid_matches[1]]
            matching_scores = scores[0][valid_matches[0]]
            results.append(
                {
                    "keypoints0": matched_keypoints0,
                    "keypoints1": matched_keypoints1,
                    "matching_scores": matching_scores,
                }
            )
        return results
    def visualize_keypoint_matching(
        self,
        images: ImageInput,
        keypoint_matching_output: list[dict[str, torch.Tensor]],
    ) -> list["Image.Image"]:
        images = validate_and_format_image_pairs(images)
        images = [to_numpy_array(image) for image in images]
        image_pairs = [images[i : i + 2] for i in range(0, len(images), 2)]
        results = []
        for image_pair, pair_output in zip(image_pairs, keypoint_matching_output):
            height0, width0 = image_pair[0].shape[:2]
            height1, width1 = image_pair[1].shape[:2]
            plot_image = np.zeros((max(height0, height1), width0 + width1, 3), dtype=np.uint8)
            plot_image[:height0, :width0] = image_pair[0]
            plot_image[:height1, width0:] = image_pair[1]
            plot_image_pil = Image.fromarray(plot_image)
            draw = ImageDraw.Draw(plot_image_pil)
            keypoints0_x, keypoints0_y = pair_output["keypoints0"].unbind(1)
            keypoints1_x, keypoints1_y = pair_output["keypoints1"].unbind(1)
            for keypoint0_x, keypoint0_y, keypoint1_x, keypoint1_y, matching_score in zip(
                keypoints0_x, keypoints0_y, keypoints1_x, keypoints1_y, pair_output["matching_scores"]
            ):
                color = self._get_color(matching_score)
                draw.line(
                    (keypoint0_x, keypoint0_y, keypoint1_x + width0, keypoint1_y),
                    fill=color,
                    width=3,
                )
                draw.ellipse((keypoint0_x - 2, keypoint0_y - 2, keypoint0_x + 2, keypoint0_y + 2), fill="black")
                draw.ellipse(
                    (keypoint1_x + width0 - 2, keypoint1_y - 2, keypoint1_x + width0 + 2, keypoint1_y + 2),
                    fill="black",
                )
            results.append(plot_image_pil)
        return results
    def _get_color(self, score):
        r = int(255 * (1 - score))
        g = int(255 * score)
        b = 0
        return (r, g, b)
__all__ = ["EfficientLoFTRImageProcessor"]