from typing import Union
import torch
from MEROAI.models.detr.image_processing_detr_fast import DetrImageProcessorFast
from ...image_transforms import center_to_corners_format
from ...utils import (
    TensorType,
    logging,
)
logger = logging.get_logger(__name__)
class DeformableDetrImageProcessorFast(DetrImageProcessorFast):
    def post_process(self, outputs, target_sizes):
        logger.warning_once(
            "`post_process` is deprecated and will be removed in v5 of MEROAI, please use"
            " `post_process_object_detection` instead, with `threshold=0.` for equivalent results.",
        )
        out_logits, out_bbox = outputs.logits, outputs.pred_boxes
        if len(out_logits) != len(target_sizes):
            raise ValueError("Make sure that you pass in as many target sizes as the batch dimension of the logits")
        if target_sizes.shape[1] != 2:
            raise ValueError("Each element of target_sizes must contain the size (h, w) of each image of the batch")
        prob = out_logits.sigmoid()
        topk_values, topk_indexes = torch.topk(prob.view(out_logits.shape[0], -1), 100, dim=1)
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
    def post_process_segmentation(self):
        raise NotImplementedError("Segmentation post-processing is not implemented for Deformable DETR yet.")
    def post_process_instance(self):
        raise NotImplementedError("Instance post-processing is not implemented for Deformable DETR yet.")
    def post_process_panoptic(self):
        raise NotImplementedError("Panoptic post-processing is not implemented for Deformable DETR yet.")
    def post_process_instance_segmentation(self):
        raise NotImplementedError("Segmentation post-processing is not implemented for Deformable DETR yet.")
    def post_process_semantic_segmentation(self):
        raise NotImplementedError("Semantic segmentation post-processing is not implemented for Deformable DETR yet.")
    def post_process_panoptic_segmentation(self):
        raise NotImplementedError("Panoptic segmentation post-processing is not implemented for Deformable DETR yet.")
__all__ = ["DeformableDetrImageProcessorFast"]