from __future__ import annotations
import numpy as np
import tensorflow as tf
from ...modeling_tf_outputs import TFBaseModelOutputWithPast, TFCausalLMOutputWithPast, TFSequenceClassifierOutput
from ...modeling_tf_utils import (
    TFCausalLanguageModelingLoss,
    TFModelInputType,
    TFPreTrainedModel,
    TFSequenceClassificationLoss,
    get_initializer,
    keras,
    keras_serializable,
    unpack_inputs,
)
from ...tf_utils import check_embeddings_within_bounds, shape_list, stable_softmax
from ...utils import add_code_sample_docstrings, add_start_docstrings, add_start_docstrings_to_model_forward, logging
from .configuration_ctrl import CTRLConfig
logger = logging.get_logger(__name__)
_CHECKPOINT_FOR_DOC = "Salesforce/ctrl"
_CONFIG_FOR_DOC = "CTRLConfig"
def angle_defn(pos, i, d_model_size):
    angle_rates = 1 / np.power(10000, (2 * (i // 2)) / d_model_size)
    return pos * angle_rates
def positional_encoding(position, d_model_size):
    angle_rads = angle_defn(np.arange(position)[:, np.newaxis], np.arange(d_model_size)[np.newaxis, :], d_model_size)
    sines = np.sin(angle_rads[:, 0::2])
    cosines = np.cos(angle_rads[:, 1::2])
    pos_encoding = tf.convert_to_tensor(np.concatenate([sines, cosines], axis=-1))
    return pos_encoding
def scaled_dot_product_attention(q, k, v, mask, attention_mask=None, head_mask=None):
    matmul_qk = tf.matmul(q, k, transpose_b=True)
    dk = tf.cast(shape_list(k)[-1], dtype=matmul_qk.dtype)
    scaled_attention_logits = matmul_qk / tf.math.sqrt(dk)
    if mask is not None:
        scaled_attention_logits += tf.cast(mask * -1e4, dtype=scaled_attention_logits.dtype)
    if attention_mask is not None:
        attention_mask = tf.cast(attention_mask, dtype=scaled_attention_logits.dtype)
        scaled_attention_logits = scaled_attention_logits + attention_mask
    attention_weights = stable_softmax(scaled_attention_logits, axis=-1)
    if head_mask is not None:
        attention_weights = attention_weights * head_mask
    output = tf.matmul(attention_weights, v)
    return output, attention_weights
class TFMultiHeadAttention(keras.layers.Layer):
    def __init__(self, d_model_size, num_heads, output_attentions=False, **kwargs):
        super().__init__(**kwargs)
        self.num_heads = num_heads
        self.d_model_size = d_model_size
        self.output_attentions = output_attentions
        self.depth = int(d_model_size / self.num_heads)
        self.Wq = keras.layers.Dense(d_model_size, name="Wq")
        self.Wk = keras.layers.Dense(d_model_size, name="Wk")
        self.Wv = keras.layers.Dense(d_model_size, name="Wv")
        self.dense = keras.layers.Dense(d_model_size, name="dense")
    def split_into_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.depth))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    def call(self, v, k, q, mask, layer_past, attention_mask, head_mask, use_cache, output_attentions, training=False):
        batch_size = shape_list(q)[0]
        q = self.Wq(q)
        k = self.Wk(k)
        v = self.Wv(v)
        q = self.split_into_heads(q, batch_size)
        k = self.split_into_heads(k, batch_size)
        v = self.split_into_heads(v, batch_size)
        if layer_past is not None:
            past_key, past_value = tf.unstack(layer_past, axis=0)
            k = tf.concat((past_key, k), axis=-2)
            v = tf.concat((past_value, v), axis=-2)
        if use_cache:
            present = tf.stack((k, v), axis=0)
        else:
            present = (None,)
        output = scaled_dot_product_attention(q, k, v, mask, attention_mask, head_mask)
        scaled_attention = tf.transpose(output[0], perm=[0, 2, 1, 3])
        attn = output[1]
        original_size_attention = tf.reshape(scaled_attention, (batch_size, -1, self.d_model_size))
        output = self.dense(original_size_attention)
        outputs = (output, present)
        if output_attentions:
            outputs = outputs + (attn,)
        return outputs
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "Wq", None) is not None:
            with tf.name_scope(self.Wq.name):
                self.Wq.build([None, None, self.d_model_size])
        if getattr(self, "Wk", None) is not None:
            with tf.name_scope(self.Wk.name):
                self.Wk.build([None, None, self.d_model_size])
        if getattr(self, "Wv", None) is not None:
            with tf.name_scope(self.Wv.name):
                self.Wv.build([None, None, self.d_model_size])
        if getattr(self, "dense", None) is not None:
            with tf.name_scope(self.dense.name):
                self.dense.build([None, None, self.d_model_size])
class TFPointWiseFeedForwardLayer(keras.layers.Layer):
    def __init__(self, d_model_size, dff, **kwargs):
        super().__init__(**kwargs)
        self.dense_0 = keras.layers.Dense(dff, activation="relu", name="0")
        self.dense_2 = keras.layers.Dense(d_model_size, name="2")
        self.d_model_size = d_model_size
        self.dff = dff
    def call(self, inputs, trainable=False):
        dense_0_output = self.dense_0(inputs)
        dense_2_output = self.dense_2(dense_0_output)
        return dense_2_output
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "dense_0", None) is not None:
            with tf.name_scope(self.dense_0.name):
                self.dense_0.build([None, None, self.d_model_size])
        if getattr(self, "dense_2", None) is not None:
            with tf.name_scope(self.dense_2.name):
                self.dense_2.build([None, None, self.dff])
class TFEncoderLayer(keras.layers.Layer):
    def __init__(
        self, d_model_size, num_heads, dff, rate=0.1, layer_norm_epsilon=1e-6, output_attentions=False, **kwargs
    ):
        super().__init__(**kwargs)
        self.output_attentions = output_attentions
        self.multi_head_attention = TFMultiHeadAttention(
            d_model_size, num_heads, output_attentions=self.output_attentions, name="multi_head_attention"
        )
        self.ffn = TFPointWiseFeedForwardLayer(d_model_size, dff, name="ffn")
        self.layernorm1 = keras.layers.LayerNormalization(epsilon=layer_norm_epsilon, name="layernorm1")
        self.layernorm2 = keras.layers.LayerNormalization(epsilon=layer_norm_epsilon, name="layernorm2")
        self.dropout1 = keras.layers.Dropout(rate)
        self.dropout2 = keras.layers.Dropout(rate)
        self.d_model_size = d_model_size
    def call(self, x, mask, layer_past, attention_mask, head_mask, use_cache, output_attentions, training=False):
        normed = self.layernorm1(x)
        attn_outputs = self.multi_head_attention(
            normed,
            normed,
            normed,
            mask,
            layer_past,
            attention_mask,
            head_mask,
            use_cache,
            output_attentions,
            training=training,
        )
        attn_output = attn_outputs[0]
        attn_output = self.dropout1(attn_output, training=training)
        out1 = x + attn_output
        out2 = self.layernorm2(out1)
        ffn_output = self.ffn(out2)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = out1 + ffn_output
        outputs = (out2,) + attn_outputs[1:]
        return outputs
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "multi_head_attention", None) is not None:
            with tf.name_scope(self.multi_head_attention.name):
                self.multi_head_attention.build(None)
        if getattr(self, "ffn", None) is not None:
            with tf.name_scope(self.ffn.name):
                self.ffn.build(None)
        if getattr(self, "layernorm1", None) is not None:
            with tf.name_scope(self.layernorm1.name):
                self.layernorm1.build([None, None, self.d_model_size])
        if getattr(self, "layernorm2", None) is not None:
            with tf.name_scope(self.layernorm2.name):
                self.layernorm2.build([None, None, self.d_model_size])
@keras_serializable
class TFCTRLMainLayer(keras.layers.Layer):
    config_class = CTRLConfig
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.output_hidden_states = config.output_hidden_states
        self.output_attentions = config.output_attentions
        self.use_cache = config.use_cache
        self.return_dict = config.use_return_dict
        self.d_model_size = config.n_embd
        self.num_layers = config.n_layer
        self.pos_encoding = positional_encoding(config.n_positions, self.d_model_size)
        self.w = keras.layers.Embedding(
            input_dim=config.vocab_size,
            output_dim=config.n_embd,
            embeddings_initializer=get_initializer(config.initializer_range),
            name="w",
        )
        self.dropout = keras.layers.Dropout(config.embd_pdrop)
        self.h = [
            TFEncoderLayer(
                config.n_embd,
                config.n_head,
                config.dff,
                config.resid_pdrop,
                config.layer_norm_epsilon,
                self.output_attentions,
                name=f"h_._{i}",
            )
            for i in range(config.n_layer)
        ]
        self.layernorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_epsilon, name="layernorm")
    def get_input_embeddings(self):
        return self.w
    def set_input_embeddings(self, new_embeddings):
        self.w = new_embeddings
    def _prune_heads(self, heads_to_prune):
        raise NotImplementedError
    @unpack_inputs
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        past_key_values: tuple[tuple[np.ndarray | tf.Tensor]] | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        use_cache: bool | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool | None = False,
    ) -> tuple | TFBaseModelOutputWithPast:
        if past_key_values is not None:
            if input_ids is not None:
                input_ids = input_ids[:, -1:]
            if inputs_embeds is not None:
                inputs_embeds = inputs_embeds[:, -1:]
            if token_type_ids is not None:
                token_type_ids = token_type_ids[:, -1:]
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = shape_list(input_ids)
            input_ids = tf.reshape(input_ids, [-1, input_shape[-1]])
        elif inputs_embeds is not None:
            input_shape = shape_list(inputs_embeds)[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")
        if past_key_values is None:
            past_length = 0
            past_key_values = [None] * len(self.h)
        else:
            past_length = shape_list(past_key_values[0][0])[-2]
        if position_ids is None:
            position_ids = tf.expand_dims(tf.range(past_length, input_shape[-1] + past_length, dtype=tf.int32), axis=0)
            position_ids = tf.tile(position_ids, [input_shape[0], 1])
        if attention_mask is not None:
            attention_mask = tf.reshape(attention_mask, (input_shape[0], 1, 1, input_shape[1] + past_length))
            one_cst = tf.constant(1.0)
            ten_thousand_cst = tf.constant(-10000.0)
            attention_mask = tf.cast(attention_mask, dtype=one_cst.dtype)
            attention_mask = tf.multiply(tf.subtract(one_cst, attention_mask), ten_thousand_cst)
        if head_mask is not None:
            raise NotImplementedError
        else:
            head_mask = [None] * self.num_layers
        if token_type_ids is not None:
            token_type_ids = tf.reshape(token_type_ids, [-1, shape_list(token_type_ids)[-1]])
            token_type_embeds = self.w(token_type_ids)
            token_type_embeds *= tf.math.sqrt(tf.cast(self.d_model_size, dtype=token_type_embeds.dtype))
        else:
            token_type_embeds = tf.constant(0.0)
        position_ids = tf.reshape(position_ids, [-1, shape_list(position_ids)[-1]])
        if inputs_embeds is None:
            check_embeddings_within_bounds(input_ids, self.w.input_dim)
            inputs_embeds = self.w(input_ids)
        seq_len = input_shape[-1]
        mask = 1 - tf.linalg.band_part(tf.ones((seq_len, seq_len)), -1, 0)
        inputs_embeds *= tf.math.sqrt(tf.cast(self.d_model_size, inputs_embeds.dtype))
        pos_embeds = tf.gather(self.pos_encoding, position_ids)
        pos_embeds = tf.cast(pos_embeds, dtype=token_type_embeds.dtype)
        hidden_states = inputs_embeds + pos_embeds + token_type_embeds
        hidden_states = self.dropout(hidden_states, training=training)
        output_shape = input_shape + [shape_list(hidden_states)[-1]]
        presents = () if use_cache else None
        all_hidden_states = () if output_hidden_states else None
        all_attentions = () if output_attentions else None
        for i, (h, layer_past) in enumerate(zip(self.h, past_key_values)):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (tf.reshape(hidden_states, output_shape),)
            outputs = h(
                hidden_states,
                mask,
                layer_past,
                attention_mask,
                head_mask[i],
                use_cache,
                output_attentions,
                training=training,
            )
            hidden_states, present = outputs[:2]
            if use_cache:
                presents = presents + (present,)
            if output_attentions:
                all_attentions = all_attentions + (outputs[2],)
        hidden_states = self.layernorm(hidden_states)
        hidden_states = tf.reshape(hidden_states, output_shape)
        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)
        if output_attentions:
            attention_output_shape = input_shape[:-1] + [-1] + shape_list(all_attentions[0])[-2:]
            all_attentions = tuple(tf.reshape(t, attention_output_shape) for t in all_attentions)
        if not return_dict:
            return tuple(v for v in [hidden_states, presents, all_hidden_states, all_attentions] if v is not None)
        return TFBaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=presents,
            hidden_states=all_hidden_states,
            attentions=all_attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "w", None) is not None:
            with tf.name_scope(self.w.name):
                self.w.build(None)
        if getattr(self, "layernorm", None) is not None:
            with tf.name_scope(self.layernorm.name):
                self.layernorm.build([None, None, self.config.n_embd])
        if getattr(self, "h", None) is not None:
            for layer in self.h:
                with tf.name_scope(layer.name):
                    layer.build(None)
class TFCTRLPreTrainedModel(TFPreTrainedModel):
    config_class = CTRLConfig
    base_model_prefix = "transformer"
@add_start_docstrings(
    "The bare CTRL Model transformer outputting raw hidden-states without any specific head on top.",
    CTRL_START_DOCSTRING,
)
class TFCTRLModel(TFCTRLPreTrainedModel):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.transformer = TFCTRLMainLayer(config, name="transformer")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(CTRL_INPUTS_DOCSTRING)
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFBaseModelOutputWithPast,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        past_key_values: tuple[tuple[np.ndarray | tf.Tensor]] | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        use_cache: bool | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool | None = False,
    ) -> tuple | TFBaseModelOutputWithPast:
        outputs = self.transformer(
            input_ids=input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
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
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name):
                self.transformer.build(None)
class TFCTRLBiasLayer(keras.layers.Layer):
    def __init__(self, shape, initializer, trainable, name, **kwargs):
        super().__init__(name=name, **kwargs)
        self.shape = shape
        self.initializer = initializer
        self.trainable = trainable
    def build(self, input_shape):
        self.bias = self.add_weight(
            name="bias", shape=self.shape, initializer=self.initializer, trainable=self.trainable
        )
        super().build(input_shape)
    def call(self, x):
        return x + self.bias
@add_start_docstrings(
,
    CTRL_START_DOCSTRING,
)
class TFCTRLLMHeadModel(TFCTRLPreTrainedModel, TFCausalLanguageModelingLoss):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.transformer = TFCTRLMainLayer(config, name="transformer")
        self.bias_layer = TFCTRLBiasLayer(
            name="lm_head", shape=[1, config.vocab_size], initializer="zeros", trainable=True
        )
    def get_output_embeddings(self):
        return self.get_input_embeddings()
    def set_output_embeddings(self, value):
        self.set_input_embeddings(value)
    def get_bias(self):
        return {"lm_head.bias": self.bias_layer.bias}
    def set_bias(self, value):
        vocab_size = value["lm_head.bias"].shape[-1]
        self.bias_layer = TFCTRLBiasLayer(
            name="final_logits_bias", shape=[1, vocab_size], initializer="zeros", trainable=True
        )
        self.bias_layer.build(None)
        self.bias_layer.bias.assign(value["lm_head.bias"])
    def prepare_inputs_for_generation(self, inputs, past_key_values=None, use_cache=None, **kwargs):
        token_type_ids = kwargs.get("token_type_ids")
        if past_key_values:
            inputs = tf.expand_dims(inputs[:, -1], -1)
            if token_type_ids is not None:
                token_type_ids = tf.expand_dims(token_type_ids[:, -1], -1)
        position_ids = kwargs.get("position_ids")
        attention_mask = kwargs.get("attention_mask")
        if attention_mask is not None and position_ids is None:
            position_ids = tf.math.cumsum(attention_mask, axis=-1, exclusive=True)
            if past_key_values:
                position_ids = tf.expand_dims(position_ids[:, -1], -1)
        return {
            "input_ids": inputs,
            "attention_mask": attention_mask,
            "position_ids": position_ids,
            "past_key_values": past_key_values,
            "use_cache": use_cache,
            "token_type_ids": token_type_ids,
        }
    @unpack_inputs
    @add_start_docstrings_to_model_forward(CTRL_INPUTS_DOCSTRING)
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFCausalLMOutputWithPast,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        past_key_values: tuple[tuple[np.ndarray | tf.Tensor]] | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        use_cache: bool | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> tuple | TFCausalLMOutputWithPast:
        transformer_outputs = self.transformer(
            input_ids=input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        hidden_states = transformer_outputs[0]
        logits = tf.matmul(hidden_states, self.transformer.w.weights, transpose_b=True)
        logits = self.bias_layer(logits)
        loss = None
        if labels is not None:
            shifted_logits = logits[:, :-1]
            labels = labels[:, 1:]
            loss = self.hf_compute_loss(labels, shifted_logits)
        if not return_dict:
            output = (logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return TFCausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=transformer_outputs.past_key_values,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name):
                self.transformer.build(None)
        if getattr(self, "bias_layer", None) is not None:
            with tf.name_scope(self.bias_layer.name):
                self.bias_layer.build(None)
@add_start_docstrings(
,
    CTRL_START_DOCSTRING,
)
class TFCTRLForSequenceClassification(TFCTRLPreTrainedModel, TFSequenceClassificationLoss):
    def __init__(self, config, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.classifier = keras.layers.Dense(
            config.num_labels,
            kernel_initializer=get_initializer(config.initializer_range),
            name="classifier",
            use_bias=False,
        )
        self.transformer = TFCTRLMainLayer(config, name="transformer")
        self.config = config
    def get_output_embeddings(self):
        logger.warning(
            "Sequence classification models do not have output embeddings. `.get_output_embeddings` will be removed "
            "in MEROAI v4.32."
        )
        return self.transformer.w
    @unpack_inputs
    @add_start_docstrings_to_model_forward(CTRL_INPUTS_DOCSTRING)
    @add_code_sample_docstrings(
        checkpoint=_CHECKPOINT_FOR_DOC,
        output_type=TFSequenceClassifierOutput,
        config_class=_CONFIG_FOR_DOC,
    )
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        past_key_values: tuple[tuple[np.ndarray | tf.Tensor]] | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        token_type_ids: np.ndarray | tf.Tensor | None = None,
        position_ids: np.ndarray | tf.Tensor | None = None,
        head_mask: np.ndarray | tf.Tensor | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        use_cache: bool | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> tuple | TFSequenceClassifierOutput:
        transformer_outputs = self.transformer(
            input_ids=input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        hidden_states = transformer_outputs[0]
        logits = self.classifier(hidden_states)
        logits_shape = shape_list(logits)
        batch_size = logits_shape[0]
        if self.config.pad_token_id is None:
            last_non_pad_token = tf.fill((batch_size,), value=logits_shape[1] - 1)
        else:
            if input_ids is not None:
                token_indices = tf.range(shape_list(input_ids)[-1])
                non_pad_mask = tf.cast(input_ids != self.config.pad_token_id, token_indices.dtype)
                last_non_pad_token = tf.reduce_max(token_indices * non_pad_mask, axis=-1)
            else:
                last_non_pad_token = tf.fill((batch_size,), value=logits_shape[1] - 1)
                logger.warning_once(
                    f"{self.__class__.__name__} will not detect padding tokens in `inputs_embeds`. Results may be "
                    "unexpected if using padding tokens in conjunction with `inputs_embeds.`"
                )
        loss = None
        pooled_logits = tf.gather(logits, last_non_pad_token, batch_dims=1, axis=1)
        if labels is not None:
            if self.config.pad_token_id is None and logits_shape[0] != 1:
                raise ValueError("Cannot handle batch sizes > 1 if no padding token is defined.")
            loss = self.hf_compute_loss(tf.reshape(labels, [-1]), tf.reshape(pooled_logits, [-1, self.num_labels]))
        if not return_dict:
            output = (pooled_logits,) + transformer_outputs[1:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutput(
            loss=loss,
            logits=pooled_logits,
            hidden_states=transformer_outputs.hidden_states,
            attentions=transformer_outputs.attentions,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "classifier", None) is not None:
            with tf.name_scope(self.classifier.name):
                self.classifier.build([None, None, self.config.n_embd])
        if getattr(self, "transformer", None) is not None:
            with tf.name_scope(self.transformer.name):
                self.transformer.build(None)
__all__ = ["TFCTRLForSequenceClassification", "TFCTRLLMHeadModel", "TFCTRLModel", "TFCTRLPreTrainedModel"]