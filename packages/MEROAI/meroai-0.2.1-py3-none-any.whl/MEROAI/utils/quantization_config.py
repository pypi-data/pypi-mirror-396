import copy
import dataclasses
import importlib.metadata
import json
import os
from dataclasses import dataclass, is_dataclass
from enum import Enum
from inspect import Parameter, signature
from typing import Any, Optional, Union
from packaging import version
from ..utils import (
    is_auto_awq_available,
    is_compressed_tensors_available,
    is_gptqmodel_available,
    is_hqq_available,
    is_quark_available,
    is_torch_available,
    is_torchao_available,
    logging,
)
from .import_utils import is_auto_gptq_available
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class QuantizationMethod(str, Enum):
    BITS_AND_BYTES = "bitsandbytes"
    GPTQ = "gptq"
    AWQ = "awq"
    AQLM = "aqlm"
    VPTQ = "vptq"
    QUANTO = "quanto"
    EETQ = "eetq"
    HIGGS = "higgs"
    HQQ = "hqq"
    COMPRESSED_TENSORS = "compressed-tensors"
    FBGEMM_FP8 = "fbgemm_fp8"
    TORCHAO = "torchao"
    BITNET = "bitnet"
    SPQR = "spqr"
    FP8 = "fp8"
    QUARK = "quark"
    FPQUANT = "fp_quant"
    AUTOROUND = "auto-round"
    MXFP4 = "mxfp4"
class AWQLinearVersion(str, Enum):
    GEMM = "gemm"
    GEMV = "gemv"
    EXLLAMA = "exllama"
    IPEX = "ipex"
    @staticmethod
    def from_str(version: str):
        version = version.lower()
        if version == "gemm":
            return AWQLinearVersion.GEMM
        elif version == "gemv":
            return AWQLinearVersion.GEMV
        elif version == "exllama":
            return AWQLinearVersion.EXLLAMA
        elif version == "ipex":
            return AWQLinearVersion.IPEX
        else:
            raise ValueError(f"Unknown AWQLinearVersion {version}")
class AwqBackendPackingMethod(str, Enum):
    AUTOAWQ = "autoawq"
    LLMAWQ = "llm-awq"
@dataclass
class QuantizationConfigMixin:
    quant_method: QuantizationMethod
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        config = cls(**config_dict)
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
                to_remove.append(key)
        for key in to_remove:
            kwargs.pop(key, None)
        if return_unused_kwargs:
            return config, kwargs
        else:
            return config
    def to_json_file(self, json_file_path: Union[str, os.PathLike]):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            config_dict = self.to_dict()
            json_string = json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
            writer.write(json_string)
    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self.__dict__)
    def __iter__(self):
        for attr, value in copy.deepcopy(self.__dict__).items():
            yield attr, value
    def __repr__(self):
        return f"{self.__class__.__name__} {self.to_json_string()}"
    def to_json_string(self, use_diff: bool = True) -> str:
        if use_diff is True:
            config_dict = self.to_diff_dict()
        else:
            config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
    def update(self, **kwargs):
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                to_remove.append(key)
        unused_kwargs = {key: value for key, value in kwargs.items() if key not in to_remove}
        return unused_kwargs
@dataclass
class AutoRoundConfig(QuantizationConfigMixin):
    def __init__(
        self,
        bits: int = 4,
        group_size: int = 128,
        sym: bool = True,
        backend: str = "auto",
        **kwargs,
    ):
        self.bits = bits
        self.group_size = group_size
        self.sym = sym
        self.backend = backend
        self.packing_format = "auto_round:gptq"
        if kwargs is not None:
            for key, value in kwargs.items():
                setattr(self, key, value)
        self.quant_method = QuantizationMethod.AUTOROUND
        self.post_init()
    def post_init(self):
        r
        if self.bits not in [2, 3, 4, 8]:
            raise ValueError(f"Only support quantization to [2,3,4,8] bits but found {self.bits}")
        if self.group_size != -1 and self.group_size <= 0:
            raise ValueError("group_size must be greater than 0 or equal to -1")
    def get_loading_attributes(self):
        loading_attributes_dict = {"backend": self.backend}
        return loading_attributes_dict
    def to_dict(self):
        config_dict = super().to_dict()
        return config_dict
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        quant_method = config_dict["quant_method"]
        if "auto-round" not in quant_method and "gptq" not in quant_method and "awq" not in quant_method:
            raise NotImplementedError(
                "Failed to convert to auto_round format. Only `gptqv1`, `awq`, and `auto-round` formats are supported."
            )
        if "gptq" in quant_method and "meta" in config_dict:
            raise NotImplementedError("Failed to convert gptq format to auto_round format. Only supports `gptqv1`")
        if "awq" in quant_method and config_dict.get("version", "gemm") != "gemm":
            raise NotImplementedError(
                "Failed to convert awq format to auto_round format. Only supports awq format with gemm version"
            )
        if "auto-round" not in quant_method:
            config_dict["packing_format"] = f"auto_round:{quant_method}"
        return super().from_dict(config_dict, return_unused_kwargs=return_unused_kwargs, **kwargs)
@dataclass
class HqqConfig(QuantizationConfigMixin):
    def __init__(
        self,
        nbits: int = 4,
        group_size: int = 64,
        view_as_float: bool = False,
        axis: Optional[int] = None,
        dynamic_config: Optional[dict] = None,
        skip_modules: list[str] = ["lm_head"],
        **kwargs,
    ):
        if is_hqq_available():
            from hqq.core.quantize import BaseQuantizeConfig as HQQBaseQuantizeConfig
        else:
            raise ImportError(
                "A valid HQQ version (>=0.2.1) is not available. Please follow the instructions to install it: `https://github.com/mobiusml/hqq/`."
            )
        for deprecated_key in ["quant_zero", "quant_scale", "offload_meta"]:
            if deprecated_key in kwargs:
                logger.info(
                    deprecated_key + " is deprecated. This parameter will be ignored in quantization settings."
                )
        if axis is None:
            axis = 1
            logger.info("Setting axis=1 as faster backends such as TorchAO or BitBlas are only compatible with it.")
        if axis not in [0, 1]:
            raise ValueError("Invalid axis value. Only 0 and 1 are allowed.")
        if dynamic_config is not None:
            self.quant_config = {}
            for key in dynamic_config:
                self.quant_config[key] = HQQBaseQuantizeConfig(**dynamic_config[key])
        else:
            self.quant_config = HQQBaseQuantizeConfig(
                **{
                    "nbits": nbits,
                    "group_size": group_size,
                    "view_as_float": view_as_float,
                    "axis": axis,
                }
            )
        self.quant_method = QuantizationMethod.HQQ
        self.skip_modules = skip_modules
        self.post_init()
    def post_init(self):
        pass
    @classmethod
    def from_dict(cls, config: dict[str, Any]):
        instance = cls()
        instance.quant_config = config["quant_config"]
        instance.skip_modules = config["skip_modules"]
        return instance
    def to_dict(self) -> dict[str, Any]:
        return {
            "quant_config": self.quant_config,
            "quant_method": self.quant_method,
            "skip_modules": self.skip_modules,
        }
    def __repr__(self):
        config_dict = self.to_dict()
        return f"{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n"
    def to_diff_dict(self) -> dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = HqqConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]:
                serializable_config_dict[key] = value
        return serializable_config_dict
@dataclass
class BitsAndBytesConfig(QuantizationConfigMixin):
    def __init__(
        self,
        load_in_8bit=False,
        load_in_4bit=False,
        llm_int8_threshold=6.0,
        llm_int8_skip_modules=None,
        llm_int8_enable_fp32_cpu_offload=False,
        llm_int8_has_fp16_weight=False,
        bnb_4bit_compute_dtype=None,
        bnb_4bit_quant_type="fp4",
        bnb_4bit_use_double_quant=False,
        bnb_4bit_quant_storage=None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.BITS_AND_BYTES
        if load_in_4bit and load_in_8bit:
            raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
        self._load_in_8bit = load_in_8bit
        self._load_in_4bit = load_in_4bit
        self.llm_int8_threshold = llm_int8_threshold
        self.llm_int8_skip_modules = llm_int8_skip_modules
        self.llm_int8_enable_fp32_cpu_offload = llm_int8_enable_fp32_cpu_offload
        self.llm_int8_has_fp16_weight = llm_int8_has_fp16_weight
        self.bnb_4bit_quant_type = bnb_4bit_quant_type
        self.bnb_4bit_use_double_quant = bnb_4bit_use_double_quant
        if bnb_4bit_compute_dtype is None:
            self.bnb_4bit_compute_dtype = torch.float32
        elif isinstance(bnb_4bit_compute_dtype, str):
            self.bnb_4bit_compute_dtype = getattr(torch, bnb_4bit_compute_dtype)
        elif isinstance(bnb_4bit_compute_dtype, torch.dtype):
            self.bnb_4bit_compute_dtype = bnb_4bit_compute_dtype
        else:
            raise ValueError("bnb_4bit_compute_dtype must be a string or a torch.dtype")
        if bnb_4bit_quant_storage is None:
            self.bnb_4bit_quant_storage = torch.uint8
        elif isinstance(bnb_4bit_quant_storage, str):
            if bnb_4bit_quant_storage not in ["float16", "float32", "int8", "uint8", "float64", "bfloat16"]:
                raise ValueError(
                    "`bnb_4bit_quant_storage` must be a valid string (one of 'float16', 'float32', 'int8', 'uint8', 'float64', 'bfloat16') "
                )
            self.bnb_4bit_quant_storage = getattr(torch, bnb_4bit_quant_storage)
        elif isinstance(bnb_4bit_quant_storage, torch.dtype):
            self.bnb_4bit_quant_storage = bnb_4bit_quant_storage
        else:
            raise ValueError("bnb_4bit_quant_storage must be a string or a torch.dtype")
        if kwargs:
            logger.info(f"Unused kwargs: {list(kwargs.keys())}. These kwargs are not used in {self.__class__}.")
        self.post_init()
    @property
    def load_in_4bit(self):
        return self._load_in_4bit
    @load_in_4bit.setter
    def load_in_4bit(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("load_in_4bit must be a boolean")
        if self.load_in_8bit and value:
            raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
        self._load_in_4bit = value
    @property
    def load_in_8bit(self):
        return self._load_in_8bit
    @load_in_8bit.setter
    def load_in_8bit(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("load_in_8bit must be a boolean")
        if self.load_in_4bit and value:
            raise ValueError("load_in_4bit and load_in_8bit are both True, but only one can be used at the same time")
        self._load_in_8bit = value
    def post_init(self):
        if not isinstance(self.load_in_4bit, bool):
            raise TypeError("load_in_4bit must be a boolean")
        if not isinstance(self.load_in_8bit, bool):
            raise TypeError("load_in_8bit must be a boolean")
        if not isinstance(self.llm_int8_threshold, float):
            raise TypeError("llm_int8_threshold must be a float")
        if self.llm_int8_skip_modules is not None and not isinstance(self.llm_int8_skip_modules, list):
            raise TypeError("llm_int8_skip_modules must be a list of strings")
        if not isinstance(self.llm_int8_enable_fp32_cpu_offload, bool):
            raise TypeError("llm_int8_enable_fp32_cpu_offload must be a boolean")
        if not isinstance(self.llm_int8_has_fp16_weight, bool):
            raise TypeError("llm_int8_has_fp16_weight must be a boolean")
        if self.bnb_4bit_compute_dtype is not None and not isinstance(self.bnb_4bit_compute_dtype, torch.dtype):
            raise TypeError("bnb_4bit_compute_dtype must be torch.dtype")
        if not isinstance(self.bnb_4bit_quant_type, str):
            raise TypeError("bnb_4bit_quant_type must be a string")
        if not isinstance(self.bnb_4bit_use_double_quant, bool):
            raise TypeError("bnb_4bit_use_double_quant must be a boolean")
        if self.load_in_4bit and not version.parse(importlib.metadata.version("bitsandbytes")) >= version.parse(
            "0.39.0"
        ):
            raise ValueError(
                "4 bit quantization requires bitsandbytes>=0.39.0 - please upgrade your bitsandbytes version"
            )
    def is_quantizable(self):
        return self.load_in_8bit or self.load_in_4bit
    def quantization_method(self):
        if self.load_in_8bit:
            return "llm_int8"
        elif self.load_in_4bit and self.bnb_4bit_quant_type == "fp4":
            return "fp4"
        elif self.load_in_4bit and self.bnb_4bit_quant_type == "nf4":
            return "nf4"
        else:
            return None
    def to_dict(self) -> dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        output["bnb_4bit_compute_dtype"] = str(output["bnb_4bit_compute_dtype"]).split(".")[1]
        output["bnb_4bit_quant_storage"] = str(output["bnb_4bit_quant_storage"]).split(".")[1]
        output["load_in_4bit"] = self.load_in_4bit
        output["load_in_8bit"] = self.load_in_8bit
        return output
    def __repr__(self):
        config_dict = self.to_dict()
        return f"{self.__class__.__name__} {json.dumps(config_dict, indent=2, sort_keys=True)}\n"
    def to_diff_dict(self) -> dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = BitsAndBytesConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if value != default_config_dict[key]:
                serializable_config_dict[key] = value
        return serializable_config_dict
class ExllamaVersion(int, Enum):
    ONE = 1
    TWO = 2
@dataclass
class GPTQConfig(QuantizationConfigMixin):
    def __init__(
        self,
        bits: int,
        tokenizer: Any = None,
        dataset: Optional[Union[list[str], str]] = None,
        group_size: int = 128,
        damp_percent: float = 0.1,
        desc_act: bool = False,
        sym: bool = True,
        true_sequential: bool = True,
        checkpoint_format: str = "gptq",
        meta: Optional[dict[str, Any]] = None,
        backend: Optional[str] = None,
        use_cuda_fp16: bool = False,
        model_seqlen: Optional[int] = None,
        block_name_to_quantize: Optional[str] = None,
        module_name_preceding_first_block: Optional[list[str]] = None,
        batch_size: int = 1,
        pad_token_id: Optional[int] = None,
        use_exllama: Optional[bool] = None,
        max_input_length: Optional[int] = None,
        exllama_config: Optional[dict[str, Any]] = None,
        cache_block_outputs: bool = True,
        modules_in_block_to_quantize: Optional[list[list[str]]] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.GPTQ
        self.bits = bits
        self.tokenizer = tokenizer
        self.dataset = dataset
        self.group_size = group_size
        self.damp_percent = damp_percent
        self.desc_act = desc_act
        self.sym = sym
        self.true_sequential = true_sequential
        self.checkpoint_format = checkpoint_format.lower()
        self.meta = meta
        self.backend = backend.lower() if isinstance(backend, str) else backend
        self.use_cuda_fp16 = use_cuda_fp16
        self.model_seqlen = model_seqlen
        self.block_name_to_quantize = block_name_to_quantize
        self.module_name_preceding_first_block = module_name_preceding_first_block
        self.batch_size = batch_size
        self.pad_token_id = pad_token_id
        self.use_exllama = use_exllama
        self.max_input_length = max_input_length
        self.exllama_config = exllama_config
        self.cache_block_outputs = cache_block_outputs
        self.modules_in_block_to_quantize = modules_in_block_to_quantize
        self.post_init()
    def get_loading_attributes(self):
        attributes_dict = copy.deepcopy(self.__dict__)
        loading_attributes = [
            "use_exllama",
            "exllama_config",
            "use_cuda_fp16",
            "max_input_length",
            "backend",
        ]
        loading_attributes_dict = {i: j for i, j in attributes_dict.items() if i in loading_attributes}
        return loading_attributes_dict
    def post_init(self):
        if self.bits not in [2, 3, 4, 8]:
            raise ValueError(f"Only support quantization to [2,3,4,8] bits but found {self.bits}")
        if self.group_size != -1 and self.group_size <= 0:
            raise ValueError("group_size must be greater than 0 or equal to -1")
        if not (0 < self.damp_percent < 1):
            raise ValueError("damp_percent must between 0 and 1.")
        if self.dataset is not None:
            if isinstance(self.dataset, str):
                if self.dataset in ["ptb", "ptb-new"]:
                    raise ValueError(
                    )
                if self.dataset not in ["wikitext2", "c4", "c4-new"]:
                    raise ValueError(
                    )
            elif not isinstance(self.dataset, list):
                raise ValueError(
                )
        if is_gptqmodel_available():
            if self.backend is None:
                self.backend = "auto_trainable" if self.use_exllama is not None and not self.use_exllama else "auto"
        else:
            if self.backend == "auto_trainable":
                self.use_exllama = False
        if self.use_exllama is None:
            self.use_exllama = True
        if self.exllama_config is None:
            self.exllama_config = {"version": ExllamaVersion.ONE}
        else:
            if "version" not in self.exllama_config:
                raise ValueError("`exllama_config` needs to have a `version` key.")
            elif self.exllama_config["version"] not in [ExllamaVersion.ONE, ExllamaVersion.TWO]:
                exllama_version = self.exllama_config["version"]
                raise ValueError(
                    f"Only supported versions are in [ExllamaVersion.ONE, ExllamaVersion.TWO] - not recognized version {exllama_version}"
                )
        if self.bits == 4 and self.use_exllama:
            if self.exllama_config["version"] == ExllamaVersion.ONE:
                logger.info(
                    "You have activated exllama backend. Note that you can get better inference "
                    "speed using exllamav2 kernel by setting `exllama_config`."
                )
            elif self.exllama_config["version"] == ExllamaVersion.TWO:
                if is_auto_gptq_available():
                    optimum_version = version.parse(importlib.metadata.version("optimum"))
                    autogptq_version = version.parse(importlib.metadata.version("auto_gptq"))
                    if optimum_version <= version.parse("1.13.2") or autogptq_version <= version.parse("0.4.2"):
                        raise ValueError(
                            f"You need optimum > 1.13.2 and auto-gptq > 0.4.2 . Make sure to have that version installed - detected version : optimum {optimum_version} and autogptq {autogptq_version}"
                        )
        if self.modules_in_block_to_quantize is not None:
            optimum_version = version.parse(importlib.metadata.version("optimum"))
            if optimum_version < version.parse("1.15.0"):
                raise ValueError(
                    "You current version of `optimum` does not support `modules_in_block_to_quantize` quantization argument, please upgrade `optimum` package to a version superior than 1.15.0 ."
                )
    def to_dict(self) -> dict[str, Any]:
        config_dict = super().to_dict()
        config_dict.pop("disable_exllama", None)
        return config_dict
    def to_dict_optimum(self):
        quant_dict = self.to_dict()
        quant_dict["disable_exllama"] = not self.use_exllama
        return quant_dict
    @classmethod
    def from_dict_optimum(cls, config_dict):
        if "disable_exllama" in config_dict:
            config_dict["use_exllama"] = not config_dict["disable_exllama"]
            config_dict.pop("disable_exllama")
        config = cls(**config_dict)
        return config
@dataclass
class AwqConfig(QuantizationConfigMixin):
    def __init__(
        self,
        bits: int = 4,
        group_size: int = 128,
        zero_point: bool = True,
        version: AWQLinearVersion = AWQLinearVersion.GEMM,
        backend: AwqBackendPackingMethod = AwqBackendPackingMethod.AUTOAWQ,
        do_fuse: Optional[bool] = None,
        fuse_max_seq_len: Optional[int] = None,
        modules_to_fuse: Optional[dict] = None,
        modules_to_not_convert: Optional[list] = None,
        exllama_config: Optional[dict[str, int]] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.AWQ
        self.bits = bits
        self.group_size = group_size
        self.zero_point = zero_point
        self.version = version
        self.backend = backend
        self.fuse_max_seq_len = fuse_max_seq_len
        self.modules_to_not_convert = modules_to_not_convert
        self.exllama_config = exllama_config
        self.modules_to_fuse = modules_to_fuse
        if do_fuse is None:
            self.do_fuse = modules_to_fuse is not None and len(modules_to_fuse) > 0
        else:
            self.do_fuse = do_fuse
        self.fuse_max_seq_len = fuse_max_seq_len
        self.post_init()
    def post_init(self):
        if self.backend not in [AwqBackendPackingMethod.AUTOAWQ, AwqBackendPackingMethod.LLMAWQ]:
            raise ValueError(
                f"Only supported quantization backends in {AwqBackendPackingMethod.AUTOAWQ} and {AwqBackendPackingMethod.LLMAWQ} - not recognized backend {self.backend}"
            )
        self.version = AWQLinearVersion.from_str(self.version)
        if self.version not in [
            AWQLinearVersion.GEMM,
            AWQLinearVersion.GEMV,
            AWQLinearVersion.EXLLAMA,
            AWQLinearVersion.IPEX,
        ]:
            raise ValueError(
                f"Only supported versions are in [AWQLinearVersion.GEMM, AWQLinearVersion.GEMV, AWQLinearVersion.EXLLAMA, AWQLinearVersion.IPEX] - not recognized version {self.version}"
            )
        if self.backend == AwqBackendPackingMethod.LLMAWQ:
            if not (torch.cuda.is_available() or torch.xpu.is_available()):
                raise ValueError("LLM-AWQ backend is only supported on CUDA and XPU")
            if torch.cuda.is_available():
                compute_capability = torch.cuda.get_device_capability()
                major, minor = compute_capability
                if major < 8:
                    raise ValueError("LLM-AWQ backend is only supported on CUDA GPUs with compute capability >= 8.0")
        if self.do_fuse and self.fuse_max_seq_len is None:
            raise ValueError(
                "You cannot enable fused modules without specifying a `fuse_max_seq_len`, make sure to pass a valid `fuse_max_seq_len` for your usecase"
            )
        if self.do_fuse:
            awq_version_supports_fusing = False
            MIN_AWQ_VERSION = "0.1.7"
            if is_auto_awq_available():
                awq_version_supports_fusing = version.parse(importlib.metadata.version("autoawq")) >= version.parse(
                    MIN_AWQ_VERSION
                )
            if not awq_version_supports_fusing:
                raise ValueError(
                    f"You current version of `autoawq` does not support module fusing, please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}."
                )
        if self.modules_to_not_convert is not None:
            awq_version_supports_non_conversion = False
            MIN_AWQ_VERSION = "0.1.8"
            if is_auto_awq_available():
                awq_version_supports_non_conversion = version.parse(
                    importlib.metadata.version("autoawq")
                ) >= version.parse(MIN_AWQ_VERSION)
            if not awq_version_supports_non_conversion:
                raise ValueError(
                    f"You current version of `autoawq` does not support module quantization skipping, please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}."
                )
        if self.do_fuse and self.modules_to_fuse is not None:
            required_keys = [
                "hidden_size",
                "num_attention_heads",
                "num_key_value_heads",
                "mlp",
                "attention",
                "layernorm",
                "use_alibi",
            ]
            if not all(key in self.modules_to_fuse for key in required_keys):
                raise ValueError(
                    f"Required fields are missing in the fusing mapping, required fields are {required_keys}"
                )
        if self.version == AWQLinearVersion.EXLLAMA:
            awq_version_supports_exllama = False
            MIN_AWQ_VERSION = "0.2.0"
            if is_auto_awq_available():
                awq_version_supports_exllama = version.parse(importlib.metadata.version("autoawq")) >= version.parse(
                    MIN_AWQ_VERSION
                )
            if not awq_version_supports_exllama:
                raise ValueError(
                    f"You current version of `autoawq` does not support exllama backend, "
                    f"please upgrade `autoawq` package to at least {MIN_AWQ_VERSION}."
                )
            if self.exllama_config is None:
                self.exllama_config = {"version": ExllamaVersion.TWO, "max_input_len": 2048, "max_batch_size": 8}
            else:
                if "version" not in self.exllama_config:
                    raise ValueError("`exllama_config` needs to have a `version` key.")
                elif self.exllama_config["version"] not in [ExllamaVersion.ONE, ExllamaVersion.TWO]:
                    exllama_version = self.exllama_config["version"]
                    raise ValueError(
                        f"Only supported versions are in [ExllamaVersion.ONE, ExllamaVersion.TWO] - not recognized version {exllama_version}"
                    )
    def get_loading_attributes(self):
        attributes_dict = copy.deepcopy(self.__dict__)
        loading_attributes = ["version", "do_fuse", "modules_to_fuse", "fuse_max_seq_len", "exllama_config"]
        loading_attributes_dict = {i: j for i, j in attributes_dict.items() if i in loading_attributes}
        return loading_attributes_dict
@dataclass
class AqlmConfig(QuantizationConfigMixin):
    def __init__(
        self,
        in_group_size: int = 8,
        out_group_size: int = 1,
        num_codebooks: int = 1,
        nbits_per_codebook: int = 16,
        linear_weights_not_to_quantize: Optional[list[str]] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.AQLM
        self.in_group_size = in_group_size
        self.out_group_size = out_group_size
        self.num_codebooks = num_codebooks
        self.nbits_per_codebook = nbits_per_codebook
        self.linear_weights_not_to_quantize = linear_weights_not_to_quantize
        self.post_init()
    def post_init(self):
        if not isinstance(self.in_group_size, int):
            raise TypeError("in_group_size must be a float")
        if not isinstance(self.out_group_size, int):
            raise TypeError("out_group_size must be a float")
        if not isinstance(self.num_codebooks, int):
            raise TypeError("num_codebooks must be a float")
        if not isinstance(self.nbits_per_codebook, int):
            raise TypeError("nbits_per_codebook must be a float")
        if self.linear_weights_not_to_quantize is not None and not isinstance(
            self.linear_weights_not_to_quantize, list
        ):
            raise ValueError("linear_weights_not_to_quantize must be a list of strings")
        if self.linear_weights_not_to_quantize is None:
            self.linear_weights_not_to_quantize = []
@dataclass
class VptqLayerConfig(QuantizationConfigMixin):
    def __init__(
        self,
        enable_norm: bool = True,
        enable_perm: bool = True,
        group_num: int = 1,
        group_size: int = -1,
        in_features: int = -1,
        indices_as_float: bool = False,
        is_indice_packed: bool = True,
        num_centroids: tuple = [-1, -1],
        num_res_centroids: tuple = [-1, -1],
        out_features: int = -1,
        outlier_size: int = 0,
        vector_lens: tuple = [-1, -1],
        **kwargs,
    ):
        self.enable_norm = enable_norm
        self.enable_perm = enable_perm
        self.group_num = group_num
        self.group_size = group_size
        self.in_features = in_features
        self.indices_as_float = indices_as_float
        self.is_indice_packed = is_indice_packed
        self.num_centroids = num_centroids
        self.num_res_centroids = num_res_centroids
        self.out_features = out_features
        self.outlier_size = outlier_size
        self.vector_lens = vector_lens
        self.post_init()
    def post_init(self):
        if self.is_indice_packed is False:
            raise ValueError("is_indice_packed should always be True")
@dataclass
class VptqConfig(QuantizationConfigMixin):
    def __init__(
        self,
        enable_proxy_error: bool = False,
        config_for_layers: dict[str, Any] = {},
        shared_layer_config: dict[str, Any] = {},
        modules_to_not_convert: Optional[list] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.VPTQ
        self.enable_proxy_error = enable_proxy_error
        self.config_for_layers: dict[str, Any] = config_for_layers
        self.shared_layer_config: dict[str, Any] = shared_layer_config
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        for layer_param in self.config_for_layers.values():
            VptqLayerConfig(**layer_param)
        if self.enable_proxy_error is True:
            raise ValueError("enable_proxy_error should always be False until we support training")
@dataclass
class QuantoConfig(QuantizationConfigMixin):
    def __init__(
        self,
        weights="int8",
        activations=None,
        modules_to_not_convert: Optional[list] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.QUANTO
        self.weights = weights
        self.activations = activations
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        accepted_weights = ["float8", "int8", "int4", "int2"]
        accepted_activations = [None, "int8", "float8"]
        if self.weights not in accepted_weights:
            raise ValueError(f"Only support weights in {accepted_weights} but found {self.weights}")
        if self.activations not in accepted_activations:
            raise ValueError(f"Only support weights in {accepted_activations} but found {self.activations}")
@dataclass
class EetqConfig(QuantizationConfigMixin):
    def __init__(
        self,
        weights: str = "int8",
        modules_to_not_convert: Optional[list] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.EETQ
        self.weights = weights
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        accepted_weights = ["int8"]
        if self.weights not in accepted_weights:
            raise ValueError(f"Only support weights in {accepted_weights} but found {self.weights}")
class CompressedTensorsConfig(QuantizationConfigMixin):
    def __init__(
        self,
        config_groups: Optional[dict[str, Union["QuantizationScheme", list[str]]]] = None,
        format: str = "dense",
        quantization_status: "QuantizationStatus" = "initialized",
        kv_cache_scheme: Optional["QuantizationArgs"] = None,
        global_compression_ratio: Optional[float] = None,
        ignore: Optional[list[str]] = None,
        sparsity_config: Optional[dict[str, Any]] = None,
        quant_method: str = "compressed-tensors",
        run_compressed: bool = True,
        **kwargs,
    ):
        if is_compressed_tensors_available():
            from compressed_tensors.config import SparsityCompressionConfig
            from compressed_tensors.quantization import QuantizationConfig
        else:
            raise ImportError(
                "compressed_tensors is not installed and is required for compressed-tensors quantization. Please install it with `pip install compressed-tensors`."
            )
        self.quantization_config = None
        self.sparsity_config = None
        self.run_compressed = run_compressed
        if config_groups or kv_cache_scheme:
            self.quantization_config = QuantizationConfig.model_validate(
                {
                    "config_groups": config_groups,
                    "quant_method": quant_method,
                    "format": format,
                    "quantization_status": quantization_status,
                    "kv_cache_scheme": kv_cache_scheme,
                    "global_compression_ratio": global_compression_ratio,
                    "ignore": ignore,
                    **kwargs,
                }
            )
        if sparsity_config:
            self.sparsity_config = SparsityCompressionConfig.load_from_registry(
                sparsity_config.get("format"), **sparsity_config
            )
        self.quant_method = QuantizationMethod.COMPRESSED_TENSORS
    def post_init(self):
        if self.run_compressed:
            if self.is_sparsification_compressed:
                logger.warning(
                    "`run_compressed` is only supported for quantized_compressed models"
                    " and not for sparsified models. Setting `run_compressed=False`"
                )
                self.run_compressed = False
            elif not self.is_quantization_compressed:
                logger.warning(
                    "`run_compressed` is only supported for compressed models. Setting `run_compressed=False`"
                )
                self.run_compressed = False
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        if "quantization_config" in config_dict:
            config_dict = dict(
                sparsity_config=config_dict.get("sparsity_config"),
                **config_dict["quantization_config"],
            )
        return super().from_dict(config_dict, return_unused_kwargs=return_unused_kwargs, **kwargs)
    def to_dict(self) -> dict[str, Any]:
        quantization_config = {}
        if self.quantization_config is not None:
            quantization_config = self.quantization_config.model_dump()
        else:
            quantization_config["quant_method"] = QuantizationMethod.COMPRESSED_TENSORS
        if self.sparsity_config is not None:
            quantization_config["sparsity_config"] = self.sparsity_config.model_dump()
        else:
            quantization_config["sparsity_config"] = {}
        return quantization_config
    def to_diff_dict(self) -> dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = CompressedTensorsConfig().to_dict()
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if key not in default_config_dict or value != default_config_dict[key]:
                serializable_config_dict[key] = value
        return serializable_config_dict
    def get_loading_attributes(self):
        return {"run_compressed": self.run_compressed}
    @property
    def is_quantized(self):
        return bool(self.quantization_config) and bool(self.quantization_config.config_groups)
    @property
    def is_quantization_compressed(self):
        from compressed_tensors.quantization import QuantizationStatus
        return self.is_quantized and self.quantization_config.quantization_status == QuantizationStatus.COMPRESSED
    @property
    def is_sparsification_compressed(self):
        from compressed_tensors.config import (
            CompressionFormat,
            SparsityCompressionConfig,
        )
        return (
            isinstance(self.sparsity_config, SparsityCompressionConfig)
            and self.sparsity_config.format != CompressionFormat.dense.value
        )
@dataclass
class FbgemmFp8Config(QuantizationConfigMixin):
    def __init__(
        self,
        activation_scale_ub: float = 1200.0,
        modules_to_not_convert: Optional[list] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.FBGEMM_FP8
        self.activation_scale_ub = activation_scale_ub
        self.modules_to_not_convert = modules_to_not_convert
    def get_loading_attributes(self):
        attributes_dict = copy.deepcopy(self.__dict__)
        loading_attributes = ["activation_scale_ub"]
        loading_attributes_dict = {i: j for i, j in attributes_dict.items() if i in loading_attributes}
        return loading_attributes_dict
@dataclass
class HiggsConfig(QuantizationConfigMixin):
    def __init__(
        self,
        bits: int = 4,
        p: int = 2,
        modules_to_not_convert: Optional[list[str]] = None,
        hadamard_size: int = 512,
        group_size: int = 256,
        tune_metadata: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        if tune_metadata is None:
            tune_metadata = {}
        self.quant_method = QuantizationMethod.HIGGS
        self.bits = bits
        self.p = p
        self.modules_to_not_convert = modules_to_not_convert
        self.hadamard_size = hadamard_size
        self.group_size = group_size
        self.tune_metadata = tune_metadata
        self.post_init()
    def post_init(self):
        if self.bits not in [2, 3, 4]:
            raise ValueError("bits must be 2, 3, or 4")
        if self.p not in [1, 2]:
            raise ValueError("p must be 1 or 2. 2 is always better in practice")
        if self.group_size not in [64, 128, 256]:
            raise ValueError("group_size must be 64, 128, or 256")
        if self.hadamard_size % self.group_size != 0:
            raise ValueError("hadamard_size must be divisible by group_size")
@dataclass
class FPQuantConfig(QuantizationConfigMixin):
    def __init__(
        self,
        forward_dtype: str = "nvfp4",
        forward_method: str = "abs_max",
        backward_dtype: str = "bf16",
        store_master_weights: bool = False,
        hadamard_group_size: Optional[int] = None,
        pseudoquantization: bool = False,
        transform_init: str = "hadamard",
        modules_to_not_convert: Optional[list[str]] = None,
        **kwargs,
    ):
        self.forward_dtype = forward_dtype
        self.forward_method = forward_method
        self.backward_dtype = backward_dtype
        self.store_master_weights = store_master_weights
        self.hadamard_group_size = hadamard_group_size
        self.pseudoquantization = pseudoquantization
        self.transform_init = transform_init
        self.modules_to_not_convert = modules_to_not_convert
        self.quant_method = QuantizationMethod.FPQUANT
        self.post_init()
    def post_init(self):
        if self.hadamard_group_size is None:
            if self.forward_dtype == "nvfp4":
                self.hadamard_group_size = 16
            else:
                self.hadamard_group_size = 32
        if self.forward_dtype == "mxfp4":
            if self.forward_method not in ["abs_max", "quest"]:
                raise ValueError("Only 'abs_max' and 'quest' are supported for forward_method for 'mxfp4'.")
            if self.hadamard_group_size is None:
                self.hadamard_group_size = 32
            if self.hadamard_group_size not in [32, 64, 128]:
                raise ValueError("Only a `hadamard_group_size` of [32, 64, 128] is supported for 'mxfp4'.")
        elif self.forward_dtype == "nvfp4":
            if self.forward_method != "abs_max":
                raise ValueError("Only 'abs_max' is supported for forward_method for 'nvfp4'.")
            if self.hadamard_group_size is None:
                self.hadamard_group_size = 16
            if self.hadamard_group_size not in [16, 32, 64, 128]:
                raise ValueError("Only a `hadamard_group_size` of [16, 32, 64, 128] is supported for 'nvfp4'.")
        else:
            raise ValueError("Only 'mxfp4' and 'nvfp4' are supported for forward_dtype for now.")
        if self.backward_dtype != "bf16":
            raise ValueError("Only 'bf16' is supported for backward_dtype for now.")
        if self.transform_init not in ["hadamard", "identity", "gsr"]:
            raise ValueError("Only 'hadamard', 'identity' and 'gsr' are supported for transform_init.")
        if self.modules_to_not_convert is None:
            self.modules_to_not_convert = ["lm_head"]
@dataclass
class TorchAoConfig(QuantizationConfigMixin):
    quant_method: QuantizationMethod
    quant_type: Union[str, "AOBaseConfig"]
    modules_to_not_convert: Optional[list]
    quant_type_kwargs: dict[str, Any]
    include_input_output_embeddings: bool
    untie_embedding_weights: bool
    def __init__(
        self,
        quant_type: Union[str, "AOBaseConfig"],
        modules_to_not_convert: Optional[list] = None,
        include_input_output_embeddings: bool = False,
        untie_embedding_weights: bool = False,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.TORCHAO
        self.quant_type = quant_type
        self.modules_to_not_convert = modules_to_not_convert
        self.quant_type_kwargs = kwargs.get("quant_type_kwargs", kwargs)
        self.include_input_output_embeddings = include_input_output_embeddings
        self.untie_embedding_weights = untie_embedding_weights
        self.post_init()
    @staticmethod
    def _get_ao_version() -> version.Version:
        if not is_torchao_available():
            raise ValueError("TorchAoConfig requires torchao to be installed. Install with `pip install torchao`")
        return version.parse(importlib.metadata.version("torchao"))
    def post_init(self):
        ao_version = self._get_ao_version()
        if isinstance(self.quant_type, str):
            self._validate_string_quant_type()
        elif ao_version > version.parse("0.9.0"):
            from torchao.quantization.quant_api import AOBaseConfig
            if not isinstance(self.quant_type, AOBaseConfig):
                raise TypeError(
                    f"quant_type must be either a string or an AOBaseConfig instance, got {type(self.quant_type)}"
                )
        else:
            raise ValueError(
                f"In torchao <= 0.9.0, quant_type must be a string. Got {type(self.quant_type)}. "
                f"Please upgrade to torchao > 0.9.0 to use AOBaseConfig instances."
            )
    def _validate_string_quant_type(self):
        methods = self._get_torchao_quant_type_to_method()
        if self.quant_type not in methods:
            raise ValueError(
                f"Unsupported string quantization type: {self.quant_type}. "
                f"Supported types: {', '.join(methods.keys())}"
            )
        method = methods[self.quant_type]
        sig = signature(method)
        valid_kwargs = {
            param.name
            for param in sig.parameters.values()
            if param.kind in [Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
        }
        invalid_kwargs = set(self.quant_type_kwargs) - valid_kwargs
        if invalid_kwargs:
            raise ValueError(
                f"Unexpected keyword arg for {self.quant_type}: {', '.join(invalid_kwargs)}. "
                f"Valid kwargs: {', '.join(valid_kwargs)}"
            )
    def _get_torchao_quant_type_to_method(self):
        from torchao.quantization import (
            autoquant,
            int4_weight_only,
            int8_dynamic_activation_int8_weight,
            int8_weight_only,
        )
        return {
            "int4_weight_only": int4_weight_only,
            "int8_weight_only": int8_weight_only,
            "int8_dynamic_activation_int8_weight": int8_dynamic_activation_int8_weight,
            "autoquant": autoquant,
        }
    def get_apply_tensor_subclass(self):
        if isinstance(self.quant_type, str):
            methods = self._get_torchao_quant_type_to_method()
            quant_type_kwargs = self.quant_type_kwargs.copy()
            if (
                not torch.cuda.is_available()
                and is_torchao_available()
                and self.quant_type == "int4_weight_only"
                and version.parse(importlib.metadata.version("torchao")) >= version.parse("0.8.0")
                and quant_type_kwargs.get("layout", None) is None
            ):
                if torch.xpu.is_available():
                    if version.parse(importlib.metadata.version("torchao")) >= version.parse(
                        "0.11.0"
                    ) and version.parse(importlib.metadata.version("torch")) > version.parse("2.7.9"):
                        from torchao.dtypes import Int4XPULayout
                        from torchao.quantization.quant_primitives import ZeroPointDomain
                        quant_type_kwargs["layout"] = Int4XPULayout()
                        quant_type_kwargs["zero_point_domain"] = ZeroPointDomain.INT
                    else:
                        raise ValueError(
                            "TorchAoConfig requires torchao >= 0.11.0 and torch >= 2.8.0 for XPU support. Please upgrade the version or use run on CPU with the cpu version pytorch."
                        )
                else:
                    from torchao.dtypes import Int4CPULayout
                    quant_type_kwargs["layout"] = Int4CPULayout()
            return methods[self.quant_type](**quant_type_kwargs)
        else:
            return self.quant_type
    def to_dict(self):
        d = super().to_dict()
        if isinstance(self.quant_type, str):
            if "quant_type_kwargs" in d and "layout" in d["quant_type_kwargs"]:
                if is_dataclass(d["quant_type_kwargs"]["layout"]):
                    d["quant_type_kwargs"]["layout"] = [
                        d["quant_type_kwargs"]["layout"].__class__.__name__,
                        dataclasses.asdict(d["quant_type_kwargs"]["layout"]),
                    ]
                if isinstance(d["quant_type_kwargs"]["layout"], list):
                    assert len(d["quant_type_kwargs"]["layout"]) == 2, "layout saves layout name and layout kwargs"
                    assert isinstance(d["quant_type_kwargs"]["layout"][0], str), "layout name must be a string"
                    assert isinstance(d["quant_type_kwargs"]["layout"][1], dict), "layout kwargs must be a dict"
                else:
                    raise ValueError("layout must be a list")
        else:
            from torchao.core.config import config_to_dict
            d["quant_type"] = {"default": config_to_dict(self.quant_type)}
        return d
    @classmethod
    def from_dict(cls, config_dict, return_unused_kwargs=False, **kwargs):
        ao_version = cls._get_ao_version()
        assert ao_version > version.parse("0.9.0"), "TorchAoConfig requires torchao > 0.9.0 for construction from dict"
        config_dict = config_dict.copy()
        quant_type = config_dict.pop("quant_type")
        if isinstance(quant_type, str):
            return cls(quant_type=quant_type, **config_dict)
        assert len(quant_type) == 1 and "default" in quant_type, (
            "Expected only one key 'default' in quant_type dictionary"
        )
        quant_type = quant_type["default"]
        from torchao.core.config import config_from_dict
        quant_type = config_from_dict(quant_type)
        return cls(quant_type=quant_type, **config_dict)
@dataclass
class BitNetQuantConfig(QuantizationConfigMixin):
    def __init__(
        self,
        modules_to_not_convert: Optional[list] = None,
        linear_class: str = "bitlinear",
        quantization_mode: str = "offline",
        use_rms_norm: bool = False,
        rms_norm_eps: Optional[float] = 1e-6,
        **kwargs,
    ):
        if linear_class not in ["bitlinear", "autobitlinear"]:
            raise ValueError(f"linear_class must be either 'bitlinear' or 'autobitlinear', but got {linear_class}")
        if quantization_mode not in ["online", "offline"]:
            raise ValueError(f"quantization_mode must be either 'online' or 'offline', but got {quantization_mode}")
        self.quant_method = QuantizationMethod.BITNET
        self.modules_to_not_convert = modules_to_not_convert
        self.linear_class = linear_class
        self.quantization_mode = quantization_mode
        self.use_rms_norm = use_rms_norm
        self.rms_norm_eps = rms_norm_eps
        self.post_init()
    def post_init(self):
        pass
@dataclass
class SpQRConfig(QuantizationConfigMixin):
    def __init__(
        self,
        bits: int = 3,
        beta1: int = 16,
        beta2: int = 16,
        shapes: Optional[dict[str, int]] = None,
        modules_to_not_convert: Optional[list[str]] = None,
        **kwargs,
    ):
        if shapes is None:
            shapes = {}
        self.shapes = shapes
        self.quant_method = QuantizationMethod.SPQR
        self.bits = bits
        self.beta1 = beta1
        self.beta2 = beta2
        self.modules_to_not_convert = modules_to_not_convert
        self.post_init()
    def post_init(self):
        if not isinstance(self.bits, int):
            raise TypeError("bits must be an int")
        if not isinstance(self.beta1, int):
            raise TypeError("beta1 must be an int")
        if not isinstance(self.beta2, int):
            raise TypeError("beta2 must be an int")
        if self.bits != 3:
            raise ValueError("SpQR currently only supports bits = 3")
        if self.beta1 != 16:
            raise ValueError("SpQR currently only supports beta1 = 16")
        if self.beta2 != 16:
            raise ValueError("SpQR currently only supports beta2 = 16")
        if not isinstance(self.shapes, dict):
            raise TypeError("shapes must be a dict")
@dataclass
class FineGrainedFP8Config(QuantizationConfigMixin):
    def __init__(
        self,
        activation_scheme: str = "dynamic",
        weight_block_size: tuple[int, int] = (128, 128),
        modules_to_not_convert: Optional[list] = None,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.FP8
        self.modules_to_not_convert = modules_to_not_convert
        self.activation_scheme = activation_scheme
        self.weight_block_size = weight_block_size
        self.post_init()
    def post_init(self):
        self.activation_scheme = self.activation_scheme.lower()
        if self.activation_scheme != "dynamic":
            raise ValueError(f"Activation scheme {self.activation_scheme} not supported")
        if len(self.weight_block_size) != 2:
            raise ValueError("weight_block_size must be a tuple of two integers")
        if self.weight_block_size[0] <= 0 or self.weight_block_size[1] <= 0:
            raise ValueError("weight_block_size must be a tuple of two positive integers")
class QuarkConfig(QuantizationConfigMixin):
    def __init__(
        self,
        **kwargs,
    ):
        if is_torch_available() and is_quark_available():
            from quark import __version__ as quark_version
            from quark.torch.export.config.config import JsonExporterConfig
            from quark.torch.export.main_export.quant_config_parser import QuantConfigParser
            from quark.torch.quantization.config.config import Config
        else:
            raise ImportError(
                "Quark is not installed. Please refer to https://quark.docs.amd.com/latest/install.html."
            )
        self.custom_mode = kwargs["quant_method"]
        self.legacy = "export" not in kwargs
        if self.custom_mode in ["awq", "fp8"]:
            self.quant_config = QuantConfigParser.from_custom_config(kwargs, is_bias_quantized=False)
            self.json_export_config = JsonExporterConfig()
        else:
            self.quant_config = Config.from_dict(kwargs)
            if "export" in kwargs:
                if "min_kv_scale" in kwargs["export"] and version.parse(quark_version) < version.parse("0.8"):
                    min_kv_scale = kwargs["export"].pop("min_kv_scale")
                    logger.warning(
                        f"The parameter `min_kv_scale={min_kv_scale}` was found in the model config.json's `quantization_config.export` configuration, but this parameter is supported only for quark>=0.8. Ignoring this configuration parameter. Please update the `amd-quark` package."
                    )
                self.json_export_config = JsonExporterConfig(**kwargs["export"])
            else:
                self.json_export_config = JsonExporterConfig()
        self.quant_method = QuantizationMethod.QUARK
@dataclass
class Mxfp4Config(QuantizationConfigMixin):
    def __init__(
        self,
        modules_to_not_convert: Optional[list] = None,
        dequantize: bool = False,
        **kwargs,
    ):
        self.quant_method = QuantizationMethod.MXFP4
        self.modules_to_not_convert = modules_to_not_convert
        self.dequantize = dequantize
    def get_loading_attributes(self):
        return {"dequantize": self.dequantize}
    def to_dict(self) -> dict[str, Any]:
        return {"quant_method": self.quant_method, "modules_to_not_convert": self.modules_to_not_convert}