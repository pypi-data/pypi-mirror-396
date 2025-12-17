from __future__ import annotations
import math
import operator
import os
import re
from functools import partial, reduce
import torch
import torch.distributed as dist
from torch import nn
from ..distributed import DistributedConfig
from ..utils import is_torch_greater_or_equal, logging
from ..utils.generic import GeneralInterface
logger = logging.get_logger(__name__)
_torch_distributed_available = torch.distributed.is_available()
if is_torch_greater_or_equal("2.5") and _torch_distributed_available:
    from torch.distributed.tensor import DTensor, Placement, Replicate, Shard
def initialize_tensor_parallelism(tp_plan, tp_size=None):
    if tp_plan is None:
        return None, None, None
    if not is_torch_greater_or_equal("2.5"):
        raise OSError("Tensor parallel is only supported for `torch>=2.5`.")
    device_type = torch._C._get_accelerator().type
    current_device = getattr(torch, device_type)
    if not torch.distributed.is_initialized():
        try:
            rank = int(os.environ["RANK"])
            local_rank = int(os.environ["LOCAL_RANK"])
            world_size = int(os.environ["WORLD_SIZE"])
            backend_map = {"cuda": "nccl", "cpu": "gloo", "xpu": "xccl", "hpu": "hccl"}
            backend = backend_map.get(device_type)
            if device_type == "cpu" and int(os.environ.get("CCL_WORKER_COUNT", "0")):
                backend = "ccl"
            if device_type == "xpu" and not is_torch_greater_or_equal("2.8", accept_dev=True):
                backend = "ccl"
            torch.distributed.init_process_group(backend=backend, rank=rank, world_size=world_size)
            current_device = getattr(torch, device_type)
            if device_type != "cpu":
                current_device.set_device(local_rank)
        except Exception as e:
            raise OSError(
                "We tried to initialize torch.distributed for you, but it failed. Make "
                "sure you init torch distributed in your script to use `tp_plan='auto'`."
            ) from e
    if device_type != "cpu":
        current_device.set_device(int(os.environ["LOCAL_RANK"]))
    index = current_device.current_device() if device_type != "cpu" else None
    tp_device = torch.device(device_type, index)
    if index is not None and index > 0:
        import sys
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")
    device_map = tp_device
    tp_size = tp_size if tp_size is not None else torch.distributed.get_world_size()
    device_mesh = torch.distributed.init_device_mesh(tp_device.type, (tp_size,))
    return tp_device, device_map, device_mesh, tp_size
def _blocks_to_block_sizes(total_size: int, blocks: int | list[int]) -> list[int]:
    if isinstance(blocks, list):
        total_blocks = sum(blocks)
        assert total_size % total_blocks == 0, f"Cannot split {total_size} in proportional blocks: {blocks}"
        part_size = total_size // total_blocks
        return [part_size * block for block in blocks]
    else:
        assert total_size % blocks == 0, f"Prepacked is not divisible by {blocks}"
        single_size = total_size // blocks
        return [single_size] * blocks
def _get_parameter_tp_plan(parameter_name: str, tp_plan: dict[str, str], is_weight=True) -> str | None:
    generic_param_name = re.sub(r"\d+", "*", parameter_name)
    if generic_param_name in tp_plan:
        return tp_plan[generic_param_name]
    elif "." in generic_param_name and generic_param_name.rsplit(".", 1)[0] in tp_plan and is_weight:
        return tp_plan[generic_param_name.rsplit(".", 1)[0]]
    return None
str_to_dtype = {
    "BOOL": torch.bool,
    "U8": torch.uint8,
    "I8": torch.int8,
    "I16": torch.int16,
    "F16": torch.float16,
    "BF16": torch.bfloat16,
    "I32": torch.int32,
    "F32": torch.float32,
    "F64": torch.float64,
    "I64": torch.int64,
    "F8_E4M3": torch.float8_e4m3fn,
}
def get_packed_weights(param, empty_param, device_mesh, rank, dim):
    slice_ = param
    total_size = empty_param.shape[dim]
    world_size = device_mesh.size()
    block_sizes = _blocks_to_block_sizes(total_size=total_size, blocks=2)
    tensors_slices = []
    block_offset = 0
    for block_size in block_sizes:
        shard_block_size = block_size // world_size
        start = rank * shard_block_size
        stop = (rank + 1) * shard_block_size
        tensors_slices += range(block_offset + start, block_offset + stop)
        block_offset += block_size
    slice_dtype = slice_.get_dtype()
    casted = False
    if slice_dtype == "F8_E4M3" or slice_dtype == "F8_E5M2":
        slice_ = slice_[...].to(torch.float16)
        casted = True
    if dim == 0:
        tensor = slice_[tensors_slices, ...]
    elif dim == 1 or dim == -2:
        tensor = slice_[:, tensors_slices, ...]
    elif dim == 2 or dim == -1:
        tensor = slice_[..., tensors_slices]
    else:
        raise ValueError(f"Unsupported dim {dim}, only dim 0, 1 or 2 are supported")
    if casted:
        return tensor
    else:
        return tensor.to(str_to_dtype[slice_dtype])
def repack_weights(
    packed_parameter: torch.Tensor,
    sharded_dim: int,
    world_size: int,
    num_blocks: int = 2,
) -> torch.Tensor:
    if num_blocks != 2:
        raise ValueError(
            "Num blocks different from 2 is not supported yet. This is most likely a bug in your implementation as we only pack gate and up projections together."
        )
    actual_sharded_dim = sharded_dim if sharded_dim >= 0 else sharded_dim + packed_parameter.ndim
    total_size_on_sharded_dim = packed_parameter.shape[actual_sharded_dim]
    original_block_size_on_dim = total_size_on_sharded_dim // num_blocks
    shard_chunk_size = original_block_size_on_dim // world_size
    prefix_shape = packed_parameter.shape[:actual_sharded_dim]
    suffix_shape = packed_parameter.shape[actual_sharded_dim + 1 :]
    tensor_view = packed_parameter.view(
        *prefix_shape,
        world_size,
        num_blocks,
        shard_chunk_size,
        *suffix_shape,
    )
    axis_ws_abs = len(prefix_shape)
    axis_npp_abs = len(prefix_shape) + 1
    permute_order = list(range(tensor_view.ndim))
    permute_order[axis_ws_abs], permute_order[axis_npp_abs] = permute_order[axis_npp_abs], permute_order[axis_ws_abs]
    tensor_permuted = tensor_view.permute(*permute_order)
    final_ordered_tensor = tensor_permuted.reshape_as(packed_parameter)
    return final_ordered_tensor
def get_tensor_shard(param, empty_param, device_mesh, rank, dim):
    param_dim = empty_param.dim()
    if dim < 0:
        dim = param_dim + dim
    if dim >= param_dim:
        raise ValueError(f"dim {dim} is out of bounds for tensor of dimension {param_dim}")
    mesh_shape = device_mesh.shape
    world_size = reduce(operator.mul, mesh_shape)
    if rank >= world_size:
        raise ValueError(f"Rank {rank} is out of bounds for mesh size {world_size}")
    shard_size = math.ceil(empty_param.shape[dim] / world_size)
    start = rank * shard_size
    end = min(start + shard_size, empty_param.shape[dim])
    slice_indices = [slice(None)] * param_dim
    if start < empty_param.shape[dim]:
        slice_indices[dim] = slice(start, end)
        return param[tuple(slice_indices)]
    dimensions = list(param.shape)
    dimensions[dim] = 0
    return torch.empty(tuple(dimensions), dtype=torch.int64)
def distribute_module(
    module: nn.Module,
    device_mesh=None,
    input_fn=None,
    output_fn=None,
) -> nn.Module:
    if len(module._forward_pre_hooks) == 0:
        if input_fn is not None:
            module.register_forward_pre_hook(lambda mod, inputs: input_fn(mod, inputs, device_mesh))
        if output_fn is not None:
            module.register_forward_hook(lambda mod, inputs, outputs: output_fn(mod, outputs, device_mesh))
    return module
class TensorParallelLayer:
    use_dtensor = True
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh): ...
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh): ...
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        raise NotImplementedError
    def prepare_module_tp(self, module: nn.Module, device_mesh) -> nn.Module:
        if self.use_dtensor:
            distribute_module(
                module,
                device_mesh,
                partial(self._prepare_input_fn, self.input_layouts, self.desired_input_layouts),
                partial(self._prepare_output_fn, self.output_layouts, self.use_local_output),
            )
class GatherParallel(TensorParallelLayer):
    def __init__(
        self,
        *,
        input_layouts: Placement | None = None,
        output_layouts: Placement | None = None,
        use_local_output: bool = True,
    ):
        super().__init__()
        self.input_layouts = (input_layouts or Replicate(),)
        self.output_layouts = output_layouts
        self.desired_input_layouts = (Replicate(),)
        self.use_local_output = use_local_output
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        mod.expert_parallel_group = device_mesh.get_group()
        if inputs and isinstance(inputs[0], DTensor):
            inputs = inputs[0].to_local()
        return inputs
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        if isinstance(outputs, torch.Tensor):
            dist.all_reduce(outputs, op=dist.ReduceOp.SUM, async_op=False)
        else:
            dist.all_reduce(outputs[0], op=dist.ReduceOp.SUM, async_op=False)
        return outputs
    def prepare_module_tp(self, module: nn.Module, device_mesh) -> nn.Module:
        distribute_module(
            module,
            device_mesh,
            partial(self._prepare_input_fn, None, None),
            partial(self._prepare_output_fn, None, None),
        )
class IsolatedParallel(TensorParallelLayer):
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh=None):
        input_tensor = inputs[0]
        if isinstance(input_tensor, DTensor):
            input_tensor = input_tensor.to_local()
        return input_tensor
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh=None):
        return outputs
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        param = param[...].to(param_casting_dtype)
        if to_contiguous:
            param = param.contiguous()
        param = param / device_mesh.size()
        return param
    def prepare_module_tp(self, module: nn.Module, device_mesh) -> nn.Module:
        distribute_module(
            module,
            device_mesh,
            partial(self._prepare_input_fn, None, None),
            partial(self._prepare_output_fn, None, None),
        )
class ReplicateParallel(TensorParallelLayer):
    def __init__(self, *, use_dtensor=True, use_local_output=True):
        super().__init__()
        self.input_layouts = (Replicate(),)
        self.output_layouts = (Replicate(),)
        self.desired_input_layouts = (Replicate(),)
        self.use_local_output = use_local_output
        self.use_dtensor = use_dtensor
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        input_tensor = inputs[0]
        if not isinstance(input_tensor, DTensor):
            input_tensor = DTensor.from_local(input_tensor, device_mesh, input_layouts, run_check=False)
        return input_tensor
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        return outputs.to_local() if use_local_output and isinstance(outputs, DTensor) else outputs
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        param = param[...].to(param_casting_dtype)
        if to_contiguous:
            param = param.contiguous()
        param = DTensor.from_local(param, device_mesh, [Replicate()], run_check=False)
        return param
class ColwiseParallel(TensorParallelLayer):
    def __init__(
        self,
        *,
        input_layouts: Placement | None = None,
        output_layouts: Placement | None = None,
        use_local_output: bool = True,
        use_dtensor=True,
    ):
        super().__init__()
        self.input_layouts = (input_layouts or Replicate(),)
        self.output_layouts = (output_layouts or Shard(-1),)
        self.desired_input_layouts = (Replicate(),)
        self.use_local_output = use_local_output
        self.use_dtensor = use_dtensor
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        input_tensor = inputs[0]
        if not isinstance(input_tensor, DTensor):
            input_tensor = DTensor.from_local(input_tensor, device_mesh, input_layouts, run_check=False)
        if input_layouts != desired_input_layouts:
            input_tensor = input_tensor.redistribute(placements=desired_input_layouts, async_op=False)
        return input_tensor
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        if param_type == "bias":
            parameter = get_tensor_shard(param, empty_param, device_mesh, rank, -1)
            shard = [Shard(-1)]
        else:
            shard = [Shard(-2)]
            parameter = get_tensor_shard(param, empty_param, device_mesh, rank, -2)
        parameter = parameter.to(param_casting_dtype)
        if to_contiguous:
            parameter = parameter.contiguous()
        if self.use_dtensor:
            parameter = DTensor.from_local(
                parameter, device_mesh, shard, run_check=False, shape=empty_param.size(), stride=empty_param.stride()
            )
        return nn.Parameter(parameter, requires_grad=parameter.is_floating_point())
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        if outputs.placements != output_layouts:
            outputs = outputs.redistribute(placements=output_layouts, async_op=False)
        return outputs.to_local() if use_local_output and isinstance(outputs, DTensor) else outputs
class PackedColwiseParallel(ColwiseParallel):
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        parameter = get_packed_weights(param, empty_param, device_mesh, rank, -2)
        parameter = parameter.to(param_casting_dtype)
        if to_contiguous:
            parameter = parameter.contiguous()
        if self.use_dtensor:
            parameter = DTensor.from_local(parameter, device_mesh, [Shard(-2)], run_check=False)
        return nn.Parameter(parameter, requires_grad=parameter.is_floating_point())
class RowwiseParallel(TensorParallelLayer):
    def __init__(
        self,
        *,
        input_layouts: Placement | None = None,
        output_layouts: Placement | None = None,
        use_local_output: bool = True,
        use_dtensor=True,
    ):
        super().__init__()
        self.input_layouts = (input_layouts or Shard(-1),)
        self.output_layouts = (output_layouts or Replicate(),)
        self.use_local_output = use_local_output
        self.use_dtensor = use_dtensor
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        if param_type != "bias":
            parameter = get_tensor_shard(param, empty_param, device_mesh, rank, -1)
            shard = [Shard(-1)]
        else:
            shard = [Replicate()]
            parameter = param[:]
        parameter = parameter.to(param_casting_dtype)
        if to_contiguous:
            parameter = parameter.contiguous()
        if self.use_dtensor:
            parameter = DTensor.from_local(
                parameter, device_mesh, shard, run_check=False, shape=empty_param.size(), stride=empty_param.stride()
            )
        return nn.Parameter(parameter, requires_grad=parameter.is_floating_point())
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        if hasattr(mod, "bias") and mod.bias is not None:
            mod._bias = mod.bias.to_local()
            mod.bias = None
        input_tensor = inputs[0]
        if not isinstance(input_tensor, DTensor):
            input_tensor = DTensor.from_local(input_tensor, device_mesh, input_layouts, run_check=False)
        if input_layouts != desired_input_layouts:
            input_tensor = input_tensor.redistribute(placements=desired_input_layouts, async_op=True)
        return input_tensor
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        if outputs.placements != output_layouts:
            outputs = outputs.redistribute(placements=output_layouts, async_op=True)
        outputs = outputs.to_local()
        if hasattr(mod, "_bias"):
            outputs = outputs + mod._bias
        return outputs
    def prepare_module_tp(self, module: nn.Module, device_mesh) -> nn.Module:
        module._distribute_module_applied = True
        if self.use_dtensor:
            if isinstance(module, nn.Linear):
                self.desired_input_layouts: tuple[Placement, ...] = (Shard(-1),)
            elif isinstance(module, nn.Embedding):
                self.desired_input_layouts = (Replicate(),)
            elif isinstance(module, nn.Parameter):
                self.desired_input_layouts = (Shard(-1),)
            else:
                raise NotImplementedError("RowwiseParallel currently only support nn.Linear and nn.Embedding!")
            distribute_module(
                module,
                device_mesh,
                partial(self._prepare_input_fn, self.input_layouts, self.desired_input_layouts),
                partial(self._prepare_output_fn, self.output_layouts, self.use_local_output),
            )
class PackedRowwiseParallel(RowwiseParallel):
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        parameter = get_packed_weights(param, empty_param, device_mesh, rank, -1)
        parameter = parameter.to(param_casting_dtype)
        if to_contiguous:
            parameter = parameter.contiguous()
        if self.use_dtensor:
            parameter = DTensor.from_local(parameter, device_mesh, [Shard(-1)], run_check=False)
        return nn.Parameter(parameter, requires_grad=parameter.is_floating_point())
class SequenceParallel(TensorParallelLayer):
    def __init__(self, *, sequence_dim: int = 1, use_local_output: bool = False, use_dtensor=False):
        super().__init__()
        self.input_layouts = (Replicate(),)
        self.desired_input_layouts = (Shard(1),)
        self.output_layouts = (Replicate(),)
        self.use_local_output = use_local_output
        self.use_dtensor = True
        self.sequence_sharding = (Shard(sequence_dim),)
        self.use_local_output = use_local_output
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        input_tensor = inputs[0]
        if not isinstance(input_tensor, DTensor):
            input_tensor = DTensor.from_local(input_tensor, device_mesh, input_layouts, run_check=False)
        if input_layouts != desired_input_layouts:
            input_tensor = input_tensor.redistribute(placements=desired_input_layouts, async_op=True)
        return input_tensor
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        outputs = outputs.redistribute(
            placements=(Replicate(),), async_op=True
        )
        return outputs.to_local()
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        parameter = param[...]
        parameter = parameter.to(param_casting_dtype)
        if to_contiguous:
            parameter = parameter.contiguous()
        if self.use_dtensor:
            parameter = DTensor.from_local(parameter, device_mesh, [Replicate()], run_check=False)
        return nn.Parameter(parameter, requires_grad=parameter.is_floating_point())
class GroupedGemmParallel(TensorParallelLayer):
    def __init__(self):
        super().__init__()
        self.use_dtensor = False
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        ep_rank = rank
        global_num_experts = empty_param.shape[0]
        if global_num_experts % device_mesh.size() != 0:
            raise ValueError(
                f"Global number of experts must be divisible by number of devices: {global_num_experts} % {device_mesh.size()} != 0"
            )
        local_num_experts = global_num_experts // device_mesh.size()
        param = param[ep_rank * local_num_experts : (ep_rank + 1) * local_num_experts].to(param_casting_dtype)
        if to_contiguous:
            param = param.contiguous()
        return param
class RouterParallel(TensorParallelLayer):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.use_dtensor = False
    @staticmethod
    def _prepare_input_fn(input_layouts, desired_input_layouts, mod, inputs, device_mesh):
        input_tensor = inputs[0]
        if isinstance(input_tensor, DTensor):
            raise NotImplementedError("RouterParallel does not support DTensor input for now")
        return input_tensor
    @staticmethod
    def _prepare_output_fn(output_layouts, use_local_output, mod, outputs, device_mesh):
        ep_rank, ep_size = device_mesh.get_local_rank(), device_mesh.size()
        if mod.num_experts % ep_size != 0:
            raise ValueError(
                f"The number of experts must be divisible by number of ep_size: {mod.num_experts} % {ep_size} != 0"
            )
        num_local_experts = mod.num_experts // ep_size
        router_scores, router_indices = outputs
        router_scores = router_scores[:, ep_rank * num_local_experts : (ep_rank + 1) * num_local_experts]
        router_indices = router_indices.masked_fill((router_indices // num_local_experts) != ep_rank, -1)
        if num_local_experts > 1:
            router_indices = torch.fmod(router_indices, num_local_experts)
        else:
            router_indices = router_indices.masked_fill(router_indices > 0, 0).masked_fill(router_indices < 0, -1)
        router_indices = router_indices.masked_fill(
            router_indices == -1, num_local_experts
        )
        return router_scores, router_indices
    def partition_tensor(self, param, empty_param, param_type, param_casting_dtype, to_contiguous, rank, device_mesh):
        param = param[...].to(param_casting_dtype)
        if to_contiguous:
            param = param.contiguous()
        return param
    def prepare_module_tp(self, module: nn.Module, device_mesh) -> nn.Module:
        distribute_module(
            module,
            device_mesh,
            partial(self._prepare_input_fn, None, None),
            partial(self._prepare_output_fn, None, None),
        )
class ParallelInterface(GeneralInterface):
    _global_mapping = (
        {
            "colwise": ColwiseParallel(),
            "rowwise": RowwiseParallel(),
            "colwise_rep": ColwiseParallel(output_layouts=Replicate()),
            "rowwise_rep": RowwiseParallel(input_layouts=Replicate()),
            "local_colwise": ColwiseParallel(use_dtensor=False),
            "local_rowwise": RowwiseParallel(use_dtensor=False),
            "local": IsolatedParallel(),
            "gather": GatherParallel(),
            "local_packed_rowwise": PackedRowwiseParallel(use_dtensor=False),
            "sequence_parallel": SequenceParallel(),
            "replicate": ReplicateParallel(),
            "grouped_gemm": GroupedGemmParallel(),
            "ep_router": RouterParallel(),
        }
        if is_torch_greater_or_equal("2.5") and _torch_distributed_available
        else {}
    )
ALL_PARALLEL_STYLES: ParallelInterface = ParallelInterface()
def convert_local_tensor_to_dtensor(
    parameter: torch.Tensor, parameter_name: str, device_mesh, tp_plan: dict[str, str]
) -> DTensor:
    _, param_type = parameter_name.rsplit(".", 1) if "." in parameter_name else parameter_name
    tp_style = _get_parameter_tp_plan(parameter_name, tp_plan)
    if not tp_style:
        return parameter
    if tp_style not in ["local_packed_rowwise", "local_rowwise", "local_colwise"]:
        return parameter
    if tp_style == "local_packed_rowwise":
        placements = [Shard(-1)]
    elif tp_style == "local_rowwise":
        if param_type == "bias":
            placements = [Replicate()]
        else:
            placements = [Shard(-1)]
    elif tp_style == "local_colwise":
        if param_type == "bias":
            placements = [Shard(-1)]
        else:
            placements = [Shard(-2)]
    return DTensor.from_local(parameter, device_mesh, placements, run_check=False)
def replace_state_dict_local_with_dtensor(
    state_dict: dict[str, torch.Tensor],
    tp_plan: dict[str, str],
    device_mesh,
) -> dict[str, torch.Tensor]:
    for key, value in state_dict.items():
        if isinstance(value, torch.Tensor) and not isinstance(value, DTensor):
            state_dict[key] = convert_local_tensor_to_dtensor(value, key, device_mesh, tp_plan)
    return state_dict
def add_tensor_parallel_hooks_to_module(
    model, module, tp_plan, layer_name, current_module_plan, device_mesh, parameter_name=None
):
    if current_module_plan is not None:
        tp_layer = ALL_PARALLEL_STYLES[current_module_plan]
        try:
            tp_layer.prepare_module_tp(module, device_mesh)
        except NotImplementedError as e:
            print(
                f"Trying to prepare {layer_name}, but it's not supported. Corresponding module: {module} Fix it's TP plan: {e}"
            )
        module._hf_tp_plan = current_module_plan
        module.__repr__ = lambda: f"{module.__repr__()}\nTP Plan: {current_module_plan}"
def shard_and_distribute_module(
    model, param, empty_param, parameter_name, param_casting_dtype, is_contiguous, rank, device_mesh
):
    param_name, param_type = parameter_name.rsplit(".", 1) if "." in parameter_name else parameter_name
    tp_plan = model.tp_plan or {}
    module_to_tp = model.get_submodule(param_name)
    rank = int(rank)
    current_shard_plan = _get_parameter_tp_plan(parameter_name, tp_plan)
    if dist.get_rank() == 0:
        if current_shard_plan is None:
            logger.info(f"Tensor sharding plan for {param_name} not found, using default 'replicate' plan.")
        else:
            logger.info(f"Tensor sharding plan for {param_name}: {current_shard_plan}")
    if current_shard_plan is not None:
        try:
            tp_layer = ALL_PARALLEL_STYLES[current_shard_plan]
            param = tp_layer.partition_tensor(
                param, empty_param, param_type, param_casting_dtype, is_contiguous, rank, device_mesh
            )
        except NotImplementedError as e:
            print(
                f"Trying to prepare {parameter_name}, but it's not supported. Corresponding module: {module_to_tp} Fix it's TP plan, current layer: {tp_layer} : {e}"
            )
    else:
        param = param[:].to(param_casting_dtype)
    if not isinstance(param, torch.nn.Parameter):
        param = torch.nn.Parameter(param, requires_grad=empty_param.is_floating_point())
    setattr(module_to_tp, param_type, param)
    return param
def verify_tp_plan(expected_keys: list[str], tp_plan: dict[str, str] | None):
    if tp_plan is None:
        return
    generic_keys = {re.sub(r"\d+", "*", key) for key in expected_keys}
    unsharded_layers = set(generic_keys)
    unused_rules = tp_plan
    for key in generic_keys:
        param_name = key.rsplit(".", 1)[0] if "." in key else key
        generic_param_name = re.sub(r"\d+", "*", param_name)
        if generic_param_name in tp_plan:
            unused_rules.pop(generic_param_name)
            unsharded_layers.discard(key)
        elif "." in generic_param_name and (parent_param_name := generic_param_name.rsplit(".", 1)[0]) in tp_plan:
            unused_rules.pop(parent_param_name)
            unsharded_layers.discard(key)
        else:
            pass
    if len(unused_rules) > 0:
        logger.warning(f"The following TP rules were not applied on any of the layers: {unused_rules}")
    if len(unsharded_layers) > 0:
        logger.warning(f"The following layers were not sharded: {', '.join(unsharded_layers)}")
def distribute_model(model, distributed_config, device_mesh, tp_size):
    model._tp_size = tp_size
    model._device_mesh = device_mesh
    if distributed_config is not None:
        if isinstance(distributed_config, dict):
            distributed_config = DistributedConfig.from_dict(distributed_config)
        model.config.distributed_config = distributed_config
    model_plan = model.tp_plan
    if model_plan is not None and is_torch_greater_or_equal("2.5") and _torch_distributed_available:
        for v in model_plan.values():
            if v not in ALL_PARALLEL_STYLES:
                raise ValueError(f"Unsupported tensor parallel style {v}. Supported styles are {ALL_PARALLEL_STYLES}")
        for name, module in model.named_modules():
            if not getattr(module, "_is_hooked", False):
                plan = _get_parameter_tp_plan(parameter_name=name, tp_plan=model_plan, is_weight=False)
                add_tensor_parallel_hooks_to_module(
                    model=model,
                    module=module,
                    tp_plan=model_plan,
                    layer_name="",
                    current_module_plan=plan,
                    device_mesh=device_mesh,
                )
            module._is_hooked = True
    return model