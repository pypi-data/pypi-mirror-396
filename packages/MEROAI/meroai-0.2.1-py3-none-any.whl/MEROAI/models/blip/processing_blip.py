from typing import Optional, Union
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import BatchEncoding, PreTokenizedInput, TextInput
class BlipProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {
            "add_special_tokens": True,
            "padding": False,
            "stride": 0,
            "return_overflowing_tokens": False,
            "return_special_tokens_mask": False,
            "return_offsets_mapping": False,
            "return_token_type_ids": False,
            "return_length": False,
            "verbose": True,
        },
        "images_kwargs": {},
    }
class BlipProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = ("BlipImageProcessor", "BlipImageProcessorFast")
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor, tokenizer, **kwargs):
        tokenizer.return_token_type_ids = False
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    def __call__(
        self,
        images: Optional[ImageInput] = None,
        text: Optional[Union[str, list[str], TextInput, PreTokenizedInput]] = None,
        audio=None,
        videos=None,
        **kwargs: Unpack[BlipProcessorKwargs],
    ) -> BatchEncoding:
        if images is None and text is None:
            raise ValueError("You have to specify either images or text.")
        text_encoding = None
        output_kwargs = self._merge_kwargs(
            BlipProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        if text is not None:
            text_encoding = self.tokenizer(text, **output_kwargs["text_kwargs"])
        if images is not None:
            encoding_image_processor = self.image_processor(images, **output_kwargs["images_kwargs"])
            if text_encoding is not None:
                encoding_image_processor.update(text_encoding)
            return encoding_image_processor
        return text_encoding
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        tokenizer_input_names = [name for name in tokenizer_input_names if name != "token_type_ids"]
        return tokenizer_input_names + image_processor_input_names
__all__ = ["BlipProcessor"]