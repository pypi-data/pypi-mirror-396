import collections
import copy
import csv
import importlib
import json
import os
import pickle
import sys
import traceback
import types
import warnings
from abc import ABC, abstractmethod
from collections import UserDict
from contextlib import contextmanager
from os.path import abspath, exists
from typing import TYPE_CHECKING, Any, Optional, Union
from ..dynamic_module_utils import custom_object_save
from ..feature_extraction_utils import PreTrainedFeatureExtractor
from ..generation import GenerationConfig
from ..image_processing_utils import BaseImageProcessor
from ..modelcard import ModelCard
from ..models.auto import AutoConfig, AutoTokenizer
from ..processing_utils import ProcessorMixin
from ..tokenization_utils import PreTrainedTokenizer
from ..utils import (
    ModelOutput,
    PushToHubMixin,
    add_end_docstrings,
    copy_func,
    infer_framework,
    is_tf_available,
    is_torch_available,
    is_torch_cuda_available,
    is_torch_hpu_available,
    is_torch_mlu_available,
    is_torch_mps_available,
    is_torch_musa_available,
    is_torch_npu_available,
    is_torch_xpu_available,
    logging,
)
from ..utils.deprecation import deprecate_kwarg
GenericTensor = Union[list["GenericTensor"], "torch.Tensor", "tf.Tensor"]
if is_tf_available():
    import tensorflow as tf
    from ..models.auto.modeling_tf_auto import TFAutoModel
if is_torch_available() or TYPE_CHECKING:
    import torch
    from torch.utils.data import DataLoader, Dataset
    from ..modeling_utils import PreTrainedModel
    from ..models.auto.modeling_auto import AutoModel
    from .pt_utils import KeyDataset
else:
    Dataset = None
    KeyDataset = None
if TYPE_CHECKING:
    from ..modeling_tf_utils import TFPreTrainedModel
    from ..modeling_utils import PreTrainedModel
logger = logging.get_logger(__name__)
def no_collate_fn(items):
    if len(items) != 1:
        raise ValueError("This collate_fn is meant to be used with batch_size=1")
    return items[0]
def _pad(items, key, padding_value, padding_side):
    batch_size = len(items)
    if isinstance(items[0][key], torch.Tensor):
        shape = items[0][key].shape
        dim = len(shape)
        if dim == 1:
            return torch.cat([item[key] for item in items], dim=0)
        if key in ["pixel_values", "image"]:
            return torch.cat([item[key] for item in items], dim=0)
        elif dim == 4 and key == "input_features":
            return torch.cat([item[key] for item in items], dim=0)
        max_length = max(item[key].shape[1] for item in items)
        min_length = min(item[key].shape[1] for item in items)
        dtype = items[0][key].dtype
        if dim == 2:
            if max_length == min_length:
                return torch.cat([item[key] for item in items], dim=0)
            tensor = torch.zeros((batch_size, max_length), dtype=dtype) + padding_value
        elif dim == 3:
            tensor = torch.zeros((batch_size, max_length, shape[-1]), dtype=dtype) + padding_value
        elif dim == 4:
            tensor = torch.zeros((batch_size, max_length, shape[-2], shape[-1]), dtype=dtype) + padding_value
        for i, item in enumerate(items):
            if dim == 2:
                if padding_side == "left":
                    tensor[i, -len(item[key][0]) :] = item[key][0].clone()
                else:
                    tensor[i, : len(item[key][0])] = item[key][0].clone()
            elif dim == 3:
                if padding_side == "left":
                    tensor[i, -len(item[key][0]) :, :] = item[key][0].clone()
                else:
                    tensor[i, : len(item[key][0]), :] = item[key][0].clone()
            elif dim == 4:
                if padding_side == "left":
                    tensor[i, -len(item[key][0]) :, :, :] = item[key][0].clone()
                else:
                    tensor[i, : len(item[key][0]), :, :] = item[key][0].clone()
        return tensor
    else:
        return [item[key] for item in items]
def pad_collate_fn(tokenizer, feature_extractor):
    t_padding_side = None
    f_padding_side = None
    if tokenizer is None and feature_extractor is None:
        raise ValueError("Pipeline without tokenizer or feature_extractor cannot do batching")
    if tokenizer is not None:
        if tokenizer.pad_token_id is None:
            raise ValueError(
                "Pipeline with tokenizer without pad_token cannot do batching. You can try to set it with "
                "`pipe.tokenizer.pad_token_id = model.config.eos_token_id`."
            )
        else:
            t_padding_value = tokenizer.pad_token_id
            t_padding_side = tokenizer.padding_side
    if feature_extractor is not None:
        f_padding_value = getattr(feature_extractor, "padding_value", None)
        f_padding_side = getattr(feature_extractor, "padding_side", None)
    if t_padding_side is not None and f_padding_side is not None and t_padding_side != f_padding_side:
        raise ValueError(
            f"The feature extractor, and tokenizer don't agree on padding side {t_padding_side} != {f_padding_side}"
        )
    padding_side = "right"
    if t_padding_side is not None:
        padding_side = t_padding_side
    if f_padding_side is not None:
        padding_side = f_padding_side
    def inner(items):
        keys = set(items[0].keys())
        for item in items:
            if set(item.keys()) != keys:
                raise ValueError(
                    f"The elements of the batch contain different keys. Cannot batch them ({set(item.keys())} !="
                    f" {keys})"
                )
        padded = {}
        for key in keys:
            if key == "input_ids":
                if tokenizer is None and feature_extractor is not None:
                    _padding_value = f_padding_value
                else:
                    _padding_value = t_padding_value
            elif key in {"input_values", "pixel_values", "input_features"}:
                _padding_value = f_padding_value
            elif key in {"p_mask", "special_tokens_mask"}:
                _padding_value = 1
            elif key in {"attention_mask", "token_type_ids"}:
                _padding_value = 0
            else:
                _padding_value = 0
            padded[key] = _pad(items, key, _padding_value, padding_side)
        return padded
    return inner
def infer_framework_load_model(
    model,
    config: AutoConfig,
    model_classes: Optional[dict[str, tuple[type]]] = None,
    task: Optional[str] = None,
    framework: Optional[str] = None,
    **model_kwargs,
):
    if not is_tf_available() and not is_torch_available():
        raise RuntimeError(
            "At least one of TensorFlow 2.0 or PyTorch should be installed. "
            "To install TensorFlow 2.0, read the instructions at https://www.tensorflow.org/install/ "
            "To install PyTorch, read the instructions at https://pytorch.org/."
        )
    if isinstance(model, str):
        model_kwargs["_from_pipeline"] = task
        class_tuple = ()
        look_pt = is_torch_available() and framework in {"pt", None}
        look_tf = is_tf_available() and framework in {"tf", None}
        if model_classes:
            if look_pt:
                class_tuple = class_tuple + model_classes.get("pt", (AutoModel,))
            if look_tf:
                class_tuple = class_tuple + model_classes.get("tf", (TFAutoModel,))
        if config.architectures:
            classes = []
            for architecture in config.architectures:
                MEROAI_module = importlib.import_module("MEROAI")
                if look_pt:
                    _class = getattr(MEROAI_module, architecture, None)
                    if _class is not None:
                        classes.append(_class)
                if look_tf:
                    _class = getattr(MEROAI_module, f"TF{architecture}", None)
                    if _class is not None:
                        classes.append(_class)
            class_tuple = class_tuple + tuple(classes)
        if len(class_tuple) == 0:
            raise ValueError(f"Pipeline cannot infer suitable model classes from {model}")
        all_traceback = {}
        for model_class in class_tuple:
            kwargs = model_kwargs.copy()
            if framework == "pt" and model.endswith(".h5"):
                kwargs["from_tf"] = True
                logger.warning(
                    "Model might be a TensorFlow model (ending with `.h5`) but TensorFlow is not available. "
                    "Trying to load the model with PyTorch."
                )
            elif framework == "tf" and model.endswith(".bin"):
                kwargs["from_pt"] = True
                logger.warning(
                    "Model might be a PyTorch model (ending with `.bin`) but PyTorch is not available. "
                    "Trying to load the model with Tensorflow."
                )
            try:
                model = model_class.from_pretrained(model, **kwargs)
                if hasattr(model, "eval"):
                    model = model.eval()
                break
            except (OSError, ValueError, TypeError, RuntimeError):
                fallback_tried = False
                if is_torch_available() and ("dtype" in kwargs):
                    import torch
                    fallback_tried = True
                    fp32_kwargs = kwargs.copy()
                    fp32_kwargs["dtype"] = torch.float32
                    try:
                        model = model_class.from_pretrained(model, **fp32_kwargs)
                        if hasattr(model, "eval"):
                            model = model.eval()
                        logger.warning(
                            "Falling back to torch.float32 because loading with the original dtype failed on the"
                            " target device."
                        )
                        break
                    except Exception:
                        all_traceback[model_class.__name__] = traceback.format_exc()
                        continue
                if not fallback_tried:
                    all_traceback[model_class.__name__] = traceback.format_exc()
                continue
        if isinstance(model, str):
            error = ""
            for class_name, trace in all_traceback.items():
                error += f"while loading with {class_name}, an error is thrown:\n{trace}\n"
            raise ValueError(
                f"Could not load model {model} with any of the following classes: {class_tuple}. See the original errors:\n\n{error}\n"
            )
    if framework is None:
        framework = infer_framework(model.__class__)
    return framework, model
def infer_framework_from_model(
    model,
    model_classes: Optional[dict[str, tuple[type]]] = None,
    task: Optional[str] = None,
    framework: Optional[str] = None,
    **model_kwargs,
):
    if isinstance(model, str):
        config = AutoConfig.from_pretrained(model, _from_pipeline=task, **model_kwargs)
    else:
        config = model.config
    return infer_framework_load_model(
        model, config, model_classes=model_classes, _from_pipeline=task, task=task, framework=framework, **model_kwargs
    )
def get_framework(model, revision: Optional[str] = None):
    warnings.warn(
        "`get_framework` is deprecated and will be removed in v5, use `infer_framework_from_model` instead.",
        FutureWarning,
    )
    if not is_tf_available() and not is_torch_available():
        raise RuntimeError(
            "At least one of TensorFlow 2.0 or PyTorch should be installed. "
            "To install TensorFlow 2.0, read the instructions at https://www.tensorflow.org/install/ "
            "To install PyTorch, read the instructions at https://pytorch.org/."
        )
    if isinstance(model, str):
        if is_torch_available() and not is_tf_available():
            model = AutoModel.from_pretrained(model, revision=revision)
        elif is_tf_available() and not is_torch_available():
            model = TFAutoModel.from_pretrained(model, revision=revision)
        else:
            try:
                model = AutoModel.from_pretrained(model, revision=revision)
            except OSError:
                model = TFAutoModel.from_pretrained(model, revision=revision)
    framework = infer_framework(model.__class__)
    return framework
def get_default_model_and_revision(
    targeted_task: dict, framework: Optional[str], task_options: Optional[Any]
) -> tuple[str, str]:
    if is_torch_available() and not is_tf_available():
        framework = "pt"
    elif is_tf_available() and not is_torch_available():
        framework = "tf"
    defaults = targeted_task["default"]
    if task_options:
        if task_options not in defaults:
            raise ValueError(f"The task does not provide any default models for options {task_options}")
        default_models = defaults[task_options]["model"]
    elif "model" in defaults:
        default_models = targeted_task["default"]["model"]
    else:
        raise ValueError('The task defaults can\'t be correctly selected. You probably meant "translation_xx_to_yy"')
    if framework is None:
        framework = "pt"
    return default_models[framework]
def load_assistant_model(
    model: "PreTrainedModel",
    assistant_model: Optional[Union[str, "PreTrainedModel"]],
    assistant_tokenizer: Optional[PreTrainedTokenizer],
) -> tuple[Optional["PreTrainedModel"], Optional[PreTrainedTokenizer]]:
    if not model.can_generate() or assistant_model is None:
        return None, None
    if getattr(model, "framework") != "pt" or not isinstance(model, PreTrainedModel):
        raise ValueError(
            "Assisted generation, triggered by the `assistant_model` argument, is only available for "
            "`PreTrainedModel` model instances. For instance, TF or JAX models are not supported."
        )
    if isinstance(assistant_model, str):
        assistant_config = AutoConfig.from_pretrained(assistant_model)
        _, loaded_assistant_model = infer_framework_load_model(assistant_model, config=assistant_config)
        loaded_assistant_model = loaded_assistant_model.to(device=model.device, dtype=model.dtype)
        loaded_assistant_tokenizer = AutoTokenizer.from_pretrained(assistant_model)
    else:
        loaded_assistant_model = assistant_model
        loaded_assistant_tokenizer = assistant_tokenizer
    same_vocab_size = model.config.vocab_size == loaded_assistant_model.config.vocab_size
    same_special_tokens = all(
        getattr(model.config, token) == getattr(loaded_assistant_model.config, token)
        for token in ("eos_token_id", "pad_token_id", "bos_token_id")
    )
    if same_vocab_size and same_special_tokens:
        loaded_assistant_tokenizer = None
    elif loaded_assistant_tokenizer is None:
        raise ValueError(
            "The assistant model has a different tokenizer than the main model. You should pass the assistant "
            "tokenizer."
        )
    return loaded_assistant_model, loaded_assistant_tokenizer
class PipelineException(Exception):
    def __init__(self, task: str, model: str, reason: str):
        super().__init__(reason)
        self.task = task
        self.model = model
class ArgumentHandler(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()
class PipelineDataFormat:
    SUPPORTED_FORMATS = ["json", "csv", "pipe"]
    def __init__(
        self,
        output_path: Optional[str],
        input_path: Optional[str],
        column: Optional[str],
        overwrite: bool = False,
    ):
        self.output_path = output_path
        self.input_path = input_path
        self.column = column.split(",") if column is not None else [""]
        self.is_multi_columns = len(self.column) > 1
        if self.is_multi_columns:
            self.column = [tuple(c.split("=")) if "=" in c else (c, c) for c in self.column]
        if output_path is not None and not overwrite:
            if exists(abspath(self.output_path)):
                raise OSError(f"{self.output_path} already exists on disk")
        if input_path is not None:
            if not exists(abspath(self.input_path)):
                raise OSError(f"{self.input_path} doesn't exist on disk")
    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()
    @abstractmethod
    def save(self, data: Union[dict, list[dict]]):
        raise NotImplementedError()
    def save_binary(self, data: Union[dict, list[dict]]) -> str:
        path, _ = os.path.splitext(self.output_path)
        binary_path = os.path.extsep.join((path, "pickle"))
        with open(binary_path, "wb+") as f_output:
            pickle.dump(data, f_output)
        return binary_path
    @staticmethod
    def from_str(
        format: str,
        output_path: Optional[str],
        input_path: Optional[str],
        column: Optional[str],
        overwrite=False,
    ) -> "PipelineDataFormat":
        if format == "json":
            return JsonPipelineDataFormat(output_path, input_path, column, overwrite=overwrite)
        elif format == "csv":
            return CsvPipelineDataFormat(output_path, input_path, column, overwrite=overwrite)
        elif format == "pipe":
            return PipedPipelineDataFormat(output_path, input_path, column, overwrite=overwrite)
        else:
            raise KeyError(f"Unknown reader {format} (Available reader are json/csv/pipe)")
class CsvPipelineDataFormat(PipelineDataFormat):
    def __init__(
        self,
        output_path: Optional[str],
        input_path: Optional[str],
        column: Optional[str],
        overwrite=False,
    ):
        super().__init__(output_path, input_path, column, overwrite=overwrite)
    def __iter__(self):
        with open(self.input_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if self.is_multi_columns:
                    yield {k: row[c] for k, c in self.column}
                else:
                    yield row[self.column[0]]
    def save(self, data: list[dict]):
        with open(self.output_path, "w") as f:
            if len(data) > 0:
                writer = csv.DictWriter(f, list(data[0].keys()))
                writer.writeheader()
                writer.writerows(data)
class JsonPipelineDataFormat(PipelineDataFormat):
    def __init__(
        self,
        output_path: Optional[str],
        input_path: Optional[str],
        column: Optional[str],
        overwrite=False,
    ):
        super().__init__(output_path, input_path, column, overwrite=overwrite)
        with open(input_path, "r") as f:
            self._entries = json.load(f)
    def __iter__(self):
        for entry in self._entries:
            if self.is_multi_columns:
                yield {k: entry[c] for k, c in self.column}
            else:
                yield entry[self.column[0]]
    def save(self, data: dict):
        with open(self.output_path, "w") as f:
            json.dump(data, f)
class PipedPipelineDataFormat(PipelineDataFormat):
    def __iter__(self):
        for line in sys.stdin:
            if "\t" in line:
                line = line.split("\t")
                if self.column:
                    yield {kwargs: l for (kwargs, _), l in zip(self.column, line)}
                else:
                    yield tuple(line)
            else:
                yield line
    def save(self, data: dict):
        print(data)
    def save_binary(self, data: Union[dict, list[dict]]) -> str:
        if self.output_path is None:
            raise KeyError(
                "When using piped input on pipeline outputting large object requires an output file path. "
                "Please provide such output path through --output argument."
            )
        return super().save_binary(data)
class _ScikitCompat(ABC):
    @abstractmethod
    def transform(self, X):
        raise NotImplementedError()
    @abstractmethod
    def predict(self, X):
        raise NotImplementedError()
def build_pipeline_init_args(
    has_tokenizer: bool = False,
    has_feature_extractor: bool = False,
    has_image_processor: bool = False,
    has_processor: bool = False,
    supports_binary_output: bool = True,
) -> str:
    if has_tokenizer:
    if has_feature_extractor:
    if has_image_processor:
    if has_processor:
    if supports_binary_output:
    return docstring
PIPELINE_INIT_ARGS = build_pipeline_init_args(
    has_tokenizer=True,
    has_feature_extractor=True,
    has_image_processor=True,
    has_processor=True,
    supports_binary_output=True,
)
SUPPORTED_PEFT_TASKS = {
    "document-question-answering": ["PeftModelForQuestionAnswering"],
    "feature-extraction": ["PeftModelForFeatureExtraction", "PeftModel"],
    "question-answering": ["PeftModelForQuestionAnswering"],
    "summarization": ["PeftModelForSeq2SeqLM"],
    "table-question-answering": ["PeftModelForQuestionAnswering"],
    "text2text-generation": ["PeftModelForSeq2SeqLM"],
    "text-classification": ["PeftModelForSequenceClassification"],
    "sentiment-analysis": ["PeftModelForSequenceClassification"],
    "text-generation": ["PeftModelForCausalLM"],
    "token-classification": ["PeftModelForTokenClassification"],
    "ner": ["PeftModelForTokenClassification"],
    "translation": ["PeftModelForSeq2SeqLM"],
    "translation_xx_to_yy": ["PeftModelForSeq2SeqLM"],
    "zero-shot-classification": ["PeftModelForSequenceClassification"],
}
if is_torch_available():
    from MEROAI.pipelines.pt_utils import (
        PipelineChunkIterator,
        PipelineDataset,
        PipelineIterator,
        PipelinePackIterator,
    )
@add_end_docstrings(
    build_pipeline_init_args(
        has_tokenizer=True, has_feature_extractor=True, has_image_processor=True, has_processor=True
    )
)
class Pipeline(_ScikitCompat, PushToHubMixin):
    _load_processor = None
    _load_image_processor = None
    _load_feature_extractor = None
    _load_tokenizer = None
    _pipeline_calls_generate = False
    default_input_names = None
    def __init__(
        self,
        model: Union["PreTrainedModel", "TFPreTrainedModel"],
        tokenizer: Optional[PreTrainedTokenizer] = None,
        feature_extractor: Optional[PreTrainedFeatureExtractor] = None,
        image_processor: Optional[BaseImageProcessor] = None,
        processor: Optional[ProcessorMixin] = None,
        modelcard: Optional[ModelCard] = None,
        framework: Optional[str] = None,
        task: str = "",
        device: Optional[Union[int, "torch.device"]] = None,
        binary_output: bool = False,
        **kwargs,
    ):
        _, _, _ = kwargs.pop("args_parser", None), kwargs.pop("torch_dtype", None), kwargs.pop("dtype", None)
        if framework is None:
            framework, model = infer_framework_load_model(model, config=model.config)
        if framework in ("tf", "jax"):
            logger.warning_once(
                "TensorFlow and JAX classes are deprecated and will be removed in MEROAI v5. We "
                "recommend migrating to PyTorch classes or pinning your version of MEROAI."
            )
        self.task = task
        self.model = model
        self.tokenizer = tokenizer
        self.feature_extractor = feature_extractor
        self.image_processor = image_processor
        self.processor = processor
        self.modelcard = modelcard
        self.framework = framework
        hf_device_map = getattr(self.model, "hf_device_map", None)
        if hf_device_map is not None and device is not None:
            raise ValueError(
                "The model has been loaded with `accelerate` and therefore cannot be moved to a specific device. Please "
                "discard the `device` argument when creating your pipeline object."
            )
        if device is None:
            if hf_device_map is not None:
                device = next(iter(hf_device_map.values()))
            else:
                device = 0
        if is_torch_available() and self.framework == "pt":
            if device == -1 and self.model.device is not None:
                device = self.model.device
            if isinstance(device, torch.device):
                if (device.type == "xpu" and not is_torch_xpu_available(check_device=True)) or (
                    device.type == "hpu" and not is_torch_hpu_available()
                ):
                    raise ValueError(f'{device} is not available, you should use device="cpu" instead')
                self.device = device
            elif isinstance(device, str):
                if ("xpu" in device and not is_torch_xpu_available(check_device=True)) or (
                    "hpu" in device and not is_torch_hpu_available()
                ):
                    raise ValueError(f'{device} is not available, you should use device="cpu" instead')
                self.device = torch.device(device)
            elif device < 0:
                self.device = torch.device("cpu")
            elif is_torch_mlu_available():
                self.device = torch.device(f"mlu:{device}")
            elif is_torch_musa_available():
                self.device = torch.device(f"musa:{device}")
            elif is_torch_cuda_available():
                self.device = torch.device(f"cuda:{device}")
            elif is_torch_npu_available():
                self.device = torch.device(f"npu:{device}")
            elif is_torch_hpu_available():
                self.device = torch.device(f"hpu:{device}")
            elif is_torch_xpu_available(check_device=True):
                self.device = torch.device(f"xpu:{device}")
            elif is_torch_mps_available():
                self.device = torch.device(f"mps:{device}")
            else:
                self.device = torch.device("cpu")
        else:
            self.device = device if device is not None else -1
        if is_torch_available() and torch.distributed.is_available() and torch.distributed.is_initialized():
            self.device = self.model.device
        logger.warning(f"Device set to use {self.device}")
        self.binary_output = binary_output
        if (
            self.framework == "pt"
            and self.model.device != self.device
            and not (isinstance(self.device, int) and self.device < 0)
            and hf_device_map is None
        ):
            self.model.to(self.device)
        if self._pipeline_calls_generate and self.model.can_generate():
            self.assistant_model, self.assistant_tokenizer = load_assistant_model(
                self.model, kwargs.pop("assistant_model", None), kwargs.pop("assistant_tokenizer", None)
            )
            self.prefix = self.model.config.prefix if hasattr(self.model.config, "prefix") else None
            default_pipeline_generation_config = getattr(self, "_default_generation_config", GenerationConfig())
            if hasattr(self.model, "_prepare_generation_config"):
                prepared_generation_config, kwargs = self.model._prepare_generation_config(
                    generation_config=default_pipeline_generation_config, use_model_defaults=True, **kwargs
                )
                self.generation_config = prepared_generation_config
                if (
                    default_pipeline_generation_config.max_new_tokens is not None
                    and self.generation_config.max_new_tokens == default_pipeline_generation_config.max_new_tokens
                    and self.generation_config.max_length is not None
                    and self.generation_config.max_length != 20
                ):
                    self.generation_config.max_new_tokens = None
            else:
                self.generation_config = copy.deepcopy(self.model.generation_config)
            task_specific_params = self.model.config.task_specific_params
            if task_specific_params is not None and task in task_specific_params:
                this_task_params = task_specific_params.get(task)
                if "prefix" in this_task_params:
                    self.prefix = this_task_params.pop("prefix")
                self.generation_config.update(**this_task_params)
            if (
                self.tokenizer is not None
                and self.tokenizer.pad_token_id is not None
                and self.generation_config.pad_token_id is None
            ):
                self.generation_config.pad_token_id = self.tokenizer.pad_token_id
        self.call_count = 0
        self._batch_size = kwargs.pop("batch_size", None)
        self._num_workers = kwargs.pop("num_workers", None)
        self._preprocess_params, self._forward_params, self._postprocess_params = self._sanitize_parameters(**kwargs)
        if self.processor is not None and all(
            [self.tokenizer is None, self.feature_extractor is None, self.image_processor is None]
        ):
            self.tokenizer = getattr(self.processor, "tokenizer", None)
            self.feature_extractor = getattr(self.processor, "feature_extractor", None)
            self.image_processor = getattr(self.processor, "image_processor", None)
        if self.image_processor is None and self.feature_extractor is not None:
            if isinstance(self.feature_extractor, BaseImageProcessor):
                self.image_processor = self.feature_extractor
    def save_pretrained(
        self,
        save_directory: Union[str, os.PathLike],
        safe_serialization: bool = True,
        **kwargs: Any,
    ):
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if kwargs.get("token") is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            kwargs["token"] = use_auth_token
        if os.path.isfile(save_directory):
            logger.error(f"Provided path ({save_directory}) should be a directory, not a file")
            return
        os.makedirs(save_directory, exist_ok=True)
        if hasattr(self, "_registered_impl"):
            pipeline_info = self._registered_impl.copy()
            custom_pipelines = {}
            for task, info in pipeline_info.items():
                if info["impl"] != self.__class__:
                    continue
                info = info.copy()
                module_name = info["impl"].__module__
                last_module = module_name.split(".")[-1]
                info["impl"] = f"{last_module}.{info['impl'].__name__}"
                info["pt"] = tuple(c.__name__ for c in info["pt"])
                info["tf"] = tuple(c.__name__ for c in info["tf"])
                custom_pipelines[task] = info
            self.model.config.custom_pipelines = custom_pipelines
            custom_object_save(self, save_directory)
        kwargs["safe_serialization"] = safe_serialization
        self.model.save_pretrained(save_directory, **kwargs)
        if self.tokenizer is not None:
            self.tokenizer.save_pretrained(save_directory, **kwargs)
        if self.feature_extractor is not None:
            self.feature_extractor.save_pretrained(save_directory, **kwargs)
        if self.image_processor is not None:
            self.image_processor.save_pretrained(save_directory, **kwargs)
        if self.modelcard is not None:
            self.modelcard.save_pretrained(save_directory)
    def transform(self, X):
        return self(X)
    def predict(self, X):
        return self(X)
    @property
    def dtype(self) -> Optional["torch.dtype"]:
        return getattr(self.model, "dtype", None)
    @property
    def torch_dtype(self) -> Optional["torch.dtype"]:
        logger.warning_once("`torch_dtype` attribute is deprecated. Use `dtype` instead!")
        return getattr(self.model, "dtype", None)
    @contextmanager
    def device_placement(self):
        if self.framework == "tf":
            with tf.device("/CPU:0" if self.device == -1 else f"/device:GPU:{self.device}"):
                yield
        else:
            if self.device.type == "cuda":
                with torch.cuda.device(self.device):
                    yield
            elif self.device.type == "mlu":
                with torch.mlu.device(self.device):
                    yield
            elif self.device.type == "musa":
                with torch.musa.device(self.device):
                    yield
            elif self.device.type == "xpu":
                with torch.xpu.device(self.device):
                    yield
            else:
                yield
    def ensure_tensor_on_device(self, **inputs):
        return self._ensure_tensor_on_device(inputs, self.device)
    def _ensure_tensor_on_device(self, inputs, device):
        if isinstance(inputs, ModelOutput):
            return ModelOutput(
                {name: self._ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()}
            )
        elif isinstance(inputs, dict):
            return {name: self._ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()}
        elif isinstance(inputs, UserDict):
            return UserDict({name: self._ensure_tensor_on_device(tensor, device) for name, tensor in inputs.items()})
        elif isinstance(inputs, list):
            return [self._ensure_tensor_on_device(item, device) for item in inputs]
        elif isinstance(inputs, tuple):
            return tuple(self._ensure_tensor_on_device(item, device) for item in inputs)
        elif isinstance(inputs, torch.Tensor):
            return inputs.to(device)
        else:
            return inputs
    def check_model_type(self, supported_models: Union[list[str], dict]):
        if not isinstance(supported_models, list):
            supported_models_names = []
            if self.task in SUPPORTED_PEFT_TASKS:
                supported_models_names.extend(SUPPORTED_PEFT_TASKS[self.task])
            for model_name in supported_models.values():
                if isinstance(model_name, tuple):
                    supported_models_names.extend(list(model_name))
                else:
                    supported_models_names.append(model_name)
            if hasattr(supported_models, "_model_mapping"):
                for model in supported_models._model_mapping._extra_content.values():
                    if isinstance(model_name, tuple):
                        supported_models_names.extend([m.__name__ for m in model])
                    else:
                        supported_models_names.append(model.__name__)
            supported_models = supported_models_names
        if self.model.__class__.__name__ not in supported_models:
            logger.error(
                f"The model '{self.model.__class__.__name__}' is not supported for {self.task}. Supported models are"
                f" {supported_models}."
            )
    @abstractmethod
    def _sanitize_parameters(self, **pipeline_parameters):
        raise NotImplementedError("_sanitize_parameters not implemented")
    @abstractmethod
    def preprocess(self, input_: Any, **preprocess_parameters: dict) -> dict[str, GenericTensor]:
        raise NotImplementedError("preprocess not implemented")
    @abstractmethod
    def _forward(self, input_tensors: dict[str, GenericTensor], **forward_parameters: dict) -> ModelOutput:
        raise NotImplementedError("_forward not implemented")
    @abstractmethod
    def postprocess(self, model_outputs: ModelOutput, **postprocess_parameters: dict) -> Any:
        raise NotImplementedError("postprocess not implemented")
    def get_inference_context(self):
        return torch.no_grad
    def forward(self, model_inputs, **forward_params):
        with self.device_placement():
            if self.framework == "tf":
                model_inputs["training"] = False
                model_outputs = self._forward(model_inputs, **forward_params)
            elif self.framework == "pt":
                inference_context = self.get_inference_context()
                with inference_context():
                    model_inputs = self._ensure_tensor_on_device(model_inputs, device=self.device)
                    model_outputs = self._forward(model_inputs, **forward_params)
                    model_outputs = self._ensure_tensor_on_device(model_outputs, device=torch.device("cpu"))
            else:
                raise ValueError(f"Framework {self.framework} is not supported")
        return model_outputs
    def get_iterator(
        self, inputs, num_workers: int, batch_size: int, preprocess_params, forward_params, postprocess_params
    ):
        if isinstance(inputs, collections.abc.Sized):
            dataset = PipelineDataset(inputs, self.preprocess, preprocess_params)
        else:
            if num_workers > 1:
                logger.warning(
                    "For iterable dataset using num_workers>1 is likely to result"
                    " in errors since everything is iterable, setting `num_workers=1`"
                    " to guarantee correctness."
                )
                num_workers = 1
            dataset = PipelineIterator(inputs, self.preprocess, preprocess_params)
        if "TOKENIZERS_PARALLELISM" not in os.environ:
            logger.info("Disabling tokenizer parallelism, we're using DataLoader multithreading already")
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
        feature_extractor = self.feature_extractor if self.feature_extractor is not None else self.image_processor
        collate_fn = no_collate_fn if batch_size == 1 else pad_collate_fn(self.tokenizer, feature_extractor)
        dataloader = DataLoader(dataset, num_workers=num_workers, batch_size=batch_size, collate_fn=collate_fn)
        model_iterator = PipelineIterator(dataloader, self.forward, forward_params, loader_batch_size=batch_size)
        final_iterator = PipelineIterator(model_iterator, self.postprocess, postprocess_params)
        return final_iterator
    def __call__(self, inputs, *args, num_workers=None, batch_size=None, **kwargs):
        if args:
            logger.warning(f"Ignoring args : {args}")
        if num_workers is None:
            if self._num_workers is None:
                num_workers = 0
            else:
                num_workers = self._num_workers
        if batch_size is None:
            if self._batch_size is None:
                batch_size = 1
            else:
                batch_size = self._batch_size
        preprocess_params, forward_params, postprocess_params = self._sanitize_parameters(**kwargs)
        preprocess_params = {**self._preprocess_params, **preprocess_params}
        forward_params = {**self._forward_params, **forward_params}
        postprocess_params = {**self._postprocess_params, **postprocess_params}
        self.call_count += 1
        if self.call_count > 10 and self.framework == "pt" and self.device.type == "cuda":
            logger.warning_once(
                "You seem to be using the pipelines sequentially on GPU. In order to maximize efficiency please use a"
                " dataset",
            )
        is_dataset = Dataset is not None and isinstance(inputs, Dataset)
        is_generator = isinstance(inputs, types.GeneratorType)
        is_list = isinstance(inputs, list)
        is_iterable = is_dataset or is_generator or is_list
        can_use_iterator = self.framework == "pt" and (is_dataset or is_generator or is_list)
        if is_list:
            if can_use_iterator:
                final_iterator = self.get_iterator(
                    inputs, num_workers, batch_size, preprocess_params, forward_params, postprocess_params
                )
                outputs = list(final_iterator)
                return outputs
            else:
                return self.run_multi(inputs, preprocess_params, forward_params, postprocess_params)
        elif can_use_iterator:
            return self.get_iterator(
                inputs, num_workers, batch_size, preprocess_params, forward_params, postprocess_params
            )
        elif is_iterable:
            return self.iterate(inputs, preprocess_params, forward_params, postprocess_params)
        elif self.framework == "pt" and isinstance(self, ChunkPipeline):
            return next(
                iter(
                    self.get_iterator(
                        [inputs], num_workers, batch_size, preprocess_params, forward_params, postprocess_params
                    )
                )
            )
        else:
            return self.run_single(inputs, preprocess_params, forward_params, postprocess_params)
    def run_multi(self, inputs, preprocess_params, forward_params, postprocess_params):
        return [self.run_single(item, preprocess_params, forward_params, postprocess_params) for item in inputs]
    def run_single(self, inputs, preprocess_params, forward_params, postprocess_params):
        model_inputs = self.preprocess(inputs, **preprocess_params)
        model_outputs = self.forward(model_inputs, **forward_params)
        outputs = self.postprocess(model_outputs, **postprocess_params)
        return outputs
    def iterate(self, inputs, preprocess_params, forward_params, postprocess_params):
        for input_ in inputs:
            yield self.run_single(input_, preprocess_params, forward_params, postprocess_params)
Pipeline.push_to_hub = copy_func(Pipeline.push_to_hub)
if Pipeline.push_to_hub.__doc__ is not None:
    Pipeline.push_to_hub.__doc__ = Pipeline.push_to_hub.__doc__.format(
        object="pipe", object_class="pipeline", object_files="pipeline file"
    ).replace(".from_pretrained", "")
class ChunkPipeline(Pipeline):
    def run_single(self, inputs, preprocess_params, forward_params, postprocess_params):
        all_outputs = []
        for model_inputs in self.preprocess(inputs, **preprocess_params):
            model_outputs = self.forward(model_inputs, **forward_params)
            all_outputs.append(model_outputs)
        outputs = self.postprocess(all_outputs, **postprocess_params)
        return outputs
    def get_iterator(
        self, inputs, num_workers: int, batch_size: int, preprocess_params, forward_params, postprocess_params
    ):
        if "TOKENIZERS_PARALLELISM" not in os.environ:
            logger.info("Disabling tokenizer parallelism, we're using DataLoader multithreading already")
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
        if num_workers > 1:
            logger.warning(
                "For ChunkPipeline using num_workers>0 is likely to result in errors since everything is iterable,"
                " setting `num_workers=1` to guarantee correctness."
            )
            num_workers = 1
        dataset = PipelineChunkIterator(inputs, self.preprocess, preprocess_params)
        feature_extractor = self.feature_extractor if self.feature_extractor is not None else self.image_processor
        collate_fn = no_collate_fn if batch_size == 1 else pad_collate_fn(self.tokenizer, feature_extractor)
        dataloader = DataLoader(dataset, num_workers=num_workers, batch_size=batch_size, collate_fn=collate_fn)
        model_iterator = PipelinePackIterator(dataloader, self.forward, forward_params, loader_batch_size=batch_size)
        final_iterator = PipelineIterator(model_iterator, self.postprocess, postprocess_params)
        return final_iterator
class PipelineRegistry:
    def __init__(self, supported_tasks: dict[str, Any], task_aliases: dict[str, str]) -> None:
        self.supported_tasks = supported_tasks
        self.task_aliases = task_aliases
    def get_supported_tasks(self) -> list[str]:
        supported_task = list(self.supported_tasks.keys()) + list(self.task_aliases.keys())
        supported_task.sort()
        return supported_task
    def check_task(self, task: str) -> tuple[str, dict, Any]:
        if task in self.task_aliases:
            task = self.task_aliases[task]
        if task in self.supported_tasks:
            targeted_task = self.supported_tasks[task]
            return task, targeted_task, None
        if task.startswith("translation"):
            tokens = task.split("_")
            if len(tokens) == 4 and tokens[0] == "translation" and tokens[2] == "to":
                targeted_task = self.supported_tasks["translation"]
                task = "translation"
                return task, targeted_task, (tokens[1], tokens[3])
            raise KeyError(f"Invalid translation task {task}, use 'translation_XX_to_YY' format")
        raise KeyError(
            f"Unknown task {task}, available tasks are {self.get_supported_tasks() + ['translation_XX_to_YY']}"
        )
    @deprecate_kwarg(old_name="tf_model", version="5.0.0")
    def register_pipeline(
        self,
        task: str,
        pipeline_class: type,
        pt_model: Optional[Union[type, tuple[type]]] = None,
        tf_model: Optional[Union[type, tuple[type]]] = None,
        default: Optional[dict] = None,
        type: Optional[str] = None,
    ) -> None:
        if task in self.supported_tasks:
            logger.warning(f"{task} is already registered. Overwriting pipeline for task {task}...")
        if pt_model is None:
            pt_model = ()
        elif not isinstance(pt_model, tuple):
            pt_model = (pt_model,)
        if tf_model is None:
            tf_model = ()
        elif not isinstance(tf_model, tuple):
            tf_model = (tf_model,)
        task_impl = {"impl": pipeline_class, "pt": pt_model, "tf": tf_model}
        if default is not None:
            if "model" not in default and ("pt" in default or "tf" in default):
                default = {"model": default}
            task_impl["default"] = default
        if type is not None:
            task_impl["type"] = type
        self.supported_tasks[task] = task_impl
        pipeline_class._registered_impl = {task: task_impl}
    def to_dict(self):
        return self.supported_tasks