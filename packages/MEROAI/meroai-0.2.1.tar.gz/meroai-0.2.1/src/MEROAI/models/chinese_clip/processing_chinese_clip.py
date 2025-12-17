import warnings
from ...processing_utils import ProcessorMixin
class ChineseCLIPProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = ("ChineseCLIPImageProcessor", "ChineseCLIPImageProcessorFast")
    tokenizer_class = ("BertTokenizer", "BertTokenizerFast")
    def __init__(self, image_processor=None, tokenizer=None, **kwargs):
        feature_extractor = None
        if "feature_extractor" in kwargs:
            warnings.warn(
                "The `feature_extractor` argument is deprecated and will be removed in v5, use `image_processor`"
                " instead.",
                FutureWarning,
            )
            feature_extractor = kwargs.pop("feature_extractor")
        image_processor = image_processor if image_processor is not None else feature_extractor
        super().__init__(image_processor, tokenizer)
        self.current_processor = self.image_processor
    @property
    def feature_extractor_class(self):
        warnings.warn(
            "`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.",
            FutureWarning,
        )
        return self.image_processor_class
__all__ = ["ChineseCLIPProcessor"]