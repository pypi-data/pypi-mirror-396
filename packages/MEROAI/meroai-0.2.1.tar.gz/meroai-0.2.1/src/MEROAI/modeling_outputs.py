import warnings
from dataclasses import dataclass
from typing import Optional
import torch
from .cache_utils import Cache, EncoderDecoderCache
from .utils import ModelOutput
@dataclass
class BaseModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithNoAttention(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPooling(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPoolingAndNoAttention(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPast(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithCrossAttentions(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPoolingAndCrossAttentions(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    past_key_values: Optional[Cache] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPastAndCrossAttentions(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class MoECausalLMOutputWithPast(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    z_loss: Optional[torch.FloatTensor] = None
    aux_loss: Optional[torch.FloatTensor] = None
    router_logits: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class MoEModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    router_probs: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class MoeModelOutputWithPast(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    router_logits: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class MoeCausalLMOutputWithPast(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    aux_loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    router_logits: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class MoEModelOutputWithPastAndCrossAttentions(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    router_probs: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class Seq2SeqModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqMoEModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_router_logits: Optional[tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_router_logits: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class CausalLMOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class CausalLMOutputWithPast(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class CausalLMOutputWithCrossAttentions(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class SequenceClassifierOutputWithPast(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[Cache] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class MaskedLMOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqLMOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqMoEOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    encoder_z_loss: Optional[torch.FloatTensor] = None
    decoder_z_loss: Optional[torch.FloatTensor] = None
    encoder_aux_loss: Optional[torch.FloatTensor] = None
    decoder_aux_loss: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_router_logits: Optional[tuple[torch.FloatTensor]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_router_logits: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class NextSentencePredictorOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class SequenceClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqSequenceClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class MultipleChoiceModelOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class TokenClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class QuestionAnsweringModelOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    start_logits: Optional[torch.FloatTensor] = None
    end_logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqQuestionAnsweringModelOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    start_logits: Optional[torch.FloatTensor] = None
    end_logits: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class SemanticSegmenterOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class ImageClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class ImageClassifierOutputWithNoAttention(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class DepthEstimatorOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    predicted_depth: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class ImageSuperResolutionOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    reconstruction: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Wav2Vec2BaseModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    extract_features: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class XVectorOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    embeddings: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BackboneOutput(ModelOutput):
    feature_maps: Optional[tuple[torch.FloatTensor]] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class BaseModelOutputWithPoolingAndProjection(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    pooler_output: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    projection_state: Optional[tuple[torch.FloatTensor]] = None
@dataclass
class Seq2SeqSpectrogramOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    spectrogram: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
@dataclass
class Seq2SeqTSModelOutput(ModelOutput):
    last_hidden_state: Optional[torch.FloatTensor] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    loc: Optional[torch.FloatTensor] = None
    scale: Optional[torch.FloatTensor] = None
    static_features: Optional[torch.FloatTensor] = None
@dataclass
class Seq2SeqTSPredictionOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    params: Optional[tuple[torch.FloatTensor, ...]] = None
    past_key_values: Optional[EncoderDecoderCache] = None
    decoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    decoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    cross_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_last_hidden_state: Optional[torch.FloatTensor] = None
    encoder_hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    encoder_attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    loc: Optional[torch.FloatTensor] = None
    scale: Optional[torch.FloatTensor] = None
    static_features: Optional[torch.FloatTensor] = None
@dataclass
class SampleTSPredictionOutput(ModelOutput):
    sequences: Optional[torch.FloatTensor] = None
@dataclass
class MaskedImageModelingOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    reconstruction: Optional[torch.FloatTensor] = None
    hidden_states: Optional[tuple[torch.FloatTensor, ...]] = None
    attentions: Optional[tuple[torch.FloatTensor, ...]] = None
    @property
    def logits(self):
        warnings.warn(
            "logits attribute is deprecated and will be removed in version 5 of MEROAI."
            " Please use the reconstruction attribute to retrieve the final output instead.",
            FutureWarning,
        )
        return self.reconstruction