from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import MultiModalData, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils import PreTokenizedInput, TextInput
from ...utils import TensorType
from ..auto import AutoTokenizer
class AriaProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {
            "padding": False,
            "return_mm_token_type_ids": False,
        },
        "images_kwargs": {
            "max_image_size": 980,
            "split_image": False,
        },
        "return_tensors": TensorType.PYTORCH,
    }
class AriaProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "AriaImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(
        self,
        image_processor=None,
        tokenizer: Union[AutoTokenizer, str] = None,
        chat_template: Optional[str] = None,
        size_conversion: Optional[dict[Union[float, int], int]] = None,
    ):
        if size_conversion is None:
            size_conversion = {490: 128, 980: 256}
        self.size_conversion = {int(k): v for k, v in size_conversion.items()}
        self.image_token = tokenizer.image_token
        self.image_token_id = tokenizer.image_token_id
        if tokenizer is not None and tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.unk_token
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(
        self,
        text: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]],
        images: Optional[ImageInput] = None,
        audio=None,
        videos=None,
        **kwargs: Unpack[AriaProcessorKwargs],
    ) -> BatchFeature:
        output_kwargs = self._merge_kwargs(
            AriaProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        if isinstance(text, str):
            text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str):
            raise TypeError("Invalid input text. Please provide a string, or a list of strings")
        if images is not None:
            image_inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
            tokens_per_image = self.size_conversion[image_inputs.pixel_values.shape[2]]
            prompt_strings = []
            num_crops = image_inputs.pop("num_crops") * tokens_per_image
            for sample in text:
                sample = sample.replace(self.tokenizer.image_token, self.tokenizer.image_token * num_crops)
                prompt_strings.append(sample)
        else:
            image_inputs = {}
            prompt_strings = text
        return_tensors = output_kwargs["text_kwargs"].pop("return_tensors", None)
        return_mm_token_type_ids = output_kwargs["text_kwargs"].pop("return_mm_token_type_ids", False)
        text_inputs = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"], return_tensors=None)
        self._check_special_mm_tokens(prompt_strings, text_inputs, modalities=["image"])
        if return_mm_token_type_ids:
            array_ids = np.array(text_inputs["input_ids"])
            mm_token_type_ids = np.zeros_like(text_inputs["input_ids"])
            mm_token_type_ids[array_ids == self.image_token_id] = 1
            text_inputs["mm_token_type_ids"] = mm_token_type_ids.tolist()
        return BatchFeature(data={**text_inputs, **image_inputs}, tensor_type=return_tensors)
    def _get_num_multimodal_tokens(self, image_sizes=None, **kwargs):
        vision_data = {}
        if image_sizes is not None:
            images_kwargs = AriaProcessorKwargs._defaults.get("images_kwargs", {})
            images_kwargs.update(kwargs)
            max_size = images_kwargs.get("max_image_size", None) or self.image_processor.max_image_size
            num_image_patches = [
                self.image_processor.get_number_of_image_patches(*image_size, images_kwargs)
                for image_size in image_sizes
            ]
            num_image_tokens = [self.size_conversion[max_size] * num_patches for num_patches in num_image_patches]
            vision_data.update({"num_image_tokens": num_image_tokens, "num_image_patches": num_image_patches})
        return MultiModalData(**vision_data)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        image_processor_input_names = [name for name in image_processor_input_names if name != "num_crops"]
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
__all__ = ["AriaProcessor"]