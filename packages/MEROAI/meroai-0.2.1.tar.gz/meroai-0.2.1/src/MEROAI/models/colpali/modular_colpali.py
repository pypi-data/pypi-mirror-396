from typing import Optional, Union
from MEROAI.models.paligemma.processing_paligemma import IMAGE_TOKEN, PaliGemmaProcessor, build_string_from_input
from ...feature_extraction_utils import BatchFeature
from ...image_utils import ImageInput, make_flat_list_of_images
from ...processing_utils import ProcessingKwargs, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import is_torch_available, logging
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class ColPaliProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {
            "padding": "longest",
        },
        "images_kwargs": {
            "data_format": "channels_first",
            "do_convert_rgb": True,
        },
        "common_kwargs": {"return_tensors": "pt"},
    }
class ColPaliProcessor(PaliGemmaProcessor):
    def __init__(
        self,
        image_processor=None,
        tokenizer=None,
        chat_template=None,
        visual_prompt_prefix: str = "Describe the image.",
        query_prefix: str = "Question: ",
    ):
        super().__init__(image_processor=image_processor, tokenizer=tokenizer, chat_template=chat_template)
        self.visual_prompt_prefix = visual_prompt_prefix
        self.query_prefix = query_prefix
    @property
    def query_augmentation_token(self) -> str:
        return self.tokenizer.pad_token
    def __call__(
        self,
        images: Optional[ImageInput] = None,
        text: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]] = None,
        audio=None,
        videos=None,
        **kwargs: Unpack[ColPaliProcessorKwargs],
    ) -> BatchFeature:
        output_kwargs = self._merge_kwargs(
            ColPaliProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        suffix = output_kwargs["text_kwargs"].pop("suffix", None)
        return_token_type_ids = suffix is not None
        if text is None and images is None:
            raise ValueError("Either text or images must be provided")
        if text is not None and images is not None:
            raise ValueError("Only one of text or images can be processed at a time")
        if images is not None:
            images = self.image_processor.fetch_images(images)
            images = make_flat_list_of_images(images)
            texts_doc = [self.visual_prompt_prefix] * len(images)
            images = [image.convert("RGB") for image in images]
            input_strings = [
                build_string_from_input(
                    prompt=prompt,
                    bos_token=self.tokenizer.bos_token,
                    image_seq_len=self.image_seq_length,
                    image_token=IMAGE_TOKEN,
                    num_images=len(image_list) if isinstance(image_list, list) else 1,
                )
                for prompt, image_list in zip(texts_doc, images)
            ]
            pixel_values = self.image_processor(images, **output_kwargs["images_kwargs"])["pixel_values"]
            if output_kwargs["text_kwargs"].get("max_length", None) is not None:
                output_kwargs["text_kwargs"]["max_length"] += self.image_seq_length
            inputs = self.tokenizer(
                input_strings,
                return_token_type_ids=False,
                **output_kwargs["text_kwargs"],
            )
            return_data = {**inputs, "pixel_values": pixel_values}
            if return_token_type_ids:
                labels = inputs["input_ids"].masked_fill(inputs["token_type_ids"] == 0, -100)
                return_data.update({"labels": labels})
            return BatchFeature(data=return_data)
        elif text is not None:
            if isinstance(text, str):
                text = [text]
            elif not (isinstance(text, list) and isinstance(text[0], str)):
                raise ValueError("Text must be a string or a list of strings")
            if suffix is None:
                suffix = self.query_augmentation_token * 10
            texts_query: list[str] = []
            for query in text:
                query = self.tokenizer.bos_token + self.query_prefix + query + suffix + "\n"
                texts_query.append(query)
            output_kwargs["text_kwargs"]["max_length"] = output_kwargs["text_kwargs"].get("max_length", 50)
            batch_query = self.tokenizer(
                texts_query,
                return_token_type_ids=False,
                **output_kwargs["text_kwargs"],
            )
            return batch_query
    def process_images(
        self,
        images: Optional[ImageInput] = None,
        **kwargs: Unpack[ColPaliProcessorKwargs],
    ) -> BatchFeature:
        return self.__call__(images=images, **kwargs)
    def process_queries(
        self,
        text: Union[TextInput, list[TextInput]],
        **kwargs: Unpack[ColPaliProcessorKwargs],
    ) -> BatchFeature:
        return self.__call__(text=text, **kwargs)
    def score_retrieval(
        self,
        query_embeddings: Union["torch.Tensor", list["torch.Tensor"]],
        passage_embeddings: Union["torch.Tensor", list["torch.Tensor"]],
        batch_size: int = 128,
        output_dtype: Optional["torch.dtype"] = None,
        output_device: Union["torch.device", str] = "cpu",
    ) -> "torch.Tensor":
        if len(query_embeddings) == 0:
            raise ValueError("No queries provided")
        if len(passage_embeddings) == 0:
            raise ValueError("No passages provided")
        if query_embeddings[0].device != passage_embeddings[0].device:
            raise ValueError("Queries and passages must be on the same device")
        if query_embeddings[0].dtype != passage_embeddings[0].dtype:
            raise ValueError("Queries and passages must have the same dtype")
        if output_dtype is None:
            output_dtype = query_embeddings[0].dtype
        scores: list[torch.Tensor] = []
        for i in range(0, len(query_embeddings), batch_size):
            batch_scores: list[torch.Tensor] = []
            batch_queries = torch.nn.utils.rnn.pad_sequence(
                query_embeddings[i : i + batch_size], batch_first=True, padding_value=0
            )
            for j in range(0, len(passage_embeddings), batch_size):
                batch_passages = torch.nn.utils.rnn.pad_sequence(
                    passage_embeddings[j : j + batch_size], batch_first=True, padding_value=0
                )
                batch_scores.append(
                    torch.einsum("bnd,csd->bcns", batch_queries, batch_passages).max(dim=3)[0].sum(dim=2)
                )
            scores.append(torch.cat(batch_scores, dim=1).to(output_dtype).to(output_device))
        return torch.cat(scores, dim=0)
__all__ = [
    "ColPaliProcessor",
]