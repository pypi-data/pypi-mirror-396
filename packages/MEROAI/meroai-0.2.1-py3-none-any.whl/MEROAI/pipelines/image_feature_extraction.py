from typing import Any, Union
from ..utils import add_end_docstrings, is_vision_available
from .base import GenericTensor, Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
@add_end_docstrings(
    build_pipeline_init_args(has_image_processor=True),
,
)
class ImageFeatureExtractionPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = False
    def _sanitize_parameters(self, image_processor_kwargs=None, return_tensors=None, pool=None, **kwargs):
        preprocess_params = {} if image_processor_kwargs is None else image_processor_kwargs
        postprocess_params = {}
        if pool is not None:
            postprocess_params["pool"] = pool
        if return_tensors is not None:
            postprocess_params["return_tensors"] = return_tensors
        if "timeout" in kwargs:
            preprocess_params["timeout"] = kwargs["timeout"]
        return preprocess_params, {}, postprocess_params
    def preprocess(self, image, timeout=None, **image_processor_kwargs) -> dict[str, GenericTensor]:
        image = load_image(image, timeout=timeout)
        model_inputs = self.image_processor(image, return_tensors=self.framework, **image_processor_kwargs)
        if self.framework == "pt":
            model_inputs = model_inputs.to(self.dtype)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, pool=None, return_tensors=False):
        pool = pool if pool is not None else False
        if pool:
            if "pooler_output" not in model_outputs:
                raise ValueError(
                    "No pooled output was returned. Make sure the model has a `pooler` layer when using the `pool` option."
                )
            outputs = model_outputs["pooler_output"]
        else:
            outputs = model_outputs[0]
        if return_tensors:
            return outputs
        if self.framework == "pt":
            return outputs.tolist()
        elif self.framework == "tf":
            return outputs.numpy().tolist()
    def __call__(self, *args: Union[str, "Image.Image", list["Image.Image"], list[str]], **kwargs: Any) -> list[Any]:
        return super().__call__(*args, **kwargs)