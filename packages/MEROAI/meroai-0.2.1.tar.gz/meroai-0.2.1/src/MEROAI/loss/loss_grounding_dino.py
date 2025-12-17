import torch
import torch.nn as nn
from ..image_transforms import center_to_corners_format
from ..utils import is_scipy_available
from .loss_for_object_detection import HungarianMatcher, ImageLoss, _set_aux_loss, generalized_box_iou
if is_scipy_available():
    from scipy.optimize import linear_sum_assignment
def sigmoid_focal_loss(
    inputs: torch.Tensor,
    targets: torch.Tensor,
    num_boxes: int,
    alpha: float = 0.25,
    gamma: float = 2,
):
    prob = inputs.sigmoid()
    ce_loss = nn.functional.binary_cross_entropy_with_logits(inputs, targets, reduction="none")
    p_t = prob * targets + (1 - prob) * (1 - targets)
    loss = ce_loss * ((1 - p_t) ** gamma)
    if alpha >= 0:
        alpha_t = alpha * targets + (1 - alpha) * (1 - targets)
        loss = alpha_t * loss
    return loss.sum() / num_boxes
class GroundingDinoHungarianMatcher(HungarianMatcher):
    @torch.no_grad()
    def forward(self, outputs, targets):
        batch_size, num_queries = outputs["logits"].shape[:2]
        out_prob = outputs["logits"].flatten(0, 1).sigmoid()
        out_bbox = outputs["pred_boxes"].flatten(0, 1)
        label_maps = outputs["label_maps"]
        label_maps = torch.cat([label_map[target["class_labels"]] for label_map, target in zip(label_maps, targets)])
        label_maps = label_maps / label_maps.sum(dim=-1, keepdim=True)
        target_bbox = torch.cat([v["boxes"] for v in targets])
        alpha = 0.25
        gamma = 2.0
        neg_cost_class = (1 - alpha) * (out_prob**gamma) * (-(1 - out_prob + 1e-8).log())
        pos_cost_class = alpha * ((1 - out_prob) ** gamma) * (-(out_prob + 1e-8).log())
        class_cost = (pos_cost_class - neg_cost_class) @ label_maps.t()
        bbox_cost = torch.cdist(out_bbox, target_bbox, p=1)
        giou_cost = -generalized_box_iou(center_to_corners_format(out_bbox), center_to_corners_format(target_bbox))
        cost_matrix = self.bbox_cost * bbox_cost + self.class_cost * class_cost + self.giou_cost * giou_cost
        cost_matrix = cost_matrix.view(batch_size, num_queries, -1).cpu()
        sizes = [len(v["boxes"]) for v in targets]
        indices = [linear_sum_assignment(c[i]) for i, c in enumerate(cost_matrix.split(sizes, -1))]
        return [(torch.as_tensor(i, dtype=torch.int64), torch.as_tensor(j, dtype=torch.int64)) for i, j in indices]
class GroundingDinoImageLoss(ImageLoss):
    def __init__(self, matcher, focal_alpha, losses):
        nn.Module.__init__(self)
        self.matcher = matcher
        self.focal_alpha = focal_alpha
        self.losses = losses
    def _get_target_classes_one_hot(self, outputs, targets, indices):
        logits = outputs["logits"]
        class_labels = torch.cat(
            [
                target["class_labels"][J] + len(outputs["label_maps"][i]) if i > 0 else target["class_labels"][J]
                for i, (target, (_, J)) in enumerate(zip(targets, indices))
            ]
        )
        label_maps = torch.cat(outputs["label_maps"], dim=0)
        idx = self._get_source_permutation_idx(indices)
        target_classes_onehot = torch.zeros_like(logits, device=logits.device, dtype=torch.long)
        target_classes_onehot[idx] = label_maps[class_labels].to(torch.long)
        return target_classes_onehot
    def loss_labels(self, outputs, targets, indices, num_boxes):
        if "logits" not in outputs:
            raise KeyError("No logits were found in the outputs")
        if "text_mask" not in outputs:
            raise KeyError("No text_mask were found in the outputs")
        target_classes_onehot = self._get_target_classes_one_hot(outputs, targets, indices)
        source_logits = outputs["logits"]
        text_mask = outputs["text_mask"]
        source_logits = torch.masked_select(source_logits, text_mask)
        target_classes_onehot = torch.masked_select(target_classes_onehot, text_mask)
        target_classes_onehot = target_classes_onehot.float()
        loss_ce = sigmoid_focal_loss(
            inputs=source_logits,
            targets=target_classes_onehot,
            num_boxes=num_boxes,
            alpha=self.focal_alpha,
            gamma=2,
        )
        losses = {"loss_ce": loss_ce}
        return losses
def GroundingDinoForObjectDetectionLoss(
    logits,
    labels,
    device,
    pred_boxes,
    config,
    label_maps,
    text_mask,
    outputs_class=None,
    outputs_coord=None,
    encoder_logits=None,
    encoder_pred_boxes=None,
):
    matcher = GroundingDinoHungarianMatcher(
        class_cost=config.class_cost, bbox_cost=config.bbox_cost, giou_cost=config.giou_cost
    )
    losses = ["labels", "boxes", "cardinality"]
    criterion = GroundingDinoImageLoss(
        matcher=matcher,
        focal_alpha=config.focal_alpha,
        losses=losses,
    )
    criterion.to(device)
    outputs_loss = {}
    outputs_loss["logits"] = logits
    outputs_loss["pred_boxes"] = pred_boxes
    outputs_loss["label_maps"] = label_maps
    outputs_loss["text_mask"] = text_mask
    auxiliary_outputs = None
    if config.auxiliary_loss:
        auxiliary_outputs = _set_aux_loss(outputs_class, outputs_coord)
        for aux_output in auxiliary_outputs:
            aux_output["label_maps"] = label_maps
            aux_output["text_mask"] = text_mask
        outputs_loss["auxiliary_outputs"] = auxiliary_outputs
    loss_dict = criterion(outputs_loss, labels)
    if config.two_stage:
        encoder_outputs_loss = {
            "logits": encoder_logits,
            "pred_boxes": encoder_pred_boxes,
            "label_maps": label_maps,
            "text_mask": text_mask,
        }
        encoder_loss_dict = criterion(encoder_outputs_loss, labels)
        encoder_loss_dict = {k + "_enc": v for k, v in encoder_loss_dict.items()}
        loss_dict.update(encoder_loss_dict)
    weight_dict = {
        "loss_ce": 2.0,
        "loss_bbox": config.bbox_loss_coefficient,
        "loss_giou": config.giou_loss_coefficient,
    }
    if config.two_stage:
        enc_weight_dict = {k + "_enc": v for k, v in weight_dict.items()}
        weight_dict.update(enc_weight_dict)
    if config.auxiliary_loss:
        aux_weight_dict = {}
        for i in range(config.decoder_layers - 1):
            aux_weight_dict.update({k + f"_{i}": v for k, v in weight_dict.items()})
        weight_dict.update(aux_weight_dict)
    loss = sum(loss_dict[k] * weight_dict[k] for k in loss_dict if k in weight_dict)
    return loss, loss_dict, auxiliary_outputs