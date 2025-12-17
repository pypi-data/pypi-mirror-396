import warnings
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
class CLIPSegProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = ("ViTImageProcessor", "ViTImageProcessorFast")
    tokenizer_class = ("CLIPTokenizer", "CLIPTokenizerFast")
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
    def __call__(self, text=None, images=None, visual_prompt=None, return_tensors=None, **kwargs):
        if text is None and visual_prompt is None and images is None:
            raise ValueError("You have to specify either text, visual prompt or images.")
        if text is not None and visual_prompt is not None:
            raise ValueError("You have to specify exactly one type of prompt. Either text or visual prompt.")
        if text is not None:
            encoding = self.tokenizer(text, return_tensors=return_tensors, **kwargs)
        if visual_prompt is not None:
            prompt_features = self.image_processor(visual_prompt, return_tensors=return_tensors, **kwargs)
        if images is not None:
            image_features = self.image_processor(images, return_tensors=return_tensors, **kwargs)
        if visual_prompt is not None and images is not None:
            encoding = {
                "pixel_values": image_features.pixel_values,
                "conditional_pixel_values": prompt_features.pixel_values,
            }
            return encoding
        elif text is not None and images is not None:
            encoding["pixel_values"] = image_features.pixel_values
            return encoding
        elif text is not None:
            return encoding
        elif visual_prompt is not None:
            encoding = {
                "conditional_pixel_values": prompt_features.pixel_values,
            }
            return encoding
        else:
            return BatchEncoding(data=dict(**image_features), tensor_type=return_tensors)
    @property
    def feature_extractor_class(self):
        warnings.warn(
            "`feature_extractor_class` is deprecated and will be removed in v5. Use `image_processor_class` instead.",
            FutureWarning,
        )
        return self.image_processor_class
    @property
    def feature_extractor(self):
        warnings.warn(
            "`feature_extractor` is deprecated and will be removed in v5. Use `image_processor` instead.",
            FutureWarning,
        )
        return self.image_processor
__all__ = ["CLIPSegProcessor"]