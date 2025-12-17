from typing import Optional
from ...processing_utils import ImagesKwargs, ProcessingKwargs, ProcessorMixin
class BridgeTowerImagesKwargs(ImagesKwargs):
    size_divisor: Optional[int]
class BridgeTowerProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: BridgeTowerImagesKwargs
    _defaults = {
        "text_kwargs": {
            "add_special_tokens": True,
            "padding": False,
            "stride": 0,
            "return_overflowing_tokens": False,
            "return_special_tokens_mask": False,
            "return_offsets_mapping": False,
            "return_length": False,
            "verbose": True,
        },
        "images_kwargs": {
            "do_normalize": True,
            "do_center_crop": True,
        },
    }
class BridgeTowerProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "BridgeTowerImageProcessor"
    tokenizer_class = ("RobertaTokenizer", "RobertaTokenizerFast")
    valid_processor_kwargs = BridgeTowerProcessorKwargs
    def __init__(self, image_processor, tokenizer):
        super().__init__(image_processor, tokenizer)
__all__ = ["BridgeTowerProcessor"]