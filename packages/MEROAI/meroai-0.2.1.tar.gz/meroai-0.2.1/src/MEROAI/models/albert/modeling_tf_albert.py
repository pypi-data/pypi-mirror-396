from __future__ import annotations
import math
from dataclasses import dataclass
import numpy as np
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_outputs import (
    TFBaseModelOutput,
    TFBaseModelOutputWithPooling,
    TFMaskedLMOutput,
    TFMultipleChoiceModelOutput,
    TFQuestionAnsweringModelOutput,
    TFSequenceClassifierOutput,
    TFTokenClassifierOutput,
)
from ...modeling_tf_utils import (
    TFMaskedLanguageModelingLoss,
    TFModelInputType,
    TFMultipleChoiceLoss,
    TFPreTrainedModel,
    TFQuestionAnsweringLoss,
    TFSequenceClassificationLoss,
    TFTokenClassificationLoss,
    get_initializer,
    keras,
    keras_serializable,
    unpack_inputs,
)
from ...tf_utils import check_embeddings_within_bounds, shape_list, stable_softmax
from ...utils import (
    ModelOutput,
    add_code_sample_docstrings,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    logging,
    replace_return_docstrings,
)
from .configuration_albert import AlbertConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "albert/albert-base-v2"
_CONFIG_FOR_DOC = "AlbertConfig"
class TFAlbertPreTrainingLoss:
    def hf_compute_loss(self, labels: tf.Tensor, logits: tf.Tensor) -> tf.Tensor:
        loss_fn = keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction=keras.losses.Reduction.NONE)
        if self.config.tf_legacy_loss:
            masked_lm_active_loss = tf.not_equal(tf.reshape(tensor=labels["labels"], shape=(-1,)), -100)
            masked_lm_reduced_logits = tf.boolean_mask(
                tensor=tf.reshape(tensor=logits[0], shape=(-1, shape_list(logits[0])[2])),
                mask=masked_lm_active_loss,
            )
            masked_lm_labels = tf.boolean_mask(
                tensor=tf.reshape(tensor=labels["labels"], shape=(-1,)), mask=masked_lm_active_loss
            )
            sentence_order_active_loss = tf.not_equal(
                tf.reshape(tensor=labels["sentence_order_label"], shape=(-1,)), -100
            )
            sentence_order_reduced_logits = tf.boolean_mask(
                tensor=tf.reshape(tensor=logits[1], shape=(-1, 2)), mask=sentence_order_active_loss
            )
            sentence_order_label = tf.boolean_mask(
                tensor=tf.reshape(tensor=labels["sentence_order_label"], shape=(-1,)), mask=sentence_order_active_loss
            )
            masked_lm_loss = loss_fn(y_true=masked_lm_labels, y_pred=masked_lm_reduced_logits)
            sentence_order_loss = loss_fn(y_true=sentence_order_label, y_pred=sentence_order_reduced_logits)
            masked_lm_loss = tf.reshape(tensor=masked_lm_loss, shape=(-1, shape_list(sentence_order_loss)[0]))
            masked_lm_loss = tf.reduce_mean(input_tensor=masked_lm_loss, axis=0)
            return masked_lm_loss + sentence_order_loss
        unmasked_lm_losses = loss_fn(y_true=tf.nn.relu(labels["labels"]), y_pred=logits[0])
        lm_loss_mask = tf.cast(labels["labels"] != -100, dtype=unmasked_lm_losses.dtype)
        masked_lm_losses = unmasked_lm_losses * lm_loss_mask
        reduced_masked_lm_loss = tf.reduce_sum(masked_lm_losses) / tf.reduce_sum(lm_loss_mask)
        sop_logits = tf.reshape(logits[1], (-1, 2))
        unmasked_sop_loss = loss_fn(y_true=tf.nn.relu(labels["sentence_order_label"]), y_pred=sop_logits)
        sop_loss_mask = tf.cast(labels["sentence_order_label"] != -100, dtype=unmasked_sop_loss.dtype)
        masked_sop_loss = unmasked_sop_loss * sop_loss_mask
        reduced_masked_sop_loss = tf.reduce_sum(masked_sop_loss) / tf.reduce_sum(sop_loss_mask)
        return tf.reshape(reduced_masked_lm_loss + reduced_masked_sop_loss, (1,))
class TFAlbertEmbeddings(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embedding_size = config.embedding_size
        self.max_position_embeddings = config.max_position_embeddings
        self.initializer_range = config.initializer_range
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
    def build(self, input_shape=None):
        with tf.name_scope("word_embeddings"):
            self.weight = self.add_weight(
                name="weight",
                shape=[self.config.vocab_size, self.embedding_size],
                initializer=get_initializer(self.initializer_range),
            )
        with tf.name_scope("token_type_embeddings"):
            self.token_type_embeddings = self.add_weight(
                name="embeddings",
                shape=[self.config.type_vocab_size, self.embedding_size],
                initializer=get_initializer(self.initializer_range),
            )
        with tf.name_scope("position_embeddings"):
            self.position_embeddings = self.add_weight(
                name="embeddings",
                shape=[self.max_position_embeddings, self.embedding_size],
                initializer=get_initializer(self.initializer_range),
            )
        if self.built:
            return
        self.built = True
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name):
                self.LayerNorm.build([None, None, self.config.embedding_size])
    def call(
        self,
        input_ids: tf.Tensor | None = None,
        position_ids: tf.Tensor | None = None,
        token_type_ids: tf.Tensor | None = None,
        inputs_embeds: tf.Tensor | None = None,
        past_key_values_length=0,
        training: bool = False,
    ) -> tf.Tensor:
        if input_ids is None and inputs_embeds is None:
            raise ValueError("Need to provide either `input_ids` or `input_embeds`.")
        if input_ids is not None:
            check_embeddings_within_bounds(input_ids, self.config.vocab_size)
            inputs_embeds = tf.gather(params=self.weight, indices=input_ids)
        input_shape = shape_list(inputs_embeds)[:-1]
        if token_type_ids is None:
            token_type_ids = tf.fill(dims=input_shape, value=0)
        if position_ids is None:
            position_ids = tf.expand_dims(
                tf.range(start=past_key_values_length, limit=input_shape[1] + past_key_values_length), axis=0
            )
        position_embeds = tf.gather(params=self.position_embeddings, indices=position_ids)
        token_type_embeds = tf.gather(params=self.token_type_embeddings, indices=token_type_ids)
        final_embeddings = inputs_embeds + position_embeds + token_type_embeds
        final_embeddings = self.LayerNorm(inputs=final_embeddings)
        final_embeddings = self.dropout(inputs=final_embeddings, training=training)
        return final_embeddings
class TFAlbertAttention(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        if config.hidden_size % config.num_attention_heads != 0:
            raise ValueError(
                f"The hidden size ({config.hidden_size}) is not a multiple of the number "
                f"of attention heads ({config.num_attention_heads})"
            )
        self.num_attention_heads = config.num_attention_heads
        self.attention_head_size = int(config.hidden_size / config.num_attention_heads)
        self.all_head_size = self.num_attention_heads * self.attention_head_size
        self.sqrt_att_head_size = math.sqrt(self.attention_head_size)
        self.output_attentions = config.output_attentions
        self.query = keras.layers.Dense(
            units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="query"
        )
        self.key = keras.layers.Dense(
            units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="key"
        )
        self.value = keras.layers.Dense(
            units=self.all_head_size, kernel_initializer=get_initializer(config.initializer_range), name="value"
        )
        self.dense = keras.layers.Dense(
            units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="dense"
        )
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.attention_dropout = keras.layers.Dropout(rate=config.attention_probs_dropout_prob)
        self.output_dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def transpose_for_scores(self, tensor: tf.Tensor, batch_size: int) -> tf.Tensor:
        tensor = tf.reshape(tensor=tensor, shape=(batch_size, -1, self.num_attention_heads, self.attention_head_size))
        return tf.transpose(tensor, perm=[0, 2, 1, 3])
    def call(
        self,
        input_tensor: tf.Tensor,
        attention_mask: tf.Tensor,
        head_mask: tf.Tensor,
        output_attentions: bool,
        training: bool = False,
    ) -> tuple[tf.Tensor]:
        batch_size = shape_list(input_tensor)[0]
        mixed_query_layer = self.query(inputs=input_tensor)
        mixed_key_layer = self.key(inputs=input_tensor)
        mixed_value_layer = self.value(inputs=input_tensor)
        query_layer = self.transpose_for_scores(mixed_query_layer, batch_size)
        key_layer = self.transpose_for_scores(mixed_key_layer, batch_size)
        value_layer = self.transpose_for_scores(mixed_value_layer, batch_size)
        attention_scores = tf.matmul(query_layer, key_layer, transpose_b=True)
        dk = tf.cast(self.sqrt_att_head_size, dtype=attention_scores.dtype)
        attention_scores = tf.divide(attention_scores, dk)
        if attention_mask is not None:
            attention_scores = tf.add(attention_scores, attention_mask)
        attention_probs = stable_softmax(logits=attention_scores, axis=-1)
        attention_probs = self.attention_dropout(inputs=attention_probs, training=training)
        if head_mask is not None:
            attention_probs = tf.multiply(attention_probs, head_mask)
        context_layer = tf.matmul(attention_probs, value_layer)
        context_layer = tf.transpose(context_layer, perm=[0, 2, 1, 3])
        context_layer = tf.reshape(tensor=context_layer, shape=(batch_size, -1, self.all_head_size))
        self_outputs = (context_layer, attention_probs) if output_attentions else (context_layer,)
        hidden_states = self_outputs[0]
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.output_dropout(inputs=hidden_states, training=training)
        attention_output = self.LayerNorm(inputs=hidden_states + input_tensor)
        outputs = (attention_output,) + self_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "query", None) is not None:
            with tf.name_scope(self.query.name):
                self.query.build([None, None, self.config.hidden_size])
        if getattr(self, "key", None) is not None:
            with tf.name_scope(self.key.name):
                self.key.build([None, None, self.config.hidden_size])
        if getattr(self, "value", None) is not None:
            with tf.name_scope(self.value.name):
                self.value.build([None, None, self.config.hidden_size])
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name):
                self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name):
                self.LayerNorm.build([None, None, self.config.hidden_size])
class TFAlbertLayer(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        self.attention = TFAlbertAttention(config, name="attention")
        self.ffn = keras.layers.Dense(
            units=config.intermediate_size, kernel_initializer=get_initializer(config.initializer_range), name="ffn"
        )
        if isinstance(config.hidden_act, str):
            self.activation = get_tf_activation(config.hidden_act)
        else:
            self.activation = config.hidden_act
        self.ffn_output = keras.layers.Dense(
            units=config.hidden_size, kernel_initializer=get_initializer(config.initializer_range), name="ffn_output"
        )
        self.full_layer_layer_norm = keras.layers.LayerNormalization(
            epsilon=config.layer_norm_eps, name="full_layer_layer_norm"
        )
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.config = config
    def call(
        self,
        hidden_states: tf.Tensor,
        attention_mask: tf.Tensor,
        head_mask: tf.Tensor,
        output_attentions: bool,
        training: bool = False,
    ) -> tuple[tf.Tensor]:
        attention_outputs = self.attention(
            input_tensor=hidden_states,
            attention_mask=attention_mask,
            head_mask=head_mask,
            output_attentions=output_attentions,
            training=training,
        )
        ffn_output = self.ffn(inputs=attention_outputs[0])
        ffn_output = self.activation(ffn_output)
        ffn_output = self.ffn_output(inputs=ffn_output)
        ffn_output = self.dropout(inputs=ffn_output, training=training)
        hidden_states = self.full_layer_layer_norm(inputs=ffn_output + attention_outputs[0])
        outputs = (hidden_states,) + attention_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "attention", None) is not None:
            with tf.name_scope(self.attention.name):
                self.attention.build(None)
        if getattr(self, "ffn", None) is not None:
            with tf.name_scope(self.ffn.name):
                self.ffn.build([None, None, self.config.hidden_size])
        if getattr(self, "ffn_output", None) is not None:
            with tf.name_scope(self.ffn_output.name):
                self.ffn_output.build([None, None, self.config.intermediate_size])
        if getattr(self, "full_layer_layer_norm", None) is not None:
            with tf.name_scope(self.full_layer_layer_norm.name):
                self.full_layer_layer_norm.build([None, None, self.config.hidden_size])
class TFAlbertLayerGroup(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        self.albert_layers = [
            TFAlbertLayer(config, name=f"albert_layers_._{i}") for i in range(config.inner_group_num)
        ]
    def call(
        self,
        hidden_states: tf.Tensor,
        attention_mask: tf.Tensor,
        head_mask: tf.Tensor,
        output_attentions: bool,
        output_hidden_states: bool,
        training: bool = False,
    ) -> TFBaseModelOutput | tuple[tf.Tensor]:
        layer_hidden_states = () if output_hidden_states else None
        layer_attentions = () if output_attentions else None
        for layer_index, albert_layer in enumerate(self.albert_layers):
            if output_hidden_states:
                layer_hidden_states = layer_hidden_states + (hidden_states,)
            layer_output = albert_layer(
                hidden_states=hidden_states,
                attention_mask=attention_mask,
                head_mask=head_mask[layer_index],
                output_attentions=output_attentions,
                training=training,
            )
            hidden_states = layer_output[0]
            if output_attentions:
                layer_attentions = layer_attentions + (layer_output[1],)
        if output_hidden_states:
            layer_hidden_states = layer_hidden_states + (hidden_states,)
        return tuple(v for v in [hidden_states, layer_hidden_states, layer_attentions] if v is not None)
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert_layers", None) is not None:
            for layer in self.albert_layers:
                with tf.name_scope(layer.name):
                    layer.build(None)
class TFAlbertTransformer(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        self.num_hidden_layers = config.num_hidden_layers
        self.num_hidden_groups = config.num_hidden_groups
        self.layers_per_group = int(config.num_hidden_layers / config.num_hidden_groups)
        self.embedding_hidden_mapping_in = keras.layers.Dense(
            units=config.hidden_size,
            kernel_initializer=get_initializer(config.initializer_range),
            name="embedding_hidden_mapping_in",
        )
        self.albert_layer_groups = [
            TFAlbertLayerGroup(config, name=f"albert_layer_groups_._{i}") for i in range(config.num_hidden_groups)
        ]
        self.config = config
    def call(
        self,
        hidden_states: tf.Tensor,
        attention_mask: tf.Tensor,
        head_mask: tf.Tensor,
        output_attentions: bool,
        output_hidden_states: bool,
        return_dict: bool,
        training: bool = False,
    ) -> TFBaseModelOutput | tuple[tf.Tensor]:
        hidden_states = self.embedding_hidden_mapping_in(inputs=hidden_states)
        all_attentions = () if output_attentions else None
        all_hidden_states = (hidden_states,) if output_hidden_states else None
        for i in range(self.num_hidden_layers):
            group_idx = int(i / (self.num_hidden_layers / self.num_hidden_groups))
            layer_group_output = self.albert_layer_groups[group_idx](
                hidden_states=hidden_states,
                attention_mask=attention_mask,
                head_mask=head_mask[group_idx * self.layers_per_group : (group_idx + 1) * self.layers_per_group],
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
                training=training,
            )
            hidden_states = layer_group_output[0]
            if output_attentions:
                all_attentions = all_attentions + layer_group_output[-1]
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states, all_attentions] if v is not None)
        return TFBaseModelOutput(
            last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_attentions
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "embedding_hidden_mapping_in", None) is not None:
            with tf.name_scope(self.embedding_hidden_mapping_in.name):
                self.embedding_hidden_mapping_in.build([None, None, self.config.embedding_size])
        if getattr(self, "albert_layer_groups", None) is not None:
            for layer in self.albert_layer_groups:
                with tf.name_scope(layer.name):
                    layer.build(None)
class TFAlbertPreTrainedModel(TFPreTrainedModel):
    config_class = AlbertConfig
    base_model_prefix = "albert"
class TFAlbertMLMHead(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, input_embeddings: keras.layers.Layer, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embedding_size = config.embedding_size
        self.dense = keras.layers.Dense(
            config.embedding_size, kernel_initializer=get_initializer(config.initializer_range), name="dense"
        )
        if isinstance(config.hidden_act, str):
            self.activation = get_tf_activation(config.hidden_act)
        else:
            self.activation = config.hidden_act
        self.LayerNorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="LayerNorm")
        self.decoder = input_embeddings
    def build(self, input_shape=None):
        self.bias = self.add_weight(shape=(self.config.vocab_size,), initializer="zeros", trainable=True, name="bias")
        self.decoder_bias = self.add_weight(
            shape=(self.config.vocab_size,), initializer="zeros", trainable=True, name="decoder/bias"
        )
        if self.built:
            return
        self.built = True
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name):
                self.dense.build([None, None, self.config.hidden_size])
        if getattr(self, "LayerNorm", None) is not None:
            with tf.name_scope(self.LayerNorm.name):
                self.LayerNorm.build([None, None, self.config.embedding_size])
    def get_output_embeddings(self) -> keras.layers.Layer:
        return self.decoder
    def set_output_embeddings(self, value: tf.Variable):
        self.decoder.weight = value
        self.decoder.vocab_size = shape_list(value)[0]
    def get_bias(self) -> dict[str, tf.Variable]:
        return {"bias": self.bias, "decoder_bias": self.decoder_bias}
    def set_bias(self, value: tf.Variable):
        self.bias = value["bias"]
        self.decoder_bias = value["decoder_bias"]
        self.config.vocab_size = shape_list(value["bias"])[0]
    def call(self, hidden_states: tf.Tensor) -> tf.Tensor:
        hidden_states = self.dense(inputs=hidden_states)
        hidden_states = self.activation(hidden_states)
        hidden_states = self.LayerNorm(inputs=hidden_states)
        seq_length = shape_list(tensor=hidden_states)[1]
        hidden_states = tf.reshape(tensor=hidden_states, shape=[-1, self.embedding_size])
        hidden_states = tf.matmul(a=hidden_states, b=self.decoder.weight, transpose_b=True)
        hidden_states = tf.reshape(tensor=hidden_states, shape=[-1, seq_length, self.config.vocab_size])
        hidden_states = tf.nn.bias_add(value=hidden_states, bias=self.decoder_bias)
        return hidden_states
@keras_serializable
class TFAlbertMainLayer(keras.layers.Layer):
    config_class = AlbertConfig
    def __init__(self, config: AlbertConfig, add_pooling_layer: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embeddings = TFAlbertEmbeddings(config, name="embeddings")
        self.encoder = TFAlbertTransformer(config, name="encoder")
        self.pooler = (
            keras.layers.Dense(
                units=config.hidden_size,
                kernel_initializer=get_initializer(config.initializer_range),
                activation="tanh",
                name="pooler",
            )
            if add_pooling_layer
            else None
        )
    def get_input_embeddings(self) -> keras.layers.Layer:
        return self.embeddings
    def set_input_embeddings(self, value: tf.Variable):
        self.embeddings.weight = value
        self.embeddings.vocab_size = shape_list(value)[0]
    def _prune_heads(self, heads_to_prune):
        raise NotImplementedError
    @unpack_inputs
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFBaseModelOutputWithPooling | tuple[tf.Tensor]:
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
        elif inputs_embeds is not None:
            input_shape = shape_list(inputs_embeds)[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        if attention_mask is None:
            attention_mask = tf.fill(dims=input_shape, value=1)
        if token_type_ids is None:
            token_type_ids = tf.fill(dims=input_shape, value=0)
        embedding_output = self.embeddings(
            input_ids=input_ids,
            position_ids=position_ids,
            token_type_ids=token_type_ids,
            inputs_embeds=inputs_embeds,
            training=training,
        )
        extended_attention_mask = tf.reshape(attention_mask, (input_shape[0], 1, 1, input_shape[1]))
        extended_attention_mask = tf.cast(extended_attention_mask, dtype=embedding_output.dtype)
        one_cst = tf.constant(1.0, dtype=embedding_output.dtype)
        ten_thousand_cst = tf.constant(-10000.0, dtype=embedding_output.dtype)
        extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)
        if head_mask is not None:
            raise NotImplementedError
        else:
            head_mask = [None] * self.config.num_hidden_layers
        encoder_outputs = self.encoder(
            hidden_states=embedding_output,
            attention_mask=extended_attention_mask,
            head_mask=head_mask,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = encoder_outputs[0]
        pooled_output = self.pooler(inputs=sequence_output[:, 0]) if self.pooler is not None else None
        if not return_dict:
            return (
                sequence_output,
                pooled_output,
            ) + encoder_outputs[1:]
        return TFBaseModelOutputWithPooling(
            last_hidden_state=sequence_output,
            pooler_output=pooled_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "embeddings", None) is not None:
            with tf.name_scope(self.embeddings.name):
                self.embeddings.build(None)
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name):
                self.encoder.build(None)
        if getattr(self, "pooler", None) is not None:
            with tf.name_scope(self.pooler.name):
                self.pooler.build([None, None, self.config.hidden_size])
@dataclass
class TFAlbertForPreTrainingOutput(ModelOutput):
    loss: tf.Tensor | None = None
    prediction_logits: tf.Tensor | None = None
    sop_logits: tf.Tensor | None = None
    hidden_states: tuple[tf.Tensor] | None = None
    attentions: tuple[tf.Tensor] | None = None
@add_start_docstrings(
    "The bare Albert Model transformer outputting raw hidden-states without any specific head on top.",
    ALBERT_START_DOCSTRING,
)
class TFAlbertModel(TFAlbertPreTrainedModel):
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.albert = TFAlbertMainLayer(config, name="albert")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFBaseModelOutputWithPooling,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool | None = False,
    ) -> TFBaseModelOutputWithPooling | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        return outputs
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
@add_start_docstrings(
,
    ALBERT_START_DOCSTRING,
)
class TFAlbertForPreTraining(TFAlbertPreTrainedModel, TFAlbertPreTrainingLoss):
    _keys_to_ignore_on_load_unexpected = [r"predictions.decoder.weight"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.albert = TFAlbertMainLayer(config, name="albert")
        self.predictions = TFAlbertMLMHead(config, input_embeddings=self.albert.embeddings, name="predictions")
        self.sop_classifier = TFAlbertSOPHead(config, name="sop_classifier")
    def get_lm_head(self) -> keras.layers.Layer:
        return self.predictions
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @replace_return_docstrings(output_type=TFAlbertForPreTrainingOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        sentence_order_label: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFAlbertForPreTrainingOutput | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output, pooled_output = outputs[:2]
        prediction_scores = self.predictions(hidden_states=sequence_output)
        sop_scores = self.sop_classifier(pooled_output=pooled_output, training=training)
        total_loss = None
        if labels is not None and sentence_order_label is not None:
            d_labels = {"labels": labels}
            d_labels["sentence_order_label"] = sentence_order_label
            total_loss = self.hf_compute_loss(labels=d_labels, logits=(prediction_scores, sop_scores))
        if not return_dict:
            output = (prediction_scores, sop_scores) + outputs[2:]
            return ((total_loss,) + output) if total_loss is not None else output
        return TFAlbertForPreTrainingOutput(
            loss=total_loss,
            prediction_logits=prediction_scores,
            sop_logits=sop_scores,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "predictions", None) is not None:
            with tf.name_scope(self.predictions.name):
                self.predictions.build(None)
        if getattr(self, "sop_classifier", None) is not None:
            with tf.name_scope(self.sop_classifier.name):
                self.sop_classifier.build(None)
class TFAlbertSOPHead(keras.layers.Layer):
    def __init__(self, config: AlbertConfig, **kwargs):
        super().__init__(**kwargs)
        self.dropout = keras.layers.Dropout(rate=config.classifier_dropout_prob)
        self.classifier = keras.layers.Dense(
            units=config.num_labels,
            kernel_initializer=get_initializer(config.initializer_range),
            name="classifier",
        )
        self.config = config
    def call(self, pooled_output: tf.Tensor, training: bool) -> tf.Tensor:
        dropout_pooled_output = self.dropout(inputs=pooled_output, training=training)
        logits = self.classifier(inputs=dropout_pooled_output)
        return logits
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name):
                self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings(, ALBERT_START_DOCSTRING)
class TFAlbertForMaskedLM(TFAlbertPreTrainedModel, TFMaskedLanguageModelingLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"predictions.decoder.weight"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.albert = TFAlbertMainLayer(config, add_pooling_layer=False, name="albert")
        self.predictions = TFAlbertMLMHead(config, input_embeddings=self.albert.embeddings, name="predictions")
    def get_lm_head(self) -> keras.layers.Layer:
        return self.predictions
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @replace_return_docstrings(output_type=TFMaskedLMOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFMaskedLMOutput | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = outputs[0]
        prediction_scores = self.predictions(hidden_states=sequence_output, training=training)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=prediction_scores)
        if not return_dict:
            output = (prediction_scores,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFMaskedLMOutput(
            loss=loss,
            logits=prediction_scores,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "predictions", None) is not None:
            with tf.name_scope(self.predictions.name):
                self.predictions.build(None)
@add_start_docstrings(
,
    ALBERT_START_DOCSTRING,
)
class TFAlbertForSequenceClassification(TFAlbertPreTrainedModel, TFSequenceClassificationLoss):
    _keys_to_ignore_on_load_unexpected = [r"predictions"]
    _keys_to_ignore_on_load_missing = [r"dropout"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.albert = TFAlbertMainLayer(config, name="albert")
        self.dropout = keras.layers.Dropout(rate=config.classifier_dropout_prob)
        self.classifier = keras.layers.Dense(
            units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="classifier"
        )
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @add_code_sample_docstrings(
        checkpoint="vumichien/albert-base-v2-imdb",
        output_type=TFSequenceClassifierOutput,
        config_class=_CONFIG_FOR_DOC,
        expected_output="'LABEL_1'",
        expected_loss=0.12,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFSequenceClassifierOutput | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        pooled_output = outputs[1]
        pooled_output = self.dropout(inputs=pooled_output, training=training)
        logits = self.classifier(inputs=pooled_output)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name):
                self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings(
,
    ALBERT_START_DOCSTRING,
)
class TFAlbertForTokenClassification(TFAlbertPreTrainedModel, TFTokenClassificationLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"predictions"]
    _keys_to_ignore_on_load_missing = [r"dropout"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.albert = TFAlbertMainLayer(config, add_pooling_layer=False, name="albert")
        classifier_dropout_prob = (
            config.classifier_dropout_prob
            if config.classifier_dropout_prob is not None
            else config.hidden_dropout_prob
        )
        self.dropout = keras.layers.Dropout(rate=classifier_dropout_prob)
        self.classifier = keras.layers.Dense(
            units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="classifier"
        )
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFTokenClassifierOutput,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFTokenClassifierOutput | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = outputs[0]
        sequence_output = self.dropout(inputs=sequence_output, training=training)
        logits = self.classifier(inputs=sequence_output)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFTokenClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name):
                self.classifier.build([None, None, self.config.hidden_size])
@add_start_docstrings(
,
    ALBERT_START_DOCSTRING,
)
class TFAlbertForQuestionAnswering(TFAlbertPreTrainedModel, TFQuestionAnsweringLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"predictions"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.albert = TFAlbertMainLayer(config, add_pooling_layer=False, name="albert")
        self.qa_outputs = keras.layers.Dense(
            units=config.num_labels, kernel_initializer=get_initializer(config.initializer_range), name="qa_outputs"
        )
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @add_code_sample_docstrings(
        checkpoint="vumichien/albert-base-v2-squad2",
        output_type=TFQuestionAnsweringModelOutput,
        config_class=_CONFIG_FOR_DOC,
        qa_target_start_index=12,
        qa_target_end_index=13,
        expected_output="'a nice puppet'",
        expected_loss=7.36,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        start_positions: np.ndarray | tf.Tensor | None = None,
        end_positions: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFQuestionAnsweringModelOutput | tuple[tf.Tensor]:
        outputs = self.albert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        sequence_output = outputs[0]
        logits = self.qa_outputs(inputs=sequence_output)
        start_logits, end_logits = tf.split(value=logits, num_or_size_splits=2, axis=-1)
        start_logits = tf.squeeze(input=start_logits, axis=-1)
        end_logits = tf.squeeze(input=end_logits, axis=-1)
        loss = None
        if start_positions is not None and end_positions is not None:
            labels = {"start_position": start_positions}
            labels["end_position"] = end_positions
            loss = self.hf_compute_loss(labels=labels, logits=(start_logits, end_logits))
        if not return_dict:
            output = (start_logits, end_logits) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFQuestionAnsweringModelOutput(
            loss=loss,
            start_logits=start_logits,
            end_logits=end_logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "qa_outputs", None) is not None:
            with tf.name_scope(self.qa_outputs.name):
                self.qa_outputs.build([None, None, self.config.hidden_size])
@add_start_docstrings(
,
    ALBERT_START_DOCSTRING,
)
class TFAlbertForMultipleChoice(TFAlbertPreTrainedModel, TFMultipleChoiceLoss):
    _keys_to_ignore_on_load_unexpected = [r"pooler", r"predictions"]
    _keys_to_ignore_on_load_missing = [r"dropout"]
    def __init__(self, config: AlbertConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.albert = TFAlbertMainLayer(config, name="albert")
        self.dropout = keras.layers.Dropout(rate=config.hidden_dropout_prob)
        self.classifier = keras.layers.Dense(
            units=1, kernel_initializer=get_initializer(config.initializer_range), name="classifier"
        )
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ALBERT_INPUTS_DOCSTRING.format("batch_size, num_choices, sequence_length"))
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFMultipleChoiceModelOutput,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFMultipleChoiceModelOutput | tuple[tf.Tensor]:
        if input_ids is not None:
            num_choices = shape_list(input_ids)[1]
            seq_length = shape_list(input_ids)[2]
        else:
            num_choices = shape_list(inputs_embeds)[1]
            seq_length = shape_list(inputs_embeds)[2]
        flat_input_ids = tf.reshape(input_ids, (-1, seq_length)) if input_ids is not None else None
        flat_attention_mask = (
            tf.reshape(tensor=attention_mask, shape=(-1, seq_length)) if attention_mask is not None else None
        )
        flat_token_type_ids = (
            tf.reshape(tensor=token_type_ids, shape=(-1, seq_length)) if token_type_ids is not None else None
        )
        flat_position_ids = (
            tf.reshape(tensor=position_ids, shape=(-1, seq_length)) if position_ids is not None else None
        )
        flat_inputs_embeds = (
            tf.reshape(tensor=inputs_embeds, shape=(-1, seq_length, shape_list(inputs_embeds)[3]))
            if inputs_embeds is not None
            else None
        )
        outputs = self.albert(
            input_ids=flat_input_ids,
            attention_mask=flat_attention_mask,
            token_type_ids=flat_token_type_ids,
            position_ids=flat_position_ids,
            head_mask=head_mask,
            inputs_embeds=flat_inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        pooled_output = outputs[1]
        pooled_output = self.dropout(inputs=pooled_output, training=training)
        logits = self.classifier(inputs=pooled_output)
        reshaped_logits = tf.reshape(tensor=logits, shape=(-1, num_choices))
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=reshaped_logits)
        if not return_dict:
            output = (reshaped_logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFMultipleChoiceModelOutput(
            loss=loss,
            logits=reshaped_logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "albert", None) is not None:
            with tf.name_scope(self.albert.name):
                self.albert.build(None)
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name):
                self.classifier.build([None, None, self.config.hidden_size])
__all__ = [
    "TFAlbertPreTrainedModel",
    "TFAlbertModel",
    "TFAlbertForPreTraining",
    "TFAlbertForMaskedLM",
    "TFAlbertForSequenceClassification",
    "TFAlbertForTokenClassification",
    "TFAlbertForQuestionAnswering",
    "TFAlbertForMultipleChoice",
    "TFAlbertMainLayer",
]