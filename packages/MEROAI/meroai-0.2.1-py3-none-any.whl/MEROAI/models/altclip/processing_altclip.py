from ...processing_utils import ProcessorMixin
from ...utils.deprecation import deprecate_kwarg
class AltCLIPProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = ("CLIPImageProcessor", "CLIPImageProcessorFast")
    tokenizer_class = ("XLMRobertaTokenizer", "XLMRobertaTokenizerFast")
    @deprecate_kwarg(old_name="feature_extractor", version="5.0.0", new_name="image_processor")
    def __init__(self, image_processor=None, tokenizer=None):
        super().__init__(image_processor, tokenizer)
__all__ = ["AltCLIPProcessor"]