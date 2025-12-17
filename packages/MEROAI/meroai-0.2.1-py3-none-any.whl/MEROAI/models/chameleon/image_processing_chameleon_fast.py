from typing import Optional
import numpy as np
import PIL
import torch
from torchvision.transforms.v2 import functional as F
from ...image_processing_utils_fast import BaseImageProcessorFast
from ...image_utils import ImageInput, PILImageResampling, SizeDict
from ...utils import auto_docstring, logging
logger = logging.get_logger(__name__)
@auto_docstring
class ChameleonImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.LANCZOS
    image_mean = [1.0, 1.0, 1.0]
    image_std = [1.0, 1.0, 1.0]
    size = {"shortest_edge": 512}
    default_to_square = False
    crop_size = {"height": 512, "width": 512}
    do_resize = True
    do_center_crop = True
    do_rescale = True
    rescale_factor = 0.0078
    do_normalize = True
    do_convert_rgb = True
    def convert_to_rgb(self, image: ImageInput) -> ImageInput:
        if not isinstance(image, PIL.Image.Image):
            return image
        elif image.mode == "RGB":
            return image
        img_rgba = np.array(image.convert("RGBA"))
        if not (img_rgba[:, :, 3] < 255).any():
            return image.convert("RGB")
        alpha = img_rgba[:, :, 3] / 255.0
        img_rgb = (1 - alpha[:, :, np.newaxis]) * 255 + alpha[:, :, np.newaxis] * img_rgba[:, :, :3]
        return PIL.Image.fromarray(img_rgb.astype("uint8"), "RGB")
    def resize(
        self,
        image: "torch.Tensor",
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"] = None,
        **kwargs,
    ) -> "torch.Tensor":
        interpolation = interpolation if interpolation is not None else F.InterpolationMode.BILINEAR
        if interpolation == F.InterpolationMode.LANCZOS:
            logger.warning_once(
                "You have used fast image processor with LANCZOS resample which not yet supported for torch.Tensor. "
                "BICUBIC resample will be used as an alternative. Please fall back to slow image processor if you "
                "want full consistency with the original model."
            )
            interpolation = F.InterpolationMode.BICUBIC
        return super().resize(
            image=image,
            size=size,
            interpolation=interpolation,
            **kwargs,
        )
__all__ = ["ChameleonImageProcessorFast"]