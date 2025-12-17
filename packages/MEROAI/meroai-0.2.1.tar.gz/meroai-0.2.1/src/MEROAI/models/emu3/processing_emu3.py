from typing import Optional, Union
import numpy as np
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ImagesKwargs, MultiModalData, ProcessingKwargs, ProcessorMixin, TextKwargs, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import is_vision_available
if is_vision_available():
    from .image_processing_emu3 import smart_resize
class Emu3TextKwargs(TextKwargs, total=False):
    return_for_image_generation: bool
class Emu3ImagesKwargs(ImagesKwargs, total=False):
    ratio: str
    image_area: int
class Emu3ProcessorKwargs(ProcessingKwargs, total=False):
    text_kwargs: Emu3TextKwargs
    images_kwargs: Emu3ImagesKwargs
    _defaults = {
        "text_kwargs": {
            "return_for_image_generation": False,
            "return_mm_token_type_ids": False,
        },
        "images_kwargs": {
            "ratio": "1:1",
            "image_area": 518400,
        },
    }
class Emu3Processor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    tokenizer_class = ("GPT2Tokenizer", "GPT2TokenizerFast")
    image_processor_class = "Emu3ImageProcessor"
    def __init__(
        self,
        image_processor,
        tokenizer,
        chat_template=None,
        **kwargs,
    ):
        self.image_token = tokenizer.image_token
        self.image_token_id = tokenizer.image_token_id
        self.image_start_token = tokenizer.boi_token
        self.image_end_token = tokenizer.eoi_token
        self.fake_token_around_image = tokenizer.image_wrapper_token
        self.eof_token = tokenizer.eof_token
        self.bos_token = tokenizer.bos_token
        self.downsample_ratio = 8
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(
        self,
        images: Optional[ImageInput] = None,
        text: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]] = None,
        audio=None,
        videos=None,
        **kwargs: Unpack[Emu3ProcessorKwargs],
    ) -> BatchFeature:
        if isinstance(text, str):
            text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str):
            raise TypeError("Invalid input text. Please provide a string, or a list of strings")
        output_kwargs = self._merge_kwargs(
            Emu3ProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        return_for_image_generation = output_kwargs["text_kwargs"].pop("return_for_image_generation", False)
        ratio = output_kwargs["images_kwargs"].pop("ratio", None)
        image_area = output_kwargs["images_kwargs"].pop("image_area", None)
        if return_for_image_generation and images is not None:
            raise ValueError("You should not provide `images` when `return_for_image_generation=True`")
        if not return_for_image_generation and text is None and images is None:
            raise ValueError("You must provide either text or images when `return_for_image_generation=False`")
        image_features = {}
        image_start_tokens = f"{self.image_start_token}"
        image_end_tokens = f"{self.eof_token}{self.image_end_token}"
        if not return_for_image_generation and images is not None:
            image_features = self.image_processor(images, **output_kwargs["images_kwargs"])
            image_sizes = iter(image_features.image_sizes)
            prompt_strings = []
            for sample in text:
                while self.image_token in sample:
                    image_size = next(image_sizes)
                    height, width = image_size
                    height = height // self.downsample_ratio
                    width = width // self.downsample_ratio
                    image_seq_length = height * (width + 1)
                    image_placeholder = f"{image_start_tokens}{height}*{width}{self.fake_token_around_image}{'<placeholder>' * image_seq_length}{image_end_tokens}"
                    sample = sample.replace(self.image_token, image_placeholder, 1)
                    sample = f"{self.bos_token}{sample}"
                prompt_strings.append(sample)
            text = [sample.replace("<placeholder>", self.image_token) for sample in prompt_strings]
        elif return_for_image_generation:
            height, width = self.calculate_generate_size(ratio, image_area, self.downsample_ratio)
            image_prompt = f"{image_start_tokens}{height}*{width}{self.fake_token_around_image}"
            text = [f"{self.bos_token}{sample}{image_prompt}" for sample in text]
            image_features["image_sizes"] = [[height, width]] * len(text)
        return_tensors = output_kwargs["text_kwargs"].pop("return_tensors", None)
        return_mm_token_type_ids = output_kwargs["text_kwargs"].pop("return_mm_token_type_ids", False)
        text_inputs = self.tokenizer(text, **output_kwargs["text_kwargs"], return_tensors=None)
        self._check_special_mm_tokens(text, text_inputs, modalities=["image"])
        if return_mm_token_type_ids:
            array_ids = np.array(text_inputs["input_ids"])
            mm_token_type_ids = np.zeros_like(text_inputs["input_ids"])
            mm_token_type_ids[array_ids == self.image_token_id] = 1
            text_inputs["mm_token_type_ids"] = mm_token_type_ids.tolist()
        return BatchFeature(data={**text_inputs, **image_features}, tensor_type=return_tensors)
    def _get_num_multimodal_tokens(self, image_sizes=None, **kwargs):
        vision_data = {}
        if image_sizes is not None:
            num_image_tokens = []
            for height, width in image_sizes:
                height, width = smart_resize(
                    height,
                    width,
                    self.image_processor.spatial_factor,
                    self.image_processor.min_pixels,
                    self.image_processor.max_pixels,
                )
                height = height // self.downsample_ratio
                width = width // self.downsample_ratio
                image_seq_length = height * (width + 1)
                num_image_tokens.append(image_seq_length)
            num_image_patches = [1] * len(image_sizes)
            vision_data.update({"num_image_tokens": num_image_tokens, "num_image_patches": num_image_patches})
        return MultiModalData(**vision_data)
    def calculate_generate_size(self, ratio, image_area, spatial_factor):
        width, height = map(int, ratio.split(":"))
        current_area = width * height
        target_ratio = (image_area / current_area) ** 0.5
        token_height = int(round(height * target_ratio / spatial_factor))
        token_width = int(round(width * target_ratio / spatial_factor))
        return token_height, token_width
    def postprocess(self, images: ImageInput, **kwargs):
        return self.image_processor.postprocess(images, **kwargs)
__all__ = ["Emu3Processor"]