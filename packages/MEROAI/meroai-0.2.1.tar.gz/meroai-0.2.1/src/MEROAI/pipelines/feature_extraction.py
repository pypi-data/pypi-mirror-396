from typing import Any, Union
from ..utils import add_end_docstrings
from .base import GenericTensor, Pipeline, build_pipeline_init_args
@add_end_docstrings(
    build_pipeline_init_args(has_tokenizer=True, supports_binary_output=False),
,
)
class FeatureExtractionPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = False
    _load_feature_extractor = False
    _load_tokenizer = True
    def _sanitize_parameters(self, truncation=None, tokenize_kwargs=None, return_tensors=None, **kwargs):
        if tokenize_kwargs is None:
            tokenize_kwargs = {}
        if truncation is not None:
            if "truncation" in tokenize_kwargs:
                raise ValueError(
                    "truncation parameter defined twice (given as keyword argument as well as in tokenize_kwargs)"
                )
            tokenize_kwargs["truncation"] = truncation
        preprocess_params = tokenize_kwargs
        postprocess_params = {}
        if return_tensors is not None:
            postprocess_params["return_tensors"] = return_tensors
        return preprocess_params, {}, postprocess_params
    def preprocess(self, inputs, **tokenize_kwargs) -> dict[str, GenericTensor]:
        model_inputs = self.tokenizer(inputs, return_tensors=self.framework, **tokenize_kwargs)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, return_tensors=False):
        if return_tensors:
            return model_outputs[0]
        if self.framework == "pt":
            return model_outputs[0].tolist()
        elif self.framework == "tf":
            return model_outputs[0].numpy().tolist()
    def __call__(self, *args: Union[str, list[str]], **kwargs: Any) -> Union[Any, list[Any]]:
        return super().__call__(*args, **kwargs)