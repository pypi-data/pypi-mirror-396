from collections import deque
from math import floor, gcd, sqrt
from typing import Optional, Union
import torch
from ...configuration_utils import PretrainedConfig
from ...generation.configuration_utils import GenerationConfig
from ...utils.metrics import attach_tracer, traced
from .cache_manager import CacheAllocator, FullAttentionCacheAllocator, SlidingAttentionCacheAllocator
from .requests import get_device_and_memory_breakdown, logger
def group_layers_by_attn_type(config: PretrainedConfig) -> tuple[list[list[int]], list[str]]:
    layer_types = getattr(config, "layer_types", None)
    if layer_types is None:
        attn_type = "sliding_attention" if getattr(config, "sliding_window", None) is not None else "full_attention"
        layer_types = [attn_type for _ in range(config.num_hidden_layers)]
    layer_counts = {}
    for i, layer_type in enumerate(layer_types):
        layer_counts[layer_type] = layer_counts.get(layer_type, []) + [i]
    group_size = gcd(*[len(indices) for indices in layer_counts.values()])
    layer_groups = []
    for layer_type, indices in layer_counts.items():
        for i in range(0, len(indices), group_size):
            layer_groups.append(indices[i : i + group_size])
    group_types = [layer_types[lg[0]] for lg in layer_groups]
    return layer_groups, group_types
@attach_tracer()
class PagedAttentionCache:
    def __init__(
        self,
        config: PretrainedConfig,
        generation_config: GenerationConfig,
        device: torch.device,
        dtype: torch.dtype = torch.float16,
        layer_device_map: Optional[dict[int, Union[str, torch.device, int]]] = None,
        tp_size: Optional[int] = None,
    ) -> None:
        self.config = config
        self.dtype = dtype
        self.device = device
        kv_heads = getattr(config, "num_key_value_heads", None)
        self.num_key_value_heads: int = kv_heads if kv_heads is not None else config.num_attention_heads
        head_dim = getattr(config, "head_dim", None)
        self.head_dim: int = head_dim if head_dim is not None else config.hidden_size // config.num_attention_heads
        self.block_size = getattr(generation_config, "block_size", 32)
        layer_groups, group_types = group_layers_by_attn_type(config)
        group_size = len(layer_groups[0])
        self.num_groups = len(layer_groups)
        self.sliding_windows = {}
        self.layer_index_to_group_indices = {}
        for i, group in enumerate(layer_groups):
            sliding_window = config.sliding_window if group_types[i] == "sliding_attention" else 1
            for j, layer in enumerate(group):
                self.layer_index_to_group_indices[layer] = (i, j)
                self.sliding_windows[layer] = sliding_window
        if tp_size is not None and tp_size > 1:
            if self.num_key_value_heads % tp_size != 0:
                raise ValueError(
                    f"Number of key value heads {self.num_key_value_heads} must be divisible by tensor parallel size {tp_size}."
                )
        page_size = self.head_dim * self.num_key_value_heads
        if getattr(config, "attn_implementation", None) == "paged_attention":
            num_attention_masks = 0
        else:
            num_attention_masks = 2 if "sliding_attention" in group_types else 1
        memory_handler = PagedAttentionMemoryHandler(
            block_size=self.block_size,
            page_size=page_size,
            num_groups=self.num_groups,
            group_size=group_size,
            peak_activation_per_token=(config.hidden_size + config.vocab_size),
            num_attention_masks=num_attention_masks,
        )
        num_blocks, max_batch_tokens = memory_handler.infer_num_blocks_and_max_batch_tokens(
            num_blocks=getattr(generation_config, "num_blocks", None),
            max_batch_tokens=getattr(generation_config, "max_batch_tokens", None),
            max_memory_percent=getattr(generation_config, "max_memory", 0.9),
            cache_dtype=self.dtype,
        )
        self.num_blocks = num_blocks
        self.max_batch_tokens = max_batch_tokens
        logger.info(
            f"PagedAttentionCache initialized with {self.num_blocks = }, {self.block_size = }, {page_size = }, "
            f"{self.max_batch_tokens = } {num_attention_masks = }"
        )
        self.key_cache: list[torch.Tensor] = []
        self.value_cache: list[torch.Tensor] = []
        self.cache_shape = (num_blocks * self.block_size + 1, self.num_key_value_heads, self.head_dim)
        for _ in range(group_size):
            new_layer_key_cache = torch.empty(self.cache_shape, dtype=self.dtype, device=self.device)
            new_layer_value_cache = torch.empty(self.cache_shape, dtype=self.dtype, device=self.device)
            torch._dynamo.mark_static_address(new_layer_key_cache)
            torch._dynamo.mark_static_address(new_layer_value_cache)
            self.key_cache.append(new_layer_key_cache)
            self.value_cache.append(new_layer_value_cache)
        logger.info(f"{self.cache_shape = } {self.key_cache[0].shape = } {self.key_cache[0].numel() = }")
        self._free_blocks = deque(range(num_blocks))
        self.group_cache_managers: list[CacheAllocator] = []
        for i, group_type in enumerate(group_types):
            if group_type == "full_attention":
                cm = FullAttentionCacheAllocator(i, self.block_size)
            elif group_type == "sliding_attention":
                cm = SlidingAttentionCacheAllocator(i, self.block_size, config.sliding_window)
            else:
                raise ValueError(f"Invalid group type: {group_type}")
            self.group_cache_managers.append(cm)
    @traced
    def allocate_blocks(self, n_blocks: int, request_id: str) -> int:
        max_allocated = 0
        for cm in self.group_cache_managers:
            allocated = cm.allocate_blocks(n_blocks, request_id, self._free_blocks)
            if allocated is None:
                return None
            max_allocated = max(max_allocated, allocated)
        return max_allocated
    @traced
    def free_blocks(self, request_id: str) -> None:
        for cm in self.group_cache_managers:
            cm.free_blocks(request_id, self._free_blocks)
    def get_num_free_blocks(self) -> int:
        return len(self._free_blocks)
    @traced
    def extend_read_indices(
        self, request_id: str, past_length: int, query_length: int, read_index: list[list[int]]
    ) -> None:
        for cm, read_indices in zip(self.group_cache_managers, read_index):
            indices = cm.get_read_indices(request_id, past_length, query_length)
            read_indices.extend(indices)
    @traced
    def extend_write_indices(
        self, request_id: str, past_length: int, query_length: int, write_index: list[list[int]]
    ) -> None:
        for cm, write_indices in zip(self.group_cache_managers, write_index):
            indices = cm.get_write_indices(request_id, past_length, query_length)
            write_indices.extend(indices)
    @traced
    def get_seqlens_k(self, request_id: str, past_length: int, query_length: int) -> dict[str, int]:
        seqlens_k = {}
        for cm in self.group_cache_managers:
            attn_type, seqlen_k = cm.get_seqlens_k(request_id, past_length, query_length)
            seqlens_k[attn_type] = seqlen_k
        return seqlens_k
    @traced
    def update(
        self,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        layer_idx: int,
        read_index: list[torch.Tensor],
        write_index: list[torch.Tensor],
        **kwargs,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        group_idx, layer_idx_in_group = self.layer_index_to_group_indices[layer_idx]
        layer_read_index = read_index[group_idx]
        layer_write_index = write_index[group_idx]
        k_cache = self.key_cache[layer_idx_in_group]
        v_cache = self.value_cache[layer_idx_in_group]
        key_states = key_states.transpose(1, 2).squeeze(0)
        value_states = value_states.transpose(1, 2).squeeze(0)
        sliding_window = self.sliding_windows[layer_idx]
        if sliding_window == 1:
            k_cache[layer_write_index, :, :] = key_states
            v_cache[layer_write_index, :, :] = value_states
            key_states_with_cache = k_cache[layer_read_index, :, :]
            value_states_with_cache = v_cache[layer_read_index, :, :]
        else:
            mask = layer_read_index == -1
            key_states_with_cache = k_cache[layer_read_index, :, :]
            key_states_with_cache[mask] = key_states
            value_states_with_cache = v_cache[layer_read_index, :, :]
            value_states_with_cache[mask] = value_states
            k_cache[layer_write_index, :, :] = key_states
            v_cache[layer_write_index, :, :] = value_states
        return key_states_with_cache, value_states_with_cache
class PagedAttentionMemoryHandler:
    _activation_dtype = torch.bfloat16
    _input_dtype = torch.int32
    _upper_bound_max_batch_tokens = 256
    _upper_bound_num_blocks = 4096
    def __init__(
        self,
        block_size: int,
        page_size: int,
        num_groups: int,
        group_size: int,
        peak_activation_per_token: int,
        num_attention_masks: int,
    ) -> None:
        self.block_size = block_size
        self.page_size = page_size
        self.num_groups = num_groups
        self.group_size = group_size
        self.peak_activation_per_token = peak_activation_per_token
        self.num_attention_masks = num_attention_masks
    @staticmethod
    def get_available_memory(max_memory_percent: float = 1.0) -> int:
        _, total, reserved, allocated = get_device_and_memory_breakdown()
        available_memory = total - max(allocated, reserved)
        available_memory = int(available_memory * max_memory_percent)
        return available_memory
    def infer_num_blocks_and_max_batch_tokens(
        self,
        num_blocks: Optional[int] = None,
        max_batch_tokens: Optional[int] = None,
        max_memory_percent: float = 0.9,
        cache_dtype: torch.dtype = torch.float16,
    ) -> tuple[int, int]:
        if num_blocks is None and max_batch_tokens is None:
            num_blocks, max_batch_tokens = self.compute_num_blocks_and_max_batch_tokens(
                max_memory_percent, cache_dtype
            )
        elif num_blocks is not None and max_batch_tokens is None:
            max_batch_tokens = self.compute_max_batch_tokens(num_blocks, max_memory_percent, cache_dtype)
        elif max_batch_tokens is not None and num_blocks is None:
            num_blocks = self.compute_num_blocks(max_batch_tokens, max_memory_percent, cache_dtype)
        available_memory = self.get_available_memory(max_memory_percent)
        memory_footprint = self.compute_memory_footprint(
            max_batch_tokens=max_batch_tokens,
            num_blocks=num_blocks,
            cache_dtype=cache_dtype,
        )
        if memory_footprint > available_memory:
            raise MemoryError(f"Memory footprint {memory_footprint} is more than available memory {available_memory}")
        return num_blocks, max_batch_tokens
    def compute_num_blocks_and_max_batch_tokens(
        self,
        max_memory_percent: float = 0.9,
        cache_dtype: torch.dtype = torch.float16,
        m: float = 0.01,
    ) -> tuple[int, int]:
        cache_memory = self.get_available_memory(max_memory_percent)
        logger.info(f"Cache memory: {cache_memory}")
        a = m * self.num_attention_masks * self._activation_dtype.itemsize
        b = 2 * (self.group_size * self.page_size * cache_dtype.itemsize + 2 * self.num_groups)
        b += m * (self.peak_activation_per_token * self._activation_dtype.itemsize + 28 + 4 * self.num_groups)
        c = -cache_memory
        logger.debug(f"Coefficients of 2nd degree polynomial: {a = }, {b = }, {c = }")
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            raise ValueError(f"Discriminant is negative: {discriminant = }")
        greatest_solution = (-b + sqrt(discriminant)) / (2 * a)
        if greatest_solution < 0:
            raise ValueError(f"Greatest solution is negative: {greatest_solution = }")
        num_pages = floor(greatest_solution)
        num_blocks = num_pages // self.block_size
        if num_blocks > self._upper_bound_num_blocks:
            logger.info(f"{num_blocks = } is too large, setting to {self._upper_bound_num_blocks = }")
            num_blocks = self._upper_bound_num_blocks
        max_batch_tokens = int(greatest_solution * m)
        if max_batch_tokens > self._upper_bound_max_batch_tokens:
            logger.info(f"{max_batch_tokens = } is too large, setting to {self._upper_bound_max_batch_tokens = }")
            max_batch_tokens = self._upper_bound_max_batch_tokens
        return num_blocks, max_batch_tokens
    def compute_max_batch_tokens(
        self,
        num_blocks: int,
        max_memory_percent: float = 0.9,
        cache_dtype: torch.dtype = torch.float16,
    ) -> int:
        cache_memory = self.get_available_memory(max_memory_percent)
        num_pages = num_blocks * self.block_size
        num = cache_memory
        num -= 2 * num_pages * (self.group_size * self.page_size * cache_dtype.itemsize + 2 * self.num_groups)
        denum = self._activation_dtype.itemsize * (
            num_pages * self.num_attention_masks + self.peak_activation_per_token
        )
        denum += 28 + 4 * self.num_groups
        max_batch_tokens = floor(num / denum)
        if max_batch_tokens > self._upper_bound_max_batch_tokens:
            logger.info(f"{max_batch_tokens = } is too large, setting to {self._upper_bound_max_batch_tokens = }")
            max_batch_tokens = self._upper_bound_max_batch_tokens
        return max_batch_tokens
    def compute_num_blocks(
        self,
        max_batch_tokens: int,
        max_memory_percent: float = 0.9,
        cache_dtype: torch.dtype = torch.float16,
    ) -> int:
        cache_memory = self.get_available_memory(max_memory_percent)
        num = cache_memory
        num -= max_batch_tokens * self.peak_activation_per_token * self._activation_dtype.itemsize
        num -= max_batch_tokens * (28 + 4 * self.num_groups)
        denum = 2 * (self.group_size * self.page_size * cache_dtype.itemsize + 2 * self.num_groups)
        denum += max_batch_tokens * (self.num_attention_masks * self._activation_dtype.itemsize)
        denum += max_batch_tokens * self._activation_dtype.itemsize
        num_pages = floor(num / denum)
        num_blocks = num_pages // self.block_size
        if num_blocks > self._upper_bound_num_blocks:
            logger.info(f"{num_blocks = } is too large, setting to {self._upper_bound_num_blocks = }")
            num_blocks = self._upper_bound_num_blocks
        return num_blocks
    def compute_memory_footprint(
        self,
        num_blocks: Optional[int] = None,
        max_batch_tokens: Optional[int] = None,
        cache_dtype: torch.dtype = torch.float16,
    ) -> tuple[int, int, int]:
        num_pages = num_blocks * self.block_size
        cache_memory_footprint = 2 * self.group_size * num_pages * self.page_size * cache_dtype.itemsize
        activation_memory_footprint = self.peak_activation_per_token * self._activation_dtype.itemsize
        activation_memory_footprint *= max_batch_tokens
        inputs_outputs_positions_and_logits_memory_footprint = 4 * max_batch_tokens * 4
        attention_memory_footprint = self.num_attention_masks * self._activation_dtype.itemsize
        attention_memory_footprint *= num_pages * max_batch_tokens
        cumulative_seqlens_memory_footprint = 3 * max_batch_tokens * 4
        write_index_memory_footprint = self.num_groups * max_batch_tokens * 4
        read_index_memory_footprint = self.num_groups * (num_pages + max_batch_tokens) * 4
        total_memory_footprint = sum(
            [
                cache_memory_footprint,
                activation_memory_footprint,
                inputs_outputs_positions_and_logits_memory_footprint,
                attention_memory_footprint,
                cumulative_seqlens_memory_footprint,
                write_index_memory_footprint,
                read_index_memory_footprint,
            ]
        )
        return total_memory_footprint