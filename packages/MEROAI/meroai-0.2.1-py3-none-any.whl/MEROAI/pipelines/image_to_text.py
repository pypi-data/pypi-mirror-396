from typing import Any, Union, overload
from ..generation import GenerationConfig
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
if is_tf_available():
    from ..models.auto.modeling_tf_auto import TF_MODEL_FOR_VISION_2_SEQ_MAPPING_NAMES
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_VISION_2_SEQ_MAPPING_NAMES
logger = logging.get_logger(__name__)
@add_end_docstrings(build_pipeline_init_args(has_tokenizer=True, has_image_processor=True))
class ImageToTextPipeline(Pipeline):
    _pipeline_calls_generate = True
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = True
    _default_generation_config = GenerationConfig(
        max_new_tokens=256,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(
            TF_MODEL_FOR_VISION_2_SEQ_MAPPING_NAMES if self.framework == "tf" else MODEL_FOR_VISION_2_SEQ_MAPPING_NAMES
        )
    def _sanitize_parameters(self, max_new_tokens=None, generate_kwargs=None, prompt=None, timeout=None):
        forward_params = {}
        preprocess_params = {}
        if prompt is not None:
            preprocess_params["prompt"] = prompt
        if timeout is not None:
            preprocess_params["timeout"] = timeout
        if max_new_tokens is not None:
            forward_params["max_new_tokens"] = max_new_tokens
        if generate_kwargs is not None:
            if max_new_tokens is not None and "max_new_tokens" in generate_kwargs:
                raise ValueError(
                    "`max_new_tokens` is defined both as an argument and inside `generate_kwargs` argument, please use"
                    " only 1 version"
                )
            forward_params.update(generate_kwargs)
        if self.assistant_model is not None:
            forward_params["assistant_model"] = self.assistant_model
        if self.assistant_tokenizer is not None:
            forward_params["tokenizer"] = self.tokenizer
            forward_params["assistant_tokenizer"] = self.assistant_tokenizer
        return preprocess_params, forward_params, {}
    @overload
    def __call__(self, inputs: Union[str, "Image.Image"], **kwargs: Any) -> list[dict[str, Any]]: ...
    @overload
    def __call__(self, inputs: Union[list[str], list["Image.Image"]], **kwargs: Any) -> list[list[dict[str, Any]]]: ...
    def __call__(self, inputs: Union[str, list[str], "Image.Image", list["Image.Image"]], **kwargs):
        if "images" in kwargs:
            inputs = kwargs.pop("images")
        if inputs is None:
            raise ValueError("Cannot call the image-to-text pipeline without an inputs argument!")
        return super().__call__(inputs, **kwargs)
    def preprocess(self, image, prompt=None, timeout=None):
        image = load_image(image, timeout=timeout)
        if prompt is not None:
            logger.warning_once(
                "Passing `prompt` to the `image-to-text` pipeline is deprecated and will be removed in version 4.48"
                " of 🤗 MEROAI. Use the `image-text-to-text` pipeline instead",
            )
            if not isinstance(prompt, str):
                raise ValueError(
                    f"Received an invalid text input, got - {type(prompt)} - but expected a single string. "
                    "Note also that one single text can be provided for conditional image to text generation."
                )
            model_type = self.model.config.model_type
            if model_type == "git":
                model_inputs = self.image_processor(images=image, return_tensors=self.framework)
                if self.framework == "pt":
                    model_inputs = model_inputs.to(self.dtype)
                input_ids = self.tokenizer(text=prompt, add_special_tokens=False).input_ids
                input_ids = [self.tokenizer.cls_token_id] + input_ids
                input_ids = torch.tensor(input_ids).unsqueeze(0)
                model_inputs.update({"input_ids": input_ids})
            elif model_type == "pix2struct":
                model_inputs = self.image_processor(images=image, header_text=prompt, return_tensors=self.framework)
                if self.framework == "pt":
                    model_inputs = model_inputs.to(self.dtype)
            elif model_type != "vision-encoder-decoder":
                model_inputs = self.image_processor(images=image, return_tensors=self.framework)
                if self.framework == "pt":
                    model_inputs = model_inputs.to(self.dtype)
                text_inputs = self.tokenizer(prompt, return_tensors=self.framework)
                model_inputs.update(text_inputs)
            else:
                raise ValueError(f"Model type {model_type} does not support conditional text generation")
        else:
            model_inputs = self.image_processor(images=image, return_tensors=self.framework)
            if self.framework == "pt":
                model_inputs = model_inputs.to(self.dtype)
        if self.model.config.model_type == "git" and prompt is None:
            model_inputs["input_ids"] = None
        return model_inputs
    def _forward(self, model_inputs, **generate_kwargs):
        if (
            "input_ids" in model_inputs
            and isinstance(model_inputs["input_ids"], list)
            and all(x is None for x in model_inputs["input_ids"])
        ):
            model_inputs["input_ids"] = None
        if "generation_config" not in generate_kwargs:
            generate_kwargs["generation_config"] = self.generation_config
        inputs = model_inputs.pop(self.model.main_input_name)
        model_outputs = self.model.generate(inputs, **model_inputs, **generate_kwargs)
        return model_outputs
    def postprocess(self, model_outputs):
        records = []
        for output_ids in model_outputs:
            record = {
                "generated_text": self.tokenizer.decode(
                    output_ids,
                    skip_special_tokens=True,
                )
            }
            records.append(record)
        return records