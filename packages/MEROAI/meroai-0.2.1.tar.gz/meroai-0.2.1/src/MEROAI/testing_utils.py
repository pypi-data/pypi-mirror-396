import ast
import collections
import contextlib
import copy
import doctest
import functools
import gc
import importlib
import inspect
import logging
import multiprocessing
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import types
import unittest
from collections import UserDict, defaultdict
from collections.abc import Generator, Iterable, Iterator, Mapping
from dataclasses import MISSING, fields
from functools import cache, wraps
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Optional, Union
from unittest import mock
from unittest.mock import patch
import huggingface_hub.utils
import requests
import urllib3
from huggingface_hub import delete_repo
from packaging import version
from MEROAI import Trainer
from MEROAI import logging as MEROAI_logging
from .integrations import (
    is_clearml_available,
    is_optuna_available,
    is_ray_available,
    is_sigopt_available,
    is_swanlab_available,
    is_tensorboard_available,
    is_trackio_available,
    is_wandb_available,
)
from .integrations.deepspeed import is_deepspeed_available
from .utils import (
    ACCELERATE_MIN_VERSION,
    GGUF_MIN_VERSION,
    TRITON_MIN_VERSION,
    is_accelerate_available,
    is_apex_available,
    is_apollo_torch_available,
    is_aqlm_available,
    is_auto_awq_available,
    is_auto_gptq_available,
    is_auto_round_available,
    is_av_available,
    is_bitsandbytes_available,
    is_bitsandbytes_multi_backend_available,
    is_bs4_available,
    is_compressed_tensors_available,
    is_cv2_available,
    is_cython_available,
    is_decord_available,
    is_detectron2_available,
    is_eetq_available,
    is_essentia_available,
    is_faiss_available,
    is_fbgemm_gpu_available,
    is_flash_attn_2_available,
    is_flash_attn_3_available,
    is_flax_available,
    is_flute_available,
    is_fp_quant_available,
    is_fsdp_available,
    is_ftfy_available,
    is_g2p_en_available,
    is_galore_torch_available,
    is_gguf_available,
    is_gptqmodel_available,
    is_grokadamw_available,
    is_hadamard_available,
    is_hqq_available,
    is_huggingface_hub_greater_or_equal,
    is_ipex_available,
    is_jinja_available,
    is_jumanpp_available,
    is_keras_nlp_available,
    is_kernels_available,
    is_levenshtein_available,
    is_librosa_available,
    is_liger_kernel_available,
    is_lomo_available,
    is_mistral_common_available,
    is_natten_available,
    is_nltk_available,
    is_onnx_available,
    is_openai_available,
    is_optimum_available,
    is_optimum_quanto_available,
    is_pandas_available,
    is_peft_available,
    is_phonemizer_available,
    is_pretty_midi_available,
    is_psutil_available,
    is_pyctcdecode_available,
    is_pytesseract_available,
    is_pytest_available,
    is_pytorch_quantization_available,
    is_quark_available,
    is_qutlass_available,
    is_rjieba_available,
    is_sacremoses_available,
    is_safetensors_available,
    is_schedulefree_available,
    is_scipy_available,
    is_sentencepiece_available,
    is_seqio_available,
    is_spacy_available,
    is_speech_available,
    is_spqr_available,
    is_sudachi_available,
    is_sudachi_projection_available,
    is_tf_available,
    is_tiktoken_available,
    is_timm_available,
    is_tokenizers_available,
    is_torch_available,
    is_torch_bf16_available_on_device,
    is_torch_bf16_gpu_available,
    is_torch_fp16_available_on_device,
    is_torch_greater_or_equal,
    is_torch_hpu_available,
    is_torch_mlu_available,
    is_torch_neuroncore_available,
    is_torch_npu_available,
    is_torch_optimi_available,
    is_torch_tensorrt_fx_available,
    is_torch_tf32_available,
    is_torch_xla_available,
    is_torch_xpu_available,
    is_torchao_available,
    is_torchaudio_available,
    is_torchcodec_available,
    is_torchdynamo_available,
    is_torchvision_available,
    is_triton_available,
    is_vision_available,
    is_vptq_available,
    strtobool,
)
if is_accelerate_available():
    from accelerate.state import AcceleratorState, PartialState
    from accelerate.utils.imports import is_fp8_available
if is_pytest_available():
    from _pytest.doctest import (
        Module,
        _get_checker,
        _get_continue_on_failure,
        _get_runner,
        _is_mocked,
        _patch_unwrap_mock_aware,
        get_optionflags,
    )
    from _pytest.outcomes import skip
    from _pytest.pathlib import import_path
    from pytest import DoctestItem
else:
    Module = object
    DoctestItem = object
SMALL_MODEL_IDENTIFIER = "julien-c/bert-xsmall-dummy"
DUMMY_UNKNOWN_IDENTIFIER = "julien-c/dummy-unknown"
DUMMY_DIFF_TOKENIZER_IDENTIFIER = "julien-c/dummy-diff-tokenizer"
USER = "__DUMMY_MEROAI_USER__"
ENDPOINT_STAGING = "https://hub-ci.huggingface.co"
TOKEN = "hf_94wBhPGp6KrrTH3KDchhKpRxZwd6dmHWLL"
_COMMON_MODEL_NAMES_MAP = {
    "config_class": "Config",
    "causal_lm_class": "ForCausalLM",
    "question_answering_class": "ForQuestionAnswering",
    "sequence_classification_class": "ForSequenceClassification",
    "token_classification_class": "ForTokenClassification",
}
if is_torch_available():
    import torch
    IS_ROCM_SYSTEM = torch.version.hip is not None
    IS_CUDA_SYSTEM = torch.version.cuda is not None
    IS_XPU_SYSTEM = getattr(torch.version, "xpu", None) is not None
else:
    IS_ROCM_SYSTEM = False
    IS_CUDA_SYSTEM = False
    IS_XPU_SYSTEM = False
logger = MEROAI_logging.get_logger(__name__)
def parse_flag_from_env(key, default=False):
    try:
        value = os.environ[key]
    except KeyError:
        _value = default
    else:
        try:
            _value = strtobool(value)
        except ValueError:
            raise ValueError(f"If set, {key} must be yes or no.")
    return _value
def parse_int_from_env(key, default=None):
    try:
        value = os.environ[key]
    except KeyError:
        _value = default
    else:
        try:
            _value = int(value)
        except ValueError:
            raise ValueError(f"If set, {key} must be a int.")
    return _value
_run_slow_tests = parse_flag_from_env("RUN_SLOW", default=False)
_run_flaky_tests = parse_flag_from_env("RUN_FLAKY", default=True)
_run_custom_tokenizers = parse_flag_from_env("RUN_CUSTOM_TOKENIZERS", default=False)
_run_staging = parse_flag_from_env("HUGGINGFACE_CO_STAGING", default=False)
_run_pipeline_tests = parse_flag_from_env("RUN_PIPELINE_TESTS", default=True)
_run_agent_tests = parse_flag_from_env("RUN_AGENT_TESTS", default=False)
def is_staging_test(test_case):
    if not _run_staging:
        return unittest.skip(reason="test is staging test")(test_case)
    else:
        try:
            import pytest
        except ImportError:
            return test_case
        else:
            return pytest.mark.is_staging_test()(test_case)
def is_pipeline_test(test_case):
    if not _run_pipeline_tests:
        return unittest.skip(reason="test is pipeline test")(test_case)
    else:
        try:
            import pytest
        except ImportError:
            return test_case
        else:
            return pytest.mark.is_pipeline_test()(test_case)
def is_agent_test(test_case):
    if not _run_agent_tests:
        return unittest.skip(reason="test is an agent test")(test_case)
    else:
        try:
            import pytest
        except ImportError:
            return test_case
        else:
            return pytest.mark.is_agent_test()(test_case)
def slow(test_case):
    return unittest.skipUnless(_run_slow_tests, "test is slow")(test_case)
def tooslow(test_case):
    return unittest.skip(reason="test is too slow")(test_case)
def skip_if_not_implemented(test_func):
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            return test_func(*args, **kwargs)
        except NotImplementedError as e:
            raise unittest.SkipTest(f"Test skipped due to NotImplementedError: {e}")
    return wrapper
def apply_skip_if_not_implemented(cls):
    for attr_name in dir(cls):
        if attr_name.startswith("test_"):
            attr = getattr(cls, attr_name)
            if callable(attr):
                setattr(cls, attr_name, skip_if_not_implemented(attr))
    return cls
def custom_tokenizers(test_case):
    return unittest.skipUnless(_run_custom_tokenizers, "test of custom tokenizers")(test_case)
def require_bs4(test_case):
    return unittest.skipUnless(is_bs4_available(), "test requires BeautifulSoup4")(test_case)
def require_galore_torch(test_case):
    return unittest.skipUnless(is_galore_torch_available(), "test requires GaLore")(test_case)
def require_apollo_torch(test_case):
    return unittest.skipUnless(is_apollo_torch_available(), "test requires APOLLO")(test_case)
def require_torch_optimi(test_case):
    return unittest.skipUnless(is_torch_optimi_available(), "test requires torch-optimi")(test_case)
def require_lomo(test_case):
    return unittest.skipUnless(is_lomo_available(), "test requires LOMO")(test_case)
def require_grokadamw(test_case):
    return unittest.skipUnless(is_grokadamw_available(), "test requires GrokAdamW")(test_case)
def require_schedulefree(test_case):
    return unittest.skipUnless(is_schedulefree_available(), "test requires schedulefree")(test_case)
def require_cv2(test_case):
    return unittest.skipUnless(is_cv2_available(), "test requires OpenCV")(test_case)
def require_levenshtein(test_case):
    return unittest.skipUnless(is_levenshtein_available(), "test requires Levenshtein")(test_case)
def require_nltk(test_case):
    return unittest.skipUnless(is_nltk_available(), "test requires NLTK")(test_case)
def require_accelerate(test_case, min_version: str = ACCELERATE_MIN_VERSION):
    return unittest.skipUnless(
        is_accelerate_available(min_version), f"test requires accelerate version >= {min_version}"
    )(test_case)
def require_triton(min_version: str = TRITON_MIN_VERSION):
    def decorator(test_case):
        return unittest.skipUnless(is_triton_available(min_version), f"test requires triton version >= {min_version}")(
            test_case
        )
    return decorator
def require_gguf(test_case, min_version: str = GGUF_MIN_VERSION):
    return unittest.skipUnless(is_gguf_available(min_version), f"test requires gguf version >= {min_version}")(
        test_case
    )
def require_fsdp(test_case, min_version: str = "1.12.0"):
    return unittest.skipUnless(is_fsdp_available(min_version), f"test requires torch version >= {min_version}")(
        test_case
    )
def require_g2p_en(test_case):
    return unittest.skipUnless(is_g2p_en_available(), "test requires g2p_en")(test_case)
def require_safetensors(test_case):
    return unittest.skipUnless(is_safetensors_available(), "test requires safetensors")(test_case)
def require_rjieba(test_case):
    return unittest.skipUnless(is_rjieba_available(), "test requires rjieba")(test_case)
def require_jinja(test_case):
    return unittest.skipUnless(is_jinja_available(), "test requires jinja")(test_case)
def require_onnx(test_case):
    return unittest.skipUnless(is_onnx_available(), "test requires ONNX")(test_case)
def require_timm(test_case):
    return unittest.skipUnless(is_timm_available(), "test requires Timm")(test_case)
def require_natten(test_case):
    return unittest.skipUnless(is_natten_available(), "test requires natten")(test_case)
def require_torch(test_case):
    return unittest.skipUnless(is_torch_available(), "test requires PyTorch")(test_case)
def require_torch_greater_or_equal(version: str):
    def decorator(test_case):
        return unittest.skipUnless(is_torch_greater_or_equal(version), f"test requires PyTorch version >= {version}")(
            test_case
        )
    return decorator
def require_huggingface_hub_greater_or_equal(version: str):
    def decorator(test_case):
        return unittest.skipUnless(
            is_huggingface_hub_greater_or_equal(version), f"test requires huggingface_hub version >= {version}"
        )(test_case)
    return decorator
def require_flash_attn(test_case):
    flash_attn_available = is_flash_attn_2_available()
    kernels_available = is_kernels_available()
    try:
        from kernels import get_kernel
        get_kernel("kernels-community/flash-attn")
    except Exception as _:
        kernels_available = False
    return unittest.skipUnless(kernels_available | flash_attn_available, "test requires Flash Attention")(test_case)
def require_kernels(test_case):
    return unittest.skipUnless(is_kernels_available(), "test requires the kernels library")(test_case)
def require_flash_attn_3(test_case):
    return unittest.skipUnless(is_flash_attn_3_available(), "test requires Flash Attention 3")(test_case)
def require_read_token(test_case):
    token = os.getenv("HF_HUB_READ_TOKEN")
    if isinstance(test_case, type):
        for attr_name in dir(test_case):
            attr = getattr(test_case, attr_name)
            if isinstance(attr, types.FunctionType):
                if getattr(attr, "__require_read_token__", False):
                    continue
                wrapped = require_read_token(attr)
                setattr(test_case, attr_name, wrapped)
        return test_case
    else:
        if getattr(test_case, "__require_read_token__", False):
            return test_case
        @functools.wraps(test_case)
        def wrapper(*args, **kwargs):
            if token is not None:
                with patch("huggingface_hub.utils._headers.get_token", return_value=token):
                    return test_case(*args, **kwargs)
            else:
                if "staticmethod" in inspect.getsource(test_case).strip():
                    if len(args) > 0 and isinstance(args[0], unittest.TestCase):
                        return test_case(*args[1:], **kwargs)
                return test_case(*args, **kwargs)
        wrapper.__require_read_token__ = True
        return wrapper
def require_peft(test_case):
    return unittest.skipUnless(is_peft_available(), "test requires PEFT")(test_case)
def require_torchvision(test_case):
    return unittest.skipUnless(is_torchvision_available(), "test requires Torchvision")(test_case)
def require_torchcodec(test_case):
    return unittest.skipUnless(is_torchcodec_available(), "test requires Torchcodec")(test_case)
def require_torch_or_tf(test_case):
    return unittest.skipUnless(is_torch_available() or is_tf_available(), "test requires PyTorch or TensorFlow")(
        test_case
    )
def require_intel_extension_for_pytorch(test_case):
    return unittest.skipUnless(
        is_ipex_available(),
        "test requires Intel Extension for PyTorch to be installed and match current PyTorch version, see"
        " https://github.com/intel/intel-extension-for-pytorch",
    )(test_case)
def require_torchaudio(test_case):
    return unittest.skipUnless(is_torchaudio_available(), "test requires torchaudio")(test_case)
def require_sentencepiece(test_case):
    return unittest.skipUnless(is_sentencepiece_available(), "test requires SentencePiece")(test_case)
def require_sacremoses(test_case):
    return unittest.skipUnless(is_sacremoses_available(), "test requires Sacremoses")(test_case)
def require_seqio(test_case):
    return unittest.skipUnless(is_seqio_available(), "test requires Seqio")(test_case)
def require_scipy(test_case):
    return unittest.skipUnless(is_scipy_available(), "test requires Scipy")(test_case)
def require_tokenizers(test_case):
    return unittest.skipUnless(is_tokenizers_available(), "test requires tokenizers")(test_case)
def require_keras_nlp(test_case):
    return unittest.skipUnless(is_keras_nlp_available(), "test requires keras_nlp")(test_case)
def require_pandas(test_case):
    return unittest.skipUnless(is_pandas_available(), "test requires pandas")(test_case)
def require_pytesseract(test_case):
    return unittest.skipUnless(is_pytesseract_available(), "test requires PyTesseract")(test_case)
def require_pytorch_quantization(test_case):
    return unittest.skipUnless(is_pytorch_quantization_available(), "test requires PyTorch Quantization Toolkit")(
        test_case
    )
def require_vision(test_case):
    return unittest.skipUnless(is_vision_available(), "test requires vision")(test_case)
def require_ftfy(test_case):
    return unittest.skipUnless(is_ftfy_available(), "test requires ftfy")(test_case)
def require_spacy(test_case):
    return unittest.skipUnless(is_spacy_available(), "test requires spacy")(test_case)
def require_torch_multi_gpu(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() > 1, "test requires multiple CUDA GPUs")(test_case)
def require_torch_multi_accelerator(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) > 1, "test requires multiple accelerators")(
        test_case
    )
def require_torch_non_multi_gpu(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() < 2, "test requires 0 or 1 GPU")(test_case)
def require_torch_non_multi_accelerator(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) < 2, "test requires 0 or 1 accelerator")(test_case)
def require_torch_up_to_2_gpus(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    import torch
    return unittest.skipUnless(torch.cuda.device_count() < 3, "test requires 0 or 1 or 2 GPUs")(test_case)
def require_torch_up_to_2_accelerators(test_case):
    if not is_torch_available():
        return unittest.skip(reason="test requires PyTorch")(test_case)
    return unittest.skipUnless(backend_device_count(torch_device) < 3, "test requires 0 or 1 or 2 accelerators")(
        test_case
    )
def require_torch_xla(test_case):
    return unittest.skipUnless(is_torch_xla_available(), "test requires TorchXLA")(test_case)
def require_torch_neuroncore(test_case):
    return unittest.skipUnless(is_torch_neuroncore_available(check_device=False), "test requires PyTorch NeuronCore")(
        test_case
    )
def require_torch_npu(test_case):
    return unittest.skipUnless(is_torch_npu_available(), "test requires PyTorch NPU")(test_case)
def require_torch_multi_npu(test_case):
    if not is_torch_npu_available():
        return unittest.skip(reason="test requires PyTorch NPU")(test_case)
    return unittest.skipUnless(torch.npu.device_count() > 1, "test requires multiple NPUs")(test_case)
def require_non_hpu(test_case):
    return unittest.skipUnless(torch_device != "hpu", "test requires a non-HPU")(test_case)
def require_torch_xpu(test_case):
    return unittest.skipUnless(is_torch_xpu_available(), "test requires XPU device")(test_case)
def require_non_xpu(test_case):
    return unittest.skipUnless(torch_device != "xpu", "test requires a non-XPU")(test_case)
def require_torch_multi_xpu(test_case):
    if not is_torch_xpu_available():
        return unittest.skip(reason="test requires PyTorch XPU")(test_case)
    return unittest.skipUnless(torch.xpu.device_count() > 1, "test requires multiple XPUs")(test_case)
def require_torch_multi_hpu(test_case):
    if not is_torch_hpu_available():
        return unittest.skip(reason="test requires PyTorch HPU")(test_case)
    return unittest.skipUnless(torch.hpu.device_count() > 1, "test requires multiple HPUs")(test_case)
if is_torch_available():
    import torch
    if "MEROAI_TEST_BACKEND" in os.environ:
        backend = os.environ["MEROAI_TEST_BACKEND"]
        try:
            _ = importlib.import_module(backend)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"Failed to import `MEROAI_TEST_BACKEND` '{backend}'! This should be the name of an installed module. The original error (look up to see its"
                f" traceback):\n{e}"
            ) from e
    if "MEROAI_TEST_DEVICE" in os.environ:
        torch_device = os.environ["MEROAI_TEST_DEVICE"]
        if torch_device == "cuda" and not torch.cuda.is_available():
            raise ValueError(
                f"MEROAI_TEST_DEVICE={torch_device}, but CUDA is unavailable. Please double-check your testing environment."
            )
        if torch_device == "xpu" and not is_torch_xpu_available():
            raise ValueError(
                f"MEROAI_TEST_DEVICE={torch_device}, but XPU is unavailable. Please double-check your testing environment."
            )
        if torch_device == "npu" and not is_torch_npu_available():
            raise ValueError(
                f"MEROAI_TEST_DEVICE={torch_device}, but NPU is unavailable. Please double-check your testing environment."
            )
        if torch_device == "mlu" and not is_torch_mlu_available():
            raise ValueError(
                f"MEROAI_TEST_DEVICE={torch_device}, but MLU is unavailable. Please double-check your testing environment."
            )
        if torch_device == "hpu" and not is_torch_hpu_available():
            raise ValueError(
                f"MEROAI_TEST_DEVICE={torch_device}, but HPU is unavailable. Please double-check your testing environment."
            )
        try:
            _ = torch.device(torch_device)
        except RuntimeError as e:
            raise RuntimeError(
                f"Unknown testing device specified by environment variable `MEROAI_TEST_DEVICE`: {torch_device}"
            ) from e
    elif torch.cuda.is_available():
        torch_device = "cuda"
    elif is_torch_npu_available():
        torch_device = "npu"
    elif is_torch_mlu_available():
        torch_device = "mlu"
    elif is_torch_hpu_available():
        torch_device = "hpu"
    elif is_torch_xpu_available():
        torch_device = "xpu"
    else:
        torch_device = "cpu"
else:
    torch_device = None
if is_tf_available():
    import tensorflow as tf
if is_flax_available():
    import jax
    jax_device = jax.default_backend()
else:
    jax_device = None
def require_torchdynamo(test_case):
    return unittest.skipUnless(is_torchdynamo_available(), "test requires TorchDynamo")(test_case)
def require_torchao(test_case):
    return unittest.skipUnless(is_torchao_available(), "test requires torchao")(test_case)
def require_torchao_version_greater_or_equal(torchao_version):
    def decorator(test_case):
        correct_torchao_version = is_torchao_available() and version.parse(
            version.parse(importlib.metadata.version("torchao")).base_version
        ) >= version.parse(torchao_version)
        return unittest.skipUnless(
            correct_torchao_version, f"Test requires torchao with the version greater than {torchao_version}."
        )(test_case)
    return decorator
def require_torch_tensorrt_fx(test_case):
    return unittest.skipUnless(is_torch_tensorrt_fx_available(), "test requires Torch-TensorRT FX")(test_case)
def require_torch_gpu(test_case):
    return unittest.skipUnless(torch_device == "cuda", "test requires CUDA")(test_case)
def require_torch_mps(test_case):
    return unittest.skipUnless(torch_device == "mps", "test requires MPS")(test_case)
def require_large_cpu_ram(test_case, memory: float = 80):
    if not is_psutil_available():
        return test_case
    import psutil
    return unittest.skipUnless(
        psutil.virtual_memory().total / 1024**3 > memory,
        f"test requires a machine with more than {memory} GiB of CPU RAM memory",
    )(test_case)
def require_torch_large_gpu(test_case, memory: float = 20):
    if torch_device != "cuda":
        return unittest.skip(reason=f"test requires a CUDA GPU with more than {memory} GiB of memory")(test_case)
    return unittest.skipUnless(
        torch.cuda.get_device_properties(0).total_memory / 1024**3 > memory,
        f"test requires a GPU with more than {memory} GiB of memory",
    )(test_case)
def require_torch_large_accelerator(test_case, memory: float = 20):
    if torch_device != "cuda" and torch_device != "xpu":
        return unittest.skip(reason=f"test requires a GPU or XPU with more than {memory} GiB of memory")(test_case)
    torch_accelerator_module = getattr(torch, torch_device)
    return unittest.skipUnless(
        torch_accelerator_module.get_device_properties(0).total_memory / 1024**3 > memory,
        f"test requires a GPU or XPU with more than {memory} GiB of memory",
    )(test_case)
def require_torch_gpu_if_bnb_not_multi_backend_enabled(test_case):
    if is_bitsandbytes_available() and is_bitsandbytes_multi_backend_available():
        return test_case
    return require_torch_gpu(test_case)
def require_torch_accelerator(test_case):
    return unittest.skipUnless(torch_device is not None and torch_device != "cpu", "test requires accelerator")(
        test_case
    )
def require_torch_fp16(test_case):
    return unittest.skipUnless(
        is_torch_fp16_available_on_device(torch_device), "test requires device with fp16 support"
    )(test_case)
def require_fp8(test_case):
    return unittest.skipUnless(is_accelerate_available() and is_fp8_available(), "test requires fp8 support")(
        test_case
    )
def require_torch_bf16(test_case):
    return unittest.skipUnless(
        is_torch_bf16_available_on_device(torch_device), "test requires device with bf16 support"
    )(test_case)
def require_torch_bf16_gpu(test_case):
    return unittest.skipUnless(
        is_torch_bf16_gpu_available(),
        "test requires torch>=1.10, using Ampere GPU or newer arch with cuda>=11.0",
    )(test_case)
def require_deterministic_for_xpu(test_case):
    @wraps(test_case)
    def wrapper(*args, **kwargs):
        if is_torch_xpu_available():
            original_state = torch.are_deterministic_algorithms_enabled()
            try:
                torch.use_deterministic_algorithms(True)
                return test_case(*args, **kwargs)
            finally:
                torch.use_deterministic_algorithms(original_state)
        else:
            return test_case(*args, **kwargs)
    return wrapper
def require_torch_tf32(test_case):
    return unittest.skipUnless(
        is_torch_tf32_available(), "test requires Ampere or a newer GPU arch, cuda>=11 and torch>=1.7"
    )(test_case)
def require_detectron2(test_case):
    return unittest.skipUnless(is_detectron2_available(), "test requires `detectron2`")(test_case)
def require_faiss(test_case):
    return unittest.skipUnless(is_faiss_available(), "test requires `faiss`")(test_case)
def require_optuna(test_case):
    return unittest.skipUnless(is_optuna_available(), "test requires optuna")(test_case)
def require_ray(test_case):
    return unittest.skipUnless(is_ray_available(), "test requires Ray/tune")(test_case)
def require_sigopt(test_case):
    return unittest.skipUnless(is_sigopt_available(), "test requires SigOpt")(test_case)
def require_swanlab(test_case):
    return unittest.skipUnless(is_swanlab_available(), "test requires swanlab")(test_case)
def require_trackio(test_case):
    return unittest.skipUnless(is_trackio_available(), "test requires trackio")(test_case)
def require_wandb(test_case):
    return unittest.skipUnless(is_wandb_available(), "test requires wandb")(test_case)
def require_clearml(test_case):
    return unittest.skipUnless(is_clearml_available(), "test requires clearml")(test_case)
def require_deepspeed(test_case):
    return unittest.skipUnless(is_deepspeed_available(), "test requires deepspeed")(test_case)
def require_apex(test_case):
    return unittest.skipUnless(is_apex_available(), "test requires apex")(test_case)
def require_aqlm(test_case):
    return unittest.skipUnless(is_aqlm_available(), "test requires aqlm")(test_case)
def require_vptq(test_case):
    return unittest.skipUnless(is_vptq_available(), "test requires vptq")(test_case)
def require_spqr(test_case):
    return unittest.skipUnless(is_spqr_available(), "test requires spqr")(test_case)
def require_eetq(test_case):
    eetq_available = is_eetq_available()
    if eetq_available:
        try:
            import eetq
        except ImportError as exc:
            if "shard_checkpoint" in str(exc):
                eetq_available = False
    return unittest.skipUnless(eetq_available, "test requires eetq")(test_case)
def require_av(test_case):
    return unittest.skipUnless(is_av_available(), "test requires av")(test_case)
def require_decord(test_case):
    return unittest.skipUnless(is_decord_available(), "test requires decord")(test_case)
def require_bitsandbytes(test_case):
    if is_bitsandbytes_available() and is_torch_available():
        try:
            import pytest
            return pytest.mark.bitsandbytes(test_case)
        except ImportError:
            return test_case
    else:
        return unittest.skip(reason="test requires bitsandbytes and torch")(test_case)
def require_optimum(test_case):
    return unittest.skipUnless(is_optimum_available(), "test requires optimum")(test_case)
def require_tensorboard(test_case):
    return unittest.skipUnless(is_tensorboard_available(), "test requires tensorboard")
def require_gptq(test_case):
    return unittest.skipUnless(
        is_gptqmodel_available() or is_auto_gptq_available(), "test requires gptqmodel or auto-gptq"
    )(test_case)
def require_hqq(test_case):
    return unittest.skipUnless(is_hqq_available(), "test requires hqq")(test_case)
def require_auto_awq(test_case):
    return unittest.skipUnless(is_auto_awq_available(), "test requires autoawq")(test_case)
def require_auto_round(test_case):
    return unittest.skipUnless(is_auto_round_available(), "test requires autoround")(test_case)
def require_optimum_quanto(test_case):
    return unittest.skipUnless(is_optimum_quanto_available(), "test requires optimum-quanto")(test_case)
def require_compressed_tensors(test_case):
    return unittest.skipUnless(is_compressed_tensors_available(), "test requires compressed_tensors")(test_case)
def require_fbgemm_gpu(test_case):
    return unittest.skipUnless(is_fbgemm_gpu_available(), "test requires fbgemm-gpu")(test_case)
def require_quark(test_case):
    return unittest.skipUnless(is_quark_available(), "test requires quark")(test_case)
def require_flute_hadamard(test_case):
    return unittest.skipUnless(
        is_flute_available() and is_hadamard_available(), "test requires flute and fast_hadamard_transform"
    )(test_case)
def require_fp_quant(test_case):
    return unittest.skipUnless(is_fp_quant_available(), "test requires fp_quant")(test_case)
def require_qutlass(test_case):
    return unittest.skipUnless(is_qutlass_available(), "test requires qutlass")(test_case)
def require_phonemizer(test_case):
    return unittest.skipUnless(is_phonemizer_available(), "test requires phonemizer")(test_case)
def require_pyctcdecode(test_case):
    return unittest.skipUnless(is_pyctcdecode_available(), "test requires pyctcdecode")(test_case)
def require_librosa(test_case):
    return unittest.skipUnless(is_librosa_available(), "test requires librosa")(test_case)
def require_liger_kernel(test_case):
    return unittest.skipUnless(is_liger_kernel_available(), "test requires liger_kernel")(test_case)
def require_essentia(test_case):
    return unittest.skipUnless(is_essentia_available(), "test requires essentia")(test_case)
def require_pretty_midi(test_case):
    return unittest.skipUnless(is_pretty_midi_available(), "test requires pretty_midi")(test_case)
def cmd_exists(cmd):
    return shutil.which(cmd) is not None
def require_usr_bin_time(test_case):
    return unittest.skipUnless(cmd_exists("/usr/bin/time"), "test requires /usr/bin/time")(test_case)
def require_sudachi(test_case):
    return unittest.skipUnless(is_sudachi_available(), "test requires sudachi")(test_case)
def require_sudachi_projection(test_case):
    return unittest.skipUnless(is_sudachi_projection_available(), "test requires sudachi which supports projection")(
        test_case
    )
def require_jumanpp(test_case):
    return unittest.skipUnless(is_jumanpp_available(), "test requires jumanpp")(test_case)
def require_cython(test_case):
    return unittest.skipUnless(is_cython_available(), "test requires cython")(test_case)
def require_tiktoken(test_case):
    return unittest.skipUnless(is_tiktoken_available(), "test requires TikToken")(test_case)
def require_speech(test_case):
    return unittest.skipUnless(is_speech_available(), "test requires torchaudio")(test_case)
def require_openai(test_case):
    return unittest.skipUnless(is_openai_available(), "test requires openai")(test_case)
def require_mistral_common(test_case):
    return unittest.skipUnless(is_mistral_common_available(), "test requires mistral-common")(test_case)
def get_gpu_count():
    if is_torch_available():
        import torch
        return torch.cuda.device_count()
    elif is_tf_available():
        import tensorflow as tf
        return len(tf.config.list_physical_devices("GPU"))
    elif is_flax_available():
        import jax
        return jax.device_count()
    else:
        return 0
def get_tests_dir(append_path=None):
    caller__file__ = inspect.stack()[1][1]
    tests_dir = os.path.abspath(os.path.dirname(caller__file__))
    while not tests_dir.endswith("tests"):
        tests_dir = os.path.dirname(tests_dir)
    if append_path:
        return os.path.join(tests_dir, append_path)
    else:
        return tests_dir
def get_steps_per_epoch(trainer: Trainer) -> int:
    training_args = trainer.args
    train_dataloader = trainer.get_train_dataloader()
    initial_training_values = trainer.set_initial_training_values(
        args=training_args,
        dataloader=train_dataloader,
        total_train_batch_size=training_args.per_device_train_batch_size,
    )
    steps_per_epoch = initial_training_values[1]
    return steps_per_epoch
def evaluate_side_effect_factory(
    side_effect_values: list[dict[str, float]],
) -> Generator[dict[str, float], None, None]:
    yield from side_effect_values
    while True:
        yield side_effect_values[-1]
def apply_print_resets(buf):
    return re.sub(r"^.*\r", "", buf, 0, re.MULTILINE)
def assert_screenout(out, what):
    out_pr = apply_print_resets(out).lower()
    match_str = out_pr.find(what.lower())
    assert match_str != -1, f"expecting to find {what} in output: f{out_pr}"
def set_config_for_less_flaky_test(config):
    target_attrs = [
        "rms_norm_eps",
        "layer_norm_eps",
        "norm_eps",
        "norm_epsilon",
        "layer_norm_epsilon",
        "batch_norm_eps",
    ]
    for target_attr in target_attrs:
        setattr(config, target_attr, 1.0)
    attrs = ["text_config", "vision_config", "text_encoder", "audio_encoder", "decoder"]
    for attr in attrs:
        if hasattr(config, attr):
            for target_attr in target_attrs:
                setattr(getattr(config, attr), target_attr, 1.0)
def set_model_for_less_flaky_test(model):
    target_names = (
        "LayerNorm",
        "GroupNorm",
        "BatchNorm",
        "RMSNorm",
        "BatchNorm2d",
        "BatchNorm1d",
        "BitGroupNormActivation",
        "WeightStandardizedConv2d",
    )
    target_attrs = ["eps", "epsilon", "variance_epsilon"]
    if is_torch_available() and isinstance(model, torch.nn.Module):
        for module in model.modules():
            if type(module).__name__.endswith(target_names):
                for attr in target_attrs:
                    if hasattr(module, attr):
                        setattr(module, attr, 1.0)
class CaptureStd:
    def __init__(self, out=True, err=True, replay=True):
        self.replay = replay
        if out:
            self.out_buf = StringIO()
            self.out = "error: CaptureStd context is unfinished yet, called too early"
        else:
            self.out_buf = None
            self.out = "not capturing stdout"
        if err:
            self.err_buf = StringIO()
            self.err = "error: CaptureStd context is unfinished yet, called too early"
        else:
            self.err_buf = None
            self.err = "not capturing stderr"
    def __enter__(self):
        if self.out_buf:
            self.out_old = sys.stdout
            sys.stdout = self.out_buf
        if self.err_buf:
            self.err_old = sys.stderr
            sys.stderr = self.err_buf
        return self
    def __exit__(self, *exc):
        if self.out_buf:
            sys.stdout = self.out_old
            captured = self.out_buf.getvalue()
            if self.replay:
                sys.stdout.write(captured)
            self.out = apply_print_resets(captured)
        if self.err_buf:
            sys.stderr = self.err_old
            captured = self.err_buf.getvalue()
            if self.replay:
                sys.stderr.write(captured)
            self.err = captured
    def __repr__(self):
        msg = ""
        if self.out_buf:
            msg += f"stdout: {self.out}\n"
        if self.err_buf:
            msg += f"stderr: {self.err}\n"
        return msg
class CaptureStdout(CaptureStd):
    def __init__(self, replay=True):
        super().__init__(err=False, replay=replay)
class CaptureStderr(CaptureStd):
    def __init__(self, replay=True):
        super().__init__(out=False, replay=replay)
class CaptureLogger:
    def __init__(self, logger):
        self.logger = logger
        self.io = StringIO()
        self.sh = logging.StreamHandler(self.io)
        self.out = ""
    def __enter__(self):
        self.logger.addHandler(self.sh)
        return self
    def __exit__(self, *exc):
        self.logger.removeHandler(self.sh)
        self.out = self.io.getvalue()
    def __repr__(self):
        return f"captured: {self.out}\n"
@contextlib.contextmanager
def LoggingLevel(level):
    orig_level = MEROAI_logging.get_verbosity()
    try:
        MEROAI_logging.set_verbosity(level)
        yield
    finally:
        MEROAI_logging.set_verbosity(orig_level)
class TemporaryHubRepo:
    def __init__(self, namespace: Optional[str] = None, token: Optional[str] = None) -> None:
        self.token = token
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_id = Path(tmp_dir).name
            if namespace is not None:
                repo_id = f"{namespace}/{repo_id}"
            self.repo_url = huggingface_hub.create_repo(repo_id, token=self.token)
    def __enter__(self):
        return self.repo_url
    def __exit__(self, exc, value, tb):
        delete_repo(repo_id=self.repo_url.repo_id, token=self.token, missing_ok=True)
@contextlib.contextmanager
def ExtendSysPath(path: Union[str, os.PathLike]) -> Iterator[None]:
    path = os.fspath(path)
    try:
        sys.path.insert(0, path)
        yield
    finally:
        sys.path.remove(path)
class TestCasePlus(unittest.TestCase):
    def setUp(self):
        self.teardown_tmp_dirs = []
        self._test_file_path = inspect.getfile(self.__class__)
        path = Path(self._test_file_path).resolve()
        self._test_file_dir = path.parents[0]
        for up in [1, 2, 3]:
            tmp_dir = path.parents[up]
            if (tmp_dir / "src").is_dir() and (tmp_dir / "tests").is_dir():
                break
        if tmp_dir:
            self._repo_root_dir = tmp_dir
        else:
            raise ValueError(f"can't figure out the root of the repo from {self._test_file_path}")
        self._tests_dir = self._repo_root_dir / "tests"
        self._examples_dir = self._repo_root_dir / "examples"
        self._src_dir = self._repo_root_dir / "src"
    @property
    def test_file_path(self):
        return self._test_file_path
    @property
    def test_file_path_str(self):
        return str(self._test_file_path)
    @property
    def test_file_dir(self):
        return self._test_file_dir
    @property
    def test_file_dir_str(self):
        return str(self._test_file_dir)
    @property
    def tests_dir(self):
        return self._tests_dir
    @property
    def tests_dir_str(self):
        return str(self._tests_dir)
    @property
    def examples_dir(self):
        return self._examples_dir
    @property
    def examples_dir_str(self):
        return str(self._examples_dir)
    @property
    def repo_root_dir(self):
        return self._repo_root_dir
    @property
    def repo_root_dir_str(self):
        return str(self._repo_root_dir)
    @property
    def src_dir(self):
        return self._src_dir
    @property
    def src_dir_str(self):
        return str(self._src_dir)
    def get_env(self):
        env = os.environ.copy()
        paths = [self.repo_root_dir_str, self.src_dir_str]
        if "/examples" in self.test_file_dir_str:
            paths.append(self.examples_dir_str)
        else:
            paths.append(self.tests_dir_str)
        paths.append(env.get("PYTHONPATH", ""))
        env["PYTHONPATH"] = ":".join(paths)
        return env
    def get_auto_remove_tmp_dir(self, tmp_dir=None, before=None, after=None):
        if tmp_dir is not None:
            if before is None:
                before = True
            if after is None:
                after = False
            path = Path(tmp_dir).resolve()
            if not tmp_dir.startswith("./"):
                raise ValueError(
                    f"`tmp_dir` can only be a relative path, i.e. `./some/path`, but received `{tmp_dir}`"
                )
            if before is True and path.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
            path.mkdir(parents=True, exist_ok=True)
        else:
            if before is None:
                before = True
            if after is None:
                after = True
            tmp_dir = tempfile.mkdtemp()
        if after is True:
            self.teardown_tmp_dirs.append(tmp_dir)
        return tmp_dir
    def python_one_liner_max_rss(self, one_liner_str):
        if not cmd_exists("/usr/bin/time"):
            raise ValueError("/usr/bin/time is required, install with `apt install time`")
        cmd = shlex.split(f"/usr/bin/time -f %M python -c '{one_liner_str}'")
        with CaptureStd() as cs:
            execute_subprocess_async(cmd, env=self.get_env())
        max_rss = int(cs.err.split("\n")[-2].replace("stderr: ", "")) * 1024
        return max_rss
    def tearDown(self):
        for path in self.teardown_tmp_dirs:
            shutil.rmtree(path, ignore_errors=True)
        self.teardown_tmp_dirs = []
        if is_accelerate_available():
            AcceleratorState._reset_state()
            PartialState._reset_state()
            for k in list(os.environ.keys()):
                if "ACCELERATE" in k:
                    del os.environ[k]
def mockenv(**kwargs):
    return mock.patch.dict(os.environ, kwargs)
@contextlib.contextmanager
def mockenv_context(*remove, **update):
    env = os.environ
    update = update or {}
    remove = remove or []
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    update_after = {k: env[k] for k in stomped}
    remove_after = frozenset(k for k in update if k not in env)
    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]
pytest_opt_registered = {}
def pytest_addoption_shared(parser):
    option = "--make-reports"
    if option not in pytest_opt_registered:
        parser.addoption(
            option,
            action="store",
            default=False,
            help="generate report files. The value of this option is used as a prefix to report names",
        )
        pytest_opt_registered[option] = 1
def pytest_terminal_summary_main(tr, id):
    from _pytest.config import create_terminal_writer
    if not len(id):
        id = "tests"
    config = tr.config
    orig_writer = config.get_terminal_writer()
    orig_tbstyle = config.option.tbstyle
    orig_reportchars = tr.reportchars
    dir = f"reports/{id}"
    Path(dir).mkdir(parents=True, exist_ok=True)
    report_files = {
        k: f"{dir}/{k}.txt"
        for k in [
            "durations",
            "errors",
            "failures_long",
            "failures_short",
            "failures_line",
            "passes",
            "stats",
            "summary_short",
            "warnings",
        ]
    }
    dlist = []
    for replist in tr.stats.values():
        for rep in replist:
            if hasattr(rep, "duration"):
                dlist.append(rep)
    if dlist:
        dlist.sort(key=lambda x: x.duration, reverse=True)
        with open(report_files["durations"], "w") as f:
            durations_min = 0.05
            f.write("slowest durations\n")
            for i, rep in enumerate(dlist):
                if rep.duration < durations_min:
                    f.write(f"{len(dlist) - i} durations < {durations_min} secs were omitted")
                    break
                f.write(f"{rep.duration:02.2f}s {rep.when:<8} {rep.nodeid}\n")
    def summary_failures_short(tr):
        reports = tr.getreports("failed")
        if not reports:
            return
        tr.write_sep("=", "FAILURES SHORT STACK")
        for rep in reports:
            msg = tr._getfailureheadline(rep)
            tr.write_sep("_", msg, red=True, bold=True)
            longrepr = re.sub(r".*_ _ _ (_ ){10,}_ _ ", "", rep.longreprtext, 0, re.MULTILINE | re.DOTALL)
            tr._tw.line(longrepr)
    config.option.tbstyle = "auto"
    with open(report_files["failures_long"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files["failures_short"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        summary_failures_short(tr)
    config.option.tbstyle = "line"
    with open(report_files["failures_line"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_failures()
    with open(report_files["errors"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_errors()
    with open(report_files["warnings"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_warnings()
        tr.summary_warnings()
    tr.reportchars = "wPpsxXEf"
    with open(report_files["summary_short"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.short_test_summary()
    with open(report_files["stats"], "w") as f:
        tr._tw = create_terminal_writer(config, f)
        tr.summary_stats()
    tr._tw = orig_writer
    tr.reportchars = orig_reportchars
    config.option.tbstyle = orig_tbstyle
import asyncio
class _RunOutput:
    def __init__(self, returncode, stdout, stderr):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
async def _read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if line:
            callback(line)
        else:
            break
async def _stream_subprocess(cmd, env=None, stdin=None, timeout=None, quiet=False, echo=False) -> _RunOutput:
    if echo:
        print("\nRunning: ", " ".join(cmd))
    p = await asyncio.create_subprocess_exec(
        cmd[0],
        *cmd[1:],
        stdin=stdin,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    out = []
    err = []
    def tee(line, sink, pipe, label=""):
        line = line.decode("utf-8").rstrip()
        sink.append(line)
        if not quiet:
            print(label, line, file=pipe)
    await asyncio.wait(
        [
            asyncio.create_task(_read_stream(p.stdout, lambda l: tee(l, out, sys.stdout, label="stdout:"))),
            asyncio.create_task(_read_stream(p.stderr, lambda l: tee(l, err, sys.stderr, label="stderr:"))),
        ],
        timeout=timeout,
    )
    return _RunOutput(await p.wait(), out, err)
def execute_subprocess_async(cmd, env=None, stdin=None, timeout=180, quiet=False, echo=True) -> _RunOutput:
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        _stream_subprocess(cmd, env=env, stdin=stdin, timeout=timeout, quiet=quiet, echo=echo)
    )
    cmd_str = " ".join(cmd)
    if result.returncode > 0:
        stderr = "\n".join(result.stderr)
        raise RuntimeError(
            f"'{cmd_str}' failed with returncode {result.returncode}\n\n"
            f"The combined stderr from workers follows:\n{stderr}"
        )
    if not result.stdout and not result.stderr:
        raise RuntimeError(f"'{cmd_str}' produced no output.")
    return result
def pytest_xdist_worker_id():
    worker = os.environ.get("PYTEST_XDIST_WORKER", "gw0")
    worker = re.sub(r"^gw", "", worker, 0, re.MULTILINE)
    return int(worker)
def get_torch_dist_unique_port():
    port = 29500
    uniq_delta = pytest_xdist_worker_id()
    return port + uniq_delta
def nested_simplify(obj, decimals=3):
    import numpy as np
    if isinstance(obj, list):
        return [nested_simplify(item, decimals) for item in obj]
    if isinstance(obj, tuple):
        return tuple(nested_simplify(item, decimals) for item in obj)
    elif isinstance(obj, np.ndarray):
        return nested_simplify(obj.tolist())
    elif isinstance(obj, Mapping):
        return {nested_simplify(k, decimals): nested_simplify(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, (str, int, np.int64)) or obj is None:
        return obj
    elif is_torch_available() and isinstance(obj, torch.Tensor):
        return nested_simplify(obj.tolist(), decimals)
    elif is_tf_available() and tf.is_tensor(obj):
        return nested_simplify(obj.numpy().tolist())
    elif isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, (np.int32, np.float32, np.float16)):
        return nested_simplify(obj.item(), decimals)
    else:
        raise Exception(f"Not supported: {type(obj)}")
def check_json_file_has_correct_format(file_path):
    with open(file_path) as f:
        lines = f.readlines()
        if len(lines) == 1:
            assert lines[0] == "{}"
        else:
            assert len(lines) >= 3
            assert lines[0].strip() == "{"
            for line in lines[1:-1]:
                left_indent = len(lines[1]) - len(lines[1].lstrip())
                assert left_indent == 2
            assert lines[-1].strip() == "}"
def to_2tuple(x):
    if isinstance(x, collections.abc.Iterable):
        return x
    return (x, x)
class SubprocessCallException(Exception):
    pass
def run_command(command: list[str], return_stdout=False):
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        if return_stdout:
            if hasattr(output, "decode"):
                output = output.decode("utf-8")
            return output
    except subprocess.CalledProcessError as e:
        raise SubprocessCallException(
            f"Command `{' '.join(command)}` failed with the following error:\n\n{e.output.decode()}"
        ) from e
class RequestCounter:
    def __enter__(self):
        self._counter = defaultdict(int)
        self._thread_id = threading.get_ident()
        self._extra_info = []
        def patched_with_thread_info(func):
            def wrap(*args, **kwargs):
                self._extra_info.append(threading.get_ident())
                return func(*args, **kwargs)
            return wrap
        self.patcher = patch.object(
            urllib3.connectionpool.log, "debug", side_effect=patched_with_thread_info(urllib3.connectionpool.log.debug)
        )
        self.mock = self.patcher.start()
        return self
    def __exit__(self, *args, **kwargs) -> None:
        assert len(self.mock.call_args_list) == len(self._extra_info)
        for thread_id, call in zip(self._extra_info, self.mock.call_args_list):
            if thread_id != self._thread_id:
                continue
            if call.args[-2] == 307:
                continue
            log = call.args[0] % call.args[1:]
            for method in ("HEAD", "GET", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"):
                if method in log:
                    self._counter[method] += 1
                    break
        self.patcher.stop()
    def __getitem__(self, key: str) -> int:
        return self._counter[key]
    @property
    def total_calls(self) -> int:
        return sum(self._counter.values())
def is_flaky(max_attempts: int = 5, wait_before_retry: Optional[float] = None, description: Optional[str] = None):
    def decorator(test_func_ref):
        @functools.wraps(test_func_ref)
        def wrapper(*args, **kwargs):
            retry_count = 1
            while retry_count < max_attempts:
                try:
                    return test_func_ref(*args, **kwargs)
                except Exception as err:
                    logger.error(f"Test failed with {err} at try {retry_count}/{max_attempts}.")
                    if wait_before_retry is not None:
                        time.sleep(wait_before_retry)
                    retry_count += 1
            return test_func_ref(*args, **kwargs)
        return unittest.skipUnless(_run_flaky_tests, "test is flaky")(wrapper)
    return decorator
def hub_retry(max_attempts: int = 5, wait_before_retry: Optional[float] = 2):
    def decorator(test_func_ref):
        @functools.wraps(test_func_ref)
        def wrapper(*args, **kwargs):
            retry_count = 1
            while retry_count < max_attempts:
                try:
                    return test_func_ref(*args, **kwargs)
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.HTTPError,
                    requests.exceptions.RequestException,
                ) as err:
                    logger.error(
                        f"Test failed with {err} at try {retry_count}/{max_attempts} as it couldn't connect to the specified Hub repository."
                    )
                    if wait_before_retry is not None:
                        time.sleep(wait_before_retry)
                    retry_count += 1
            return test_func_ref(*args, **kwargs)
        return wrapper
    return decorator
def run_first(test_case):
    import pytest
    return pytest.mark.order(1)(test_case)
def run_test_in_subprocess(test_case, target_func, inputs=None, timeout=None):
    if timeout is None:
        timeout = int(os.environ.get("PYTEST_TIMEOUT", "600"))
    start_methohd = "spawn"
    ctx = multiprocessing.get_context(start_methohd)
    input_queue = ctx.Queue(1)
    output_queue = ctx.JoinableQueue(1)
    input_queue.put(inputs, timeout=timeout)
    process = ctx.Process(target=target_func, args=(input_queue, output_queue, timeout))
    process.start()
    try:
        results = output_queue.get(timeout=timeout)
        output_queue.task_done()
    except Exception as e:
        process.terminate()
        test_case.fail(e)
    process.join(timeout=timeout)
    if results["error"] is not None:
        test_case.fail(f"{results['error']}")
def run_test_using_subprocess(func):
    import pytest
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if os.getenv("_INSIDE_SUB_PROCESS", None) == "1":
            func(*args, **kwargs)
        else:
            test = " ".join(os.environ.get("PYTEST_CURRENT_TEST").split(" ")[:-1])
            try:
                env = copy.deepcopy(os.environ)
                env["_INSIDE_SUB_PROCESS"] = "1"
                env["CI"] = "true"
                if "pytestconfig" in kwargs:
                    command = list(kwargs["pytestconfig"].invocation_params.args)
                    for idx, x in enumerate(command):
                        if x in kwargs["pytestconfig"].args:
                            test = test.split("::")[1:]
                            command[idx] = "::".join([f"{func.__globals__['__file__']}"] + test)
                    command = [f"{sys.executable}", "-m", "pytest"] + command
                    command = [x for x in command if x != "--no-summary"]
                else:
                    command = [f"{sys.executable}", "-m", "pytest", f"{test}"]
                subprocess.run(command, env=env, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                exception_message = e.stdout.decode()
                lines = exception_message.split("\n")
                if "= test session starts =" in lines[0]:
                    text = ""
                    for line in lines[1:]:
                        if line.startswith("FAILED "):
                            text = line[len("FAILED ") :]
                            text = "".join(text.split(" - ")[1:])
                        elif line.startswith("=") and line.endswith("=") and " failed in " in line:
                            break
                        elif len(text) > 0:
                            text += f"\n{line}"
                    text = "(subprocess) " + text
                    lines = [text] + lines
                exception_message = "\n".join(lines)
                raise pytest.fail(exception_message, pytrace=False)
    return wrapper
def preprocess_string(string, skip_cuda_tests):
    codeblock_pattern = r"(```(?:python|py)\s*\n\s*>>> )(.*?```)"
    codeblocks = re.split(codeblock_pattern, string, flags=re.DOTALL)
    is_cuda_found = False
    for i, codeblock in enumerate(codeblocks):
        if "load_dataset(" in codeblock and "# doctest: +IGNORE_RESULT" not in codeblock:
            codeblocks[i] = re.sub(r"(>>> .*load_dataset\(.*)", r"\1 # doctest: +IGNORE_RESULT", codeblock)
        if (
            (">>>" in codeblock or "..." in codeblock)
            and re.search(r"cuda|to\(0\)|device=0", codeblock)
            and skip_cuda_tests
        ):
            is_cuda_found = True
            break
    modified_string = ""
    if not is_cuda_found:
        modified_string = "".join(codeblocks)
    return modified_string
class HfDocTestParser(doctest.DocTestParser):
, re.MULTILINE | re.VERBOSE
    )
    skip_cuda_tests: bool = bool(os.environ.get("SKIP_CUDA_DOCTEST", "0"))
    def parse(self, string, name="<string>"):
        string = preprocess_string(string, self.skip_cuda_tests)
        return super().parse(string, name)
class HfDoctestModule(Module):
    def collect(self) -> Iterable[DoctestItem]:
        class MockAwareDocTestFinder(doctest.DocTestFinder):
            def _find_lineno(self, obj, source_lines):
                if isinstance(obj, property):
                    obj = getattr(obj, "fget", obj)
                if hasattr(obj, "__wrapped__"):
                    obj = inspect.unwrap(obj)
                return super()._find_lineno(
                    obj,
                    source_lines,
                )
            def _find(self, tests, obj, name, module, source_lines, globs, seen) -> None:
                if _is_mocked(obj):
                    return
                with _patch_unwrap_mock_aware():
                    super()._find(
                        tests, obj, name, module, source_lines, globs, seen
                    )
        if self.path.name == "conftest.py":
            module = self.config.pluginmanager._importconftest(
                self.path,
                self.config.getoption("importmode"),
                rootpath=self.config.rootpath,
            )
        else:
            try:
                module = import_path(
                    self.path,
                    root=self.config.rootpath,
                    mode=self.config.getoption("importmode"),
                )
            except ImportError:
                if self.config.getvalue("doctest_ignore_import_errors"):
                    skip("unable to import module %r" % self.path)
                else:
                    raise
        finder = MockAwareDocTestFinder(parser=HfDocTestParser())
        optionflags = get_optionflags(self)
        runner = _get_runner(
            verbose=False,
            optionflags=optionflags,
            checker=_get_checker(),
            continue_on_failure=_get_continue_on_failure(self.config),
        )
        for test in finder.find(module, module.__name__):
            if test.examples:
                yield DoctestItem.from_parent(self, name=test.name, runner=runner, dtest=test)
def _device_agnostic_dispatch(device: str, dispatch_table: dict[str, Callable], *args, **kwargs):
    if device not in dispatch_table:
        if not callable(dispatch_table["default"]):
            return dispatch_table["default"]
        return dispatch_table["default"](*args, **kwargs)
    fn = dispatch_table[device]
    if not callable(fn):
        return fn
    return fn(*args, **kwargs)
if is_torch_available():
    BACKEND_MANUAL_SEED = {
        "cuda": torch.cuda.manual_seed,
        "cpu": torch.manual_seed,
        "default": torch.manual_seed,
    }
    BACKEND_EMPTY_CACHE = {
        "cuda": torch.cuda.empty_cache,
        "cpu": None,
        "default": None,
    }
    BACKEND_DEVICE_COUNT = {
        "cuda": torch.cuda.device_count,
        "cpu": lambda: 0,
        "default": lambda: 1,
    }
    BACKEND_RESET_MAX_MEMORY_ALLOCATED = {
        "cuda": torch.cuda.reset_max_memory_allocated,
        "cpu": None,
        "default": None,
    }
    BACKEND_MAX_MEMORY_ALLOCATED = {
        "cuda": torch.cuda.max_memory_allocated,
        "cpu": 0,
        "default": 0,
    }
    BACKEND_RESET_PEAK_MEMORY_STATS = {
        "cuda": torch.cuda.reset_peak_memory_stats,
        "cpu": None,
        "default": None,
    }
    BACKEND_MEMORY_ALLOCATED = {
        "cuda": torch.cuda.memory_allocated,
        "cpu": 0,
        "default": 0,
    }
    BACKEND_SYNCHRONIZE = {
        "cuda": torch.cuda.synchronize,
        "cpu": None,
        "default": None,
    }
    BACKEND_TORCH_ACCELERATOR_MODULE = {
        "cuda": torch.cuda,
        "cpu": None,
        "default": None,
    }
else:
    BACKEND_MANUAL_SEED = {"default": None}
    BACKEND_EMPTY_CACHE = {"default": None}
    BACKEND_DEVICE_COUNT = {"default": lambda: 0}
    BACKEND_RESET_MAX_MEMORY_ALLOCATED = {"default": None}
    BACKEND_RESET_PEAK_MEMORY_STATS = {"default": None}
    BACKEND_MAX_MEMORY_ALLOCATED = {"default": 0}
    BACKEND_MEMORY_ALLOCATED = {"default": 0}
    BACKEND_SYNCHRONIZE = {"default": None}
    BACKEND_TORCH_ACCELERATOR_MODULE = {"default": None}
if is_torch_hpu_available():
    BACKEND_MANUAL_SEED["hpu"] = torch.hpu.manual_seed
    BACKEND_DEVICE_COUNT["hpu"] = torch.hpu.device_count
    BACKEND_TORCH_ACCELERATOR_MODULE["hpu"] = torch.hpu
if is_torch_mlu_available():
    BACKEND_EMPTY_CACHE["mlu"] = torch.mlu.empty_cache
    BACKEND_MANUAL_SEED["mlu"] = torch.mlu.manual_seed
    BACKEND_DEVICE_COUNT["mlu"] = torch.mlu.device_count
    BACKEND_TORCH_ACCELERATOR_MODULE["mlu"] = torch.mlu
if is_torch_npu_available():
    BACKEND_EMPTY_CACHE["npu"] = torch.npu.empty_cache
    BACKEND_MANUAL_SEED["npu"] = torch.npu.manual_seed
    BACKEND_DEVICE_COUNT["npu"] = torch.npu.device_count
    BACKEND_TORCH_ACCELERATOR_MODULE["npu"] = torch.npu
if is_torch_xpu_available():
    BACKEND_EMPTY_CACHE["xpu"] = torch.xpu.empty_cache
    BACKEND_MANUAL_SEED["xpu"] = torch.xpu.manual_seed
    BACKEND_DEVICE_COUNT["xpu"] = torch.xpu.device_count
    BACKEND_RESET_MAX_MEMORY_ALLOCATED["xpu"] = torch.xpu.reset_peak_memory_stats
    BACKEND_RESET_PEAK_MEMORY_STATS["xpu"] = torch.xpu.reset_peak_memory_stats
    BACKEND_MAX_MEMORY_ALLOCATED["xpu"] = torch.xpu.max_memory_allocated
    BACKEND_MEMORY_ALLOCATED["xpu"] = torch.xpu.memory_allocated
    BACKEND_SYNCHRONIZE["xpu"] = torch.xpu.synchronize
    BACKEND_TORCH_ACCELERATOR_MODULE["xpu"] = torch.xpu
if is_torch_xla_available():
    BACKEND_EMPTY_CACHE["xla"] = torch.cuda.empty_cache
    BACKEND_MANUAL_SEED["xla"] = torch.cuda.manual_seed
    BACKEND_DEVICE_COUNT["xla"] = torch.cuda.device_count
def backend_manual_seed(device: str, seed: int):
    return _device_agnostic_dispatch(device, BACKEND_MANUAL_SEED, seed)
def backend_empty_cache(device: str):
    return _device_agnostic_dispatch(device, BACKEND_EMPTY_CACHE)
def backend_device_count(device: str):
    return _device_agnostic_dispatch(device, BACKEND_DEVICE_COUNT)
def backend_reset_max_memory_allocated(device: str):
    return _device_agnostic_dispatch(device, BACKEND_RESET_MAX_MEMORY_ALLOCATED)
def backend_reset_peak_memory_stats(device: str):
    return _device_agnostic_dispatch(device, BACKEND_RESET_PEAK_MEMORY_STATS)
def backend_max_memory_allocated(device: str):
    return _device_agnostic_dispatch(device, BACKEND_MAX_MEMORY_ALLOCATED)
def backend_memory_allocated(device: str):
    return _device_agnostic_dispatch(device, BACKEND_MEMORY_ALLOCATED)
def backend_synchronize(device: str):
    return _device_agnostic_dispatch(device, BACKEND_SYNCHRONIZE)
def backend_torch_accelerator_module(device: str):
    return _device_agnostic_dispatch(device, BACKEND_TORCH_ACCELERATOR_MODULE)
if is_torch_available():
    if "MEROAI_TEST_DEVICE_SPEC" in os.environ:
        device_spec_path = os.environ["MEROAI_TEST_DEVICE_SPEC"]
        if not Path(device_spec_path).is_file():
            raise ValueError(
                f"Specified path to device spec file is not a file or not found. Received '{device_spec_path}"
            )
        device_spec_dir, _ = os.path.split(os.path.realpath(device_spec_path))
        sys.path.append(device_spec_dir)
        try:
            import_name = device_spec_path[: device_spec_path.index(".py")]
        except ValueError as e:
            raise ValueError(f"Provided device spec file was not a Python file! Received '{device_spec_path}") from e
        device_spec_module = importlib.import_module(import_name)
        try:
            device_name = device_spec_module.DEVICE_NAME
        except AttributeError as e:
            raise AttributeError("Device spec file did not contain `DEVICE_NAME`") from e
        if "MEROAI_TEST_DEVICE" in os.environ and torch_device != device_name:
            msg = f"Mismatch between environment variable `MEROAI_TEST_DEVICE` '{torch_device}' and device found in spec '{device_name}'\n"
            msg += "Either unset `MEROAI_TEST_DEVICE` or ensure it matches device spec name."
            raise ValueError(msg)
        torch_device = device_name
        def update_mapping_from_spec(device_fn_dict: dict[str, Callable], attribute_name: str):
            try:
                spec_fn = getattr(device_spec_module, attribute_name)
                device_fn_dict[torch_device] = spec_fn
            except AttributeError as e:
                if "default" not in device_fn_dict:
                    raise AttributeError(
                        f"`{attribute_name}` not found in '{device_spec_path}' and no default fallback function found."
                    ) from e
        update_mapping_from_spec(BACKEND_MANUAL_SEED, "MANUAL_SEED_FN")
        update_mapping_from_spec(BACKEND_EMPTY_CACHE, "EMPTY_CACHE_FN")
        update_mapping_from_spec(BACKEND_DEVICE_COUNT, "DEVICE_COUNT_FN")
def compare_pipeline_output_to_hub_spec(output, hub_spec):
    missing_keys = []
    unexpected_keys = []
    all_field_names = {field.name for field in fields(hub_spec)}
    matching_keys = sorted([key for key in output if key in all_field_names])
    for field in fields(hub_spec):
        if field.default is MISSING and field.name not in output:
            missing_keys.append(field.name)
    for output_key in output:
        if output_key not in all_field_names:
            unexpected_keys.append(output_key)
    if missing_keys or unexpected_keys:
        error = ["Pipeline output does not match Hub spec!"]
        if matching_keys:
            error.append(f"Matching keys: {matching_keys}")
        if missing_keys:
            error.append(f"Missing required keys in pipeline output: {missing_keys}")
        if unexpected_keys:
            error.append(f"Keys in pipeline output that are not in Hub spec: {unexpected_keys}")
        raise KeyError("\n".join(error))
@require_torch
def cleanup(device: str, gc_collect=False):
    if gc_collect:
        gc.collect()
    backend_empty_cache(device)
    torch._dynamo.reset()
DeviceProperties = tuple[Optional[str], Optional[int], Optional[int]]
PackedDeviceProperties = tuple[Optional[str], Union[None, int, tuple[int, int]]]
@cache
def get_device_properties() -> DeviceProperties:
    if IS_CUDA_SYSTEM or IS_ROCM_SYSTEM:
        import torch
        major, minor = torch.cuda.get_device_capability()
        if IS_ROCM_SYSTEM:
            return ("rocm", major, minor)
        else:
            return ("cuda", major, minor)
    elif IS_XPU_SYSTEM:
        import torch
        arch = torch.xpu.get_device_capability()["architecture"]
        gen_mask = 0x000000FF00000000
        gen = (arch & gen_mask) >> 32
        return ("xpu", gen, None)
    else:
        return (torch_device, None, None)
def unpack_device_properties(
    properties: Optional[PackedDeviceProperties] = None,
) -> DeviceProperties:
    if properties is None:
        return get_device_properties()
    device_type, major_minor = properties
    if major_minor is None:
        major, minor = None, None
    elif isinstance(major_minor, int):
        major, minor = major_minor, None
    else:
        major, minor = major_minor
    return device_type, major, minor
class Expectations(UserDict[PackedDeviceProperties, Any]):
    def get_expectation(self) -> Any:
        return self.find_expectation(get_device_properties())
    def unpacked(self) -> list[tuple[DeviceProperties, Any]]:
        return [(unpack_device_properties(k), v) for k, v in self.data.items()]
    @staticmethod
    def is_default(expectation_key: PackedDeviceProperties) -> bool:
        return all(p is None for p in expectation_key)
    @staticmethod
    def score(properties: DeviceProperties, other: DeviceProperties) -> float:
        device_type, major, minor = properties
        other_device_type, other_major, other_minor = other
        score = 0
        if device_type is not None and device_type == other_device_type:
            score += 1
            if major is not None and major == other_major:
                score += 1
                if minor is not None and minor == other_minor:
                    score += 1
        elif device_type in ["cuda", "rocm"] and other_device_type in ["cuda", "rocm"]:
            score = 0.1
        if Expectations.is_default(other):
            score = 0.5
        return score
    def find_expectation(self, properties: DeviceProperties = (None, None, None)) -> Any:
        (result_key, result) = max(
            self.unpacked(),
            key=lambda x: (
                Expectations.score(properties, x[0]),
                x[0][1] if x[0][1] is not None else -1,
                x[0][2] if x[0][2] is not None else -1,
            ),
        )
        if Expectations.score(properties, result_key) == 0:
            raise ValueError(f"No matching expectation found for {properties}")
        return result
    def __repr__(self):
        return f"{self.data}"
def patch_torch_compile_force_graph():
    force_fullgraph = os.environ.get("TORCH_COMPILE_FORCE_FULLGRAPH", "")
    force_fullgraph = force_fullgraph.lower() in ("yes", "true", "on", "t", "y", "1")
    if force_fullgraph:
        import torch
        orig_method = torch.compile
        def patched(*args, **kwargs):
            kwargs["fullgraph"] = True
            return orig_method(*args, **kwargs)
        torch.compile = patched
def _get_test_info():
    full_test_name = os.environ.get("PYTEST_CURRENT_TEST", "").split(" ")[0]
    test_file, test_class, test_name = full_test_name.split("::")
    stack_from_inspect = inspect.stack()
    actual_test_file, _actual_test_class = test_file, test_class
    test_frame, test_obj, test_method = None, None, None
    for frame in reversed(stack_from_inspect):
        if (
            frame.function == test_name
            and "self" in frame.frame.f_locals
            and hasattr(frame.frame.f_locals["self"], test_name)
        ):
            test_frame = frame
            test_obj = frame.frame.f_locals["self"]
            actual_test_file = frame.filename
            test_method = getattr(test_obj, test_name)
            break
    if test_frame is not None:
        line_number = test_frame.lineno
    frame_of_patched_obj = None
    captured_frames = []
    to_capture = False
    for frame in reversed(stack_from_inspect):
        if (
            frame.function == test_name
            and "self" in frame.frame.f_locals
            and hasattr(frame.frame.f_locals["self"], test_name)
        ):
            to_capture = True
        elif "patched" == frame.frame.f_code.co_name:
            frame_of_patched_obj = frame
            to_capture = False
            break
        if to_capture:
            captured_frames.append(frame)
    tb_next = None
    for frame_info in reversed(captured_frames):
        tb = types.TracebackType(tb_next, frame_info.frame, frame_info.frame.f_lasti, frame_info.frame.f_lineno)
        tb_next = tb
    test_traceback = tb
    origin_method_being_patched = frame_of_patched_obj.frame.f_locals["orig_method"]
    stack = traceback.extract_stack()
    caller_frame = None
    for frame in reversed(stack):
        if origin_method_being_patched.__name__ in frame.line:
            caller_frame = frame
    caller_path = os.path.relpath(caller_frame.filename)
    caller_lineno = caller_frame.lineno
    test_lineno = line_number
    from _pytest._code.source import Source
    with open(actual_test_file) as fp:
        s = fp.read()
        source = Source(s)
        test_code_context = "\n".join(source.getstatement(test_lineno - 1).lines)
    with open(caller_path) as fp:
        s = fp.read()
        source = Source(s)
        caller_code_context = "\n".join(source.getstatement(caller_lineno - 1).lines)
    test_info = f"test:\n\n{full_test_name}\n\n{'-' * 80}\n\ntest context: {actual_test_file}:{test_lineno}\n\n{test_code_context}"
    test_info = f"{test_info}\n\n{'-' * 80}\n\ncaller context: {caller_path}:{caller_lineno}\n\n{caller_code_context}"
    return (
        full_test_name,
        test_file,
        test_lineno,
        test_obj,
        test_method,
        test_frame,
        test_traceback,
        test_code_context,
        caller_path,
        caller_lineno,
        caller_code_context,
        test_info,
    )
def _get_call_arguments(code_context):
    def get_argument_name(node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return ast.unparse(node)
        elif isinstance(node, ast.Constant):
            return repr(node.value)
        else:
            return ast.unparse(node)
    indent = len(code_context) - len(code_context.lstrip())
    code_context = code_context.replace(" " * indent, "")
    try:
        tree = ast.parse(code_context, mode="eval")
        assert isinstance(tree.body, ast.Call)
        call_node = tree.body
        if call_node:
            result = {
                "positional_args": [],
                "keyword_args": {},
                "starargs": None,
                "kwargs": None,
            }
            for arg in call_node.args:
                arg_name = get_argument_name(arg)
                result["positional_args"].append(arg_name)
            for keyword in call_node.keywords:
                if keyword.arg is None:
                    result["kwargs"] = get_argument_name(keyword.value)
                else:
                    arg_name = get_argument_name(keyword.value)
                    result["keyword_args"][keyword.arg] = arg_name
            return result
    except (SyntaxError, AttributeError) as e:
        print(f"Error parsing: {e}")
    return None
def _prepare_debugging_info(test_info, info):
    info = f"{test_info}\n\n{info}"
    p = os.path.join(os.environ.get("_PATCHED_TESTING_METHODS_OUTPUT_DIR", ""), "captured_info.txt")
    with open(p, "a") as fp:
        fp.write(f"{info}\n\n{'=' * 120}\n\n")
    return info
def _patched_tearDown(self, *args, **kwargs):
    regular_failures_info = []
    if hasattr(self, "_outcome") and self._outcome.errors:
        for error_entry in self._outcome.errors:
            test_instance, (exc_type, exc_obj, exc_tb) = error_entry
            regular_failures_info.append(
                {
                    "message": f"{str(exc_obj)}\n\n",
                    "type": exc_type.__name__,
                    "file": "test_modeling_vit.py",
                    "line": 237,
                }
            )
        self._outcome.errors.clear()
    orig_tearDown = _patched_tearDown.orig_tearDown
    type(self).tearDown = orig_tearDown
    orig_tearDown(self, *args, **kwargs)
    test_method = getattr(self, self._testMethodName)
    captured_failures = test_method.__func__.captured_failures[id(test_method)]
    captured_exceptions = captured_failures[0]["exception"]
    captured_traceback = captured_failures[0]["traceback"]
    capturued_info = [x["info"] for x in captured_failures]
    capturued_info_str = f"\n\n{'=' * 80}\n\n".join(capturued_info)
    if regular_failures_info:
        enhanced_exception = type(captured_exceptions)(enhanced_message)
        enhanced_exception.__cause__ = captured_exceptions.__cause__
        enhanced_exception.__context__ = captured_exceptions.__context__
        captured_exceptions = enhanced_exception
    del test_method.__func__.captured_failures
    raise captured_exceptions.with_traceback(captured_traceback)
def _patch_with_call_info(module_or_class, attr_name, _parse_call_info_func, target_args):
    orig_method = getattr(module_or_class, attr_name)
    if not callable(orig_method):
        return
    def patched(*args, **kwargs):
        if not os.environ.get("PYTEST_CURRENT_TEST", ""):
            return orig_method(*args, **kwargs)
        try:
            orig_method(*args, **kwargs)
        except AssertionError as e:
            captured_exception = e
            (
                full_test_name,
                test_file,
                test_lineno,
                test_obj,
                test_method,
                test_frame,
                test_traceback,
                test_code_context,
                caller_path,
                caller_lineno,
                caller_code_context,
                test_info,
            ) = _get_test_info()
            test_info = f"{test_info}\n\n{'-' * 80}\n\npatched method: {orig_method.__module__}.{orig_method.__name__}"
            call_argument_expressions = _get_call_arguments(caller_code_context)
            info = _parse_call_info_func(orig_method, args, kwargs, call_argument_expressions, target_args)
            info = _prepare_debugging_info(test_info, info)
            if os.getenv("CI") == "true":
                raise captured_exception.with_traceback(test_traceback)
            captured_failure = {
                "result": "failed",
                "exception": captured_exception,
                "traceback": test_traceback,
                "info": info,
            }
            if getattr(test_method.__func__, "captured_failures", None) is None:
                test_method.__func__.captured_failures = {}
            if id(test_method) not in test_method.__func__.captured_failures:
                test_method.__func__.captured_failures[id(test_method)] = []
            test_method.__func__.captured_failures[id(test_method)].append(captured_failure)
            if not hasattr(type(test_obj).tearDown, "orig_tearDown"):
                orig_tearDown = type(test_obj).tearDown
                _patched_tearDown.orig_tearDown = orig_tearDown
                type(test_obj).tearDown = _patched_tearDown
    setattr(module_or_class, attr_name, patched)
def _parse_call_info(func, args, kwargs, call_argument_expressions, target_args):
    signature = inspect.signature(func)
    signature_names = [param.name for param_name, param in signature.parameters.items()]
    if len(args) == len(call_argument_expressions["positional_args"]) + 1:
        call_argument_expressions["positional_args"] = ["self"] + call_argument_expressions["positional_args"]
    param_position_mapping = {param_name: idx for idx, param_name in enumerate(signature_names)}
    arg_info = {}
    for arg_name in target_args:
        if arg_name in kwargs:
            arg_value = kwargs[arg_name]
            arg_expr = call_argument_expressions["keyword_args"][arg_name]
        else:
            arg_pos = param_position_mapping[arg_name]
            arg_value = args[arg_pos]
            arg_expr = call_argument_expressions["positional_args"][arg_pos]
        arg_value_str = _format_py_obj(arg_value)
        arg_info[arg_name] = {"arg_expr": arg_expr, "arg_value_str": arg_value_str}
    info = ""
    for arg_name in arg_info:
        arg_expr, arg_value_str = arg_info[arg_name]["arg_expr"], arg_info[arg_name]["arg_value_str"]
        info += f"{'-' * 80}\n\nargument name: `{arg_name}`\nargument expression: `{arg_expr}`\n\nargument value:\n\n{arg_value_str}\n\n"
    info = info[:-2]
    return info
def patch_testing_methods_to_collect_info():
    p = os.path.join(os.environ.get("_PATCHED_TESTING_METHODS_OUTPUT_DIR", ""), "captured_info.txt")
    Path(p).unlink(missing_ok=True)
    if is_torch_available():
        import torch
        _patch_with_call_info(torch.testing, "assert_close", _parse_call_info, target_args=("actual", "expected"))
    _patch_with_call_info(unittest.case.TestCase, "assertEqual", _parse_call_info, target_args=("first", "second"))
    _patch_with_call_info(unittest.case.TestCase, "assertListEqual", _parse_call_info, target_args=("list1", "list2"))
    _patch_with_call_info(
        unittest.case.TestCase, "assertTupleEqual", _parse_call_info, target_args=("tuple1", "tuple2")
    )
    _patch_with_call_info(unittest.case.TestCase, "assertSetEqual", _parse_call_info, target_args=("set1", "set1"))
    _patch_with_call_info(unittest.case.TestCase, "assertDictEqual", _parse_call_info, target_args=("d1", "d2"))
    _patch_with_call_info(unittest.case.TestCase, "assertIn", _parse_call_info, target_args=("member", "container"))
    _patch_with_call_info(unittest.case.TestCase, "assertNotIn", _parse_call_info, target_args=("member", "container"))
    _patch_with_call_info(unittest.case.TestCase, "assertLess", _parse_call_info, target_args=("a", "b"))
    _patch_with_call_info(unittest.case.TestCase, "assertLessEqual", _parse_call_info, target_args=("a", "b"))
    _patch_with_call_info(unittest.case.TestCase, "assertGreater", _parse_call_info, target_args=("a", "b"))
    _patch_with_call_info(unittest.case.TestCase, "assertGreaterEqual", _parse_call_info, target_args=("a", "b"))
def torchrun(script: str, nproc_per_node: int, is_torchrun: bool = True, env: Optional[dict] = None):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
        tmp.write(script)
        tmp.flush()
        tmp.seek(0)
        if is_torchrun:
            cmd = (
                f"torchrun --nproc_per_node {nproc_per_node} --master_port {get_torch_dist_unique_port()} {tmp.name}"
            ).split()
        else:
            cmd = ["python3", tmp.name]
        try:
            _ = subprocess.run(cmd, capture_output=True, env=env, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"The following error was captured: {e.stderr}")
def _format_tensor(t, indent_level=0, sci_mode=None):
    if not isinstance(t, torch.Tensor):
        t = torch.tensor(t)
    is_scalar = False
    if t.ndim == 0:
        t = torch.tensor([t])
        is_scalar = True
    if t.ndim <= 1 or set(t.shape[0:-1]) == {1}:
        t = t.detach().to("cpu")
        t_str = str(t)
        t_str = t_str.replace("tensor(", "").replace(")", "")
        while "[ " in t_str:
            t_str = t_str.replace("[ ", "[")
        t_str = t_str.replace("\n", " ")
        while "  " in t_str:
            t_str = t_str.replace("  ", " ")
        if is_scalar:
            t_str = t_str[1:-1]
        t_str = " " * 4 * indent_level + t_str
        return t_str
    else:
        t_str = str(t)
        if sci_mode is None:
            sci_mode = "e+" in t_str or "e-" in t_str
        torch.set_printoptions(sci_mode=sci_mode)
        t_str = " " * 4 * indent_level + "[\n"
        t_str += ",\n".join(_format_tensor(x, indent_level=indent_level + 1, sci_mode=sci_mode) for x in t)
        t_str += ",\n" + " " * 4 * indent_level + "]"
        torch.set_printoptions(sci_mode=None)
    return t_str
def _quote_string(s):
    has_single_quote = "'" in s
    has_double_quote = '"' in s
    if has_single_quote and has_double_quote:
        s = s.replace('"', r"\"")
        return f'"{s}"'
    elif has_single_quote:
        return f'"{s}"'
    elif has_double_quote:
        return f"'{s}'"
    else:
        return f'"{s}"'
def _format_py_obj(obj, indent=0, mode="", cache=None, prefix=""):
    if cache is None:
        cache = {}
    else:
        if (id(obj), indent, mode, prefix) in cache:
            return cache[(id(obj), indent, mode, prefix)]
    if str(obj.__class__) == "<class 'torch.Tensor'>":
        return _format_tensor(obj)
    elif obj.__class__.__name__ == "str":
        quoted_string = _quote_string(obj)
        quoted_string = quoted_string.replace("\n", r"\n")
        output = quoted_string
    elif obj.__class__.__name__ in ["int", "float"]:
        output = str(obj)
    elif obj.__class__.__name__ in ["list", "tuple", "dict"]:
        parenthesis = {
            "list": "[]",
            "tuple": "()",
            "dict": "{}",
        }
        p1, p2 = parenthesis[obj.__class__.__name__]
        elements_without_indent = []
        if isinstance(obj, dict):
            for idx, (k, v) in enumerate(obj.items()):
                last_element = idx == len(obj) - 1
                ok = _format_py_obj(k, indent=indent + 1, mode="one-line", cache=cache)
                ov = _format_py_obj(
                    v,
                    indent=indent + 1,
                    mode=mode,
                    cache=cache,
                    prefix=ok.lstrip() + ": " + "," if not last_element else "",
                )
                elements_without_indent.append(f"{ok.lstrip()}: {ov.lstrip()}")
        else:
            for idx, x in enumerate(obj):
                last_element = idx == len(obj) - 1
                o = _format_py_obj(
                    x, indent=indent + 1, mode=mode, cache=cache, prefix="," if not last_element else ""
                )
                elements_without_indent.append(o.lstrip())
        groups = []
        buf = []
        for idx, x in enumerate(elements_without_indent):
            buf.append(x)
            x_expanded = "\n" in buf[-1]
            not_last_element = idx != len(elements_without_indent) - 1
            should_finalize_x = x_expanded or len(f"{' ' * (4 * (indent + 1))}") + len(
                ", ".join(buf[-1:])
            ) > 120 - int(not_last_element)
            should_finalize_buf = x_expanded
            if not should_finalize_buf:
                buf_not_fit_into_one_line = len(f"{' ' * (4 * (indent + 1))}") + len(", ".join(buf)) > 120 - int(
                    not_last_element
                )
                should_finalize_buf = buf_not_fit_into_one_line
            if (type(obj[idx]) if type(obj) is not dict else type(list(obj.values())[idx])) in [list, tuple, dict]:
                should_finalize_x = True
                should_finalize_buf = True
            prev_type = None
            current_type = type(obj[idx]) if type(obj) is not dict else type(list(obj.values())[idx])
            if len(buf) > 1:
                prev_type = type(obj[idx - 1]) if type(obj) is not dict else type(list(obj.values())[idx - 1])
                type_changed = current_type != prev_type
                if type_changed:
                    should_finalize_buf = True
            if prev_type is None or (prev_type is str and current_type is str):
                should_finalize_buf = False
            if current_type is str:
                should_finalize_x = False
                if prev_type in [None, str]:
                    should_finalize_buf = False
            if should_finalize_buf:
                orig_buf_len = len(buf)
                if orig_buf_len > 1:
                    not_fit_into_one_line = None
                    if prev_type is str:
                        not_fit_into_one_line = len(f"{' ' * (4 * (indent + 1))}") + len(", ".join(buf[:-1])) > 120 - 1
                    if not_fit_into_one_line:
                        for x in buf[:-1]:
                            groups.append([x])
                    else:
                        groups.append(buf[:-1])
                    buf = buf[-1:]
                if should_finalize_x:
                    groups.append(buf)
                    buf = []
        if len(buf) > 0:
            not_fit_into_one_line = None
            if current_type is str:
                not_fit_into_one_line = len(f"{' ' * (4 * (indent + 1))}") + len(", ".join(buf)) > 120
            if not_fit_into_one_line:
                for x in buf:
                    groups.append([x])
            else:
                groups.append(buf)
        output = f"{' ' * 4 * indent}{p1}\n"
        element_strings = [f"{' ' * (4 * (indent + 1))}" + ", ".join(buf) for buf in groups]
        output += ",\n".join(element_strings)
        output += f"\n{' ' * 4 * indent}{p2}"
        no_new_line_in_elements = all("\n" not in x for x in element_strings)
        could_use_one_line = no_new_line_in_elements
        if could_use_one_line:
            one_line_form = ", ".join([x.lstrip() for x in element_strings])
            one_line_form = f"{p1}{one_line_form}{p2}"
            if mode == "one-line":
                return output
            could_use_one_line = len(f"{' ' * 4 * indent}") + len(prefix) + len(one_line_form) <= 120
            def use_one_line_repr(obj):
                if type(obj) in (list, tuple, dict):
                    element_types = []
                    if type(obj) is dict:
                        element_types.extend(type(x) for x in obj.values())
                    elif type(obj) in [list, tuple]:
                        element_types.extend(type(x) for x in obj)
                    if any(x in (list, tuple, dict) for x in element_types):
                        if len(obj) > 1:
                            return False
                        if type(obj) is not type(obj[0]):
                            return False
                        return no_new_line_in_elements
                    if len(set(element_types)) > 1:
                        return False
                    if element_types[0] in [int, float]:
                        return no_new_line_in_elements
                    elif element_types[0] is str:
                        if len(obj) == 1:
                            return no_new_line_in_elements
                        else:
                            return could_use_one_line
                return True
            if use_one_line_repr(obj):
                output = f"{' ' * 4 * indent}{one_line_form}"
    cache[(id(obj), indent, mode, prefix)] = output
    return output