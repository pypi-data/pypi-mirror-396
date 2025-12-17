import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import torch
from ...utils.logging import logging
from ...utils.metrics import traced
logger = logging.getLogger("ContinuousBatchingLogger")
def get_device_and_memory_breakdown() -> tuple[torch.device, int, int, int]:
    if torch.cuda.is_available():
        device = torch.device("cuda")
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        total_memory = torch.cuda.get_device_properties(device).total_memory
        reserved_memory = torch.cuda.memory_reserved(device)
        allocated_memory = torch.cuda.memory_allocated(device)
    elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
        device = torch.device("mps")
        total_memory = torch.mps.driver_allocated_memory()
        allocated_memory = total_memory - torch.mps.recommended_max_memory()
        reserved_memory = 0
    else:
        device = torch.device("cpu")
        total_memory = None
        reserved_memory = 0
        allocated_memory = 0
    return device, total_memory, reserved_memory, allocated_memory
class RequestStatus(Enum):
    PENDING = "pending"
    PREFILLING = "prefilling"
    PREFILLING_SPLIT = "prefilling_split"
    SPLIT_PENDING_REMAINDER = "split_pending_remainder"
    DECODING = "decoding"
    FINISHED = "finished"
    FAILED = "failed"
@dataclass
class GenerationOutput:
    request_id: str
    prompt_ids: list[int] = field(default_factory=list)
    generated_tokens: list[int] = field(default_factory=list)
    logprobs: list[float] = field(default_factory=list)
    error: Optional[str] = None
    status: RequestStatus = RequestStatus.PENDING
    created_time: float = field(default_factory=time.time)
@dataclass
class RequestState:
    request_id: str
    full_prompt_ids: Optional[list[int]] = None
    prompt_ids: Optional[list[int]] = None
    remaining_prompt_ids: list[int] = field(default_factory=list)
    static_outputs: list[int] = field(default_factory=list)
    allocated_blocks: int = 0
    position_offset: int = 0
    _status: RequestStatus = RequestStatus.PENDING
    max_new_tokens: int = 20
    eos_token_id: int = -1
    created_time: float = field(default_factory=time.time)
    error: Optional[str] = None
    lifespan: tuple[float, float] = (-1, -1)
    @property
    def status(self) -> RequestStatus:
        return self._status
    @status.setter
    def status(self, value: RequestStatus):
        if self._status == RequestStatus.PENDING:
            self.lifespan = (time.time(), -1)
        elif value == RequestStatus.FINISHED:
            self.lifespan = (self.lifespan[0], time.time())
            self.log_end_of_request()
        self._status = value
    def log_end_of_request(self):
        prefill_len = len(self.full_prompt_ids)
        decode_len = self.generated_len()
        start_time = self.lifespan[0] - self.created_time
        end_time = self.lifespan[1] - self.created_time
        logger.info(
            f"Request {self.request_id} finished: {prefill_len = } {decode_len = } {start_time = } {end_time = }"
        )
    def current_len(self) -> int:
        return self.position_offset
    def generated_len(self) -> int:
        return len(self.static_outputs)
    @traced
    def update_with_token(self, token_id: int) -> bool:
        if self.status != RequestStatus.DECODING:
            return False
        is_eos = token_id == self.eos_token_id and self.eos_token_id != -1
        is_max_len = self.generated_len() >= self.max_new_tokens
        if not (is_max_len and not is_eos):
            self.static_outputs.extend([token_id])
        if is_eos or is_max_len:
            self.status = RequestStatus.FINISHED
            return True
        return False
    def __repr__(self):
        msg = [
            f"request_id={self.request_id}",
            f"status={self._status}",
            f"out_tokens={self.generated_len()}",
            f"query_length={len(self.prompt_ids)}",
            f"remaining_tokens={len(self.remaining_prompt_ids)}",
            f"kv_length={self.position_offset}",
            f"full_prompt_length={len(self.full_prompt_ids)}",
            f"allocated_blocks={self.allocated_blocks}",
            f"generated_tokens={self.static_outputs}",
        ]
        return "RequestState(\n\t" + ",\n\t".join(msg) + "\n)"
    def to_generation_output(self):
        return GenerationOutput(
            request_id=self.request_id,
            prompt_ids=self.full_prompt_ids,
            status=self.status,
            generated_tokens=self.static_outputs,
            logprobs=[],
            error=self.error,
        )