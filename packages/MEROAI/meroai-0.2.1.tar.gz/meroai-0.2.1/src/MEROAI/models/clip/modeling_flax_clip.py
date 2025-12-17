from typing import Any, Optional, Union
import flax
import flax.linen as nn
import jax
import jax.numpy as jnp
from flax.core.frozen_dict import FrozenDict, freeze, unfreeze
from flax.linen import combine_masks, make_causal_mask
from flax.linen.attention import dot_product_attention_weights
from flax.traverse_util import flatten_dict, unflatten_dict
from jax import lax
from ...modeling_flax_outputs import FlaxBaseModelOutput, FlaxBaseModelOutputWithPooling
from ...modeling_flax_utils import (
    ACT2FN,
    FlaxPreTrainedModel,
    append_replace_return_docstrings,
    overwrite_call_docstring,
)
from ...utils import ModelOutput, add_start_docstrings, logging
from .configuration_clip import CLIPConfig, CLIPTextConfig, CLIPVisionConfig
logger = logging.get_logger(__name__)
@flax.struct.dataclass
class FlaxCLIPTextModelOutput(ModelOutput):
    text_embeds: jnp.ndarray = None
    last_hidden_state: jnp.ndarray = None
    hidden_states: Optional[tuple[jnp.ndarray, ...]] = None
    attentions: Optional[tuple[jnp.ndarray, ...]] = None
@flax.struct.dataclass
class FlaxCLIPOutput(ModelOutput):
    logits_per_image: jnp.ndarray = None
    logits_per_text: jnp.ndarray = None
    text_embeds: jnp.ndarray = None
    image_embeds: jnp.ndarray = None
    text_model_output: FlaxBaseModelOutputWithPooling = None
    vision_model_output: FlaxBaseModelOutputWithPooling = None
    def to_tuple(self) -> tuple[Any]:
        return tuple(
            self[k] if k not in ["text_model_output", "vision_model_output"] else getattr(self, k).to_tuple()
            for k in self.keys()
        )
class FlaxCLIPVisionEmbeddings(nn.Module):
    config: CLIPVisionConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        embed_dim = self.config.hidden_size
        image_size = self.config.image_size
        patch_size = self.config.patch_size
        self.class_embedding = self.param("class_embedding", jax.nn.initializers.normal(stddev=0.02), (embed_dim,))
        self.patch_embedding = nn.Conv(
            embed_dim,
            kernel_size=(patch_size, patch_size),
            strides=(patch_size, patch_size),
            padding="VALID",
            use_bias=False,
            dtype=self.dtype,
            kernel_init=jax.nn.initializers.normal(),
        )
        self.num_patches = (image_size // patch_size) ** 2
        num_positions = self.num_patches + 1
        self.position_embedding = nn.Embed(num_positions, embed_dim, embedding_init=jax.nn.initializers.normal())
        self.position_ids = jnp.expand_dims(jnp.arange(0, num_positions, dtype="i4"), axis=0)
    def __call__(self, pixel_values):
        patch_embeds = self.patch_embedding(pixel_values)
        batch_size, height, width, channels = patch_embeds.shape
        patch_embeds = jnp.reshape(patch_embeds, (batch_size, height * width, channels))
        class_embeds = jnp.expand_dims(self.class_embedding, axis=(0, 1))
        class_embeds = jnp.tile(class_embeds, (batch_size, 1, 1))
        embeddings = jnp.concatenate([class_embeds, patch_embeds], axis=1)
        embeddings = embeddings + self.position_embedding(self.position_ids)
        return embeddings
class FlaxCLIPTextEmbeddings(nn.Module):
    config: CLIPTextConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        embed_dim = self.config.hidden_size
        self.token_embedding = nn.Embed(self.config.vocab_size, embed_dim, embedding_init=jax.nn.initializers.normal())
        self.position_embedding = nn.Embed(
            self.config.max_position_embeddings, embed_dim, embedding_init=jax.nn.initializers.normal()
        )
        self.position_ids = jnp.expand_dims(
            jnp.arange(0, self.config.max_position_embeddings, dtype="i4"), axis=(0, 1)
        )
    def __call__(self, input_ids, position_ids):
        input_embeds = self.token_embedding(input_ids.astype("i4"))
        position_embeds = self.position_embedding(position_ids.astype("i4"))
        embeddings = input_embeds + position_embeds
        return embeddings
class FlaxCLIPAttention(nn.Module):
    config: Union[CLIPTextConfig, CLIPVisionConfig]
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.embed_dim = self.config.hidden_size
        self.num_heads = self.config.num_attention_heads
        self.head_dim = self.embed_dim // self.num_heads
        if self.head_dim * self.num_heads != self.embed_dim:
            raise ValueError(
                f"embed_dim must be divisible by num_heads (got `embed_dim`: {self.embed_dim} and `num_heads`:"
                f" {self.num_heads})."
            )
        self.scale = self.head_dim**-0.5
        self.dropout = self.config.attention_dropout
        self.k_proj = nn.Dense(self.embed_dim, dtype=self.dtype, kernel_init=jax.nn.initializers.normal(0.01))
        self.v_proj = nn.Dense(self.embed_dim, dtype=self.dtype, kernel_init=jax.nn.initializers.normal(0.01))
        self.q_proj = nn.Dense(self.embed_dim, dtype=self.dtype, kernel_init=jax.nn.initializers.normal(0.01))
        self.out_proj = nn.Dense(self.embed_dim, dtype=self.dtype, kernel_init=jax.nn.initializers.normal(0.01))
        self.causal = isinstance(self.config, CLIPTextConfig)
        if self.causal:
            self.causal_mask = make_causal_mask(jnp.ones((1, self.config.max_position_embeddings), dtype="i4"))
    def _split_heads(self, hidden_states):
        return hidden_states.reshape(hidden_states.shape[:2] + (self.num_heads, self.head_dim))
    def _merge_heads(self, hidden_states):
        return hidden_states.reshape(hidden_states.shape[:2] + (self.embed_dim,))
    def __call__(
        self,
        hidden_states,
        attention_mask=None,
        deterministic: bool = True,
        output_attentions: bool = False,
    ):
        query = self.q_proj(hidden_states)
        key = self.k_proj(hidden_states)
        value = self.v_proj(hidden_states)
        query = self._split_heads(query)
        key = self._split_heads(key)
        value = self._split_heads(value)
        causal_attention_mask = None
        if self.causal:
            query_length, key_length = query.shape[1], key.shape[1]
            causal_attention_mask = self.causal_mask[:, :, key_length - query_length : key_length, :key_length]
        if attention_mask is not None and causal_attention_mask is not None:
            attention_mask = jnp.expand_dims(attention_mask, axis=(-3, -2))
            attention_mask = combine_masks(attention_mask, causal_attention_mask, dtype="i4")
        elif causal_attention_mask is not None:
            attention_mask = causal_attention_mask
        elif attention_mask is not None:
            attention_mask = jnp.expand_dims(attention_mask, axis=(-3, -2))
        if attention_mask is not None:
            attention_bias = lax.select(
                attention_mask > 0,
                jnp.full(attention_mask.shape, 0.0).astype(self.dtype),
                jnp.full(attention_mask.shape, jnp.finfo(self.dtype).min).astype(self.dtype),
            )
        else:
            attention_bias = None
        dropout_rng = None
        if not deterministic and self.dropout > 0.0:
            dropout_rng = self.make_rng("dropout")
        attn_weights = dot_product_attention_weights(
            query,
            key,
            bias=attention_bias,
            dropout_rng=dropout_rng,
            dropout_rate=self.dropout,
            deterministic=deterministic,
            dtype=self.dtype,
            precision=None,
        )
        attn_output = jnp.einsum("...hqk,...khd->...qhd", attn_weights, value)
        attn_output = self._merge_heads(attn_output)
        attn_output = self.out_proj(attn_output)
        outputs = (attn_output, attn_weights) if output_attentions else (attn_output,)
        return outputs
class FlaxCLIPMLP(nn.Module):
    config: Union[CLIPTextConfig, CLIPVisionConfig]
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.activation_fn = ACT2FN[self.config.hidden_act]
        self.fc1 = nn.Dense(
            self.config.intermediate_size,
            dtype=self.dtype,
            kernel_init=jax.nn.initializers.normal(0.01),
        )
        self.fc2 = nn.Dense(self.config.hidden_size, dtype=self.dtype, kernel_init=jax.nn.initializers.normal(0.01))
    def __call__(self, hidden_states):
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.activation_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        return hidden_states
class FlaxCLIPEncoderLayer(nn.Module):
    config: Union[CLIPTextConfig, CLIPVisionConfig]
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.self_attn = FlaxCLIPAttention(self.config, dtype=self.dtype)
        self.layer_norm1 = nn.LayerNorm(epsilon=self.config.layer_norm_eps, dtype=self.dtype)
        self.mlp = FlaxCLIPMLP(self.config, dtype=self.dtype)
        self.layer_norm2 = nn.LayerNorm(epsilon=self.config.layer_norm_eps, dtype=self.dtype)
    def __call__(
        self,
        hidden_states,
        attention_mask,
        deterministic: bool = True,
        output_attentions: bool = False,
    ):
        residual = hidden_states
        hidden_states = self.layer_norm1(hidden_states)
        attn_outputs = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            deterministic=deterministic,
            output_attentions=output_attentions,
        )
        hidden_states = attn_outputs[0]
        hidden_states = residual + hidden_states
        residual = hidden_states
        hidden_states = self.layer_norm2(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states
        outputs = (hidden_states,)
        if output_attentions:
            outputs += attn_outputs[1:]
        return outputs
class FlaxCLIPLayerCollection(nn.Module):
    config: Union[CLIPTextConfig, CLIPVisionConfig]
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.layers = [
            FlaxCLIPEncoderLayer(self.config, name=str(i), dtype=self.dtype)
            for i in range(self.config.num_hidden_layers)
        ]
    def __call__(
        self,
        hidden_states,
        attention_mask=None,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        all_attentions = () if output_attentions else None
        all_hidden_states = () if output_hidden_states else None
        for layer in self.layers:
            if output_hidden_states:
                all_hidden_states += (hidden_states,)
            layer_outputs = layer(
                hidden_states, attention_mask, deterministic=deterministic, output_attentions=output_attentions
            )
            hidden_states = layer_outputs[0]
            if output_attentions:
                all_attentions += (layer_outputs[1],)
        if output_hidden_states:
            all_hidden_states += (hidden_states,)
        outputs = (hidden_states,)
        if not return_dict:
            return tuple(v for v in outputs if v is not None)
        return FlaxBaseModelOutput(
            last_hidden_state=hidden_states, hidden_states=all_hidden_states, attentions=all_attentions
        )
class FlaxCLIPEncoder(nn.Module):
    config: Union[CLIPTextConfig, CLIPVisionConfig]
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.layers = FlaxCLIPLayerCollection(self.config, dtype=self.dtype)
    def __call__(
        self,
        inputs_embeds,
        attention_mask=None,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        return self.layers(
            hidden_states=inputs_embeds,
            attention_mask=attention_mask,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
class FlaxCLIPTextTransformer(nn.Module):
    config: CLIPTextConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.embeddings = FlaxCLIPTextEmbeddings(self.config, dtype=self.dtype)
        self.encoder = FlaxCLIPEncoder(self.config, dtype=self.dtype)
        self.final_layer_norm = nn.LayerNorm(epsilon=self.config.layer_norm_eps, dtype=self.dtype)
        self.eos_token_id = self.config.eos_token_id
    def __call__(
        self,
        input_ids,
        attention_mask,
        position_ids,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states = self.embeddings(input_ids=input_ids, position_ids=position_ids)
        encoder_outputs = self.encoder(
            inputs_embeds=hidden_states,
            attention_mask=attention_mask,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        last_hidden_state = encoder_outputs[0]
        last_hidden_state = self.final_layer_norm(last_hidden_state)
        if self.eos_token_id == 2:
            pooled_output = last_hidden_state[jnp.arange(last_hidden_state.shape[0]), input_ids.argmax(axis=-1)]
        else:
            pooled_output = last_hidden_state[
                jnp.arange(last_hidden_state.shape[0]), (input_ids == self.eos_token_id).argmax(axis=-1)
            ]
        if not return_dict:
            return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return FlaxBaseModelOutputWithPooling(
            last_hidden_state=last_hidden_state,
            pooler_output=pooled_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
class FlaxCLIPVisionTransformer(nn.Module):
    config: CLIPVisionConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.embeddings = FlaxCLIPVisionEmbeddings(self.config, dtype=self.dtype)
        self.pre_layrnorm = nn.LayerNorm(epsilon=self.config.layer_norm_eps, dtype=self.dtype)
        self.encoder = FlaxCLIPEncoder(self.config, dtype=self.dtype)
        self.post_layernorm = nn.LayerNorm(epsilon=self.config.layer_norm_eps, dtype=self.dtype)
    def __call__(
        self,
        pixel_values=None,
        deterministic: bool = True,
        output_attentions=None,
        output_hidden_states=None,
        return_dict: bool = True,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict
        hidden_states = self.embeddings(pixel_values)
        hidden_states = self.pre_layrnorm(hidden_states)
        encoder_outputs = self.encoder(
            inputs_embeds=hidden_states,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        last_hidden_state = encoder_outputs[0]
        pooled_output = last_hidden_state[:, 0, :]
        pooled_output = self.post_layernorm(pooled_output)
        if not return_dict:
            return (last_hidden_state, pooled_output) + encoder_outputs[1:]
        return FlaxBaseModelOutputWithPooling(
            last_hidden_state=last_hidden_state,
            pooler_output=pooled_output,
            hidden_states=encoder_outputs.hidden_states,
            attentions=encoder_outputs.attentions,
        )
class FlaxCLIPTextPreTrainedModel(FlaxPreTrainedModel):
    config_class = CLIPTextConfig
    module_class: nn.Module = None
    def __init__(
        self,
        config: CLIPTextConfig,
        input_shape=(1, 1),
        seed: int = 0,
        dtype: jnp.dtype = jnp.float32,
        _do_init: bool = True,
        **kwargs,
    ):
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: jax.random.PRNGKey, input_shape: tuple, params: FrozenDict = None) -> FrozenDict:
        input_ids = jnp.zeros(input_shape, dtype="i4")
        position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_shape)
        attention_mask = jnp.ones_like(input_ids)
        params_rng, dropout_rng = jax.random.split(rng)
        rngs = {"params": params_rng, "dropout": dropout_rng}
        random_params = self.module.init(rngs, input_ids, attention_mask, position_ids)["params"]
        if params is not None:
            random_params = flatten_dict(unfreeze(random_params))
            params = flatten_dict(unfreeze(params))
            for missing_key in self._missing_keys:
                params[missing_key] = random_params[missing_key]
            self._missing_keys = set()
            return freeze(unflatten_dict(params))
        else:
            return random_params
    def __call__(
        self,
        input_ids,
        attention_mask=None,
        position_ids=None,
        params: Optional[dict] = None,
        dropout_rng: jax.random.PRNGKey = None,
        train: bool = False,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if position_ids is None:
            position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_ids.shape)
        if attention_mask is None:
            attention_mask = jnp.ones_like(input_ids)
        rngs = {}
        if dropout_rng is not None:
            rngs["dropout"] = dropout_rng
        return self.module.apply(
            {"params": params or self.params},
            jnp.array(input_ids, dtype="i4"),
            jnp.array(attention_mask, dtype="i4"),
            jnp.array(position_ids, dtype="i4"),
            not train,
            output_attentions,
            output_hidden_states,
            return_dict,
            rngs=rngs,
        )
class FlaxCLIPVisionPreTrainedModel(FlaxPreTrainedModel):
    config_class = CLIPVisionConfig
    main_input_name = "pixel_values"
    module_class: nn.Module = None
    def __init__(
        self,
        config: CLIPVisionConfig,
        input_shape: Optional[tuple] = None,
        seed: int = 0,
        dtype: jnp.dtype = jnp.float32,
        _do_init: bool = True,
        **kwargs,
    ):
        if input_shape is None:
            input_shape = (1, config.image_size, config.image_size, 3)
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: jax.random.PRNGKey, input_shape: tuple, params: FrozenDict = None) -> FrozenDict:
        pixel_values = jax.random.normal(rng, input_shape)
        params_rng, dropout_rng = jax.random.split(rng)
        rngs = {"params": params_rng, "dropout": dropout_rng}
        random_params = self.module.init(rngs, pixel_values)["params"]
        if params is not None:
            random_params = flatten_dict(unfreeze(random_params))
            params = flatten_dict(unfreeze(params))
            for missing_key in self._missing_keys:
                params[missing_key] = random_params[missing_key]
            self._missing_keys = set()
            return freeze(unflatten_dict(params))
        else:
            return random_params
    def __call__(
        self,
        pixel_values,
        params: Optional[dict] = None,
        dropout_rng: jax.random.PRNGKey = None,
        train: bool = False,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        pixel_values = jnp.transpose(pixel_values, (0, 2, 3, 1))
        rngs = {}
        if dropout_rng is not None:
            rngs["dropout"] = dropout_rng
        return self.module.apply(
            {"params": params or self.params},
            jnp.array(pixel_values, dtype=jnp.float32),
            not train,
            output_attentions,
            output_hidden_states,
            return_dict,
            rngs=rngs,
        )
class FlaxCLIPPreTrainedModel(FlaxPreTrainedModel):
    config_class = CLIPConfig
    module_class: nn.Module = None
    def __init__(
        self,
        config: CLIPConfig,
        input_shape: Optional[tuple] = None,
        seed: int = 0,
        dtype: jnp.dtype = jnp.float32,
        _do_init: bool = True,
        **kwargs,
    ):
        if input_shape is None:
            input_shape = ((1, 1), (1, config.vision_config.image_size, config.vision_config.image_size, 3))
        module = self.module_class(config=config, dtype=dtype, **kwargs)
        super().__init__(config, module, input_shape=input_shape, seed=seed, dtype=dtype, _do_init=_do_init)
    def init_weights(self, rng: jax.random.PRNGKey, input_shape: tuple, params: FrozenDict = None) -> FrozenDict:
        input_ids = jnp.zeros(input_shape[0], dtype="i4")
        position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_shape[0])
        attention_mask = jnp.ones_like(input_ids)
        pixel_values = jax.random.normal(rng, input_shape[1])
        params_rng, dropout_rng = jax.random.split(rng)
        rngs = {"params": params_rng, "dropout": dropout_rng}
        random_params = self.module.init(rngs, input_ids, pixel_values, attention_mask, position_ids)["params"]
        if params is not None:
            random_params = flatten_dict(unfreeze(random_params))
            params = flatten_dict(unfreeze(params))
            for missing_key in self._missing_keys:
                params[missing_key] = random_params[missing_key]
            self._missing_keys = set()
            return freeze(unflatten_dict(params))
        else:
            return random_params
    def __call__(
        self,
        input_ids,
        pixel_values,
        attention_mask=None,
        position_ids=None,
        params: Optional[dict] = None,
        dropout_rng: jax.random.PRNGKey = None,
        train: bool = False,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ):
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        if position_ids is None:
            position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_ids.shape)
        if attention_mask is None:
            attention_mask = jnp.ones_like(input_ids)
        pixel_values = jnp.transpose(pixel_values, (0, 2, 3, 1))
        rngs = {}
        if dropout_rng is not None:
            rngs["dropout"] = dropout_rng
        return self.module.apply(
            {"params": params or self.params},
            jnp.array(input_ids, dtype="i4"),
            jnp.array(pixel_values, dtype=jnp.float32),
            jnp.array(attention_mask, dtype="i4"),
            jnp.array(position_ids, dtype="i4"),
            not train,
            output_attentions,
            output_hidden_states,
            return_dict,
            rngs=rngs,
        )
    def get_text_features(
        self,
        input_ids,
        attention_mask=None,
        position_ids=None,
        params: Optional[dict] = None,
        dropout_rng: jax.random.PRNGKey = None,
        train=False,
    ):
        if position_ids is None:
            position_ids = jnp.broadcast_to(jnp.arange(jnp.atleast_2d(input_ids).shape[-1]), input_ids.shape)
        if attention_mask is None:
            attention_mask = jnp.ones_like(input_ids)
        rngs = {}
        if dropout_rng is not None:
            rngs["dropout"] = dropout_rng
        def _get_features(module, input_ids, attention_mask, position_ids, deterministic):
            text_outputs = module.text_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                deterministic=deterministic,
            )
            pooled_output = text_outputs[1]
            text_features = module.text_projection(pooled_output)
            return text_features
        return self.module.apply(
            {"params": params or self.params},
            jnp.array(input_ids, dtype="i4"),
            jnp.array(attention_mask, dtype="i4"),
            jnp.array(position_ids, dtype="i4"),
            not train,
            method=_get_features,
            rngs=rngs,
        )
    def get_image_features(
        self, pixel_values, params: Optional[dict] = None, dropout_rng: jax.random.PRNGKey = None, train=False
    ):
        pixel_values = jnp.transpose(pixel_values, (0, 2, 3, 1))
        rngs = {}
        if dropout_rng is not None:
            rngs["dropout"] = dropout_rng
        def _get_features(module, pixel_values, deterministic):
            vision_outputs = module.vision_model(pixel_values=pixel_values, deterministic=deterministic)
            pooled_output = vision_outputs[1]
            image_features = module.visual_projection(pooled_output)
            return image_features
        return self.module.apply(
            {"params": params or self.params},
            jnp.array(pixel_values, dtype=jnp.float32),
            not train,
            method=_get_features,
            rngs=rngs,
        )
class FlaxCLIPTextModule(nn.Module):
    config: CLIPTextConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.text_model = FlaxCLIPTextTransformer(self.config, dtype=self.dtype)
    def __call__(
        self,
        input_ids,
        attention_mask,
        position_ids,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        return self.text_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
class FlaxCLIPTextModel(FlaxCLIPTextPreTrainedModel):
    module_class = FlaxCLIPTextModule
overwrite_call_docstring(FlaxCLIPTextModel, CLIP_TEXT_INPUTS_DOCSTRING + FLAX_CLIP_TEXT_MODEL_DOCSTRING)
append_replace_return_docstrings(
    FlaxCLIPTextModel, output_type=FlaxBaseModelOutputWithPooling, config_class=CLIPTextConfig
)
class FlaxCLIPTextModelWithProjectionModule(nn.Module):
    config: CLIPTextConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.text_model = FlaxCLIPTextTransformer(self.config, dtype=self.dtype)
        self.text_projection = nn.Dense(self.config.projection_dim, use_bias=False, dtype=self.dtype)
    def __call__(
        self,
        input_ids,
        attention_mask,
        position_ids,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        text_outputs = self.text_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        pooled_output = text_outputs[1]
        text_embeds = self.text_projection(pooled_output)
        if not return_dict:
            return (text_embeds, text_outputs[0]) + text_outputs[2:]
        return FlaxCLIPTextModelOutput(
            text_embeds=text_embeds,
            last_hidden_state=text_outputs.last_hidden_state,
            hidden_states=text_outputs.hidden_states,
            attentions=text_outputs.attentions,
        )
class FlaxCLIPTextModelWithProjection(FlaxCLIPTextPreTrainedModel):
    module_class = FlaxCLIPTextModelWithProjectionModule
overwrite_call_docstring(
    FlaxCLIPTextModelWithProjection, CLIP_TEXT_INPUTS_DOCSTRING + FLAX_CLIP_TEXT_MODEL_WITH_PROJECTION_DOCSTRING
)
append_replace_return_docstrings(
    FlaxCLIPTextModelWithProjection, output_type=FlaxCLIPTextModelOutput, config_class=CLIPTextConfig
)
class FlaxCLIPVisionModule(nn.Module):
    config: CLIPVisionConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        self.vision_model = FlaxCLIPVisionTransformer(self.config, dtype=self.dtype)
    def __call__(
        self,
        pixel_values,
        deterministic: bool = True,
        output_attentions: bool = False,
        output_hidden_states: bool = False,
        return_dict: bool = True,
    ):
        return self.vision_model(
            pixel_values=pixel_values,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
class FlaxCLIPVisionModel(FlaxCLIPVisionPreTrainedModel):
    module_class = FlaxCLIPVisionModule
overwrite_call_docstring(FlaxCLIPVisionModel, CLIP_VISION_INPUTS_DOCSTRING + FLAX_CLIP_VISION_MODEL_DOCSTRING)
append_replace_return_docstrings(
    FlaxCLIPVisionModel, output_type=FlaxBaseModelOutputWithPooling, config_class=CLIPVisionConfig
)
class FlaxCLIPModule(nn.Module):
    config: CLIPConfig
    dtype: jnp.dtype = jnp.float32
    def setup(self):
        text_config = self.config.text_config
        vision_config = self.config.vision_config
        self.projection_dim = self.config.projection_dim
        self.text_embed_dim = text_config.hidden_size
        self.vision_embed_dim = vision_config.hidden_size
        self.text_model = FlaxCLIPTextTransformer(text_config, dtype=self.dtype)
        self.vision_model = FlaxCLIPVisionTransformer(vision_config, dtype=self.dtype)
        self.visual_projection = nn.Dense(
            self.projection_dim,
            dtype=self.dtype,
            kernel_init=jax.nn.initializers.normal(0.02),
            use_bias=False,
        )
        self.text_projection = nn.Dense(
            self.projection_dim,
            dtype=self.dtype,
            kernel_init=jax.nn.initializers.normal(0.02),
            use_bias=False,
        )
        self.logit_scale = self.param(
            "logit_scale", lambda _, shape: jnp.ones(shape) * self.config.logit_scale_init_value, []
        )
    def __call__(
        self,
        input_ids=None,
        pixel_values=None,
        attention_mask=None,
        position_ids=None,
        deterministic: bool = True,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = return_dict if return_dict is not None else self.config.return_dict
        vision_outputs = self.vision_model(
            pixel_values=pixel_values,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        text_outputs = self.text_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            deterministic=deterministic,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        image_embeds = vision_outputs[1]
        image_embeds = self.visual_projection(image_embeds)
        text_embeds = text_outputs[1]
        text_embeds = self.text_projection(text_embeds)
        image_embeds = image_embeds / jnp.linalg.norm(image_embeds, axis=-1, keepdims=True)
        text_embeds = text_embeds / jnp.linalg.norm(text_embeds, axis=-1, keepdims=True)
        logit_scale = jnp.exp(self.logit_scale)
        logits_per_text = jnp.matmul(text_embeds, image_embeds.T) * logit_scale
        logits_per_image = logits_per_text.T
        if not return_dict:
            return (logits_per_image, logits_per_text, text_embeds, image_embeds, text_outputs, vision_outputs)
        return FlaxCLIPOutput(
            logits_per_image=logits_per_image,
            logits_per_text=logits_per_text,
            text_embeds=text_embeds,
            image_embeds=image_embeds,
            text_model_output=text_outputs,
            vision_model_output=vision_outputs,
        )
@add_start_docstrings(CLIP_START_DOCSTRING)
class FlaxCLIPModel(FlaxCLIPPreTrainedModel):
    module_class = FlaxCLIPModule
overwrite_call_docstring(FlaxCLIPModel, CLIP_INPUTS_DOCSTRING + FLAX_CLIP_MODEL_DOCSTRING)
append_replace_return_docstrings(FlaxCLIPModel, output_type=FlaxCLIPOutput, config_class=CLIPConfig)
__all__ = [
    "FlaxCLIPModel",
    "FlaxCLIPPreTrainedModel",
    "FlaxCLIPTextModel",
    "FlaxCLIPTextPreTrainedModel",
    "FlaxCLIPTextModelWithProjection",
    "FlaxCLIPVisionModel",
    "FlaxCLIPVisionPreTrainedModel",
]