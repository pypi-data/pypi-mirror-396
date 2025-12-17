from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, Optional
import torch
from .configuration_utils import PretrainedConfig
from .utils import (
    is_hqq_available,
    is_quanto_greater,
    is_torch_greater_or_equal,
    is_torchdynamo_compiling,
    logging,
)
if is_hqq_available():
    from hqq.core.quantize import Quantizer as HQQQuantizer
_is_torch_greater_or_equal_than_2_7 = is_torch_greater_or_equal("2.7", accept_dev=True)
logger = logging.get_logger(__name__)
class CacheLayerMixin(ABC):
    is_compileable = False
    def __init__(self):
        self.keys: Optional[torch.Tensor] = None
        self.values: Optional[torch.Tensor] = None
        self.is_initialized = False
    def __repr__(self):
        return f"{self.__class__.__name__}"
    @abstractmethod
    def lazy_initialization(self, key_states: torch.Tensor): ...
    @abstractmethod
    def update(
        self, key_states: torch.Tensor, value_states: torch.Tensor, cache_kwargs: Optional[dict[str, Any]] = None
    ) -> tuple[torch.Tensor, torch.Tensor]: ...
    @abstractmethod
    def get_mask_sizes(self, cache_position: torch.Tensor) -> tuple[int, int]: ...
    @abstractmethod
    def get_seq_length(self) -> int: ...
    @abstractmethod
    def get_max_cache_shape(self) -> int: ...
    def offload(self):
        if self.is_initialized:
            self.keys = self.keys.to("cpu", non_blocking=True)
            self.values = self.values.to("cpu", non_blocking=True)
    def prefetch(self):
        if self.is_initialized and self.keys.device != self.device:
            self.keys = self.keys.to(self.device, non_blocking=True)
            self.values = self.values.to(self.device, non_blocking=True)
    def reset(self) -> None:
        if self.is_initialized:
            self.keys.zero_()
            self.values.zero_()
        if hasattr(self, "cumulative_length"):
            self.cumulative_length = 0
    def reorder_cache(self, beam_idx: torch.LongTensor) -> None:
        if self.get_seq_length() > 0:
            self.keys = self.keys.index_select(0, beam_idx.to(self.keys.device))
            self.values = self.values.index_select(0, beam_idx.to(self.values.device))
class DynamicLayer(CacheLayerMixin):
    is_sliding = False
    def lazy_initialization(self, key_states: torch.Tensor):
        self.dtype, self.device = key_states.dtype, key_states.device
        self.keys = torch.tensor([], dtype=self.dtype, device=self.device)
        self.values = torch.tensor([], dtype=self.dtype, device=self.device)
        self.is_initialized = True
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not self.is_initialized:
            self.lazy_initialization(key_states)
        self.keys = torch.cat([self.keys, key_states], dim=-2)
        self.values = torch.cat([self.values, value_states], dim=-2)
        return self.keys, self.values
    def get_mask_sizes(self, cache_position: torch.Tensor) -> tuple[int, int]:
        kv_offset = 0
        query_length = cache_position.shape[0]
        kv_length = self.get_seq_length() + query_length
        return kv_length, kv_offset
    def get_seq_length(self) -> int:
        if not self.is_initialized or self.keys.numel() == 0:
            return 0
        return self.keys.shape[-2]
    def get_max_cache_shape(self) -> int:
        return -1
    def crop(self, max_length: int) -> None:
        if max_length < 0:
            max_length = self.get_seq_length() - abs(max_length)
        if self.get_seq_length() <= max_length:
            return
        self.keys = self.keys[..., :max_length, :]
        self.values = self.values[..., :max_length, :]
    def batch_repeat_interleave(self, repeats: int) -> None:
        if self.get_seq_length() > 0:
            self.keys = self.keys.repeat_interleave(repeats, dim=0)
            self.values = self.values.repeat_interleave(repeats, dim=0)
    def batch_select_indices(self, indices: torch.Tensor) -> None:
        if self.get_seq_length() > 0:
            self.keys = self.keys[indices, ...]
            self.values = self.values[indices, ...]
class DynamicSlidingWindowLayer(DynamicLayer):
    is_sliding = True
    def __init__(self, sliding_window: int):
        super().__init__()
        self.sliding_window = sliding_window
        self.cumulative_length = 0
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not self.is_initialized:
            self.lazy_initialization(key_states)
        self.cumulative_length += key_states.shape[-2]
        full_key_states = torch.cat([self.keys, key_states], dim=-2)
        full_value_states = torch.cat([self.values, value_states], dim=-2)
        self.keys = full_key_states[:, :, -self.sliding_window + 1 :, :]
        self.values = full_value_states[:, :, -self.sliding_window + 1 :, :]
        return full_key_states, full_value_states
    def get_mask_sizes(self, cache_position: torch.Tensor) -> tuple[int, int]:
        query_length = cache_position.shape[0]
        is_full = self.cumulative_length >= self.sliding_window
        kv_offset = max(self.cumulative_length - self.sliding_window + 1, 0)
        if is_full:
            kv_length = self.sliding_window - 1 + query_length
        else:
            kv_length = self.cumulative_length + query_length
        return kv_length, kv_offset
    def get_seq_length(self) -> int:
        return self.cumulative_length
    def get_max_cache_shape(self) -> int:
        return self.sliding_window
    def crop(self, max_length: int) -> None:
        if self.get_seq_length() >= self.sliding_window:
            raise ValueError(
                "Cannot `crop` a `DynamicSlidingWindowLayer` after it has seen more tokens than its"
                "sliding window (otherwise some states are lost)"
            )
        super().crop(max_length)
        self.cumulative_length = self.keys.shape[-2]
class StaticLayer(CacheLayerMixin):
    is_compileable = True
    is_sliding = False
    def __init__(self, max_cache_len: int):
        super().__init__()
        self.max_cache_len = max_cache_len
    def lazy_initialization(self, key_states: torch.Tensor):
        self.max_batch_size, self.num_heads, _, self.head_dim = key_states.shape
        self.dtype, self.device = key_states.dtype, key_states.device
        self.keys = torch.zeros(
            (self.max_batch_size, self.num_heads, self.max_cache_len, self.head_dim),
            dtype=self.dtype,
            device=self.device,
        )
        self.values = torch.zeros(
            (self.max_batch_size, self.num_heads, self.max_cache_len, self.head_dim),
            dtype=self.dtype,
            device=self.device,
        )
        if not is_torchdynamo_compiling():
            torch._dynamo.mark_static_address(self.keys)
            torch._dynamo.mark_static_address(self.values)
        self.is_initialized = True
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not self.is_initialized:
            self.lazy_initialization(key_states)
        cache_position = cache_kwargs.get("cache_position") if cache_kwargs is not None else None
        cache_position = (
            cache_position if cache_position is not None else torch.arange(key_states.shape[-2], device=self.device)
        )
        try:
            self.keys.index_copy_(2, cache_position, key_states)
            self.values.index_copy_(2, cache_position, value_states)
        except NotImplementedError:
            self.keys[:, :, cache_position] = key_states
            self.values[:, :, cache_position] = value_states
        return self.keys, self.values
    def get_mask_sizes(self, cache_position: torch.Tensor) -> tuple[int, int]:
        kv_offset = 0
        kv_length = self.max_cache_len
        return kv_length, kv_offset
    def get_seq_length(self) -> int:
        return (self.keys[0, 0].any(dim=-1)).sum() if self.is_initialized else 0
    def get_max_cache_shape(self) -> int:
        return self.max_cache_len
class StaticSlidingWindowLayer(StaticLayer):
    is_sliding = True
    def __init__(self, max_cache_len: int, sliding_window: int):
        effective_max_cache_len = min(sliding_window, max_cache_len)
        super().__init__(max_cache_len=effective_max_cache_len)
        self.cumulative_length = 0
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if not self.is_initialized:
            self.lazy_initialization(key_states)
        cache_position = cache_kwargs.get("cache_position") if cache_kwargs is not None else None
        cache_position = (
            cache_position if cache_position is not None else torch.arange(key_states.shape[-2], device=self.device)
        )
        cumulative_length = self.cumulative_length
        is_full = cumulative_length >= self.max_cache_len
        self.cumulative_length += key_states.shape[-2]
        if is_full:
            if key_states.shape[-2] == 1:
                new_keys = self.keys.roll(-1, dims=-2)
                new_values = self.values.roll(-1, dims=-2)
                index = torch.tensor([-1], dtype=int, device=self.device)
                new_keys[:, :, index] = key_states
                new_values[:, :, index] = value_states
                self.keys.copy_(new_keys)
                self.values.copy_(new_values)
                return self.keys, self.values
            else:
                full_key_states = torch.cat((self.keys[:, :, 1:, :], key_states), dim=-2)
                full_value_states = torch.cat((self.values[:, :, 1:, :], value_states), dim=-2)
        elif cumulative_length + key_states.shape[2] > self.max_cache_len:
            if cumulative_length == 0:
                full_key_states = key_states
                full_value_states = value_states
            else:
                full_key_states = torch.cat((self.keys[:, :, :cumulative_length, :], key_states), dim=-2)
                full_value_states = torch.cat((self.values[:, :, :cumulative_length, :], value_states), dim=-2)
        else:
            try:
                self.keys.index_copy_(2, cache_position, key_states)
                self.values.index_copy_(2, cache_position, value_states)
            except NotImplementedError:
                self.keys[:, :, cache_position] = key_states
                self.values[:, :, cache_position] = value_states
            return self.keys, self.values
        self.keys.copy_(full_key_states[:, :, -self.max_cache_len :, :])
        self.values.copy_(full_value_states[:, :, -self.max_cache_len :, :])
        return full_key_states, full_value_states
    def get_mask_sizes(self, cache_position: torch.Tensor) -> tuple[int, int]:
        query_length = cache_position.shape[0]
        sliding_window = self.max_cache_len
        is_full = self.cumulative_length >= self.max_cache_len
        kv_offset = max(self.cumulative_length - sliding_window + 1, 0)
        if is_full:
            kv_length = sliding_window + query_length - 1
        elif self.cumulative_length + query_length > sliding_window:
            kv_length = self.cumulative_length + query_length
        else:
            kv_length = sliding_window
        return kv_length, kv_offset
    def get_seq_length(self) -> int:
        return self.cumulative_length
class QuantizedLayer(DynamicLayer):
    def __init__(
        self,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        super().__init__()
        self.nbits = nbits
        self.axis_key = axis_key
        self.axis_value = axis_value
        self.q_group_size = q_group_size
        self.residual_length = residual_length
        self.cumulative_length = 0
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        self.cumulative_length += key_states.shape[-2]
        if not self.is_initialized:
            self.lazy_initialization(key_states)
            self._quantized_keys = self._quantize(key_states.contiguous(), axis=self.axis_key)
            self._quantized_values = self._quantize(value_states.contiguous(), axis=self.axis_value)
            return key_states, value_states
        dequant_keys = self._dequantize(self._quantized_keys)
        dequant_values = self._dequantize(self._quantized_values)
        keys_to_return = torch.cat([dequant_keys, self.keys, key_states], dim=-2)
        values_to_return = torch.cat([dequant_values, self.values, value_states], dim=-2)
        if self.keys.dim() == 4 and self.keys.shape[-2] + 1 >= self.residual_length:
            self._quantized_keys = self._quantize(keys_to_return.contiguous(), axis=self.axis_key)
            self._quantized_values = self._quantize(values_to_return.contiguous(), axis=self.axis_value)
            self.keys = torch.tensor([], dtype=key_states.dtype, device=key_states.device)
            self.values = torch.tensor([], dtype=key_states.dtype, device=key_states.device)
        else:
            self.keys = torch.cat([self.keys, key_states], dim=-2)
            self.values = torch.cat([self.values, value_states], dim=-2)
        return keys_to_return, values_to_return
    @abstractmethod
    def _quantize(self, tensor, axis): ...
    @abstractmethod
    def _dequantize(self, q_tensor): ...
    def get_seq_length(self) -> int:
        return self.cumulative_length
class QuantoQuantizedLayer(QuantizedLayer):
    def __init__(
        self,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        super().__init__(
            nbits=nbits,
            axis_key=axis_key,
            axis_value=axis_value,
            q_group_size=q_group_size,
            residual_length=residual_length,
        )
        if is_quanto_greater("0.2.5", accept_dev=True):
            from optimum.quanto import MaxOptimizer, qint2, qint4
        else:
            raise ImportError(
                "You need optimum-quanto package version to be greater or equal than 0.2.5 to use `QuantoQuantizedCache`. "
            )
        if self.nbits not in [2, 4]:
            raise ValueError(f"`nbits` for `quanto` backend has to be one of [`2`, `4`] but got {self.nbits}")
        if self.axis_key not in [0, -1]:
            raise ValueError(f"`axis_key` for `quanto` backend has to be one of [`0`, `-1`] but got {self.axis_key}")
        if self.axis_value not in [0, -1]:
            raise ValueError(
                f"`axis_value` for `quanto` backend has to be one of [`0`, `-1`] but got {self.axis_value}"
            )
        self.qtype = qint4 if self.nbits == 4 else qint2
        self.optimizer = MaxOptimizer()
    def _quantize(self, tensor, axis):
        from optimum.quanto import quantize_weight
        scale, zeropoint = self.optimizer(tensor, self.qtype, axis, self.q_group_size)
        qtensor = quantize_weight(tensor, self.qtype, axis, scale, zeropoint, self.q_group_size)
        return qtensor
    def _dequantize(self, qtensor):
        return qtensor.dequantize()
class HQQQuantizedLayer(QuantizedLayer):
    def __init__(
        self,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        super().__init__(
            nbits=nbits,
            axis_key=axis_key,
            axis_value=axis_value,
            q_group_size=q_group_size,
            residual_length=residual_length,
        )
        if not is_hqq_available():
            raise ImportError("You need to install `hqq` to use `HQQQuantizedLayer`")
        if self.nbits not in [1, 2, 3, 4, 8]:
            raise ValueError(
                f"`nbits` for `HQQ` backend has to be one of [`1`, `2`, `3`, `4`, `8`] but got {self.nbits}"
            )
        if self.axis_key not in [0, 1]:
            raise ValueError(f"`axis_key` for `HQQ` backend has to be one of [`0`, `1`] but got {self.axis_key}")
        if self.axis_value not in [0, 1]:
            raise ValueError(f"`axis_value` for `HQQ` backend has to be one of [`0`, `1`] but got {self.axis_value}")
        self.quantizer = HQQQuantizer
    def _quantize(self, tensor, axis):
        qtensor, meta = self.quantizer.quantize(
            tensor,
            axis=axis,
            device=self.keys.device,
            compute_dtype=self.keys.dtype,
            nbits=self.nbits,
            group_size=self.q_group_size,
        )
        meta["compute_dtype"] = self.keys.dtype
        self.quantizer.cuda(qtensor, meta=meta, device=self.keys.device)
        meta["scale"] = meta["scale"].to(qtensor.device)
        meta["zero"] = meta["zero"].to(qtensor.device)
        return qtensor, meta
    def _dequantize(self, qtensor):
        quant_tensor, meta = qtensor
        tensor = self.quantizer.dequantize(quant_tensor, meta)
        return tensor
class Cache:
    def __init__(
        self,
        layers: Optional[list[CacheLayerMixin]] = None,
        layer_class_to_replicate: Optional[type[CacheLayerMixin]] = None,
        offloading: bool = False,
        offload_only_non_sliding: bool = True,
    ):
        if layers is not None and layer_class_to_replicate is not None:
            raise ValueError(
                "You can construct a Cache either from a list `layers` of all the predefined `CacheLayer`, or from a "
                "`layer_class_to_replicate`, in which case the Cache will append a new layer corresponding to "
                "`layer_class_to_replicate` for each new call to `update` with an idx not already in the Cache."
            )
        if layers is None and layer_class_to_replicate is None:
            raise ValueError(
                "You should provide exactly one of `layers` or `layer_class_to_replicate` to initialize a Cache."
            )
        self.layers = layers if layers is not None else []
        self.layer_class_to_replicate = layer_class_to_replicate
        self.offloading = offloading
        if self.offloading:
            self.only_non_sliding = offload_only_non_sliding
            self.prefetch_stream = torch.Stream() if _is_torch_greater_or_equal_than_2_7 else torch.cuda.Stream()
    def __repr__(self):
        return f"{self.__class__.__name__}(layers={self.layers})"
    def prefetch(self, layer_idx: int, only_non_sliding: bool = True):
        if only_non_sliding:
            try:
                layer_idx = layer_idx + self.is_sliding[layer_idx:].index(False)
            except ValueError:
                layer_idx = self.is_sliding.index(False)
        else:
            layer_idx = layer_idx if layer_idx < len(self.layers) else 0
        with self.prefetch_stream if _is_torch_greater_or_equal_than_2_7 else torch.cuda.stream(self.prefetch_stream):
            self.layers[layer_idx].prefetch()
    def offload(self, layer_idx: int, only_non_sliding: bool = True):
        if not (only_non_sliding and self.is_sliding[layer_idx]):
            self.layers[layer_idx].offload()
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        layer_idx: int,
        cache_kwargs: Optional[dict[str, Any]] = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        if self.layer_class_to_replicate is not None:
            while len(self.layers) <= layer_idx:
                self.layers.append(self.layer_class_to_replicate())
        if self.offloading:
            torch.cuda.default_stream(key_states.device).wait_stream(self.prefetch_stream)
            self.prefetch(layer_idx + 1, self.only_non_sliding)
        keys, values = self.layers[layer_idx].update(key_states, value_states, cache_kwargs)
        if self.offloading:
            self.offload(layer_idx, self.only_non_sliding)
        return keys, values
    def early_initialization(
        self, batch_size: int, num_heads: int, head_dim: int, dtype: torch.dtype, device: torch.device
    ):
        fake_keys_tensor = torch.zeros((batch_size, num_heads, 0, head_dim), dtype=dtype, device=device)
        for layer in self.layers:
            layer.lazy_initialization(fake_keys_tensor)
    def get_seq_length(self, layer_idx: int = 0) -> int:
        if layer_idx >= len(self.layers):
            return 0
        return self.layers[layer_idx].get_seq_length()
    def get_mask_sizes(self, cache_position: torch.Tensor, layer_idx: int) -> tuple[int, int]:
        if layer_idx >= len(self.layers):
            return cache_position.shape[0], 0
        return self.layers[layer_idx].get_mask_sizes(cache_position)
    def get_max_cache_shape(self, layer_idx: int = 0) -> int:
        if layer_idx >= len(self.layers):
            return -1
        return self.layers[layer_idx].get_max_cache_shape()
    def reset(self):
        for layer_idx in range(len(self.layers)):
            self.layers[layer_idx].reset()
    def reorder_cache(self, beam_idx: torch.LongTensor):
        for layer_idx in range(len(self.layers)):
            self.layers[layer_idx].reorder_cache(beam_idx)
    def crop(self, max_length: int):
        for layer_idx in range(len(self.layers)):
            self.layers[layer_idx].crop(max_length)
    def batch_repeat_interleave(self, repeats: int):
        for layer_idx in range(len(self.layers)):
            self.layers[layer_idx].batch_repeat_interleave(repeats)
    def batch_select_indices(self, indices: torch.Tensor):
        for layer_idx in range(len(self.layers)):
            self.layers[layer_idx].batch_select_indices(indices)
    @property
    def max_batch_size(self) -> int:
        values = [layer.max_batch_size for layer in self.layers]
        if len(set(values)) > 1:
            raise ValueError(f"Max batch size is not consistent across layers: {values}")
        return values[0]
    @property
    def max_cache_len(self) -> int:
        values = [layer.max_cache_len for layer in self.layers]
        return max(values)
    @property
    def is_compileable(self) -> bool:
        if len(self.layers) == 0:
            return False
        return all(layer.is_compileable for layer in self.layers)
    @property
    def is_initialized(self) -> bool:
        return len(self.layers) > 0 and all(layer.is_initialized for layer in self.layers)
    @property
    def is_sliding(self) -> list[bool]:
        return [getattr(layer, "is_sliding", False) for layer in self.layers]
    def __getitem__(self, layer_idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        if layer_idx < len(self.layers):
            return self.layers[layer_idx].keys, self.layers[layer_idx].values
        else:
            raise KeyError(
                f"Cache only has {len(self.layers)} layers, attempted to access layer with index {layer_idx}"
            )
    def __iter__(self):
        for layer_idx in range(len(self)):
            yield (self.layers[layer_idx].keys, self.layers[layer_idx].values)
    def __len__(self):
        return len(self.layers)
class DynamicCache(Cache):
    def __init__(
        self,
        ddp_cache_data: Optional[Iterable[tuple[torch.Tensor, torch.Tensor]]] = None,
        config: Optional[PretrainedConfig] = None,
        offloading: bool = False,
        offload_only_non_sliding: bool = False,
    ):
        layers = []
        if config is not None:
            decoder_config = config.get_text_config(decoder=True)
            sliding_window = getattr(decoder_config, "sliding_window", None) or getattr(
                decoder_config, "attention_chunk_size", None
            )
            layer_types = getattr(decoder_config, "layer_types", None)
            if layer_types is None:
                layer_types = [
                    "sliding_attention" if sliding_window is not None else "full_attention"
                    for _ in range(decoder_config.num_hidden_layers)
                ]
            if hasattr(decoder_config, "num_kv_shared_layers"):
                layer_types = layer_types[: -decoder_config.num_kv_shared_layers]
            for layer_type in layer_types:
                if layer_type in ("sliding_attention", "chunked_attention"):
                    layers.append(DynamicSlidingWindowLayer(sliding_window=sliding_window))
                else:
                    layers.append(DynamicLayer())
        if ddp_cache_data is not None:
            for layer_idx, (key_states, value_states) in enumerate(ddp_cache_data):
                if config is None:
                    layers.append(DynamicLayer())
                _, _ = layers[layer_idx].update(key_states, value_states)
        if len(layers) == 0:
            super().__init__(
                layer_class_to_replicate=DynamicLayer,
                offloading=offloading,
                offload_only_non_sliding=offload_only_non_sliding,
            )
        else:
            super().__init__(layers=layers, offloading=offloading, offload_only_non_sliding=offload_only_non_sliding)
    def to_legacy_cache(self) -> tuple[tuple[torch.Tensor, torch.Tensor]]:
        legacy_cache = ()
        for layer in self.layers:
            legacy_cache += ((layer.keys, layer.values),)
        return legacy_cache
    @classmethod
    def from_legacy_cache(cls, past_key_values: tuple[tuple[torch.Tensor, torch.Tensor]]) -> "DynamicCache":
        cache = cls()
        if past_key_values is None:
            logger.warning_once("past_key_values should not be None in from_legacy_cache()")
        if past_key_values is not None:
            for layer_idx in range(len(past_key_values)):
                key_states, value_states = past_key_values[layer_idx]
                cache.update(key_states, value_states, layer_idx)
        return cache
class StaticCache(Cache):
    def __init__(
        self,
        config: PretrainedConfig,
        max_cache_len: int,
        offloading: bool = False,
        offload_only_non_sliding: bool = True,
        **kwargs,
    ):
        config = config.get_text_config(decoder=True)
        layer_types = getattr(config, "layer_types", None)
        if layer_types is None:
            if getattr(config, "sliding_window", None) is not None:
                layer_types = ["sliding_attention" for _ in range(config.num_hidden_layers)]
            elif getattr(config, "attention_chunk_size", None) is not None:
                layer_types = ["chunked_attention" for _ in range(config.num_hidden_layers)]
            else:
                layer_types = ["full_attention" for _ in range(config.num_hidden_layers)]
        if hasattr(config, "num_kv_shared_layers"):
            layer_types = layer_types[: -config.num_kv_shared_layers]
        layers = []
        for layer_type in layer_types:
            if layer_type == "sliding_attention":
                layer = StaticSlidingWindowLayer(max_cache_len=max_cache_len, sliding_window=config.sliding_window)
            elif layer_type == "chunked_attention":
                layer = StaticSlidingWindowLayer(
                    max_cache_len=max_cache_len, sliding_window=config.attention_chunk_size
                )
            else:
                layer = StaticLayer(max_cache_len=max_cache_len)
            layers.append(layer)
        super().__init__(layers=layers, offloading=offloading, offload_only_non_sliding=offload_only_non_sliding)
class QuantizedCache(Cache):
    def __init__(
        self,
        backend: str,
        config: PretrainedConfig,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        if backend == "quanto":
            layer_class = QuantoQuantizedLayer
        elif backend == "hqq":
            layer_class = HQQQuantizedLayer
        else:
            raise ValueError(f"Unknown quantization backend `{backend}`")
        config = config.get_text_config(decoder=True)
        layers = [
            layer_class(nbits, axis_key, axis_value, q_group_size, residual_length)
            for _ in range(config.num_hidden_layers)
        ]
        super().__init__(layers=layers)
class EncoderDecoderCache(Cache):
    def __init__(self, *caches) -> None:
        if len(caches) == 1:
            self.self_attention_cache = DynamicCache()
            self.cross_attention_cache = DynamicCache()
            for layer_idx, key_value_states in enumerate(caches[0]):
                key_states, value_states = key_value_states[:2]
                self.self_attention_cache.update(key_states, value_states, layer_idx)
                if len(key_value_states) > 2:
                    key_states, value_states = key_value_states[2:]
                    self.cross_attention_cache.update(key_states, value_states, layer_idx)
        elif len(caches) == 2:
            if not isinstance(caches[0], Cache) or not isinstance(caches[1], Cache):
                raise TypeError(f"One of the two arguments is not a Cache: {type(caches[0]) = }, {type(caches[1]) = }")
            self.self_attention_cache = caches[0]
            self.cross_attention_cache = caches[1]
        else:
            raise ValueError(f"Expected 1 or 2 arguments, got {len(caches)}")
        self.is_updated = {}
        for layer_idx in range(len(self.cross_attention_cache)):
            self.is_updated[layer_idx] = bool(self.cross_attention_cache.get_seq_length(layer_idx) > 0)
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(self_attention_cache={self.self_attention_cache}, cross_attention_cache="
            f"{self.cross_attention_cache})"
        )
    def __iter__(self):
        for layer_idx in range(len(self)):
            yield (
                self.self_attention_cache.layers[layer_idx].keys,
                self.self_attention_cache.layers[layer_idx].values,
                self.cross_attention_cache.layers[layer_idx].keys,
                self.cross_attention_cache.layers[layer_idx].values,
            )
    def __getitem__(self, layer_idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if layer_idx < len(self):
            return (
                self.self_attention_cache.layers[layer_idx].keys,
                self.self_attention_cache.layers[layer_idx].values,
                self.cross_attention_cache.layers[layer_idx].keys,
                self.cross_attention_cache.layers[layer_idx].values,
            )
        else:
            raise KeyError(f"Cache only has {len(self)} layers, attempted to access layer with index {layer_idx}")
    def __len__(self):
        return len(self.self_attention_cache)
    def to_legacy_cache(self) -> tuple[tuple[torch.Tensor]]:
        legacy_cache = ()
        if len(self.cross_attention_cache) > 0:
            for self_attn, cross_attn in zip(
                self.self_attention_cache.to_legacy_cache(), self.cross_attention_cache.to_legacy_cache()
            ):
                legacy_cache += (self_attn + cross_attn,)
        else:
            legacy_cache = self.self_attention_cache.to_legacy_cache()
        return legacy_cache
    @classmethod
    def from_legacy_cache(
        cls, past_key_values: Optional[Iterable[tuple[torch.FloatTensor, ...]]]
    ) -> "EncoderDecoderCache":
        cache = cls(DynamicCache(), DynamicCache())
        if past_key_values is None:
            logger.warning_once("past_key_values should not be None in from_legacy_cache()")
        else:
            for layer_idx, key_value_states in enumerate(past_key_values):
                key_states, value_states = key_value_states[:2]
                cache.self_attention_cache.update(key_states, value_states, layer_idx)
                if len(key_value_states) > 2:
                    key_states, value_states = key_value_states[2:]
                    cache.cross_attention_cache.update(key_states, value_states, layer_idx)
                    cache.is_updated[layer_idx] = True
        return cache
    def get_seq_length(self, layer_idx: int = 0) -> int:
        return self.self_attention_cache.get_seq_length(layer_idx)
    def reset(self):
        self.self_attention_cache.reset()
        self.cross_attention_cache.reset()
        for layer_idx in self.is_updated:
            self.is_updated[layer_idx] = False
    def reorder_cache(self, beam_idx: torch.LongTensor):
        self.self_attention_cache.reorder_cache(beam_idx)
        self.cross_attention_cache.reorder_cache(beam_idx)
    def check_dynamic_cache(self, method: str):
        if not (
            isinstance(self.self_attention_cache, DynamicCache)
            and isinstance(self.cross_attention_cache, DynamicCache)
        ):
            raise ValueError(
                f"`{method}` is only defined for dynamic cache, got {self.self_attention_cache.__str__()} for the self "
                f"attention cache and {self.cross_attention_cache.__str__()} for the cross attention cache."
            )
    def crop(self, maximum_length: int):
        self.check_dynamic_cache(self.crop.__name__)
        self.self_attention_cache.crop(maximum_length)
    def batch_split(self, full_batch_size: int, split_size: int) -> "list[EncoderDecoderCache]":
        self.check_dynamic_cache(self.batch_split.__name__)
        self_attention_cache = self.self_attention_cache.batch_split(full_batch_size, split_size)
        cross_attention_cache = self.cross_attention_cache.batch_split(full_batch_size, split_size)
        out = []
        for self_attn, cross_attn in zip(self_attention_cache, cross_attention_cache):
            out.append(EncoderDecoderCache(self_attn, cross_attn))
        return out
    def batch_repeat_interleave(self, repeats: int):
        self.check_dynamic_cache(self.batch_repeat_interleave.__name__)
        self.self_attention_cache.batch_repeat_interleave(repeats)
        self.cross_attention_cache.batch_repeat_interleave(repeats)
    def batch_select_indices(self, indices: torch.Tensor):
        self.check_dynamic_cache(self.batch_select_indices.__name__)
        self.self_attention_cache.batch_select_indices(indices)
        self.cross_attention_cache.batch_select_indices(indices)
    def get_max_cache_shape(self) -> int:
        return self.self_attention_cache.get_max_cache_shape()
    def get_mask_sizes(self, cache_position: torch.Tensor, layer_idx: int) -> tuple[int, int]:
        return self.self_attention_cache.get_mask_sizes(cache_position, layer_idx)
    @property
    def is_sliding(self):
        return self.self_attention_cache.is_sliding
    @property
    def is_compileable(self) -> bool:
        return self.self_attention_cache.is_compileable
class SlidingWindowLayer(StaticSlidingWindowLayer):
    def __init__(self, max_cache_len: int, sliding_window: int):
        logger.warning_once(
            "`SlidingWindowLayer` is deprecated and will be removed in version v4.59 "
            "Use `StaticSlidingWindowLayer` instead, which is a better name for it."
        )
        super().__init__(max_cache_len, sliding_window)
class ChunkedSlidingLayer(StaticSlidingWindowLayer):
    def __init__(self, max_cache_len: int, sliding_window: int):
        logger.warning_once(
            "`ChunkedSlidingLayer` is deprecated and will be removed in version v4.59 "
            "Use `StaticSlidingWindowLayer` instead, which has the exact same functionalities."
        )
        super().__init__(max_cache_len, sliding_window)
class OffloadedCache(DynamicCache):
    def __init__(self) -> None:
        logger.warning_once(
            "`OffloadedCache` is deprecated and will be removed in version v4.59 "
            "Use `DynamicCache(offloading=True)` instead"
        )
        super().__init__(offloading=True)
class OffloadedStaticCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_cache_len: int, *args, **kwargs):
        logger.warning_once(
            "`OffloadedStaticCache` is deprecated and will be removed in version v4.59 "
            "Use `StaticCache(..., offloading=True)` instead"
        )
        super().__init__(config=config, max_cache_len=max_cache_len, offloading=True)
class SlidingWindowCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_cache_len: int, *args, **kwargs):
        logger.warning_once(
            "`SlidingWindowCache` is deprecated and will be removed in version v4.59 "
            "Use `StaticCache(...)` instead which will correctly infer the type of each layer."
        )
        super().__init__(config=config, max_cache_len=max_cache_len)
class HybridCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_cache_len: int, *args, **kwargs):
        logger.warning_once(
            "`HybridCache` is deprecated and will be removed in version v4.59 "
            "Use `StaticCache(...)` instead which will correctly infer the type of each layer."
        )
        super().__init__(config=config, max_cache_len=max_cache_len)
class HybridChunkedCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_cache_len: int, *args, **kwargs):
        logger.warning_once(
            "`HybridChunkedCache` is deprecated and will be removed in version v4.59 "
            "Use `StaticCache(...)` instead which will correctly infer the type of each layer."
        )
        super().__init__(config=config, max_cache_len=max_cache_len)
class OffloadedHybridCache(StaticCache):
    def __init__(self, config: PretrainedConfig, max_cache_len: int, *args, **kwargs):
        logger.warning_once(
            "`OffloadedHybridCache` is deprecated and will be removed in version v4.59 "
            "Use `StaticCache(..., offload=True)` instead which will correctly infer the type of each layer."
        )
        super().__init__(config=config, max_cache_len=max_cache_len, offloading=True)
class QuantoQuantizedCache(QuantizedCache):
    def __init__(
        self,
        config: PretrainedConfig,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        logger.warning_once(
            "`QuantoQuantizedCache` is deprecated and will be removed in version v4.59 "
            "Use `QuantizedCache(backend='quanto', ...)` instead."
        )
        super().__init__("quanto", config, nbits, axis_key, axis_value, q_group_size, residual_length)
class HQQQuantizedCache(QuantizedCache):
    def __init__(
        self,
        config: PretrainedConfig,
        nbits: int = 4,
        axis_key: int = 0,
        axis_value: int = 0,
        q_group_size: int = 64,
        residual_length: int = 128,
    ):
        logger.warning_once(
            "`HQQQuantizedCache` is deprecated and will be removed in version v4.59 "
            "Use `QuantizedCache(backend='hqq', ...)` instead."
        )
        super().__init__("hqq", config, nbits, axis_key, axis_value, q_group_size, residual_length)
class SinkCache(Cache):
    def __init__(self, **kwargs) -> None:
        raise NotImplementedError(
            "`SinkCache` has been moved as a `custom_generate` repository on the Hub: "
            "https://huggingface.co/MEROAI-community/sink_cache. See the repository for usage examples."
        )