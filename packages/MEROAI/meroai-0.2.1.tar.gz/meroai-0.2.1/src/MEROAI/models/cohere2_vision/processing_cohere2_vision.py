from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ImagesKwargs, MultiModalData, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
class Cohere2VisionImagesKwargs(ImagesKwargs, total=False):
    max_patches: Optional[int]
class Cohere2VisionProcessorKwargs(ProcessingKwargs, total=False):
    images_kwargs: Cohere2VisionImagesKwargs
    _defaults = {
        "text_kwargs": {
            "padding_side": "left",
            "padding": True,
            "return_mm_token_type_ids": False,
        },
    }
class Cohere2VisionProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(
        self,
        image_processor=None,
        tokenizer=None,
        chat_template=None,
        **kwargs,
    ):
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
        self.patch_size = self.image_processor.patch_size
        self.boi_token = tokenizer.boi_token
        self.eoi_token = tokenizer.eoi_token
        self.image_token = tokenizer.image_token
        self.img_line_break_token = tokenizer.img_line_break_token
        self.image_token_id = tokenizer.image_token_id
        self.image_ids = tokenizer.convert_tokens_to_ids(
            [
                self.image_token,
                self.boi_token,
                self.eoi_token,
                self.img_line_break_token,
            ]
        )
    def __call__(
        self,
        images: Optional[ImageInput] = None,
        text: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]] = None,
        **kwargs: Unpack[Cohere2VisionProcessorKwargs],
    ) -> BatchFeature:
        if text is None:
            raise ValueError("You have to specify text.")
        elif not isinstance(text, (list, tuple)):
            text = [text]
        output_kwargs = self._merge_kwargs(
            Cohere2VisionProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        image_inputs = {}
        if images is not None:
            image_inputs = self.image_processor(images=images, **output_kwargs["images_kwargs"])
            batch_num_patches = iter(image_inputs.pop("num_patches"))
            processed_text = []
            for sample in text:
                while self.image_token in sample:
                    num_patches = next(batch_num_patches)
                    img_patches_per_tile = int(self.patch_size**2)
                    img_string = f"{self.boi_token}"
                    for idx in range(1, num_patches):
                        img_string += "<placeholder>" * img_patches_per_tile + self.img_line_break_token
                    img_string += "<placeholder>" * img_patches_per_tile + self.img_line_break_token
                    img_string += f"{self.eoi_token}"
                    sample = sample.replace(self.image_token, img_string, 1)
                processed_text.append(sample)
            text = [sample.replace("<placeholder>", self.image_token) for sample in processed_text]
        return_tensors = output_kwargs["text_kwargs"].pop("return_tensors", None)
        return_mm_token_type_ids = output_kwargs["text_kwargs"].pop("return_mm_token_type_ids", False)
        text_inputs = self.tokenizer(text, **output_kwargs["text_kwargs"], return_tensors=None)
        if return_mm_token_type_ids:
            array_ids = np.array(text_inputs["input_ids"])
            mm_token_type_ids = np.zeros_like(text_inputs["input_ids"])
            mm_token_type_ids[np.isin(array_ids, self.image_ids)] = 1
            text_inputs["mm_token_type_ids"] = mm_token_type_ids.tolist()
        return BatchFeature(data={**text_inputs, **image_inputs}, tensor_type=return_tensors)
    def _get_num_multimodal_tokens(self, image_sizes=None, **kwargs):
        vision_data = {}
        if image_sizes is not None:
            images_kwargs = Cohere2VisionProcessorKwargs._defaults.get("images_kwargs", {})
            images_kwargs.update(kwargs)
            num_image_patches = [
                self.image_processor.get_number_of_image_patches(*image_size, images_kwargs)
                for image_size in image_sizes
            ]
            token_per_patch = int(self.patch_size**2)
            num_image_tokens = [
                2 + sum(token_per_patch + 1 for _ in range(num_patches)) for num_patches in num_image_patches
            ]
            vision_data.update({"num_image_tokens": num_image_tokens, "num_image_patches": num_image_patches})
        return MultiModalData(**vision_data)
    def batch_decode(self, *args, **kwargs):
        return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs):
        return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(tokenizer_input_names) + list(image_processor_input_names)
__all__ = ["Cohere2VisionProcessor"]