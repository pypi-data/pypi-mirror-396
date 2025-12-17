from __future__ import annotations
from dataclasses import dataclass
import tensorflow as tf
from ...modeling_tf_outputs import TFBaseModelOutputWithPooling
from ...modeling_tf_utils import TFModelInputType, TFPreTrainedModel, get_initializer, keras, shape_list, unpack_inputs
from ...utils import (
    ModelOutput,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    logging,
    replace_return_docstrings,
)
from ..bert.modeling_tf_bert import TFBertMainLayer
from .configuration_dpr import DPRConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "DPRConfig"
@dataclass
class TFDPRContextEncoderOutput(ModelOutput):
    pooler_output: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
    attentions: tuple[tf.Tensor, ...] | None = None
@dataclass
class TFDPRQuestionEncoderOutput(ModelOutput):
    pooler_output: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
    attentions: tuple[tf.Tensor, ...] | None = None
@dataclass
class TFDPRReaderOutput(ModelOutput):
    start_logits: tf.Tensor | None = None
    end_logits: tf.Tensor | None = None
    relevance_logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor, ...] | None = None
    attentions: tuple[tf.Tensor, ...] | None = None
class TFDPREncoderLayer(keras.layers.Layer):
    base_model_prefix = "bert_model"
    def __init__(self, config: DPRConfig, **kwargs):
        super().__init__(**kwargs)
        self.bert_model = TFBertMainLayer(config, add_pooling_layer=False, name="bert_model")
        self.config = config
        if self.config.hidden_size <= 0:
            raise ValueError("Encoder hidden_size can't be zero")
        self.projection_dim = config.projection_dim
        if self.projection_dim > 0:
            self.encode_proj = keras.layers.Dense(
                config.projection_dim, kernel_initializer=get_initializer(config.initializer_range), name="encode_proj"
            )
    @unpack_inputs
    def call(
        self,
        input_ids: tf.Tensor | None = None,
        attention_mask: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFBaseModelOutputWithPooling | tuple[tf.Tensor, ...]:
        outputs = self.bert_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = outputs[0]
        pooled_output = sequence_output[:, 0, :]
        if self.projection_dim > 0:
            pooled_output = self.encode_proj(pooled_output)
        if not return_dict:
            return (sequence_output, pooled_output) + outputs[1:]
        return TFBaseModelOutputWithPooling(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    @property
    def embeddings_size(self) -> int:
        if self.projection_dim > 0:
            return self.projection_dim
        return self.bert_model.config.hidden_size
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "bert_model", None) is not None:
            with tf.name_scope(self.bert_model.name):
                self.bert_model.build(None)
        if getattr(self, "encode_proj", None) is not None:
            with tf.name_scope(self.encode_proj.name):
                self.encode_proj.build(None)
class TFDPRSpanPredictorLayer(keras.layers.Layer):
    base_model_prefix = "encoder"
    def __init__(self, config: DPRConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.encoder = TFDPREncoderLayer(config, name="encoder")
        self.qa_outputs = keras.layers.Dense(
            2, kernel_initializer=get_initializer(config.initializer_range), name="qa_outputs"
        )
        self.qa_classifier = keras.layers.Dense(
            1, kernel_initializer=get_initializer(config.initializer_range), name="qa_classifier"
        )
    @unpack_inputs
    def call(
        self,
        input_ids: tf.Tensor | None = None,
        attention_mask: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = False,
        training: bool = False,
    ) -> TFDPRReaderOutput | tuple[tf.Tensor, ...]:
        n_passages, sequence_length = shape_list(input_ids) if input_ids is not None else shape_list(inputs_embeds)[:2]
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = outputs[0]
        logits = self.qa_outputs(sequence_output)
        start_logits, end_logits = tf.split(logits, 2, axis=-1)
        start_logits = tf.squeeze(start_logits, axis=-1)
        end_logits = tf.squeeze(end_logits, axis=-1)
        relevance_logits = self.qa_classifier(sequence_output[:, 0, :])
        start_logits = tf.reshape(start_logits, [n_passages, sequence_length])
        end_logits = tf.reshape(end_logits, [n_passages, sequence_length])
        relevance_logits = tf.reshape(relevance_logits, [n_passages])
        if not return_dict:
            return (start_logits, end_logits, relevance_logits) + outputs[2:]
        return TFDPRReaderOutput(
            start_logits=start_logits,
            end_logits=end_logits,
            relevance_logits=relevance_logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name):
                self.encoder.build(None)
        if getattr(self, "qa_outputs", None) is not None:
            with tf.name_scope(self.qa_outputs.name):
                self.qa_outputs.build([None, None, self.encoder.embeddings_size])
        if getattr(self, "qa_classifier", None) is not None:
            with tf.name_scope(self.qa_classifier.name):
                self.qa_classifier.build([None, None, self.encoder.embeddings_size])
class TFDPRSpanPredictor(TFPreTrainedModel):
    base_model_prefix = "encoder"
    def __init__(self, config: DPRConfig, **kwargs):
        super().__init__(config, **kwargs)
        self.encoder = TFDPRSpanPredictorLayer(config)
    @unpack_inputs
    def call(
        self,
        input_ids: tf.Tensor | None = None,
        attention_mask: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = False,
        training: bool = False,
    ) -> TFDPRReaderOutput | tuple[tf.Tensor, ...]:
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        return outputs
class TFDPREncoder(TFPreTrainedModel):
    base_model_prefix = "encoder"
    def __init__(self, config: DPRConfig, **kwargs):
        super().__init__(config, **kwargs)
        self.encoder = TFDPREncoderLayer(config)
    @unpack_inputs
    def call(
        self,
        input_ids: tf.Tensor | None = None,
        attention_mask: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = False,
        training: bool = False,
    ) -> TFDPRReaderOutput | tuple[tf.Tensor, ...]:
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        return outputs
class TFDPRPretrainedContextEncoder(TFPreTrainedModel):
    config_class = DPRConfig
    base_model_prefix = "ctx_encoder"
class TFDPRPretrainedQuestionEncoder(TFPreTrainedModel):
    config_class = DPRConfig
    base_model_prefix = "question_encoder"
class TFDPRPretrainedReader(TFPreTrainedModel):
    config_class = DPRConfig
    base_model_prefix = "reader"
@add_start_docstrings(
    "The bare DPRContextEncoder transformer outputting pooler outputs as context representations.",
    TF_DPR_START_DOCSTRING,
)
class TFDPRContextEncoder(TFDPRPretrainedContextEncoder):
    def __init__(self, config: DPRConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.ctx_encoder = TFDPREncoderLayer(config, name="ctx_encoder")
    def get_input_embeddings(self):
        try:
            return self.ctx_encoder.bert_model.get_input_embeddings()
        except AttributeError:
            self.build()
            return self.ctx_encoder.bert_model.get_input_embeddings()
    @unpack_inputs
    @add_start_docstrings_to_model_forward(TF_DPR_ENCODERS_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=TFDPRContextEncoderOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFDPRContextEncoderOutput | tuple[tf.Tensor, ...]:
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
        elif inputs_embeds is not None:
            input_shape = shape_list(inputs_embeds)[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        if attention_mask is None:
            attention_mask = (
                tf.ones(input_shape, dtype=tf.dtypes.int32)
                if input_ids is None
                else (input_ids != self.config.pad_token_id)
            )
        if token_type_ids is None:
            token_type_ids = tf.zeros(input_shape, dtype=tf.dtypes.int32)
        outputs = self.ctx_encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        if not return_dict:
            return outputs[1:]
        return TFDPRContextEncoderOutput(
            pooler_output=outputs.pooler_output, hidden_states=outputs.hidden_states, attentions=outputs.attentions
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "ctx_encoder", None) is not None:
            with tf.name_scope(self.ctx_encoder.name):
                self.ctx_encoder.build(None)
@add_start_docstrings(
    "The bare DPRQuestionEncoder transformer outputting pooler outputs as question representations.",
    TF_DPR_START_DOCSTRING,
)
class TFDPRQuestionEncoder(TFDPRPretrainedQuestionEncoder):
    def __init__(self, config: DPRConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.question_encoder = TFDPREncoderLayer(config, name="question_encoder")
    def get_input_embeddings(self):
        try:
            return self.question_encoder.bert_model.get_input_embeddings()
        except AttributeError:
            self.build()
            return self.question_encoder.bert_model.get_input_embeddings()
    @unpack_inputs
    @add_start_docstrings_to_model_forward(TF_DPR_ENCODERS_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=TFDPRQuestionEncoderOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFDPRQuestionEncoderOutput | tuple[tf.Tensor, ...]:
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
        elif inputs_embeds is not None:
            input_shape = shape_list(inputs_embeds)[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        if attention_mask is None:
            attention_mask = (
                tf.ones(input_shape, dtype=tf.dtypes.int32)
                if input_ids is None
                else (input_ids != self.config.pad_token_id)
            )
        if token_type_ids is None:
            token_type_ids = tf.zeros(input_shape, dtype=tf.dtypes.int32)
        outputs = self.question_encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        if not return_dict:
            return outputs[1:]
        return TFDPRQuestionEncoderOutput(
            pooler_output=outputs.pooler_output, hidden_states=outputs.hidden_states, attentions=outputs.attentions
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "question_encoder", None) is not None:
            with tf.name_scope(self.question_encoder.name):
                self.question_encoder.build(None)
@add_start_docstrings(
    "The bare DPRReader transformer outputting span predictions.",
    TF_DPR_START_DOCSTRING,
)
class TFDPRReader(TFDPRPretrainedReader):
    def __init__(self, config: DPRConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.span_predictor = TFDPRSpanPredictorLayer(config, name="span_predictor")
    def get_input_embeddings(self):
        try:
            return self.span_predictor.encoder.bert_model.get_input_embeddings()
        except AttributeError:
            self.build()
            return self.span_predictor.encoder.bert_model.get_input_embeddings()
    @unpack_inputs
    @add_start_docstrings_to_model_forward(TF_DPR_READER_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=TFDPRReaderOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFDPRReaderOutput | tuple[tf.Tensor, ...]:
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
        elif inputs_embeds is not None:
            input_shape = shape_list(inputs_embeds)[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        if attention_mask is None:
            attention_mask = tf.ones(input_shape, dtype=tf.dtypes.int32)
        return self.span_predictor(
            input_ids=input_ids,
            attention_mask=attention_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "span_predictor", None) is not None:
            with tf.name_scope(self.span_predictor.name):
                self.span_predictor.build(None)
__all__ = [
    "TFDPRContextEncoder",
    "TFDPRPretrainedContextEncoder",
    "TFDPRPretrainedQuestionEncoder",
    "TFDPRPretrainedReader",
    "TFDPRQuestionEncoder",
    "TFDPRReader",
]