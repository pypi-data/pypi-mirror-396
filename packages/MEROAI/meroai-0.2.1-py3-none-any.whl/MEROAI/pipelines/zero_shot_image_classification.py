import warnings
from collections import UserDict
from typing import Any, Union, overload
from ..utils import (
    add_end_docstrings,
    is_tf_available,
    is_torch_available,
    is_vision_available,
    logging,
    requires_backends,
)
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING_NAMES
if is_tf_available():
    from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING_NAMES
    from ..tf_utils import stable_softmax
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class ZeroShotImageClassificationPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        requires_backends(self, "vision")
        self.check_model_type(
            TF_MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING_NAMES
            if self.framework == "tf"
            else MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING_NAMES
        )
    @overload
    def __call__(
        self, image: Union[str, "Image.Image"], candidate_labels: list[str], **kwargs: Any
    ) -> list[dict[str, Any]]: ...
    @overload
    def __call__(
        self, image: Union[list[str], list["Image.Image"]], candidate_labels: list[str], **kwargs: Any
    ) -> list[list[dict[str, Any]]]: ...
    def __call__(
        self,
        image: Union[str, list[str], "Image.Image", list["Image.Image"]],
        candidate_labels: list[str],
        **kwargs: Any,
    ) -> Union[list[dict[str, Any]], list[list[dict[str, Any]]]]:
        if "images" in kwargs:
            image = kwargs.pop("images")
        if image is None:
            raise ValueError("Cannot call the zero-shot-image-classification pipeline without an images argument!")
        return super().__call__(image, candidate_labels=candidate_labels, **kwargs)
    def _sanitize_parameters(self, tokenizer_kwargs=None, **kwargs):
        preprocess_params = {}
        if "candidate_labels" in kwargs:
            preprocess_params["candidate_labels"] = kwargs["candidate_labels"]
        if "timeout" in kwargs:
            preprocess_params["timeout"] = kwargs["timeout"]
        if "hypothesis_template" in kwargs:
            preprocess_params["hypothesis_template"] = kwargs["hypothesis_template"]
        if tokenizer_kwargs is not None:
            warnings.warn(
                "The `tokenizer_kwargs` argument is deprecated and will be removed in version 5 of MEROAI",
                FutureWarning,
            )
            preprocess_params["tokenizer_kwargs"] = tokenizer_kwargs
        return preprocess_params, {}, {}
    def preprocess(
        self,
        image,
        candidate_labels=None,
        hypothesis_template="This is a photo of {}.",
        timeout=None,
        tokenizer_kwargs=None,
    ):
        if tokenizer_kwargs is None:
            tokenizer_kwargs = {}
        image = load_image(image, timeout=timeout)
        inputs = self.image_processor(images=[image], return_tensors=self.framework)
        if self.framework == "pt":
            inputs = inputs.to(self.dtype)
        inputs["candidate_labels"] = candidate_labels
        sequences = [hypothesis_template.format(x) for x in candidate_labels]
        tokenizer_default_kwargs = {"padding": True}
        if "siglip" in self.model.config.model_type:
            tokenizer_default_kwargs.update(padding="max_length", max_length=64, truncation=True)
        tokenizer_default_kwargs.update(tokenizer_kwargs)
        text_inputs = self.tokenizer(sequences, return_tensors=self.framework, **tokenizer_default_kwargs)
        inputs["text_inputs"] = [text_inputs]
        return inputs
    def _forward(self, model_inputs):
        candidate_labels = model_inputs.pop("candidate_labels")
        text_inputs = model_inputs.pop("text_inputs")
        if isinstance(text_inputs[0], UserDict):
            text_inputs = text_inputs[0]
        else:
            text_inputs = text_inputs[0][0]
        outputs = self.model(**text_inputs, **model_inputs)
        model_outputs = {
            "candidate_labels": candidate_labels,
            "logits": outputs.logits_per_image,
        }
        return model_outputs
    def postprocess(self, model_outputs):
        candidate_labels = model_outputs.pop("candidate_labels")
        logits = model_outputs["logits"][0]
        if self.framework == "pt" and "siglip" in self.model.config.model_type:
            probs = torch.sigmoid(logits).squeeze(-1)
            scores = probs.tolist()
            if not isinstance(scores, list):
                scores = [scores]
        elif self.framework == "pt":
            probs = logits.softmax(dim=-1).squeeze(-1)
            scores = probs.tolist()
            if not isinstance(scores, list):
                scores = [scores]
        elif self.framework == "tf":
            probs = stable_softmax(logits, axis=-1)
            scores = probs.numpy().tolist()
        else:
            raise ValueError(f"Unsupported framework: {self.framework}")
        result = [
            {"score": score, "label": candidate_label}
            for score, candidate_label in sorted(zip(scores, candidate_labels), key=lambda x: -x[0])
        ]
        return result