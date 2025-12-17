import torch
from torch import nn
from torch.nn import CrossEntropyLoss, MSELoss
from ....modeling_outputs import BaseModelOutputWithPooling, SequenceClassifierOutput
from ....modeling_utils import ModuleUtilsMixin
from ....utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "MMBTConfig"
class ModalEmbeddings(nn.Module):
    def __init__(self, config, encoder, embeddings):
        super().__init__()
        self.config = config
        self.encoder = encoder
        self.proj_embeddings = nn.Linear(config.modal_hidden_size, config.hidden_size)
        self.position_embeddings = embeddings.position_embeddings
        self.token_type_embeddings = embeddings.token_type_embeddings
        self.word_embeddings = embeddings.word_embeddings
        self.LayerNorm = embeddings.LayerNorm
        self.dropout = nn.Dropout(p=config.hidden_dropout_prob)
    def forward(self, input_modal, start_token=None, end_token=None, position_ids=None, token_type_ids=None):
        token_embeddings = self.proj_embeddings(self.encoder(input_modal))
        seq_length = token_embeddings.size(1)
        if start_token is not None:
            start_token_embeds = self.word_embeddings(start_token)
            seq_length += 1
            token_embeddings = torch.cat([start_token_embeds.unsqueeze(1), token_embeddings], dim=1)
        if end_token is not None:
            end_token_embeds = self.word_embeddings(end_token)
            seq_length += 1
            token_embeddings = torch.cat([token_embeddings, end_token_embeds.unsqueeze(1)], dim=1)
        if position_ids is None:
            position_ids = torch.arange(seq_length, dtype=torch.long, device=input_modal.device)
            position_ids = position_ids.unsqueeze(0).expand(input_modal.size(0), seq_length)
        if token_type_ids is None:
            token_type_ids = torch.zeros(
                (input_modal.size(0), seq_length), dtype=torch.long, device=input_modal.device
            )
        position_embeddings = self.position_embeddings(position_ids)
        token_type_embeddings = self.token_type_embeddings(token_type_ids)
        embeddings = token_embeddings + position_embeddings + token_type_embeddings
        embeddings = self.LayerNorm(embeddings)
        embeddings = self.dropout(embeddings)
        return embeddings
@add_start_docstrings(
    "The bare MMBT Model outputting raw hidden-states without any specific head on top.",
    MMBT_START_DOCSTRING,
)
class MMBTModel(nn.Module, ModuleUtilsMixin):
    def __init__(self, config, transformer, encoder):
        super().__init__()
        self.config = config
        self.transformer = transformer
        self.modal_encoder = ModalEmbeddings(config, encoder, transformer.embeddings)
    @add_start_docstrings_to_model_forward(MMBT_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=BaseModelOutputWithPooling, config_class=_CONFIG_FOR_DOC)
    def forward(
        self,
        input_modal,
        input_ids=None,
        modal_start_tokens=None,
        modal_end_tokens=None,
        attention_mask=None,
        token_type_ids=None,
        modal_token_type_ids=None,
        position_ids=None,
        modal_position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        encoder_hidden_states=None,
        encoder_attention_mask=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_txt_shape = input_ids.size()
        elif inputs_embeds is not None:
            input_txt_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        device = input_ids.device if input_ids is not None else inputs_embeds.device
        modal_embeddings = self.modal_encoder(
            input_modal,
            start_token=modal_start_tokens,
            end_token=modal_end_tokens,
            position_ids=modal_position_ids,
            token_type_ids=modal_token_type_ids,
        )
        input_modal_shape = modal_embeddings.size()[:-1]
        if token_type_ids is None:
            token_type_ids = torch.ones(input_txt_shape, dtype=torch.long, device=device)
        txt_embeddings = self.transformer.embeddings(
            input_ids=input_ids, position_ids=position_ids, token_type_ids=token_type_ids, inputs_embeds=inputs_embeds
        )
        embedding_output = torch.cat([modal_embeddings, txt_embeddings], 1)
        input_shape = embedding_output.size()[:-1]
        if attention_mask is None:
            attention_mask = torch.ones(input_shape, device=device)
        else:
            attention_mask = torch.cat(
                [torch.ones(input_modal_shape, device=device, dtype=torch.long), attention_mask], dim=1
            )
        if encoder_attention_mask is None:
            encoder_attention_mask = torch.ones(input_shape, device=device)
        else:
            encoder_attention_mask = torch.cat(
                [torch.ones(input_modal_shape, device=device), encoder_attention_mask], dim=1
            )
        extended_attention_mask = self.get_extended_attention_mask(attention_mask, input_shape)
        encoder_extended_attention_mask = self.invert_attention_mask(encoder_attention_mask)
        head_mask = self.get_head_mask(head_mask, self.config.num_hidden_layers)
        encoder_outputs = self.transformer.encoder(
            embedding_output,
            attention_mask=extended_attention_mask,
            head_mask=head_mask,
            encoder_hidden_states=encoder_hidden_states,
            encoder_attention_mask=encoder_extended_attention_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        sequence_output = encoder_outputs[0]
        pooled_output = self.transformer.pooler(sequence_output)
        if not return_dict:
            return (sequence_output, pooled_output) + encoder_outputs[1:]
        return BaseModelOutputWithPooling(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
    def get_input_embeddings(self):
        return self.embeddings.word_embeddings
    def set_input_embeddings(self, value):
        self.embeddings.word_embeddings = value
@add_start_docstrings(
,
    MMBT_START_DOCSTRING,
    MMBT_INPUTS_DOCSTRING,
)
class MMBTForClassification(nn.Module):
    def __init__(self, config, transformer, encoder):
        super().__init__()
        self.num_labels = config.num_labels
        self.mmbt = MMBTModel(config, transformer, encoder)
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(config.hidden_size, config.num_labels)
    def forward(
        self,
        input_modal,
        input_ids=None,
        modal_start_tokens=None,
        modal_end_tokens=None,
        attention_mask=None,
        token_type_ids=None,
        modal_token_type_ids=None,
        position_ids=None,
        modal_position_ids=None,
        head_mask=None,
        inputs_embeds=None,
        labels=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        outputs = self.mmbt(
            input_modal=input_modal,
            input_ids=input_ids,
            modal_start_tokens=modal_start_tokens,
            modal_end_tokens=modal_end_tokens,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            modal_token_type_ids=modal_token_type_ids,
            position_ids=position_ids,
            modal_position_ids=modal_position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            return_dict=return_dict,
        )
        pooled_output = outputs[1]
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        loss = None
        if labels is not None:
            if self.num_labels == 1:
                loss_fct = MSELoss()
                loss = loss_fct(logits.view(-1), labels.view(-1))
            else:
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return SequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
__all__ = ["MMBTForClassification", "MMBTModel", "ModalEmbeddings"]