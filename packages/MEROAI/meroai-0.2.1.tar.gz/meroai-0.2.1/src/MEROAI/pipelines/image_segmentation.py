from typing import Any, Union, overload
import numpy as np
from ..utils import add_end_docstrings, is_torch_available, is_vision_available, logging, requires_backends
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available():
    from ..models.auto.modeling_auto import (
        MODEL_FOR_IMAGE_SEGMENTATION_MAPPING_NAMES,
        MODEL_FOR_INSTANCE_SEGMENTATION_MAPPING_NAMES,
        MODEL_FOR_SEMANTIC_SEGMENTATION_MAPPING_NAMES,
        MODEL_FOR_UNIVERSAL_SEGMENTATION_MAPPING_NAMES,
    )
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class ImageSegmentationPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.framework == "tf":
            raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        requires_backends(self, "vision")
        mapping = MODEL_FOR_IMAGE_SEGMENTATION_MAPPING_NAMES.copy()
        mapping.update(MODEL_FOR_SEMANTIC_SEGMENTATION_MAPPING_NAMES)
        mapping.update(MODEL_FOR_INSTANCE_SEGMENTATION_MAPPING_NAMES)
        mapping.update(MODEL_FOR_UNIVERSAL_SEGMENTATION_MAPPING_NAMES)
        self.check_model_type(mapping)
    def _sanitize_parameters(self, **kwargs):
        preprocess_kwargs = {}
        postprocess_kwargs = {}
        if "subtask" in kwargs:
            postprocess_kwargs["subtask"] = kwargs["subtask"]
            preprocess_kwargs["subtask"] = kwargs["subtask"]
        if "threshold" in kwargs:
            postprocess_kwargs["threshold"] = kwargs["threshold"]
        if "mask_threshold" in kwargs:
            postprocess_kwargs["mask_threshold"] = kwargs["mask_threshold"]
        if "overlap_mask_area_threshold" in kwargs:
            postprocess_kwargs["overlap_mask_area_threshold"] = kwargs["overlap_mask_area_threshold"]
        if "timeout" in kwargs:
            preprocess_kwargs["timeout"] = kwargs["timeout"]
        return preprocess_kwargs, {}, postprocess_kwargs
    @overload
    def __call__(self, inputs: Union[str, "Image.Image"], **kwargs: Any) -> list[dict[str, Any]]: ...
    @overload
    def __call__(self, inputs: Union[list[str], list["Image.Image"]], **kwargs: Any) -> list[list[dict[str, Any]]]: ...
    def __call__(
        self, inputs: Union[str, "Image.Image", list[str], list["Image.Image"]], **kwargs: Any
    ) -> Union[list[dict[str, Any]], list[list[dict[str, Any]]]]:
        if "images" in kwargs:
            inputs = kwargs.pop("images")
        if inputs is None:
            raise ValueError("Cannot call the image-classification pipeline without an inputs argument!")
        return super().__call__(inputs, **kwargs)
    def preprocess(self, image, subtask=None, timeout=None):
        image = load_image(image, timeout=timeout)
        target_size = [(image.height, image.width)]
        if self.model.config.__class__.__name__ == "OneFormerConfig":
            if subtask is None:
                kwargs = {}
            else:
                kwargs = {"task_inputs": [subtask]}
            inputs = self.image_processor(images=[image], return_tensors="pt", **kwargs)
            if self.framework == "pt":
                inputs = inputs.to(self.dtype)
            inputs["task_inputs"] = self.tokenizer(
                inputs["task_inputs"],
                padding="max_length",
                max_length=self.model.config.task_seq_len,
                return_tensors=self.framework,
            )["input_ids"]
        else:
            inputs = self.image_processor(images=[image], return_tensors="pt")
            if self.framework == "pt":
                inputs = inputs.to(self.dtype)
        inputs["target_size"] = target_size
        return inputs
    def _forward(self, model_inputs):
        target_size = model_inputs.pop("target_size")
        model_outputs = self.model(**model_inputs)
        model_outputs["target_size"] = target_size
        return model_outputs
    def postprocess(
        self, model_outputs, subtask=None, threshold=0.9, mask_threshold=0.5, overlap_mask_area_threshold=0.5
    ):
        fn = None
        if subtask in {"panoptic", None} and hasattr(self.image_processor, "post_process_panoptic_segmentation"):
            fn = self.image_processor.post_process_panoptic_segmentation
        elif subtask in {"instance", None} and hasattr(self.image_processor, "post_process_instance_segmentation"):
            fn = self.image_processor.post_process_instance_segmentation
        if fn is not None:
            outputs = fn(
                model_outputs,
                threshold=threshold,
                mask_threshold=mask_threshold,
                overlap_mask_area_threshold=overlap_mask_area_threshold,
                target_sizes=model_outputs["target_size"],
            )[0]
            annotation = []
            segmentation = outputs["segmentation"]
            for segment in outputs["segments_info"]:
                mask = (segmentation == segment["id"]) * 255
                mask = Image.fromarray(mask.numpy().astype(np.uint8), mode="L")
                label = self.model.config.id2label[segment["label_id"]]
                score = segment["score"]
                annotation.append({"score": score, "label": label, "mask": mask})
        elif subtask in {"semantic", None} and hasattr(self.image_processor, "post_process_semantic_segmentation"):
            outputs = self.image_processor.post_process_semantic_segmentation(
                model_outputs, target_sizes=model_outputs["target_size"]
            )[0]
            annotation = []
            segmentation = outputs.numpy()
            labels = np.unique(segmentation)
            for label in labels:
                mask = (segmentation == label) * 255
                mask = Image.fromarray(mask.astype(np.uint8), mode="L")
                label = self.model.config.id2label[label]
                annotation.append({"score": None, "label": label, "mask": mask})
        else:
            raise ValueError(f"Subtask {subtask} is not supported for model {type(self.model)}")
        return annotation