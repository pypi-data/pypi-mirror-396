from ...processing_utils import ProcessingKwargs, ProcessorMixin
class AlignProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {
            "padding": "max_length",
            "max_length": 64,
        },
    }
class AlignProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "EfficientNetImageProcessor"
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    valid_processor_kwargs = AlignProcessorKwargs
    def __init__(self, image_processor, tokenizer):
        super().__init__(image_processor, tokenizer)
__all__ = ["AlignProcessor"]