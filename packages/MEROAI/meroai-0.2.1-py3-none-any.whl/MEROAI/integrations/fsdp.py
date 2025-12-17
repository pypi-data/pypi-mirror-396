from __future__ import annotations
import os
from typing import TYPE_CHECKING
from ..utils import is_torch_available, strtobool
if TYPE_CHECKING:
    from torch import nn
def is_fsdp_managed_module(module: nn.Module) -> bool:
    if not is_torch_available():
        return False
    import torch
    if not torch.distributed.is_available():
        return False
    import torch.distributed.fsdp
    return isinstance(module, torch.distributed.fsdp.FullyShardedDataParallel) or getattr(
        module, "_is_fsdp_managed_module", False
    )
def is_fsdp_enabled():
    if is_torch_available():
        import torch
        return (
            torch.distributed.is_available()
            and torch.distributed.is_initialized()
            and strtobool(os.environ.get("ACCELERATE_USE_FSDP", "False")) == 1
            and strtobool(os.environ.get("FSDP_CPU_RAM_EFFICIENT_LOADING", "False")) == 1
        )
    return False