from dataclasses import dataclass
from typing import Optional
from torch import nn
from MEROAI import AutoModelForImageTextToText
from ...cache_utils import Cache
from ...modeling_utils import PreTrainedModel
from ...utils import ModelOutput, auto_docstring, can_return_tuple, is_torch_available
from .configuration_colqwen2 import ColQwen2Config
if is_torch_available():
    import torch
@auto_docstring
class ColQwen2PreTrainedModel(PreTrainedModel):
    config: ColQwen2Config
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
class ColQwen2ForRetrievalOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    embeddings: Optional[torch.Tensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor]] = None
    attentions: Optional[tuple[torch.FloatTensor]] = None
@auto_docstring(
)
class ColQwen2ForRetrieval(ColQwen2PreTrainedModel):
    _checkpoint_conversion_mapping = {}
    def __init__(self, config: ColQwen2Config):
        super().__init__(config)
        self.config = config
        self.vocab_size = config.vlm_config.text_config.vocab_size
        self.vlm = AutoModelForImageTextToText.from_config(config.vlm_config)
        self.embedding_dim = self.config.embedding_dim
        self.embedding_proj_layer = nn.Linear(
            self.config.vlm_config.text_config.hidden_size,
            self.embedding_dim,
        )
        self._tied_weights_keys = [f"vlm.{k}" for k in (self.vlm._tied_weights_keys or [])]
        self.post_init()
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        labels: Optional[torch.LongTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        pixel_values: Optional[torch.Tensor] = None,
        image_grid_thw: Optional[torch.LongTensor] = None,
        cache_position: Optional[torch.LongTensor] = None,
    ) -> ColQwen2ForRetrievalOutput:
        if pixel_values is not None and image_grid_thw is not None:
            offsets = image_grid_thw[:, 1] * image_grid_thw[:, 2]
            pixel_values = torch.cat(
                [pixel_sequence[:offset] for pixel_sequence, offset in zip(pixel_values, offsets)],
                dim=0,
            )
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        position_ids, rope_deltas = self.vlm.model.get_rope_index(
            input_ids=input_ids,
            image_grid_thw=image_grid_thw,
            video_grid_thw=None,
            attention_mask=attention_mask,
        )
        if inputs_embeds is None:
            inputs_embeds = self.vlm.language_model.embed_tokens(input_ids)
            if pixel_values is not None:
                pixel_values = pixel_values.type(self.vlm.visual.get_dtype())
                image_embeds = self.vlm.visual(pixel_values, grid_thw=image_grid_thw)
                image_mask = (
                    (input_ids == self.config.vlm_config.image_token_id).unsqueeze(-1).expand_as(inputs_embeds)
                )
                image_embeds = image_embeds.to(inputs_embeds.device, inputs_embeds.dtype)
                inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)
        vlm_output = self.vlm.model(
            input_ids=None,
            position_ids=position_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            cache_position=cache_position,
        )
        vlm_hidden_states = vlm_output.hidden_states if output_hidden_states else None
        last_hidden_states = vlm_output[0]
        proj_dtype = self.embedding_proj_layer.weight.dtype
        embeddings = self.embedding_proj_layer(last_hidden_states.to(proj_dtype))
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        if attention_mask is not None:
            embeddings = embeddings * attention_mask.unsqueeze(-1)
        return ColQwen2ForRetrievalOutput(
            embeddings=embeddings,
            past_key_values=vlm_output.past_key_values,
            hidden_states=vlm_hidden_states,
            attentions=vlm_output.attentions,
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
__all__ = ["ColQwen2ForRetrieval", "ColQwen2PreTrainedModel"]