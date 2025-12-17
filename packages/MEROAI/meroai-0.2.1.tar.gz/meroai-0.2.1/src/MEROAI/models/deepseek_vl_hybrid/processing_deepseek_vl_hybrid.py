from typing import Optional, Union
from ...image_processing_utils_fast import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
class DeepseekVLHybridProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {"padding": False},
        "common_kwargs": {"return_tensors": "pt"},
    }
class DeepseekVLHybridProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["chat_template", "num_image_tokens"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(
        self,
        image_processor,
        tokenizer,
        chat_template=None,
        num_image_tokens=576,
    ):
        self.image_token = tokenizer.image_token
        self.num_image_tokens = num_image_tokens
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(
        self,
        text: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]] = None,
        images: Optional[ImageInput] = None,
        **kwargs: Unpack[DeepseekVLHybridProcessorKwargs],
    ) -> BatchFeature:
        output_kwargs = self._merge_kwargs(
            DeepseekVLHybridProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs
        )
        if text is None and images is None:
            raise ValueError("You must specify either text or images.")
        if text is not None:
            if isinstance(text, str):
                text = [text]
            elif not (isinstance(text, (list, tuple)) and all(isinstance(t, str) for t in text)):
                raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        prompt_strings = []
        one_img_tokens = self.image_token * self.num_image_tokens
        for prompt in text:
            prompt = prompt.replace(self.image_token, one_img_tokens)
            prompt_strings.append(prompt)
        data = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"])
        if images is not None:
            inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
            data["pixel_values"] = inputs["pixel_values"]
            data["high_res_pixel_values"] = inputs["high_res_pixel_values"]
        return BatchFeature(data=data)
    def batch_decode(self, *args, **kwargs):
        return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs):
        return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
__all__ = ["DeepseekVLHybridProcessor"]