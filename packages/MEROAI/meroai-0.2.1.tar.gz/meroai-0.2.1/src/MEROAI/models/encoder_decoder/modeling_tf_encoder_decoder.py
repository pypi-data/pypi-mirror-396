from __future__ import annotations
import inspect
import re
import warnings
import numpy as np
import tensorflow as tf
from ...configuration_utils import PretrainedConfig
from ...modeling_tf_outputs import TFBaseModelOutput, TFSeq2SeqLMOutput
from ...modeling_tf_utils import (
    TFCausalLanguageModelingLoss,
    TFModelInputType,
    TFPreTrainedModel,
    get_initializer,
    keras,
    unpack_inputs,
)
from ...tf_utils import shape_list
from ...utils import (
    ModelOutput,
    add_start_docstrings,
    add_start_docstrings_to_model_forward,
    logging,
    replace_return_docstrings,
)
from ..auto.configuration_auto import AutoConfig
from ..auto.modeling_tf_auto import TFAutoModel, TFAutoModelForCausalLM
from .configuration_encoder_decoder import EncoderDecoderConfig
logger = logging.get_logger(__name__)
_CONFIG_FOR_DOC = "EncoderDecoderConfig"
DEPRECATION_WARNING = (
    "Version v4.17.0 introduces a better way to train encoder-decoder models by computing the loss inside the"
    " encoder-decoder framework rather than in the decoder itself. You may observe training discrepancies if"
    " fine-tuning a model trained with versions anterior to 4.17.0. The decoder_input_ids are now created based on the"
    " labels, no need to pass them yourself anymore."
)
def shift_tokens_right(input_ids: tf.Tensor, pad_token_id: int, decoder_start_token_id: int):
    if pad_token_id is None:
        raise ValueError("Make sure to set the pad_token_id attribute of the model's configuration.")
    pad_token_id = tf.cast(pad_token_id, input_ids.dtype)
    if decoder_start_token_id is None:
        raise ValueError("Make sure to set the decoder_start_token_id attribute of the model's configuration.")
    decoder_start_token_id = tf.cast(decoder_start_token_id, input_ids.dtype)
    start_tokens = tf.fill((shape_list(input_ids)[0], 1), decoder_start_token_id)
    shifted_input_ids = tf.concat([start_tokens, input_ids[:, :-1]], -1)
    shifted_input_ids = tf.where(
        shifted_input_ids == -100, tf.fill(shape_list(shifted_input_ids), pad_token_id), shifted_input_ids
    )
    assert_gte0 = tf.debugging.assert_greater_equal(shifted_input_ids, tf.constant(0, dtype=input_ids.dtype))
    with tf.control_dependencies([assert_gte0]):
        shifted_input_ids = tf.identity(shifted_input_ids)
    return shifted_input_ids
@add_start_docstrings(ENCODER_DECODER_START_DOCSTRING)
class TFEncoderDecoderModel(TFPreTrainedModel, TFCausalLanguageModelingLoss):
    config_class = EncoderDecoderConfig
    base_model_prefix = "encoder_decoder"
    load_weight_prefix = "tf_encoder_decoder_model"
    def __init__(
        self,
        config: PretrainedConfig | None = None,
        encoder: TFPreTrainedModel | None = None,
        decoder: TFPreTrainedModel | None = None,
    ):
        if config is None and (encoder is None or decoder is None):
            raise ValueError("Either a configuration or an encoder and a decoder has to be provided.")
        if config is None:
            config = EncoderDecoderConfig.from_encoder_decoder_configs(encoder.config, decoder.config)
        else:
            if not isinstance(config, self.config_class):
                raise ValueError(f"config: {config} has to be of type {self.config_class}")
        if config.decoder.cross_attention_hidden_size is not None:
            if config.decoder.cross_attention_hidden_size != config.encoder.hidden_size:
                raise ValueError(
                    "If `cross_attention_hidden_size` is specified in the decoder's configuration, it has to be equal"
                    f" to the encoder's `hidden_size`. Got {config.decoder.cross_attention_hidden_size} for"
                    f" `config.decoder.cross_attention_hidden_size` and {config.encoder.hidden_size} for"
                    " `config.encoder.hidden_size`."
                )
        super().__init__(config)
        if encoder is None:
            encoder = TFAutoModel.from_config(config.encoder, name="encoder")
        if decoder is None:
            decoder = TFAutoModelForCausalLM.from_config(config.decoder, name="decoder")
        self.encoder = encoder
        self.decoder = decoder
        if self.encoder.config.to_dict() != self.config.encoder.to_dict():
            logger.warning(
                f"Config of the encoder: {self.encoder.__class__} is overwritten by shared encoder config:"
                f" {self.config.encoder}"
            )
        if self.decoder.config.to_dict() != self.config.decoder.to_dict():
            logger.warning(
                f"Config of the decoder: {self.decoder.__class__} is overwritten by shared decoder config:"
                f" {self.config.decoder}"
            )
        self.encoder.config = self.config.encoder
        self.decoder.config = self.config.decoder
        if (
            self.encoder.config.hidden_size != self.decoder.config.hidden_size
            and self.decoder.config.cross_attention_hidden_size is None
        ):
            self.enc_to_dec_proj = keras.layers.Dense(
                units=self.decoder.config.hidden_size,
                kernel_initializer=get_initializer(config.encoder.initializer_range),
                name="enc_to_dec_proj",
            )
        if self.encoder.get_output_embeddings() is not None:
            raise ValueError(
                f"The encoder {self.encoder} should not have a LM Head. Please use a model without LM Head"
            )
        decoder_signature = set(inspect.signature(self.decoder.call).parameters.keys())
        if "encoder_hidden_states" not in decoder_signature:
            raise ValueError(
                "The selected decoder is not prepared for the encoder hidden states to be passed. Please see the "
                "following discussion on GitHub: https://github.com/huggingface/MEROAI/issues/23350"
            )
    def get_encoder(self):
        return self.encoder
    def get_input_embeddings(self):
        return self.encoder.get_input_embeddings()
    def get_output_embeddings(self):
        return self.decoder.get_output_embeddings()
    def set_output_embeddings(self, new_embeddings):
        return self.decoder.set_output_embeddings(new_embeddings)
    def tf_to_pt_weight_rename(self, tf_weight):
        encoder_model_type = self.config.encoder.model_type
        if "encoder" in tf_weight and "decoder" not in tf_weight:
            return (re.sub(rf"encoder\.{encoder_model_type}\.", "encoder.", tf_weight),)
        else:
            return (tf_weight,)
    @classmethod
    def from_encoder_decoder_pretrained(
        cls,
        encoder_pretrained_model_name_or_path: str | None = None,
        decoder_pretrained_model_name_or_path: str | None = None,
        *model_args,
        **kwargs,
    ) -> TFPreTrainedModel:
        kwargs_encoder = {
            argument[len("encoder_") :]: value for argument, value in kwargs.items() if argument.startswith("encoder_")
        }
        kwargs_decoder = {
            argument[len("decoder_") :]: value for argument, value in kwargs.items() if argument.startswith("decoder_")
        }
        for key in kwargs_encoder:
            del kwargs["encoder_" + key]
        for key in kwargs_decoder:
            del kwargs["decoder_" + key]
        encoder = kwargs_encoder.pop("model", None)
        if encoder is None:
            if encoder_pretrained_model_name_or_path is None:
                raise ValueError(
                    "If `encoder_model` is not defined as an argument, a `encoder_pretrained_model_name_or_path` has "
                    "to be defined."
                )
            if "config" not in kwargs_encoder:
                encoder_config = AutoConfig.from_pretrained(encoder_pretrained_model_name_or_path)
                if encoder_config.is_decoder is True or encoder_config.add_cross_attention is True:
                    logger.info(
                        f"Initializing {encoder_pretrained_model_name_or_path} as a encoder model "
                        "from a decoder model. Cross-attention and causal mask are disabled."
                    )
                    encoder_config.is_decoder = False
                    encoder_config.add_cross_attention = False
                kwargs_encoder["config"] = encoder_config
            kwargs_encoder["name"] = "encoder"
            kwargs_encoder["load_weight_prefix"] = cls.load_weight_prefix
            encoder = TFAutoModel.from_pretrained(encoder_pretrained_model_name_or_path, *model_args, **kwargs_encoder)
        decoder = kwargs_decoder.pop("model", None)
        if decoder is None:
            if decoder_pretrained_model_name_or_path is None:
                raise ValueError(
                    "If `decoder_model` is not defined as an argument, a `decoder_pretrained_model_name_or_path` has "
                    "to be defined."
                )
            if "config" not in kwargs_decoder:
                decoder_config = AutoConfig.from_pretrained(decoder_pretrained_model_name_or_path)
                if decoder_config.is_decoder is False or decoder_config.add_cross_attention is False:
                    logger.info(
                        f"Initializing {decoder_pretrained_model_name_or_path} as a decoder model. Cross attention"
                        f" layers are added to {decoder_pretrained_model_name_or_path} and randomly initialized if"
                        f" {decoder_pretrained_model_name_or_path}'s architecture allows for cross attention layers."
                    )
                    decoder_config.is_decoder = True
                    decoder_config.add_cross_attention = True
                kwargs_decoder["config"] = decoder_config
            if kwargs_decoder["config"].is_decoder is False or kwargs_decoder["config"].add_cross_attention is False:
                logger.warning(
                    f"Decoder model {decoder_pretrained_model_name_or_path} is not initialized as a decoder. "
                    f"In order to initialize {decoder_pretrained_model_name_or_path} as a decoder, "
                    "make sure that the attributes `is_decoder` and `add_cross_attention` of `decoder_config` "
                    "passed to `.from_encoder_decoder_pretrained(...)` are set to `True` or do not pass a "
                    "`decoder_config` to `.from_encoder_decoder_pretrained(...)`"
                )
            kwargs_decoder["name"] = "decoder"
            kwargs_decoder["load_weight_prefix"] = cls.load_weight_prefix
            decoder = TFAutoModelForCausalLM.from_pretrained(decoder_pretrained_model_name_or_path, **kwargs_decoder)
        if encoder.name != "encoder":
            raise ValueError("encoder model must be created with the name `encoder`.")
        if decoder.name != "decoder":
            raise ValueError("decoder model must be created with the name `decoder`.")
        config = EncoderDecoderConfig.from_encoder_decoder_configs(encoder.config, decoder.config, **kwargs)
        return cls(encoder=encoder, decoder=decoder, config=config)
    @unpack_inputs
    @add_start_docstrings_to_model_forward(ENCODER_DECODER_INPUTS_DOCSTRING.format("batch_size, sequence_length"))
    @replace_return_docstrings(output_type=TFSeq2SeqLMOutput, config_class=_CONFIG_FOR_DOC)
    def call(
        self,
        input_ids: TFModelInputType | None = None,
        attention_mask: np.ndarray | tf.Tensor | None = None,
        decoder_input_ids: np.ndarray | tf.Tensor | None = None,
        decoder_attention_mask: np.ndarray | tf.Tensor | None = None,
        encoder_outputs: np.ndarray | tf.Tensor | None = None,
        past_key_values: tuple[tuple[tf.Tensor]] | None = None,
        inputs_embeds: np.ndarray | tf.Tensor | None = None,
        decoder_inputs_embeds: np.ndarray | tf.Tensor | None = None,
        labels: np.ndarray | tf.Tensor | None = None,
        use_cache: bool | None = None,
        output_attentions: bool | None = None,
        output_hidden_states: bool | None = None,
        return_dict: bool | None = None,
        training: bool = False,
        **kwargs,
    ) -> TFSeq2SeqLMOutput | tuple[tf.Tensor]:
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        kwargs_encoder = {argument: value for argument, value in kwargs.items() if not argument.startswith("decoder_")}
        kwargs_decoder = {
            argument[len("decoder_") :]: value for argument, value in kwargs.items() if argument.startswith("decoder_")
        }
        if encoder_outputs is not None:
            if return_dict and not isinstance(encoder_outputs, ModelOutput):
                raise ValueError(
                    "If `return_dict=True` and `encoder_outputs` is provided, it should be an instance of "
                    f"`ModelOutput`. Got an instance {type(encoder_outputs)} for `encoder_outputs`."
                )
        if encoder_outputs is None:
            encoder_inputs = {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "inputs_embeds": inputs_embeds,
                "output_attentions": output_attentions,
                "output_hidden_states": output_hidden_states,
                "return_dict": return_dict,
                "training": training,
            }
            encoder_inputs.update(kwargs_encoder)
            if "labels" in encoder_inputs:
                labels = encoder_inputs.pop("labels")
            if "decoder_input_ids" in encoder_inputs:
                decoder_input_ids = encoder_inputs.pop("decoder_input_ids")
            if "decoder_attention_mask" in encoder_inputs:
                decoder_attention_mask = encoder_inputs.pop("decoder_attention_mask")
            encoder_outputs = self.encoder(**encoder_inputs)
        encoder_hidden_states = encoder_outputs[0]
        if (
            self.encoder.config.hidden_size != self.decoder.config.hidden_size
            and self.decoder.config.cross_attention_hidden_size is None
        ):
            encoder_hidden_states = self.enc_to_dec_proj(encoder_hidden_states)
        if (labels is not None) and (decoder_input_ids is None and decoder_inputs_embeds is None):
            decoder_input_ids = shift_tokens_right(
                labels, self.config.pad_token_id, self.config.decoder_start_token_id
            )
        decoder_inputs = {
            "input_ids": decoder_input_ids,
            "attention_mask": decoder_attention_mask,
            "encoder_hidden_states": encoder_hidden_states,
            "encoder_attention_mask": attention_mask,
            "inputs_embeds": decoder_inputs_embeds,
            "output_attentions": output_attentions,
            "output_hidden_states": output_hidden_states,
            "use_cache": use_cache,
            "past_key_values": past_key_values,
            "return_dict": return_dict,
            "training": training,
        }
        decoder_inputs.update(kwargs_decoder)
        decoder_outputs = self.decoder(**decoder_inputs)
        logits = decoder_outputs[0]
        loss = None
        if labels is not None:
            warnings.warn(DEPRECATION_WARNING, FutureWarning)
            loss = self.hf_compute_loss(labels, logits)
        if not return_dict:
            past_key_values = None
            if use_cache:
                past_key_values = decoder_outputs[1]
            start_index = sum([1 if x is not None else 0 for x in (loss, logits, past_key_values)])
            if not isinstance(encoder_outputs, tuple):
                encoder_outputs = encoder_outputs.to_tuple()
            output = (loss, logits, past_key_values) + decoder_outputs[start_index:] + encoder_outputs
            output = tuple(x for x in output if x is not None)
            return output
        return TFSeq2SeqLMOutput(
            loss=loss,
            logits=decoder_outputs.logits,
            past_key_values=decoder_outputs.past_key_values,
            decoder_hidden_states=decoder_outputs.hidden_states,
            decoder_attentions=decoder_outputs.attentions,
            cross_attentions=decoder_outputs.cross_attentions,
            encoder_last_hidden_state=encoder_outputs.last_hidden_state,
            encoder_hidden_states=encoder_outputs.hidden_states,
            encoder_attentions=encoder_outputs.attentions,
        )
    def prepare_inputs_for_generation(
        self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, encoder_outputs=None, **kwargs
    ):
        decoder_inputs = self.decoder.prepare_inputs_for_generation(input_ids, past_key_values=past_key_values)
        decoder_attention_mask = decoder_inputs.get("attention_mask", None)
        past_key_values = decoder_inputs.get("past_key_values")
        if past_key_values is None:
            past_key_values = decoder_inputs.get("past")
        input_dict = {
            "input_ids": None,
            "attention_mask": attention_mask,
            "decoder_attention_mask": decoder_attention_mask,
            "decoder_input_ids": decoder_inputs["input_ids"],
            "encoder_outputs": TFBaseModelOutput(last_hidden_state=encoder_outputs[0]),
            "past_key_values": past_key_values,
            "use_cache": use_cache,
        }
        return input_dict
    def prepare_decoder_input_ids_from_labels(self, labels: tf.Tensor):
        return shift_tokens_right(labels, self.config.pad_token_id, self.config.decoder_start_token_id)
    def resize_token_embeddings(self, *args, **kwargs):
        raise NotImplementedError(
            "Resizing the embedding layers via the TFEncoderDecoderModel directly is not supported.Please use the"
            " respective methods of the wrapped objects (model.encoder.resize_token_embeddings(...) or"
            " model.decoder.resize_token_embeddings(...))"
        )
    def _reorder_cache(self, past, beam_idx):
        return self.decoder._reorder_cache(past, beam_idx)
    def build(self, input_shape=None):
        if self.built:
            return
        self.built = True
        if getattr(self, "enc_to_dec_proj", None) is not None:
            with tf.name_scope(self.enc_to_dec_proj.name):
                self.enc_to_dec_proj.build([None, None, self.encoder.config.hidden_size])
        if getattr(self, "encoder", None) is not None:
            with tf.name_scope(self.encoder.name):
                self.encoder.build(None)
        if getattr(self, "decoder", None) is not None:
            with tf.name_scope(self.decoder.name):
                self.decoder.build(None)
__all__ = ["TFEncoderDecoderModel"]