from typing import Optional, Union
import torch
import torch.nn as nn
from ...configuration_utils import PretrainedConfig
from ...image_processing_utils import BatchFeature
from ...image_utils import ImageInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import (
    PreTokenizedInput,
    TextInput,
)
from ...utils import (
    auto_docstring,
    logging,
)
from ..auto import CONFIG_MAPPING, AutoConfig, AutoModel
from ..idefics.modeling_idefics import IdeficsBaseModelOutputWithPast, IdeficsCausalLMOutputWithPast
from ..janus.image_processing_janus import JanusImageProcessor
from ..janus.image_processing_janus_fast import JanusImageProcessorFast
from ..janus.modeling_janus import JanusForConditionalGeneration, JanusModel, JanusPreTrainedModel
logger = logging.get_logger(__name__)
class DeepseekVLConfig(PretrainedConfig):
    model_type = "deepseek_vl"
    sub_configs = {"text_config": AutoConfig, "vision_config": AutoConfig}
    def __init__(
        self,
        text_config: Optional[AutoConfig] = None,
        vision_config: Optional[AutoConfig] = None,
        image_token_id: int = 100015,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if text_config is None:
            text_config = {}
            logger.info("`text_config` is `None`. Initializing the `LlamaConfig` with default values.")
        if vision_config is None:
            vision_config = {}
            logger.info("`vision_config` is `None`. Initializing the `SiglipVisionConfig` with default values.")
        if isinstance(text_config, dict):
            text_config["model_type"] = text_config.get("model_type", "llama")
            text_config = CONFIG_MAPPING[text_config["model_type"]](**text_config)
        if isinstance(vision_config, dict):
            vision_config["model_type"] = vision_config.get("model_type", "siglip_vision_model")
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        self.text_config = text_config
        self.vision_config = vision_config
        self.image_token_id = image_token_id
class DeepseekVLBaseModelOutputWithPast(IdeficsBaseModelOutputWithPast):
    pass
class DeepseekVLCausalLMOutputWithPast(IdeficsCausalLMOutputWithPast):
    pass
class DeepseekVLAligner(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        in_features = config.vision_config.hidden_size
        out_features = config.text_config.hidden_size
        self.linear1 = nn.Linear(in_features, out_features)
        self.activation = nn.GELU()
        self.linear2 = nn.Linear(out_features, out_features)
    def forward(self, vision_encodings: torch.Tensor) -> torch.Tensor:
        x = self.linear1(vision_encodings)
        x = self.activation(x)
        x = self.linear2(x)
        return x
class DeepseekVLPreTrainedModel(JanusPreTrainedModel):
    _no_split_modules = ["LlamaDecoderLayer"]
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=self.config.text_config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
@auto_docstring
class DeepseekVLModel(JanusModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.vision_model = AutoModel.from_config(config.vision_config)
        self.aligner = DeepseekVLAligner(config)
        self.language_model = AutoModel.from_config(config=config.text_config)
        self.gradient_checkpointing = False
        self.post_init()
        del self.vqmodel
        del self.generation_embeddings
        del self.generation_aligner
        del self.generation_head
class DeepseekVLForConditionalGeneration(JanusForConditionalGeneration):
    def prepare_embeddings_for_image_generation(self):
        raise AttributeError("Not needed for DeepseekVL")
    def decode_image_tokens(self):
        raise AttributeError("Not needed for DeepseekVL")
    def generate(self):
        raise AttributeError("Not needed for DeepseekVL")
class DeepseekVLImageProcessor(JanusImageProcessor):
    def __init__(self, **super_kwargs):
        super().__init__(**super_kwargs)
    def postprocess(self):
        raise AttributeError("Not needed for DeepseekVL")
    def unnormalize(self):
        raise AttributeError("Not needed for DeepseekVL")
class DeepseekVLImageProcessorFast(JanusImageProcessorFast):
    def __init__(self, **super_kwargs):
        super().__init__(**super_kwargs)
    def postprocess(self):
        raise AttributeError("Not needed for DeepseekVL")
class DeepseekVLProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {"padding": False},
        "common_kwargs": {"return_tensors": "pt"},
    }
class DeepseekVLProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    valid_kwargs = ["chat_template", "num_image_tokens"]
    image_processor_class = "AutoImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(
        self,
        image_processor,
        tokenizer,
        chat_template=None,
        num_image_tokens=576,
    ):
        self.image_token = tokenizer.image_token
        self.num_image_tokens = num_image_tokens
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(
        self,
        text: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]] = None,
        images: Optional[ImageInput] = None,
        **kwargs: Unpack[DeepseekVLProcessorKwargs],
    ) -> BatchFeature:
        output_kwargs = self._merge_kwargs(
            DeepseekVLProcessorKwargs, tokenizer_init_kwargs=self.tokenizer.init_kwargs, **kwargs
        )
        if text is None and images is None:
            raise ValueError("You must specify either text or images.")
        if text is not None:
            if isinstance(text, str):
                text = [text]
            elif not (isinstance(text, (list, tuple)) and all(isinstance(t, str) for t in text)):
                raise ValueError("Invalid input text. Please provide a string, or a list of strings")
        prompt_strings = []
        one_img_tokens = self.image_token * self.num_image_tokens
        for prompt in text:
            prompt = prompt.replace(self.image_token, one_img_tokens)
            prompt_strings.append(prompt)
        data = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"])
        if images is not None:
            data["pixel_values"] = self.image_processor(images, **output_kwargs["images_kwargs"])["pixel_values"]
        return BatchFeature(data=data)
    def batch_decode(self, *args, **kwargs):
        return self.tokenizer.batch_decode(*args, **kwargs)
    def decode(self, *args, **kwargs):
        return self.tokenizer.decode(*args, **kwargs)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
__all__ = [
    "DeepseekVLConfig",
    "DeepseekVLPreTrainedModel",
    "DeepseekVLModel",
    "DeepseekVLForConditionalGeneration",
    "DeepseekVLImageProcessor",
    "DeepseekVLImageProcessorFast",
    "DeepseekVLProcessor",
]