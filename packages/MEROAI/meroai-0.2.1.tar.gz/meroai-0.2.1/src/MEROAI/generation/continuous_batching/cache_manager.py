from abc import ABC, abstractmethod
from collections import deque
from math import ceil
from typing import Optional
from .requests import logger
class CacheAllocator(ABC):
    _index: int
    _block_table: dict[str, list[int]]
    @abstractmethod
    def allocate_blocks(self, n_blocks: int, request_id: str, free_blocks: deque[int]) -> Optional[int]:
        pass
    def free_blocks(self, request_id: str, free_blocks: deque[int]) -> None:
        if request_id in self._block_table:
            blocks_to_free = self._block_table.pop(request_id)
            free_blocks.extend(blocks_to_free)
        else:
            logger.warning(
                f"CacheAllocator {self._index} attempted to free blocks for non-existent request_id: {request_id}"
            )
    @abstractmethod
    def get_read_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        pass
    @abstractmethod
    def get_write_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        pass
    @abstractmethod
    def get_seqlens_k(self, request_id: str, past_length: int, query_length: int) -> tuple[str, int]:
        pass
class FullAttentionCacheAllocator(CacheAllocator):
    def __init__(self, index: int, block_size: int) -> None:
        self._index = index
        self.block_size = block_size
        self._block_table = {}
    def allocate_blocks(self, n_blocks: int, request_id: str, free_blocks: deque[int]) -> Optional[int]:
        if len(free_blocks) < n_blocks:
            return None
        if request_id not in self._block_table:
            self._block_table[request_id] = []
        self._block_table[request_id].extend(free_blocks.popleft() for _ in range(n_blocks))
        return n_blocks
    def get_read_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        block_table = self._block_table.get(request_id)
        if block_table is None:
            raise ValueError(f"No block table found for request {request_id}")
        physical_indices = []
        for i in range(past_length + query_length):
            block_idx = i // self.block_size
            block_offset = i % self.block_size
            physical_index = block_table[block_idx] * self.block_size + block_offset
            physical_indices.append(physical_index)
        return physical_indices
    def get_write_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        block_table = self._block_table.get(request_id)
        if block_table is None:
            raise ValueError(f"No block table found for request {request_id}")
        physical_indices = []
        for i in range(past_length, past_length + query_length):
            block_idx = i // self.block_size
            block_offset = i % self.block_size
            physical_index = block_table[block_idx] * self.block_size + block_offset
            physical_indices.append(physical_index)
        return physical_indices
    def get_seqlens_k(self, request_id: str, past_length: int, query_length: int) -> tuple[str, int]:
        seqlens_k = past_length + query_length
        return "full_attention", seqlens_k
class SlidingAttentionCacheAllocator(CacheAllocator):
    def __init__(self, index: int, block_size: int, sliding_window: int) -> None:
        self._index = index
        self.block_size = block_size
        self.sliding_window = sliding_window
        self._max_blocks_per_request = ceil(self.sliding_window / self.block_size)
        self._block_table = {}
    def allocate_blocks(self, n_blocks: int, request_id: str, free_blocks: deque[int]) -> Optional[int]:
        if request_id not in self._block_table:
            self._block_table[request_id] = []
        already_allocated = len(self._block_table[request_id])
        if already_allocated == self._max_blocks_per_request:
            return 0
        after_allocation = min(already_allocated + n_blocks, self._max_blocks_per_request)
        actual_n_blocks = after_allocation - already_allocated
        if len(free_blocks) < actual_n_blocks:
            return None
        self._block_table[request_id].extend(free_blocks.popleft() for _ in range(actual_n_blocks))
        return actual_n_blocks
    def get_read_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        block_table = self._block_table.get(request_id)
        if block_table is None:
            raise ValueError(f"No block table found for request {request_id}")
        start_index = 0 if past_length < self.sliding_window else past_length % self.sliding_window
        cache_length = min(past_length, self.sliding_window - 1)
        physical_indices = []
        for i in range(start_index, start_index + cache_length):
            i %= self.sliding_window
            block_idx = i // self.block_size
            block_offset = i % self.block_size
            physical_index = block_table[block_idx] * self.block_size + block_offset
            physical_indices.append(physical_index)
        return physical_indices + [-1] * query_length
    def get_write_indices(self, request_id: str, past_length: int, query_length: int) -> list[int]:
        block_table = self._block_table.get(request_id)
        if block_table is None:
            raise ValueError(f"No block table found for request {request_id}")
        start_index = past_length % self.sliding_window
        cache_length = min(query_length, self.sliding_window)
        padding_length = query_length - cache_length
        physical_indices = []
        for i in range(start_index, start_index + cache_length):
            i %= self.sliding_window
            block_idx = i // self.block_size
            block_offset = i % self.block_size
            physical_index = block_table[block_idx] * self.block_size + block_offset
            physical_indices.append(physical_index)
        if padding_length > 0:
            physical_indices = [-1] * padding_length + physical_indices
        return physical_indices
    def get_seqlens_k(self, request_id: str, past_length: int, query_length: int) -> tuple[str, int]:
        seqlens_k = query_length + min(past_length, self.sliding_window - 1)
        return "sliding_attention", seqlens_k