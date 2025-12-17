import pathlib
from typing import Any, Optional, Union
import torch
from torch import nn
from torchvision.io import read_image
from torchvision.transforms.v2 import functional as F
from ...image_processing_utils import BatchFeature, get_size_dict
from ...image_processing_utils_fast import (
    BaseImageProcessorFast,
    DefaultFastImageProcessorKwargs,
    SizeDict,
    get_image_size_for_max_height_width,
    get_max_height_width,
    safe_squeeze,
)
from ...image_transforms import center_to_corners_format, corners_to_center_format
from ...image_utils import (
    IMAGENET_DEFAULT_MEAN,
    IMAGENET_DEFAULT_STD,
    AnnotationFormat,
    AnnotationType,
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    get_image_size,
    validate_annotations,
)
from ...processing_utils import Unpack
from ...utils import TensorType, auto_docstring, logging
from ...utils.import_utils import requires
from .image_processing_conditional_detr import (
    compute_segments,
    convert_segmentation_to_rle,
    get_size_with_aspect_ratio,
    remove_low_and_no_objects,
)
logger = logging.get_logger(__name__)
class ConditionalDetrFastImageProcessorKwargs(DefaultFastImageProcessorKwargs):
    format: Optional[Union[str, AnnotationFormat]]
    do_convert_annotations: Optional[bool]
    return_segmentation_masks: Optional[bool]
SUPPORTED_ANNOTATION_FORMATS = (AnnotationFormat.COCO_DETECTION, AnnotationFormat.COCO_PANOPTIC)
def convert_coco_poly_to_mask(segmentations, height: int, width: int, device: torch.device) -> torch.Tensor:
    try:
        from pycocotools import mask as coco_mask
    except ImportError:
        raise ImportError("Pycocotools is not installed in your environment.")
    masks = []
    for polygons in segmentations:
        rles = coco_mask.frPyObjects(polygons, height, width)
        mask = coco_mask.decode(rles)
        if len(mask.shape) < 3:
            mask = mask[..., None]
        mask = torch.as_tensor(mask, dtype=torch.uint8, device=device)
        mask = torch.any(mask, axis=2)
        masks.append(mask)
    if masks:
        masks = torch.stack(masks, axis=0)
    else:
        masks = torch.zeros((0, height, width), dtype=torch.uint8, device=device)
    return masks
def prepare_coco_detection_annotation(
    image,
    target,
    return_segmentation_masks: bool = False,
    input_data_format: Optional[Union[ChannelDimension, str]] = None,
):
    image_height, image_width = image.size()[-2:]
    image_id = target["image_id"]
    image_id = torch.as_tensor([image_id], dtype=torch.int64, device=image.device)
    annotations = target["annotations"]
    classes = []
    area = []
    boxes = []
    keypoints = []
    for obj in annotations:
        if "iscrowd" not in obj or obj["iscrowd"] == 0:
            classes.append(obj["category_id"])
            area.append(obj["area"])
            boxes.append(obj["bbox"])
            if "keypoints" in obj:
                keypoints.append(obj["keypoints"])
    classes = torch.as_tensor(classes, dtype=torch.int64, device=image.device)
    area = torch.as_tensor(area, dtype=torch.float32, device=image.device)
    iscrowd = torch.zeros_like(classes, dtype=torch.int64, device=image.device)
    boxes = torch.as_tensor(boxes, dtype=torch.float32, device=image.device).reshape(-1, 4)
    boxes[:, 2:] += boxes[:, :2]
    boxes[:, 0::2] = boxes[:, 0::2].clip(min=0, max=image_width)
    boxes[:, 1::2] = boxes[:, 1::2].clip(min=0, max=image_height)
    keep = (boxes[:, 3] > boxes[:, 1]) & (boxes[:, 2] > boxes[:, 0])
    new_target = {
        "image_id": image_id,
        "class_labels": classes[keep],
        "boxes": boxes[keep],
        "area": area[keep],
        "iscrowd": iscrowd[keep],
        "orig_size": torch.as_tensor([int(image_height), int(image_width)], dtype=torch.int64, device=image.device),
    }
    if keypoints:
        keypoints = torch.as_tensor(keypoints, dtype=torch.float32, device=image.device)
        keypoints = keypoints[keep]
        num_keypoints = keypoints.shape[0]
        keypoints = keypoints.reshape((-1, 3)) if num_keypoints else keypoints
        new_target["keypoints"] = keypoints
    if return_segmentation_masks:
        segmentation_masks = [obj["segmentation"] for obj in annotations]
        masks = convert_coco_poly_to_mask(segmentation_masks, image_height, image_width, device=image.device)
        new_target["masks"] = masks[keep]
    return new_target
def masks_to_boxes(masks: torch.Tensor) -> torch.Tensor:
    if masks.numel() == 0:
        return torch.zeros((0, 4), device=masks.device)
    h, w = masks.shape[-2:]
    y = torch.arange(0, h, dtype=torch.float32, device=masks.device)
    x = torch.arange(0, w, dtype=torch.float32, device=masks.device)
    y, x = torch.meshgrid(y, x, indexing="ij")
    x_mask = masks * torch.unsqueeze(x, 0)
    x_max = x_mask.view(x_mask.shape[0], -1).max(-1)[0]
    x_min = (
        torch.where(masks, x.unsqueeze(0), torch.tensor(1e8, device=masks.device)).view(masks.shape[0], -1).min(-1)[0]
    )
    y_mask = masks * torch.unsqueeze(y, 0)
    y_max = y_mask.view(y_mask.shape[0], -1).max(-1)[0]
    y_min = (
        torch.where(masks, y.unsqueeze(0), torch.tensor(1e8, device=masks.device)).view(masks.shape[0], -1).min(-1)[0]
    )
    return torch.stack([x_min, y_min, x_max, y_max], 1)
def rgb_to_id(color):
    if isinstance(color, torch.Tensor) and len(color.shape) == 3:
        if color.dtype == torch.uint8:
            color = color.to(torch.int32)
        return color[:, :, 0] + 256 * color[:, :, 1] + 256 * 256 * color[:, :, 2]
    return int(color[0] + 256 * color[1] + 256 * 256 * color[2])
def prepare_coco_panoptic_annotation(
    image: torch.Tensor,
    target: dict,
    masks_path: Union[str, pathlib.Path],
    return_masks: bool = True,
    input_data_format: Union[ChannelDimension, str] = None,
) -> dict:
    image_height, image_width = get_image_size(image, channel_dim=input_data_format)
    annotation_path = pathlib.Path(masks_path) / target["file_name"]
    new_target = {}
    new_target["image_id"] = torch.as_tensor(
        [target["image_id"] if "image_id" in target else target["id"]], dtype=torch.int64, device=image.device
    )
    new_target["size"] = torch.as_tensor([image_height, image_width], dtype=torch.int64, device=image.device)
    new_target["orig_size"] = torch.as_tensor([image_height, image_width], dtype=torch.int64, device=image.device)
    if "segments_info" in target:
        masks = read_image(annotation_path).permute(1, 2, 0).to(dtype=torch.int32, device=image.device)
        masks = rgb_to_id(masks)
        ids = torch.as_tensor([segment_info["id"] for segment_info in target["segments_info"]], device=image.device)
        masks = masks == ids[:, None, None]
        masks = masks.to(torch.bool)
        if return_masks:
            new_target["masks"] = masks
        new_target["boxes"] = masks_to_boxes(masks)
        new_target["class_labels"] = torch.as_tensor(
            [segment_info["category_id"] for segment_info in target["segments_info"]],
            dtype=torch.int64,
            device=image.device,
        )
        new_target["iscrowd"] = torch.as_tensor(
            [segment_info["iscrowd"] for segment_info in target["segments_info"]],
            dtype=torch.int64,
            device=image.device,
        )
        new_target["area"] = torch.as_tensor(
            [segment_info["area"] for segment_info in target["segments_info"]],
            dtype=torch.float32,
            device=image.device,
        )
    return new_target
@auto_docstring
@requires(backends=("torchvision", "torch"))
class ConditionalDetrImageProcessorFast(BaseImageProcessorFast):
    resample = PILImageResampling.BILINEAR
    image_mean = IMAGENET_DEFAULT_MEAN
    image_std = IMAGENET_DEFAULT_STD
    format = AnnotationFormat.COCO_DETECTION
    do_resize = True
    do_rescale = True
    do_normalize = True
    do_pad = True
    size = {"shortest_edge": 800, "longest_edge": 1333}
    default_to_square = False
    model_input_names = ["pixel_values", "pixel_mask"]
    valid_kwargs = ConditionalDetrFastImageProcessorKwargs
    def __init__(self, **kwargs: Unpack[ConditionalDetrFastImageProcessorKwargs]) -> None:
        if "pad_and_return_pixel_mask" in kwargs:
            kwargs["do_pad"] = kwargs.pop("pad_and_return_pixel_mask")
        size = kwargs.pop("size", None)
        if "max_size" in kwargs:
            logger.warning_once(
                "The `max_size` parameter is deprecated and will be removed in v4.26. "
                "Please specify in `size['longest_edge'] instead`.",
            )
            max_size = kwargs.pop("max_size")
        else:
            max_size = None if size is None else 1333
        size = size if size is not None else {"shortest_edge": 800, "longest_edge": 1333}
        self.size = get_size_dict(size, max_size=max_size, default_to_square=False)
        do_convert_annotations = kwargs.get("do_convert_annotations")
        do_normalize = kwargs.get("do_normalize")
        if do_convert_annotations is None and getattr(self, "do_convert_annotations", None) is None:
            self.do_convert_annotations = do_normalize if do_normalize is not None else self.do_normalize
        super().__init__(**kwargs)
    @classmethod
    def from_dict(cls, image_processor_dict: dict[str, Any], **kwargs):
        image_processor_dict = image_processor_dict.copy()
        if "max_size" in kwargs:
            image_processor_dict["max_size"] = kwargs.pop("max_size")
        if "pad_and_return_pixel_mask" in kwargs:
            image_processor_dict["pad_and_return_pixel_mask"] = kwargs.pop("pad_and_return_pixel_mask")
        return super().from_dict(image_processor_dict, **kwargs)
    def prepare_annotation(
        self,
        image: torch.Tensor,
        target: dict,
        format: Optional[AnnotationFormat] = None,
        return_segmentation_masks: Optional[bool] = None,
        masks_path: Optional[Union[str, pathlib.Path]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> dict:
        format = format if format is not None else self.format
        if format == AnnotationFormat.COCO_DETECTION:
            return_segmentation_masks = False if return_segmentation_masks is None else return_segmentation_masks
            target = prepare_coco_detection_annotation(
                image, target, return_segmentation_masks, input_data_format=input_data_format
            )
        elif format == AnnotationFormat.COCO_PANOPTIC:
            return_segmentation_masks = True if return_segmentation_masks is None else return_segmentation_masks
            target = prepare_coco_panoptic_annotation(
                image,
                target,
                masks_path=masks_path,
                return_masks=return_segmentation_masks,
                input_data_format=input_data_format,
            )
        else:
            raise ValueError(f"Format {format} is not supported.")
        return target
    def resize(
        self,
        image: torch.Tensor,
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"] = None,
        **kwargs,
    ) -> torch.Tensor:
        interpolation = interpolation if interpolation is not None else F.InterpolationMode.BILINEAR
        if size.shortest_edge and size.longest_edge:
            new_size = get_size_with_aspect_ratio(
                image.size()[-2:],
                size["shortest_edge"],
                size["longest_edge"],
            )
        elif size.max_height and size.max_width:
            new_size = get_image_size_for_max_height_width(image.size()[-2:], size["max_height"], size["max_width"])
        elif size.height and size.width:
            new_size = (size["height"], size["width"])
        else:
            raise ValueError(
                "Size must contain 'height' and 'width' keys or 'shortest_edge' and 'longest_edge' keys. Got"
                f" {size.keys()}."
            )
        image = F.resize(
            image,
            size=new_size,
            interpolation=interpolation,
            **kwargs,
        )
        return image
    def resize_annotation(
        self,
        annotation: dict[str, Any],
        orig_size: tuple[int, int],
        target_size: tuple[int, int],
        threshold: float = 0.5,
        interpolation: Optional["F.InterpolationMode"] = None,
    ):
        interpolation = interpolation if interpolation is not None else F.InterpolationMode.NEAREST_EXACT
        ratio_height, ratio_width = [target / orig for target, orig in zip(target_size, orig_size)]
        new_annotation = {}
        new_annotation["size"] = target_size
        for key, value in annotation.items():
            if key == "boxes":
                boxes = value
                scaled_boxes = boxes * torch.as_tensor(
                    [ratio_width, ratio_height, ratio_width, ratio_height], dtype=torch.float32, device=boxes.device
                )
                new_annotation["boxes"] = scaled_boxes
            elif key == "area":
                area = value
                scaled_area = area * (ratio_width * ratio_height)
                new_annotation["area"] = scaled_area
            elif key == "masks":
                masks = value[:, None]
                masks = [F.resize(mask, target_size, interpolation=interpolation) for mask in masks]
                masks = torch.stack(masks).to(torch.float32)
                masks = masks[:, 0] > threshold
                new_annotation["masks"] = masks
            elif key == "size":
                new_annotation["size"] = target_size
            else:
                new_annotation[key] = value
        return new_annotation
    def normalize_annotation(self, annotation: dict, image_size: tuple[int, int]) -> dict:
        image_height, image_width = image_size
        norm_annotation = {}
        for key, value in annotation.items():
            if key == "boxes":
                boxes = value
                boxes = corners_to_center_format(boxes)
                boxes /= torch.as_tensor(
                    [image_width, image_height, image_width, image_height], dtype=torch.float32, device=boxes.device
                )
                norm_annotation[key] = boxes
            else:
                norm_annotation[key] = value
        return norm_annotation
    def _update_annotation_for_padded_image(
        self,
        annotation: dict,
        input_image_size: tuple[int, int],
        output_image_size: tuple[int, int],
        padding,
        update_bboxes,
    ) -> dict:
        new_annotation = {}
        new_annotation["size"] = output_image_size
        ratio_height, ratio_width = (input / output for output, input in zip(output_image_size, input_image_size))
        for key, value in annotation.items():
            if key == "masks":
                masks = value
                masks = F.pad(
                    masks,
                    padding,
                    fill=0,
                )
                masks = safe_squeeze(masks, 1)
                new_annotation["masks"] = masks
            elif key == "boxes" and update_bboxes:
                boxes = value
                boxes *= torch.as_tensor([ratio_width, ratio_height, ratio_width, ratio_height], device=boxes.device)
                new_annotation["boxes"] = boxes
            elif key == "size":
                new_annotation["size"] = output_image_size
            else:
                new_annotation[key] = value
        return new_annotation
    def pad(
        self,
        image: torch.Tensor,
        padded_size: tuple[int, int],
        annotation: Optional[dict[str, Any]] = None,
        update_bboxes: bool = True,
        fill: int = 0,
    ):
        original_size = image.size()[-2:]
        padding_bottom = padded_size[0] - original_size[0]
        padding_right = padded_size[1] - original_size[1]
        if padding_bottom < 0 or padding_right < 0:
            raise ValueError(
                f"Padding dimensions are negative. Please make sure that the padded size is larger than the "
                f"original size. Got padded size: {padded_size}, original size: {original_size}."
            )
        if original_size != padded_size:
            padding = [0, 0, padding_right, padding_bottom]
            image = F.pad(image, padding, fill=fill)
            if annotation is not None:
                annotation = self._update_annotation_for_padded_image(
                    annotation, original_size, padded_size, padding, update_bboxes
                )
        pixel_mask = torch.zeros(padded_size, dtype=torch.int64, device=image.device)
        pixel_mask[: original_size[0], : original_size[1]] = 1
        return image, pixel_mask, annotation
    @auto_docstring
    def preprocess(
        self,
        images: ImageInput,
        annotations: Optional[Union[AnnotationType, list[AnnotationType]]] = None,
        masks_path: Optional[Union[str, pathlib.Path]] = None,
        **kwargs: Unpack[ConditionalDetrFastImageProcessorKwargs],
    ) -> BatchFeature:
        if "pad_and_return_pixel_mask" in kwargs:
            kwargs["do_pad"] = kwargs.pop("pad_and_return_pixel_mask")
            logger.warning_once(
                "The `pad_and_return_pixel_mask` argument is deprecated and will be removed in a future version, "
                "use `do_pad` instead."
            )
        if "max_size" in kwargs:
            logger.warning_once(
                "The `max_size` argument is deprecated and will be removed in a future version, use"
                " `size['longest_edge']` instead."
            )
            kwargs["size"] = kwargs.pop("max_size")
        return super().preprocess(images, annotations, masks_path, **kwargs)
    def _preprocess(
        self,
        images: list["torch.Tensor"],
        annotations: Optional[Union[AnnotationType, list[AnnotationType]]],
        masks_path: Optional[Union[str, pathlib.Path]],
        return_segmentation_masks: bool,
        do_resize: bool,
        size: SizeDict,
        interpolation: Optional["F.InterpolationMode"],
        do_rescale: bool,
        rescale_factor: float,
        do_normalize: bool,
        do_convert_annotations: bool,
        image_mean: Optional[Union[float, list[float]]],
        image_std: Optional[Union[float, list[float]]],
        do_pad: bool,
        pad_size: Optional[SizeDict],
        format: Optional[Union[str, AnnotationFormat]],
        return_tensors: Optional[Union[str, TensorType]],
        **kwargs,
    ) -> BatchFeature:
        if annotations is not None and isinstance(annotations, dict):
            annotations = [annotations]
        if annotations is not None and len(images) != len(annotations):
            raise ValueError(
                f"The number of images ({len(images)}) and annotations ({len(annotations)}) do not match."
            )
        format = AnnotationFormat(format)
        if annotations is not None:
            validate_annotations(format, SUPPORTED_ANNOTATION_FORMATS, annotations)
        if (
            masks_path is not None
            and format == AnnotationFormat.COCO_PANOPTIC
            and not isinstance(masks_path, (pathlib.Path, str))
        ):
            raise ValueError(
                "The path to the directory containing the mask PNG files should be provided as a"
                f" `pathlib.Path` or string object, but is {type(masks_path)} instead."
            )
        data = {}
        processed_images = []
        processed_annotations = []
        pixel_masks = []
        for image, annotation in zip(images, annotations if annotations is not None else [None] * len(images)):
            if annotations is not None:
                annotation = self.prepare_annotation(
                    image,
                    annotation,
                    format,
                    return_segmentation_masks=return_segmentation_masks,
                    masks_path=masks_path,
                    input_data_format=ChannelDimension.FIRST,
                )
            if do_resize:
                resized_image = self.resize(image, size=size, interpolation=interpolation)
                if annotations is not None:
                    annotation = self.resize_annotation(
                        annotation,
                        orig_size=image.size()[-2:],
                        target_size=resized_image.size()[-2:],
                    )
                image = resized_image
            image = self.rescale_and_normalize(image, do_rescale, rescale_factor, do_normalize, image_mean, image_std)
            if do_convert_annotations and annotations is not None:
                annotation = self.normalize_annotation(annotation, get_image_size(image, ChannelDimension.FIRST))
            processed_images.append(image)
            processed_annotations.append(annotation)
        images = processed_images
        annotations = processed_annotations if annotations is not None else None
        if do_pad:
            if pad_size is not None:
                padded_size = (pad_size.height, pad_size.width)
            else:
                padded_size = get_max_height_width(images)
            padded_images = []
            padded_annotations = []
            for image, annotation in zip(images, annotations if annotations is not None else [None] * len(images)):
                if padded_size == image.size()[-2:]:
                    padded_images.append(image)
                    pixel_masks.append(torch.ones(padded_size, dtype=torch.int64, device=image.device))
                    padded_annotations.append(annotation)
                    continue
                image, pixel_mask, annotation = self.pad(
                    image, padded_size, annotation=annotation, update_bboxes=do_convert_annotations
                )
                padded_images.append(image)
                padded_annotations.append(annotation)
                pixel_masks.append(pixel_mask)
            images = padded_images
            annotations = padded_annotations if annotations is not None else None
            data.update({"pixel_mask": torch.stack(pixel_masks, dim=0)})
        data.update({"pixel_values": torch.stack(images, dim=0)})
        encoded_inputs = BatchFeature(data, tensor_type=return_tensors)
        if annotations is not None:
            encoded_inputs["labels"] = [
                BatchFeature(annotation, tensor_type=return_tensors) for annotation in annotations
            ]
        return encoded_inputs
    def post_process(self, outputs, target_sizes):
        logging.warning_once(
            "`post_process` is deprecated and will be removed in v5 of MEROAI, please use"
            " `post_process_object_detection` instead, with `threshold=0.` for equivalent results.",
        )
        out_logits, out_bbox = outputs.logits, outputs.pred_boxes
        if len(out_logits) != len(target_sizes):
            raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        if target_sizes.shape[1] != 2:
            raise ValueError("Each element of target_sizes must contain the size (h, w) of each image of the batch")
        prob = out_logits.sigmoid()
        topk_values, topk_indexes = torch.topk(prob.view(out_logits.shape[0], -1), 300, dim=1)
        scores = topk_values
        topk_boxes = torch.div(topk_indexes, out_logits.shape[2], rounding_mode="floor")
        labels = topk_indexes % out_logits.shape[2]
        boxes = center_to_corners_format(out_bbox)
        boxes = torch.gather(boxes, 1, topk_boxes.unsqueeze(-1).repeat(1, 1, 4))
        img_h, img_w = target_sizes.unbind(1)
        scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1)
        boxes = boxes * scale_fct[:, None, :]
        results = [{"scores": s, "labels": l, "boxes": b} for s, l, b in zip(scores, labels, boxes)]
        return results
    def post_process_object_detection(
        self, outputs, threshold: float = 0.5, target_sizes: Union[TensorType, list[tuple]] = None, top_k: int = 100
    ):
        out_logits, out_bbox = outputs.logits, outputs.pred_boxes
        if target_sizes is not None:
            if len(out_logits) != len(target_sizes):
                raise ValueError(
                    "Make sure that you pass in as many target sizes as the batch dimension of the logits"
                )
        prob = out_logits.sigmoid()
        prob = prob.view(out_logits.shape[0], -1)
        k_value = min(top_k, prob.size(1))
        topk_values, topk_indexes = torch.topk(prob, k_value, dim=1)
        scores = topk_values
        topk_boxes = torch.div(topk_indexes, out_logits.shape[2], rounding_mode="floor")
        labels = topk_indexes % out_logits.shape[2]
        boxes = center_to_corners_format(out_bbox)
        boxes = torch.gather(boxes, 1, topk_boxes.unsqueeze(-1).repeat(1, 1, 4))
        if target_sizes is not None:
            if isinstance(target_sizes, list):
                img_h = torch.Tensor([i[0] for i in target_sizes])
                img_w = torch.Tensor([i[1] for i in target_sizes])
            else:
                img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(boxes.device)
            boxes = boxes * scale_fct[:, None, :]
        results = []
        for s, l, b in zip(scores, labels, boxes):
            score = s[s > threshold]
            label = l[s > threshold]
            box = b[s > threshold]
            results.append({"scores": score, "labels": label, "boxes": box})
        return results
    def post_process_semantic_segmentation(self, outputs, target_sizes: Optional[list[tuple[int, int]]] = None):
        class_queries_logits = outputs.logits
        masks_queries_logits = outputs.pred_masks
        masks_classes = class_queries_logits.softmax(dim=-1)[..., :-1]
        masks_probs = masks_queries_logits.sigmoid()
        segmentation = torch.einsum("bqc, bqhw -> bchw", masks_classes, masks_probs)
        batch_size = class_queries_logits.shape[0]
        if target_sizes is not None:
            if batch_size != len(target_sizes):
                raise ValueError(
                    "Make sure that you pass in as many target sizes as the batch dimension of the logits"
                )
            semantic_segmentation = []
            for idx in range(batch_size):
                resized_logits = nn.functional.interpolate(
                    segmentation[idx].unsqueeze(dim=0), size=target_sizes[idx], mode="bilinear", align_corners=False
                )
                semantic_map = resized_logits[0].argmax(dim=0)
                semantic_segmentation.append(semantic_map)
        else:
            semantic_segmentation = segmentation.argmax(dim=1)
            semantic_segmentation = [semantic_segmentation[i] for i in range(semantic_segmentation.shape[0])]
        return semantic_segmentation
    def post_process_instance_segmentation(
        self,
        outputs,
        threshold: float = 0.5,
        mask_threshold: float = 0.5,
        overlap_mask_area_threshold: float = 0.8,
        target_sizes: Optional[list[tuple[int, int]]] = None,
        return_coco_annotation: Optional[bool] = False,
    ) -> list[dict]:
        class_queries_logits = outputs.logits
        masks_queries_logits = outputs.pred_masks
        batch_size = class_queries_logits.shape[0]
        num_labels = class_queries_logits.shape[-1] - 1
        mask_probs = masks_queries_logits.sigmoid()
        pred_scores, pred_labels = nn.functional.softmax(class_queries_logits, dim=-1).max(-1)
        results: list[dict[str, TensorType]] = []
        for i in range(batch_size):
            mask_probs_item, pred_scores_item, pred_labels_item = remove_low_and_no_objects(
                mask_probs[i], pred_scores[i], pred_labels[i], threshold, num_labels
            )
            if mask_probs_item.shape[0] <= 0:
                height, width = target_sizes[i] if target_sizes is not None else mask_probs_item.shape[1:]
                segmentation = torch.zeros((height, width)) - 1
                results.append({"segmentation": segmentation, "segments_info": []})
                continue
            target_size = target_sizes[i] if target_sizes is not None else None
            segmentation, segments = compute_segments(
                mask_probs=mask_probs_item,
                pred_scores=pred_scores_item,
                pred_labels=pred_labels_item,
                mask_threshold=mask_threshold,
                overlap_mask_area_threshold=overlap_mask_area_threshold,
                label_ids_to_fuse=[],
                target_size=target_size,
            )
            if return_coco_annotation:
                segmentation = convert_segmentation_to_rle(segmentation)
            results.append({"segmentation": segmentation, "segments_info": segments})
        return results
    def post_process_panoptic_segmentation(
        self,
        outputs,
        threshold: float = 0.5,
        mask_threshold: float = 0.5,
        overlap_mask_area_threshold: float = 0.8,
        label_ids_to_fuse: Optional[set[int]] = None,
        target_sizes: Optional[list[tuple[int, int]]] = None,
    ) -> list[dict]:
        if label_ids_to_fuse is None:
            logger.warning_once("`label_ids_to_fuse` unset. No instance will be fused.")
            label_ids_to_fuse = set()
        class_queries_logits = outputs.logits
        masks_queries_logits = outputs.pred_masks
        batch_size = class_queries_logits.shape[0]
        num_labels = class_queries_logits.shape[-1] - 1
        mask_probs = masks_queries_logits.sigmoid()
        pred_scores, pred_labels = nn.functional.softmax(class_queries_logits, dim=-1).max(-1)
        results: list[dict[str, TensorType]] = []
        for i in range(batch_size):
            mask_probs_item, pred_scores_item, pred_labels_item = remove_low_and_no_objects(
                mask_probs[i], pred_scores[i], pred_labels[i], threshold, num_labels
            )
            if mask_probs_item.shape[0] <= 0:
                height, width = target_sizes[i] if target_sizes is not None else mask_probs_item.shape[1:]
                segmentation = torch.zeros((height, width)) - 1
                results.append({"segmentation": segmentation, "segments_info": []})
                continue
            target_size = target_sizes[i] if target_sizes is not None else None
            segmentation, segments = compute_segments(
                mask_probs=mask_probs_item,
                pred_scores=pred_scores_item,
                pred_labels=pred_labels_item,
                mask_threshold=mask_threshold,
                overlap_mask_area_threshold=overlap_mask_area_threshold,
                label_ids_to_fuse=label_ids_to_fuse,
                target_size=target_size,
            )
            results.append({"segmentation": segmentation, "segments_info": segments})
        return results
__all__ = ["ConditionalDetrImageProcessorFast"]