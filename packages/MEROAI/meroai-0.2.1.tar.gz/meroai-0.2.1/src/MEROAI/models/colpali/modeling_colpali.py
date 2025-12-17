from dataclasses import dataclass
from typing import Optional
import torch
from torch import nn
from MEROAI import AutoModelForImageTextToText
from ...cache_utils import Cache
from ...modeling_utils import PreTrainedModel
from ...utils import ModelOutput, auto_docstring, can_return_tuple
from .configuration_colpali import ColPaliConfig
@auto_docstring
class ColPaliPreTrainedModel(PreTrainedModel):
    config: ColPaliConfig
    base_model_prefix = "model"
    _no_split_modules = []
    _supports_sdpa = True
    _supports_flash_attn = True
    _supports_flex_attn = True
    def _init_weights(self, module):
        std = (
            self.config.initializer_range
            if hasattr(self.config, "initializer_range")
            else self.config.vlm_config.text_config.initializer_range
        )
        if isinstance(module, (nn.Linear, nn.Conv2d)):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
@dataclass
@auto_docstring(
)
class ColPaliForRetrievalOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    embeddings: Optional[torch.Tensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[torch.FloatTensor]] = None
    image_hidden_states: Optional[torch.FloatTensor] = None
@auto_docstring(
)
class ColPaliForRetrieval(ColPaliPreTrainedModel):
    _checkpoint_conversion_mapping = {
        "vlm.language_model.model": "vlm.model.language_model",
        "vlm.vision_tower": "vlm.model.vision_tower",
        "vlm.multi_modal_projector": "vlm.model.multi_modal_projector",
        "vlm.language_model.lm_head": "vlm.lm_head",
    }
    def __init__(self, config: ColPaliConfig):
        super().__init__(config)
        self.config = config
        self.vocab_size = config.vlm_config.text_config.vocab_size
        self.vlm = AutoModelForImageTextToText.from_config(config.vlm_config)
        self._tied_weights_keys = [f"vlm.language_model.{k}" for k in (self.vlm._tied_weights_keys or [])]
        self.embedding_dim = self.config.embedding_dim
        self.embedding_proj_layer = nn.Linear(
            self.config.vlm_config.text_config.hidden_size,
            self.embedding_dim,
        )
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        **kwargs,
    ) -> ColPaliForRetrievalOutput:
        if pixel_values is not None:
            pixel_values = pixel_values.to(dtype=self.dtype)
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        vlm_output = self.vlm.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
            output_hidden_states=True,
            return_dict=True,
            output_attentions=output_attentions,
            **kwargs,
        )
        vlm_hidden_states = vlm_output.hidden_states if output_hidden_states else None
        vlm_image_hidden_states = vlm_output.image_hidden_states if pixel_values is not None else None
        last_hidden_states = vlm_output[0]
        proj_dtype = self.embedding_proj_layer.weight.dtype
        embeddings = self.embedding_proj_layer(last_hidden_states.to(proj_dtype))
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        if attention_mask is not None:
            embeddings = embeddings * attention_mask.unsqueeze(-1)
        return ColPaliForRetrievalOutput(
            embeddings=embeddings,
            past_key_values=vlm_output.past_key_values,
            hidden_states=vlm_hidden_states,
            attentions=vlm_output.attentions,
            image_hidden_states=vlm_image_hidden_states,
        )
    def get_input_embeddings(self):
        return self.vlm.get_input_embeddings()
    def set_input_embeddings(self, value):
        self.vlm.set_input_embeddings(value)
    def get_output_embeddings(self):
        return self.vlm.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings):
        self.vlm.set_output_embeddings(new_embeddings)
    def tie_weights(self):
        return self.vlm.tie_weights()
    def resize_token_embeddings(
        self,
        new_num_tokens: Optional[int] = None,
        pad_to_multiple_of: Optional[int] = None,
        mean_resizing: bool = True,
    ) -> nn.Embedding:
        model_embeds = self.vlm.resize_token_embeddings(
            new_num_tokens=new_num_tokens,
            pad_to_multiple_of=pad_to_multiple_of,
            mean_resizing=mean_resizing,
        )
        self.config.vlm_config.text_config.vocab_size = model_embeds.num_embeddings
        self.config.vlm_config.vocab_size = model_embeds.num_embeddings
        self.vlm.vocab_size = model_embeds.num_embeddings
        self.vocab_size = model_embeds.num_embeddings
        return model_embeds
__all__ = [
    "ColPaliForRetrieval",
    "ColPaliPreTrainedModel",
]