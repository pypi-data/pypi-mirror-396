from __future__ import annotations
import warnings
from dataclasses import dataclass
import tensorflow as tf
from .utils import ModelOutput
@dataclass
class TFBaseModelOutput(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithNoAttention(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
@dataclass
class TFBaseModelOutputWithPooling(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    pooler_output: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPoolingAndNoAttention(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    pooler_output: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
@dataclass
class TFBaseModelOutputWithPoolingAndCrossAttentions(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    pooler_output: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPast(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithCrossAttentions(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFBaseModelOutputWithPastAndCrossAttentions(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqModelOutput(ModelOutput):
    last_hidden_state: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    decoder_hidden_states: tuple[tf.Tensor] | None = None
    decoder_attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: tuple[tf.Tensor] | None = None
    encoder_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutputWithPast(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFCausalLMOutputWithCrossAttentions(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFMaskedLMOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqLMOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    decoder_hidden_states: tuple[tf.Tensor] | None = None
    decoder_attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: tuple[tf.Tensor] | None = None
    encoder_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFNextSentencePredictorOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSequenceClassifierOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqSequenceClassifierOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    decoder_hidden_states: tuple[tf.Tensor] | None = None
    decoder_attentions: tuple[tf.Tensor] | None = None
    cross_attentions: tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: tuple[tf.Tensor] | None = None
    encoder_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSemanticSegmenterOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSemanticSegmenterOutputWithNoAttention(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
@dataclass
class TFImageClassifierOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFMultipleChoiceModelOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFTokenClassifierOutput(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFQuestionAnsweringModelOutput(ModelOutput):
    loss: tf.Tensor | None = None
    start_logits: tf.Tensor | None = None
    end_logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSeq2SeqQuestionAnsweringModelOutput(ModelOutput):
    loss: tf.Tensor | None = None
    start_logits: tf.Tensor | None = None
    end_logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    decoder_hidden_states: tuple[tf.Tensor] | None = None
    decoder_attentions: tuple[tf.Tensor] | None = None
    encoder_last_hidden_state: tf.Tensor | None = None
    encoder_hidden_states: tuple[tf.Tensor] | None = None
    encoder_attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFSequenceClassifierOutputWithPast(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    past_key_values: list[tf.Tensor] | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@dataclass
class TFImageClassifierOutputWithNoAttention(ModelOutput):
    loss: tf.Tensor | None = None
    logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
@dataclass
class TFMaskedImageModelingOutput(ModelOutput):
    loss: tf.Tensor | None = None
    reconstruction: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
    @property
    def logits(self):
        warnings.warn(
            "logits attribute is deprecated and will be removed in version 5 of MEROAI."
            " Please use the reconstruction attribute to retrieve the final output instead.",
            FutureWarning,
        )
        return self.reconstruction