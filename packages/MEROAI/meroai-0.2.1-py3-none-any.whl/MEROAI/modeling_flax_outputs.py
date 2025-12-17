from typing import Optional
import flax
import jax.numpy as jnp
from .utils import ModelOutput
@flax.struct.dataclass
class FlaxBaseModelOutput(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithNoAttention(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPoolingAndNoAttention(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    pooler_output: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxImageClassifierOutputWithNoAttention(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPast(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    past_key_values: Optional[dict[str, jnp.ndarray]] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPooling(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    pooler_output: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPoolingAndCrossAttentions(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    pooler_output: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxBaseModelOutputWithPastAndCrossAttentions(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqModelOutput(ModelOutput):
    last_hidden_state: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxCausalLMOutputWithCrossAttentions(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxMaskedLMOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
FlaxCausalLMOutput = FlaxMaskedLMOutput
@flax.struct.dataclass
class FlaxSeq2SeqLMOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxNextSentencePredictorOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSequenceClassifierOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqSequenceClassifierOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxMultipleChoiceModelOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxTokenClassifierOutput(ModelOutput):
    logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxQuestionAnsweringModelOutput(ModelOutput):
    start_logits: Optional[jnp.ndarray] = None
    end_logits: Optional[jnp.ndarray] = None
    hidden_states: Optional[tuple[jnp.ndarray]] = None
    attentions: Optional[tuple[jnp.ndarray]] = None
@flax.struct.dataclass
class FlaxSeq2SeqQuestionAnsweringModelOutput(ModelOutput):
    start_logits: Optional[jnp.ndarray] = None
    end_logits: Optional[jnp.ndarray] = None
    past_key_values: Optional[tuple[tuple[jnp.ndarray]]] = None
    decoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    decoder_attentions: Optional[tuple[jnp.ndarray]] = None
    cross_attentions: Optional[tuple[jnp.ndarray]] = None
    encoder_last_hidden_state: Optional[jnp.ndarray] = None
    encoder_hidden_states: Optional[tuple[jnp.ndarray]] = None
    encoder_attentions: Optional[tuple[jnp.ndarray]] = None