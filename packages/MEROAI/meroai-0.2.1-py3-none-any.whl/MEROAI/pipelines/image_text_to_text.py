import enum
from collections.abc import Iterable
from typing import Any, Optional, Union, overload
from ..generation import GenerationConfig
from ..processing_utils import ProcessingKwargs, Unpack
from ..utils import (
    add_end_docstrings,
    is_torch_available,
    is_vision_available,
    logging,
    requires_backends,
)
from .base import Pipeline, build_pipeline_init_args
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_images, valid_images
if is_torch_available():
    from ..models.auto.modeling_auto import MODEL_FOR_IMAGE_TEXT_TO_TEXT_MAPPING_NAMES
    from .pt_utils import KeyDataset
logger = logging.get_logger(__name__)
IMAGE_TOKEN = "<image>"
class ReturnType(enum.Enum):
    TENSORS = 0
    NEW_TEXT = 1
    FULL_TEXT = 2
class Chat:
    def __init__(
        self, messages: dict, images: Optional[Union[str, list[str], "Image.Image", list["Image.Image"]]] = None
    ):
        for message in messages:
            if not ("role" in message and "content" in message):
                raise ValueError("When passing chat dicts as input, each dict must have a 'role' and 'content' key.")
        messages = add_images_to_messages(messages, images)
        self.messages = messages
def add_images_to_messages(
    messages: dict, images: Optional[Union[str, list[str], "Image.Image", list["Image.Image"]]]
):
    if images is None:
        images = []
    elif not isinstance(images, Iterable) or isinstance(images, str):
        images = [images]
    idx_images = 0
    for message in messages:
        for content in message["content"]:
            if not isinstance(content, dict):
                continue
            content_type = content.get("type")
            if content_type == "image":
                if not any(key in content for key in ["image", "url", "path", "base64"]):
                    if idx_images < len(images):
                        content["image"] = images[idx_images]
                        idx_images += 1
                    else:
                        raise ValueError(
                            "The number of images in the chat messages should be the same as the number of images passed to the pipeline."
                        )
            elif content_type == "image_url":
                if isinstance(content.get("image_url"), dict) and "url" in content["image_url"]:
                    content["type"] = "image"
                    content["image"] = content["image_url"]["url"]
                    del content["image_url"]
                else:
                    raise ValueError(
                        "Wrong format for 'image_url' content type. The content should have an 'image_url' dict with a 'url' key."
                    )
    if idx_images != len(images):
        raise ValueError(
            "The number of images in the chat messages should be the same as the number of images passed to the pipeline."
        )
    return messages
@add_end_docstrings(build_pipeline_init_args(has_processor=True))
class ImageTextToTextPipeline(Pipeline):
    _load_processor = True
    _load_image_processor = False
    _load_feature_extractor = False
    _load_tokenizer = False
    _pipeline_calls_generate = True
    _default_generation_config = GenerationConfig(
        max_new_tokens=256,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        self.check_model_type(MODEL_FOR_IMAGE_TEXT_TO_TEXT_MAPPING_NAMES)
    def _sanitize_parameters(
        self,
        max_new_tokens=None,
        generate_kwargs=None,
        timeout=None,
        return_full_text=None,
        return_tensors=None,
        return_type=None,
        clean_up_tokenization_spaces=None,
        stop_sequence=None,
        continue_final_message=None,
        skip_special_tokens=None,
        **kwargs: Unpack[ProcessingKwargs],
    ):
        forward_kwargs = {}
        preprocess_params = {}
        postprocess_params = {}
        preprocess_params.update(kwargs)
        if timeout is not None:
            preprocess_params["timeout"] = timeout
        if continue_final_message is not None:
            preprocess_params["continue_final_message"] = continue_final_message
        if generate_kwargs is not None:
            forward_kwargs["generate_kwargs"] = generate_kwargs
        if stop_sequence is not None:
            stop_sequence_ids = self.processor.tokenizer.encode(stop_sequence, add_special_tokens=False)
            if len(stop_sequence_ids) > 1:
                logger.warning_once(
                    "Stopping on a multiple token sequence is not yet supported on MEROAI. The first token of"
                    " the stop sequence will be used as the stop sequence string in the interim."
                )
            generate_kwargs["eos_token_id"] = stop_sequence_ids[0]
        if generate_kwargs is not None:
            forward_kwargs["generate_kwargs"] = generate_kwargs
        if max_new_tokens is not None:
            if "generate_kwargs" not in forward_kwargs:
                forward_kwargs["generate_kwargs"] = {}
            if "max_new_tokens" in forward_kwargs["generate_kwargs"]:
                raise ValueError(
                    "'max_new_tokens' is defined twice, once in 'generate_kwargs' and once as a direct parameter,"
                    " please use only one"
                )
            forward_kwargs["generate_kwargs"]["max_new_tokens"] = max_new_tokens
        if return_full_text is not None and return_type is None:
            if return_tensors is not None:
                raise ValueError("`return_full_text` is mutually exclusive with `return_tensors`")
            return_type = ReturnType.FULL_TEXT if return_full_text else ReturnType.NEW_TEXT
        if return_tensors is not None and return_type is None:
            return_type = ReturnType.TENSORS
        if return_type is not None:
            postprocess_params["return_type"] = return_type
        if continue_final_message is not None:
            postprocess_params["continue_final_message"] = continue_final_message
        if clean_up_tokenization_spaces is not None:
            postprocess_params["clean_up_tokenization_spaces"] = clean_up_tokenization_spaces
        if skip_special_tokens is not None:
            postprocess_params["skip_special_tokens"] = skip_special_tokens
        return preprocess_params, forward_kwargs, postprocess_params
    @overload
    def __call__(
        self,
        image: Optional[Union[str, "Image.Image"]] = None,
        text: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]: ...
    @overload
    def __call__(
        self,
        image: Optional[Union[list[str], list["Image.Image"]]] = None,
        text: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> list[list[dict[str, Any]]]: ...
    def __call__(
        self,
        images: Optional[
            Union[
                str,
                list[str],
                list[list[str]],
                "Image.Image",
                list["Image.Image"],
                list[list["Image.Image"]],
                list[dict],
            ]
        ] = None,
        text: Optional[Union[str, list[str], list[dict]]] = None,
        **kwargs,
    ) -> Union[list[dict[str, Any]], list[list[dict[str, Any]]]]:
        if images is None and text is None:
            raise ValueError("You must at least provide either text or images.")
        def _is_chat(arg):
            return isinstance(arg, (list, tuple, KeyDataset)) and isinstance(arg[0], (list, tuple, dict))
        if _is_chat(text):
            if isinstance(text[0], dict):
                return super().__call__(Chat(text, images), **kwargs)
            else:
                if images is None:
                    images = [None] * len(text)
                chats = [Chat(chat, image) for chat, image in zip(text, images)]
                return super().__call__(chats, **kwargs)
        elif text is None and _is_chat(images):
            if isinstance(images[0], dict):
                return super().__call__(Chat(images), **kwargs)
            else:
                chats = [Chat(image) for image in images]
                return super().__call__(chats, **kwargs)
        elif images is not None and text is None and not valid_images(images):
            return super().__call__(images, **kwargs)
        if getattr(self.processor, "chat_template", None) is not None:
            logger.warning_once(
                "The input data was not formatted as a chat with dicts containing 'role' and 'content' keys, even "
                "though this model supports chat. Consider using the chat format for better results. For more "
                "information, see https://huggingface.co/docs/MEROAI/en/chat_templating"
            )
        if images is None:
            return super().__call__(text, **kwargs)
        if text is None:
            raise ValueError("You must provide text for this pipeline.")
        return super().__call__({"images": images, "text": text}, **kwargs)
    def preprocess(self, inputs=None, timeout=None, continue_final_message=None, **processing_kwargs):
        if isinstance(inputs, Chat):
            if continue_final_message is None:
                continue_final_message = inputs.messages[-1]["role"] == "assistant"
            model_inputs = self.processor.apply_chat_template(
                inputs.messages,
                add_generation_prompt=not continue_final_message,
                continue_final_message=continue_final_message,
                return_tensors=self.framework,
                tokenize=True,
                return_dict=True,
            )
            model_inputs["text"] = inputs
            return model_inputs
        if isinstance(inputs, (list, tuple, str)):
            images = None
            text = inputs
            inputs_text = inputs
        else:
            images = load_images(inputs["images"], timeout=timeout)
            text = inputs["text"]
            inputs_text = inputs["text"]
        if isinstance(text, (list, tuple)) and len(text) > 1:
            processing_kwargs.setdefault("padding", True)
        model_inputs = self.processor(images=images, text=text, return_tensors=self.framework, **processing_kwargs).to(
            dtype=self.dtype
        )
        model_inputs["text"] = inputs_text
        return model_inputs
    def _forward(self, model_inputs, generate_kwargs=None):
        generate_kwargs = {} if generate_kwargs is None else generate_kwargs
        prompt_text = model_inputs.pop("text")
        input_ids = (
            model_inputs["input_ids"] if "input_ids" in model_inputs else model_inputs["decoder_input_ids"]
        )
        if "generation_config" not in generate_kwargs:
            generate_kwargs["generation_config"] = self.generation_config
        generated_sequence = self.model.generate(**model_inputs, **generate_kwargs)
        return {"generated_sequence": generated_sequence, "prompt_text": prompt_text, "input_ids": input_ids}
    def postprocess(
        self,
        model_outputs,
        return_type=ReturnType.FULL_TEXT,
        continue_final_message=None,
        skip_special_tokens=None,
        **postprocess_kwargs,
    ):
        input_texts = model_outputs["prompt_text"]
        input_texts = [input_texts] if isinstance(input_texts, (str, Chat)) else input_texts
        generated_sequence = model_outputs["generated_sequence"]
        input_ids = model_outputs["input_ids"]
        if return_type == ReturnType.TENSORS:
            return [
                {"input_text": input_texts[i], "generated_token_ids": generated_sequence[i]}
                for i in range(len(input_texts))
            ]
        skip_special_tokens = skip_special_tokens if skip_special_tokens is not None else True
        generated_texts = self.processor.post_process_image_text_to_text(
            generated_sequence, skip_special_tokens=skip_special_tokens, **postprocess_kwargs
        )
        decoded_inputs = self.processor.post_process_image_text_to_text(
            input_ids, skip_special_tokens=skip_special_tokens, **postprocess_kwargs
        )
        if return_type in {ReturnType.NEW_TEXT, ReturnType.FULL_TEXT}:
            new_generated_texts = []
            for text_generated, decoded_input in zip(generated_texts, decoded_inputs):
                index_input_text = text_generated.find(decoded_input)
                if 0 <= index_input_text <= 2:
                    new_generated_texts.append(text_generated[index_input_text + len(decoded_input) :])
                else:
                    new_generated_texts.append(text_generated)
            generated_texts = new_generated_texts
        if return_type == ReturnType.FULL_TEXT:
            full_texts = []
            for prompt_text, generated_text in zip(input_texts, generated_texts):
                if isinstance(prompt_text, str):
                    generated_text = prompt_text + generated_text
                elif isinstance(prompt_text, Chat):
                    if continue_final_message is None:
                        continue_final_message = prompt_text.messages[-1]["role"] == "assistant"
                    if continue_final_message:
                        new_text = dict(prompt_text.messages[-1]["content"][-1].items())
                        new_text["text"] += generated_text
                        generated_text = list(prompt_text.messages)[:-1] + [
                            {
                                "role": prompt_text.messages[-1]["role"],
                                "content": prompt_text.messages[-1]["content"][:-1] + [new_text],
                            }
                        ]
                    else:
                        generated_text = list(prompt_text.messages) + [
                            {"role": "assistant", "content": generated_text}
                        ]
                full_texts.append(generated_text)
            generated_texts = full_texts
        records = [
            {
                "input_text": input_text.messages if isinstance(input_text, Chat) else input_text,
                "generated_text": generated_text,
            }
            for input_text, generated_text in zip(input_texts, generated_texts)
        ]
        return records