from typing import Any, Union, overload
from ..utils import (
    add_end_docstrings,
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
    from ..models.auto.modeling_auto import MODEL_FOR_DEPTH_ESTIMATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_image_processor=True))
class DepthEstimationPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(MODEL_FOR_DEPTH_ESTIMATION_MAPPING_NAMES)
    @overload
    def __call__(self, inputs: Union[str, "Image.Image"], **kwargs: Any) -> dict[str, Any]: ...
    @overload
    def __call__(self, inputs: list[Union[str, "Image.Image"]], **kwargs: Any) -> list[dict[str, Any]]: ...
    def __call__(
        self, inputs: Union[str, list[str], "Image.Image", list["Image.Image"]], **kwargs: Any
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        if "images" in kwargs:
            inputs = kwargs.pop("images")
        if inputs is None:
            raise ValueError("Cannot call the depth-estimation pipeline without an inputs argument!")
        return super().__call__(inputs, **kwargs)
    def _sanitize_parameters(self, timeout=None, parameters=None, **kwargs):
        preprocess_params = {}
        if timeout is not None:
            preprocess_params["timeout"] = timeout
        if isinstance(parameters, dict) and "timeout" in parameters:
            preprocess_params["timeout"] = parameters["timeout"]
        return preprocess_params, {}, {}
    def preprocess(self, image, timeout=None):
        image = load_image(image, timeout)
        model_inputs = self.image_processor(images=image, return_tensors=self.framework)
        if self.framework == "pt":
            model_inputs = model_inputs.to(self.dtype)
        model_inputs["target_size"] = image.size[::-1]
        return model_inputs
    def _forward(self, model_inputs):
        target_size = model_inputs.pop("target_size")
        model_outputs = self.model(**model_inputs)
        model_outputs["target_size"] = target_size
        return model_outputs
    def postprocess(self, model_outputs):
        outputs = self.image_processor.post_process_depth_estimation(
            model_outputs,
            [model_outputs["target_size"]],
        )
        formatted_outputs = []
        for output in outputs:
            depth = output["predicted_depth"].detach().cpu().numpy()
            depth = (depth - depth.min()) / (depth.max() - depth.min())
            depth = Image.fromarray((depth * 255).astype("uint8"))
            formatted_outputs.append({"predicted_depth": output["predicted_depth"], "depth": depth})
        return formatted_outputs[0] if len(outputs) == 1 else formatted_outputs