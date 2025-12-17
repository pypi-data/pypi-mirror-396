from __future__ import annotations
import numpy as np
import tensorflow as tf
from ...activations_tf import get_tf_activation
from ...modeling_tf_outputs import TFBaseModelOutput, TFBaseModelOutputWithPooling, TFSequenceClassifierOutput
from ...modeling_tf_utils import (
    TFModelInputType,
    TFPreTrainedModel,
    TFSequenceClassificationLoss,
    get_initializer,
    keras,
    keras_serializable,
    unpack_inputs,
)
from ...tf_utils import shape_list
from ...utils import add_start_docstrings, add_start_docstrings_to_model_forward, logging, replace_return_docstrings
from .configuration_convnext import ConvNextConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "ConvNextConfig"
_CHECKPOINT_FOR_DOC = "facebook/convnext-tiny-224"
class TFConvNextDropPath(keras.layers.Layer):
    def __init__(self, drop_path: float, **kwargs):
        super().__init__(**kwargs)
        self.drop_path = drop_path
    def call(self, x: tf.Tensor, training=None):
        if training:
            keep_prob = 1 - self.drop_path
            shape = (tf.shape(x)[0],) + (1,) * (len(tf.shape(x)) - 1)
            random_tensor = keep_prob + tf.random.uniform(shape, 0, 1)
            random_tensor = tf.floor(random_tensor)
            return (x / keep_prob) * random_tensor
        return x
class TFConvNextEmbeddings(keras.layers.Layer):
    def __init__(self, config: ConvNextConfig, **kwargs):
        super().__init__(**kwargs)
        self.patch_embeddings = keras.layers.Conv2D(
            filters=config.hidden_sizes[0],
            kernel_size=config.patch_size,
            strides=config.patch_size,
            name="patch_embeddings",
            kernel_initializer=get_initializer(config.initializer_range),
            bias_initializer=keras.initializers.Zeros(),
        )
        self.layernorm = keras.layers.LayerNormalization(epsilon=1e-6, name="layernorm")
        self.num_channels = config.num_channels
        self.config = config
    def call(self, pixel_values):
        if isinstance(pixel_values, dict):
            pixel_values = pixel_values["pixel_values"]
        tf.debugging.assert_equal(
            shape_list(pixel_values)[1],
            self.num_channels,
            message="Make sure that the channel dimension of the pixel values match with the one set in the configuration.",
        )
        pixel_values = tf.transpose(pixel_values, perm=(0, 2, 3, 1))
        embeddings = self.patch_embeddings(pixel_values)
        embeddings = self.layernorm(embeddings)
        return embeddings
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "patch_embeddings", None) is not None:
            with tf.name_scope(self.patch_embeddings.name):
                self.patch_embeddings.build([None, None, None, self.config.num_channels])
        if getattr(self, "layernorm", None) is not None:
            with tf.name_scope(self.layernorm.name):
                self.layernorm.build([None, None, None, self.config.hidden_sizes[0]])
class TFConvNextLayer(keras.layers.Layer):
    def __init__(self, config, dim, drop_path=0.0, **kwargs):
        super().__init__(**kwargs)
        self.dim = dim
        self.config = config
        self.dwconv = keras.layers.Conv2D(
            filters=dim,
            kernel_size=7,
            padding="same",
            groups=dim,
            kernel_initializer=get_initializer(config.initializer_range),
            bias_initializer="zeros",
            name="dwconv",
        )
        self.layernorm = keras.layers.LayerNormalization(
            epsilon=1e-6,
            name="layernorm",
        )
        self.pwconv1 = keras.layers.Dense(
            units=4 * dim,
            kernel_initializer=get_initializer(config.initializer_range),
            bias_initializer="zeros",
            name="pwconv1",
        )
        self.act = get_tf_activation(config.hidden_act)
        self.pwconv2 = keras.layers.Dense(
            units=dim,
            kernel_initializer=get_initializer(config.initializer_range),
            bias_initializer="zeros",
            name="pwconv2",
        )
        self.drop_path = (
            TFConvNextDropPath(drop_path, name="drop_path")
            if drop_path > 0.0
            else keras.layers.Activation("linear", name="drop_path")
        )
    def build(self, input_shape: tf.TensorShape = None):
        self.layer_scale_parameter = (
            self.add_weight(
                shape=(self.dim,),
                initializer=keras.initializers.Constant(value=self.config.layer_scale_init_value),
                trainable=True,
                name="layer_scale_parameter",
            )
            if self.config.layer_scale_init_value > 0
            else None
        )
        if self.built:
            return
        self.built = True
        if getattr(self, "dwconv", None) is not None:
            with tf.name_scope(self.dwconv.name):
                self.dwconv.build([None, None, None, self.dim])
        if getattr(self, "layernorm", None) is not None:
            with tf.name_scope(self.layernorm.name):
                self.layernorm.build([None, None, None, self.dim])
        if getattr(self, "pwconv1", None) is not None:
            with tf.name_scope(self.pwconv1.name):
                self.pwconv1.build([None, None, self.dim])
        if getattr(self, "pwconv2", None) is not None:
            with tf.name_scope(self.pwconv2.name):
                self.pwconv2.build([None, None, 4 * self.dim])
        if getattr(self, "drop_path", None) is not None:
            with tf.name_scope(self.drop_path.name):
                self.drop_path.build(None)
    def call(self, hidden_states, training=False):
        input = hidden_states
        x = self.dwconv(hidden_states)
        x = self.layernorm(x)
        x = self.pwconv1(x)
        x = self.act(x)
        x = self.pwconv2(x)
        if self.layer_scale_parameter is not None:
            x = self.layer_scale_parameter * x
        x = input + self.drop_path(x, training=training)
        return x
class TFConvNextStage(keras.layers.Layer):
    def __init__(
        self,
        config: ConvNextConfig,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 2,
        stride: int = 2,
        depth: int = 2,
        drop_path_rates: list[float] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if in_channels != out_channels or stride > 1:
            self.downsampling_layer = [
                keras.layers.LayerNormalization(
                    epsilon=1e-6,
                    name="downsampling_layer.0",
                ),
                keras.layers.Conv2D(
                    filters=out_channels,
                    kernel_size=kernel_size,
                    strides=stride,
                    kernel_initializer=get_initializer(config.initializer_range),
                    bias_initializer=keras.initializers.Zeros(),
                    name="downsampling_layer.1",
                ),
            ]
        else:
            self.downsampling_layer = [tf.identity]
        drop_path_rates = drop_path_rates or [0.0] * depth
        self.layers = [
            TFConvNextLayer(
                config,
                dim=out_channels,
                drop_path=drop_path_rates[j],
                name=f"layers.{j}",
            )
            for j in range(depth)
        ]
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = stride
    def call(self, hidden_states):
        for layer in self.downsampling_layer:
            hidden_states = layer(hidden_states)
        for layer in self.layers:
            hidden_states = layer(hidden_states)
        return hidden_states
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "layers", None) is not None:
            for layer in self.layers:
                with tf.name_scope(layer.name):
                    layer.build(None)
        if self.in_channels != self.out_channels or self.stride > 1:
            with tf.name_scope(self.downsampling_layer[0].name):
                self.downsampling_layer[0].build([None, None, None, self.in_channels])
            with tf.name_scope(self.downsampling_layer[1].name):
                self.downsampling_layer[1].build([None, None, None, self.in_channels])
class TFConvNextEncoder(keras.layers.Layer):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.stages = []
        drop_path_rates = tf.linspace(0.0, config.drop_path_rate, sum(config.depths))
        drop_path_rates = tf.split(drop_path_rates, config.depths)
        drop_path_rates = [x.numpy().tolist() for x in drop_path_rates]
        prev_chs = config.hidden_sizes[0]
        for i in range(config.num_stages):
            out_chs = config.hidden_sizes[i]
            stage = TFConvNextStage(
                config,
                in_channels=prev_chs,
                out_channels=out_chs,
                stride=2 if i > 0 else 1,
                depth=config.depths[i],
                drop_path_rates=drop_path_rates[i],
                name=f"stages.{i}",
            )
            self.stages.append(stage)
            prev_chs = out_chs
    def call(self, hidden_states, output_hidden_states=False, return_dict=True):
        all_hidden_states = () if output_hidden_states else None
        for i, layer_module in enumerate(self.stages):
            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)
            hidden_states = layer_module(hidden_states)
        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)
        if not return_dict:
            return tuple(v for v in [hidden_states, all_hidden_states] if v is not None)
        return TFBaseModelOutput(last_hidden_state=hidden_states, hidden_states=all_hidden_states)
    def build(self, input_shape=None):
        for stage in self.stages:
            with tf.name_scope(stage.name):
                stage.build(None)
@keras_serializable
class TFConvNextMainLayer(keras.layers.Layer):
    config_class = ConvNextConfig
    def __init__(self, config: ConvNextConfig, add_pooling_layer: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.embeddings = TFConvNextEmbeddings(config, name="embeddings")
        self.encoder = TFConvNextEncoder(config, name="encoder")
        self.layernorm = keras.layers.LayerNormalization(epsilon=config.layer_norm_eps, name="layernorm")
        self.pooler = keras.layers.GlobalAvgPool2D(data_format="channels_first") if add_pooling_layer else None
    @unpack_inputs
    def call(
        self,
        pixel_values: TFModelInputType | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFBaseModelOutputWithPooling | tuple[tf.Tensor]:
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None:
            raise ValueError("You have to specify pixel_values")
        embedding_output = self.embeddings(pixel_values, training=training)
        encoder_outputs = self.encoder(
            embedding_output,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        last_hidden_state = encoder_outputs[0]
        last_hidden_state = tf.transpose(last_hidden_state, perm=(0, 3, 1, 2))
        pooled_output = self.layernorm(self.pooler(last_hidden_state))
        if output_hidden_states:
            hidden_states = tuple(tf.transpose(h, perm=(0, 3, 1, 2)) for h in encoder_outputs[1])
        if not return_dict:
            hidden_states = hidden_states if output_hidden_states else ()
            return (last_hidden_state, pooled_output) + hidden_states
        return TFBaseModelOutputWithPooling(
            last_hidden_state=last_hidden_state,
            pooler_output=pooled_output,
            hidden_states=hidden_states if output_hidden_states else encoder_outputs.hidden_states,
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
        if getattr(self, "layernorm", None) is not None:
            with tf.name_scope(self.layernorm.name):
                self.layernorm.build([None, self.config.hidden_sizes[-1]])
class TFConvNextPreTrainedModel(TFPreTrainedModel):
    config_class = ConvNextConfig
    base_model_prefix = "convnext"
    main_input_name = "pixel_values"
@add_start_docstrings(
    "The bare ConvNext model outputting raw features without any specific head on top.",
    CONVNEXT_START_DOCSTRING,
)
class TFConvNextModel(TFConvNextPreTrainedModel):
    def __init__(self, config, *inputs, add_pooling_layer=True, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.convnext = TFConvNextMainLayer(config, add_pooling_layer=add_pooling_layer, name="convnext")
    @unpack_inputs
    @add_start_docstrings_to_model_forward(CONVNEXT_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=TFBaseModelOutputWithPooling, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        pixel_values: TFModelInputType | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
    ) -> TFBaseModelOutputWithPooling | tuple[tf.Tensor]:
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None:
            raise ValueError("You have to specify pixel_values")
        outputs = self.convnext(
            pixel_values=pixel_values,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        if not return_dict:
            return (outputs[0],) + outputs[1:]
        return TFBaseModelOutputWithPooling(
            last_hidden_state=outputs.last_hidden_state,
            pooler_output=outputs.pooler_output,
            hidden_states=outputs.hidden_states,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "convnext", None) is not None:
            with tf.name_scope(self.convnext.name):
                self.convnext.build(None)
@add_start_docstrings(
,
    CONVNEXT_START_DOCSTRING,
)
class TFConvNextForImageClassification(TFConvNextPreTrainedModel, TFSequenceClassificationLoss):
    def __init__(self, config: ConvNextConfig, *inputs, **kwargs):
        super().__init__(config, *inputs, **kwargs)
        self.num_labels = config.num_labels
        self.convnext = TFConvNextMainLayer(config, name="convnext")
        self.classifier = keras.layers.Dense(
            units=config.num_labels,
            kernel_initializer=get_initializer(config.initializer_range),
            bias_initializer="zeros",
            name="classifier",
        )
        self.config = config
    @unpack_inputs
    @add_start_docstrings_to_model_forward(CONVNEXT_INPUTS_DOCSTRING)
    @replace_return_docstrings(output_type=TFSequenceClassifierOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        pixel_values: TFModelInputType | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        training: bool | None = False,
    ) -> TFSequenceClassifierOutput | tuple[tf.Tensor]:
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        if pixel_values is None:
            raise ValueError("You have to specify pixel_values")
        outputs = self.convnext(
            pixel_values,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            training=training,
        )
        pooled_output = outputs.pooler_output if return_dict else outputs[1]
        logits = self.classifier(pooled_output)
        loss = None if labels is None else self.hf_compute_loss(labels=labels, logits=logits)
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TFSequenceClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
        )
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "convnext", None) is not None:
            with tf.name_scope(self.convnext.name):
                self.convnext.build(None)
        if getattr(self, "classifier", None) is not None:
            if hasattr(self.classifier, "name"):
                with tf.name_scope(self.classifier.name):
                    self.classifier.build([None, None, self.config.hidden_sizes[-1]])
__all__ = ["TFConvNextForImageClassification", "TFConvNextModel", "TFConvNextPreTrainedModel"]