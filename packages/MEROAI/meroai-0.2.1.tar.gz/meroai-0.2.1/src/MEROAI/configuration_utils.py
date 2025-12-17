import copy
import json
import os
import warnings
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union
from packaging import version
from . import __version__
from .dynamic_module_utils import custom_object_save
from .modeling_gguf_pytorch_utils import load_gguf_checkpoint
from .utils import (
    CONFIG_NAME,
    PushToHubMixin,
    cached_file,
    copy_func,
    download_url,
    extract_commit_hash,
    is_remote_url,
    is_torch_available,
    logging,
)
from .utils.generic import is_timm_config_dict
if TYPE_CHECKING:
    import torch
logger = logging.get_logger(__name__)
SpecificPretrainedConfigType = TypeVar("SpecificPretrainedConfigType", bound="PretrainedConfig")
class PretrainedConfig(PushToHubMixin):
    model_type: str = ""
    base_config_key: str = ""
    sub_configs: dict[str, type["PretrainedConfig"]] = {}
    has_no_defaults_at_init: bool = False
    attribute_map: dict[str, str] = {}
    base_model_tp_plan: Optional[dict[str, Any]] = None
    base_model_pp_plan: Optional[dict[str, tuple[list[str]]]] = None
    base_model_ep_plan: Optional[dict[str, tuple[list[str]]]] = None
    _auto_class: Optional[str] = None
    def __setattr__(self, key, value):
        if key in super().__getattribute__("attribute_map"):
            key = super().__getattribute__("attribute_map")[key]
        super().__setattr__(key, value)
    def __getattribute__(self, key):
        if key != "attribute_map" and key in super().__getattribute__("attribute_map"):
            key = super().__getattribute__("attribute_map")[key]
        return super().__getattribute__(key)
    def __init__(
        self,
        *,
        output_hidden_states: bool = False,
        output_attentions: bool = False,
        return_dict: bool = True,
        torchscript: bool = False,
        dtype: Optional[Union[str, "torch.dtype"]] = None,
        pruned_heads: Optional[dict[int, list[int]]] = None,
        tie_word_embeddings: bool = True,
        chunk_size_feed_forward: int = 0,
        is_encoder_decoder: bool = False,
        is_decoder: bool = False,
        cross_attention_hidden_size: Optional[int] = None,
        add_cross_attention: bool = False,
        tie_encoder_decoder: bool = False,
        architectures: Optional[list[str]] = None,
        finetuning_task: Optional[str] = None,
        id2label: Optional[dict[int, str]] = None,
        label2id: Optional[dict[str, int]] = None,
        num_labels: Optional[int] = None,
        task_specific_params: Optional[dict[str, Any]] = None,
        problem_type: Optional[str] = None,
        tokenizer_class: Optional[str] = None,
        prefix: Optional[str] = None,
        bos_token_id: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None,
        sep_token_id: Optional[int] = None,
        decoder_start_token_id: Optional[int] = None,
        **kwargs,
    ):
        if label2id is not None and not isinstance(label2id, dict):
            raise ValueError("Argument label2id should be a dictionary.")
        if id2label is not None and not isinstance(id2label, dict):
            raise ValueError("Argument id2label should be a dictionary.")
        if num_labels is not None and id2label is not None and len(id2label) != num_labels:
            logger.warning(
                f"You passed `num_labels={num_labels}` which is incompatible to "
                f"the `id2label` map of length `{len(id2label)}`."
            )
        if problem_type is not None and problem_type not in (
            "regression",
            "single_label_classification",
            "multi_label_classification",
        ):
            raise ValueError(
                f"The config parameter `problem_type` was not understood: received {problem_type} "
                "but only 'regression', 'single_label_classification' and 'multi_label_classification' are valid."
            )
        if (torch_dtype := kwargs.pop("torch_dtype", None)) is not None:
            dtype = dtype if dtype is not None else torch_dtype
        if dtype is not None and isinstance(dtype, str) and is_torch_available():
            import torch
            dtype = getattr(torch, dtype)
        self.return_dict = return_dict
        self.output_hidden_states = output_hidden_states
        self.torchscript = torchscript
        self.dtype = dtype
        self._output_attentions = output_attentions
        self.pruned_heads = pruned_heads if pruned_heads is not None else {}
        self.tie_word_embeddings = tie_word_embeddings
        self.chunk_size_feed_forward = chunk_size_feed_forward
        self.is_encoder_decoder = is_encoder_decoder
        self.is_decoder = is_decoder
        self.cross_attention_hidden_size = cross_attention_hidden_size
        self.add_cross_attention = add_cross_attention
        self.tie_encoder_decoder = tie_encoder_decoder
        self.architectures = architectures
        self.finetuning_task = finetuning_task
        self.id2label = id2label
        self.label2id = label2id
        self.task_specific_params = task_specific_params
        self.problem_type = problem_type
        if self.id2label is None:
            self._create_id_label_maps(num_labels if num_labels is not None else 2)
        else:
            self.id2label = {int(key): value for key, value in self.id2label.items()}
        self.tokenizer_class = tokenizer_class
        self.prefix = prefix
        self.bos_token_id = bos_token_id
        self.pad_token_id = pad_token_id
        self.eos_token_id = eos_token_id
        self.sep_token_id = sep_token_id
        self.decoder_start_token_id = decoder_start_token_id
        for parameter_name, default_value in self._get_global_generation_defaults().items():
            setattr(self, parameter_name, kwargs.pop(parameter_name, default_value))
        self._name_or_path = str(kwargs.pop("name_or_path", ""))
        self._commit_hash = kwargs.pop("_commit_hash", None)
        self._attn_implementation = kwargs.pop("attn_implementation", None)
        self.MEROAI_version = kwargs.pop("MEROAI_version", None)
        if kwargs.get("gradient_checkpointing", False):
            warnings.warn(
                "Passing `gradient_checkpointing` to a config initialization is deprecated and will be removed in v5 "
                "MEROAI. Using `model.gradient_checkpointing_enable()` instead, or if you are using the "
                "`Trainer` API, pass `gradient_checkpointing=True` in your `TrainingArguments`."
            )
        for key, value in kwargs.items():
            try:
                setattr(self, key, value)
            except AttributeError as err:
                logger.error(f"Can't set {key} with value {value} for {self}")
                raise err
        self.tf_legacy_loss = kwargs.pop("tf_legacy_loss", False)
        self.use_bfloat16 = kwargs.pop("use_bfloat16", False)
    def _create_id_label_maps(self, num_labels: int):
        self.id2label = {i: f"LABEL_{i}" for i in range(num_labels)}
        self.label2id = dict(zip(self.id2label.values(), self.id2label.keys()))
    @property
    def name_or_path(self) -> Optional[str]:
        return getattr(self, "_name_or_path", None)
    @name_or_path.setter
    def name_or_path(self, value):
        self._name_or_path = str(value)
    @property
    def output_attentions(self):
        return self._output_attentions
    @output_attentions.setter
    def output_attentions(self, value: bool):
        if value and self._attn_implementation is None:
            self._attn_implementation = "eager"
        if value and self._attn_implementation != "eager":
            raise ValueError(
                "The `output_attentions` attribute is not supported when using the `attn_implementation` set to "
                f"{self._attn_implementation}. Please set it to 'eager' instead."
            )
        self._output_attentions = value
    @property
    def use_return_dict(self) -> bool:
        return self.return_dict and not self.torchscript
    @property
    def num_labels(self) -> int:
        return len(self.id2label)
    @num_labels.setter
    def num_labels(self, num_labels: int):
        if self.id2label is None or self.num_labels != num_labels:
            self._create_id_label_maps(num_labels)
    @property
    def _attn_implementation(self):
        return self._attn_implementation_internal
    @_attn_implementation.setter
    def _attn_implementation(self, value: Optional[Union[str, dict]]):
        current_attn = getattr(self, "_attn_implementation", None)
        attn_implementation = value if not isinstance(value, dict) else value.get("", current_attn)
        self._attn_implementation_internal = attn_implementation
        for subconfig_key in self.sub_configs:
            subconfig = getattr(self, subconfig_key, None)
            if subconfig is not None:
                current_subconfig_attn = getattr(subconfig, "_attn_implementation", None)
                sub_implementation = (
                    value if not isinstance(value, dict) else value.get(subconfig_key, current_subconfig_attn)
                )
                subconfig._attn_implementation = sub_implementation
    @property
    def torch_dtype(self):
        logger.warning_once("`torch_dtype` is deprecated! Use `dtype` instead!")
        return self.dtype
    @torch_dtype.setter
    def torch_dtype(self, value):
        logger.warning_once("`torch_dtype` is deprecated! Use `dtype` instead!")
        self.dtype = value
    def save_pretrained(self, save_directory: Union[str, os.PathLike], push_to_hub: bool = False, **kwargs):
        self._set_token_in_kwargs(kwargs)
        if os.path.isfile(save_directory):
            raise AssertionError(f"Provided path ({save_directory}) should be a directory, not a file")
        non_default_generation_parameters = self._get_non_default_generation_parameters()
        if len(non_default_generation_parameters) > 0:
            warnings.warn(
                "Some non-default generation parameters are set in the model config. These should go into either a) "
                "`model.generation_config` (as opposed to `model.config`); OR b) a GenerationConfig file "
                "(https://huggingface.co/docs/MEROAI/generation_strategies#save-a-custom-decoding-strategy-with-your-model)."
                "This warning will become an exception in the future."
                f"\nNon-default generation parameters: {str(non_default_generation_parameters)}",
                UserWarning,
            )
        os.makedirs(save_directory, exist_ok=True)
        if push_to_hub:
            commit_message = kwargs.pop("commit_message", None)
            repo_id = kwargs.pop("repo_id", save_directory.split(os.path.sep)[-1])
            repo_id = self._create_repo(repo_id, **kwargs)
            files_timestamps = self._get_files_timestamps(save_directory)
        if "MEROAI_weights" in self:
            delattr(self, "MEROAI_weights")
        if self._auto_class is not None:
            custom_object_save(self, save_directory, config=self)
        output_config_file = os.path.join(save_directory, CONFIG_NAME)
        self.to_json_file(output_config_file, use_diff=True)
        logger.info(f"Configuration saved in {output_config_file}")
        if push_to_hub:
            self._upload_modified_files(
                save_directory,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=kwargs.get("token"),
            )
    @staticmethod
    def _set_token_in_kwargs(kwargs, token=None):
        if token is None:
            token = kwargs.pop("token", None)
        use_auth_token = kwargs.pop("use_auth_token", None)
        if use_auth_token is not None:
            warnings.warn(
                "The `use_auth_token` argument is deprecated and will be removed in v5 of MEROAI. Please use `token` instead.",
                FutureWarning,
            )
            if token is not None:
                raise ValueError(
                    "`token` and `use_auth_token` are both specified. Please set only the argument `token`."
                )
            token = use_auth_token
        if token is not None:
            kwargs["token"] = token
    @classmethod
    def from_pretrained(
        cls: type[SpecificPretrainedConfigType],
        pretrained_model_name_or_path: Union[str, os.PathLike],
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        **kwargs,
    ) -> SpecificPretrainedConfigType:
        kwargs["cache_dir"] = cache_dir
        kwargs["force_download"] = force_download
        kwargs["local_files_only"] = local_files_only
        kwargs["revision"] = revision
        cls._set_token_in_kwargs(kwargs, token)
        config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
        if cls.base_config_key and cls.base_config_key in config_dict:
            config_dict = config_dict[cls.base_config_key]
        if "model_type" in config_dict and hasattr(cls, "model_type") and config_dict["model_type"] != cls.model_type:
            for v in config_dict.values():
                if isinstance(v, dict) and v.get("model_type") == cls.model_type:
                    config_dict = v
            if config_dict["model_type"] != cls.model_type:
                logger.warning(
                    f"You are using a model of type {config_dict['model_type']} to instantiate a model of type "
                    f"{cls.model_type}. This is not supported for all configurations of models and can yield errors."
                )
        return cls.from_dict(config_dict, **kwargs)
    @classmethod
    def get_config_dict(
        cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        cls._set_token_in_kwargs(kwargs)
        original_kwargs = copy.deepcopy(kwargs)
        config_dict, kwargs = cls._get_config_dict(pretrained_model_name_or_path, **kwargs)
        if config_dict is None:
            return {}, kwargs
        if "_commit_hash" in config_dict:
            original_kwargs["_commit_hash"] = config_dict["_commit_hash"]
        if "configuration_files" in config_dict:
            configuration_file = get_configuration_file(config_dict["configuration_files"])
            config_dict, kwargs = cls._get_config_dict(
                pretrained_model_name_or_path, _configuration_file=configuration_file, **original_kwargs
            )
        return config_dict, kwargs
    @classmethod
    def _get_config_dict(
        cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        cache_dir = kwargs.pop("cache_dir", None)
        force_download = kwargs.pop("force_download", False)
        resume_download = kwargs.pop("resume_download", None)
        proxies = kwargs.pop("proxies", None)
        token = kwargs.pop("token", None)
        local_files_only = kwargs.pop("local_files_only", False)
        revision = kwargs.pop("revision", None)
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        subfolder = kwargs.pop("subfolder", "")
        from_pipeline = kwargs.pop("_from_pipeline", None)
        from_auto_class = kwargs.pop("_from_auto", False)
        commit_hash = kwargs.pop("_commit_hash", None)
        gguf_file = kwargs.get("gguf_file")
        if trust_remote_code is True:
            logger.warning(
                "The argument `trust_remote_code` is to be used with Auto classes. It has no effect here and is"
                " ignored."
            )
        user_agent = {"file_type": "config", "from_auto_class": from_auto_class}
        if from_pipeline is not None:
            user_agent["using_pipeline"] = from_pipeline
        pretrained_model_name_or_path = str(pretrained_model_name_or_path)
        is_local = os.path.isdir(pretrained_model_name_or_path)
        if os.path.isfile(os.path.join(subfolder, pretrained_model_name_or_path)):
            resolved_config_file = pretrained_model_name_or_path
            is_local = True
        elif is_remote_url(pretrained_model_name_or_path):
            configuration_file = pretrained_model_name_or_path if gguf_file is None else gguf_file
            resolved_config_file = download_url(pretrained_model_name_or_path)
        else:
            configuration_file = kwargs.pop("_configuration_file", CONFIG_NAME) if gguf_file is None else gguf_file
            try:
                resolved_config_file = cached_file(
                    pretrained_model_name_or_path,
                    configuration_file,
                    cache_dir=cache_dir,
                    force_download=force_download,
                    proxies=proxies,
                    resume_download=resume_download,
                    local_files_only=local_files_only,
                    token=token,
                    user_agent=user_agent,
                    revision=revision,
                    subfolder=subfolder,
                    _commit_hash=commit_hash,
                )
                if resolved_config_file is None:
                    return None, kwargs
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            except OSError:
                raise
            except Exception:
                raise OSError(
                    f"Can't load the configuration of '{pretrained_model_name_or_path}'. If you were trying to load it"
                    " from 'https://huggingface.co/models', make sure you don't have a local directory with the same"
                    f" name. Otherwise, make sure '{pretrained_model_name_or_path}' is the correct path to a directory"
                    f" containing a {configuration_file} file"
                )
        try:
            if gguf_file:
                config_dict = load_gguf_checkpoint(resolved_config_file, return_tensors=False)["config"]
            else:
                config_dict = cls._dict_from_json_file(resolved_config_file)
            config_dict["_commit_hash"] = commit_hash
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise OSError(f"It looks like the config file at '{resolved_config_file}' is not a valid JSON file.")
        if is_local:
            logger.info(f"loading configuration file {resolved_config_file}")
        else:
            logger.info(f"loading configuration file {configuration_file} from cache at {resolved_config_file}")
        if "model_type" not in config_dict and is_timm_config_dict(config_dict):
            config_dict["model_type"] = "timm_wrapper"
        return config_dict, kwargs
    @classmethod
    def from_dict(
        cls: type[SpecificPretrainedConfigType], config_dict: dict[str, Any], **kwargs
    ) -> SpecificPretrainedConfigType:
        return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)
        kwargs.pop("_from_auto", None)
        kwargs.pop("_from_pipeline", None)
        if "_commit_hash" in kwargs and "_commit_hash" in config_dict:
            kwargs["_commit_hash"] = config_dict["_commit_hash"]
        if (torch_dtype := kwargs.pop("torch_dtype", None)) is not None:
            logger.warning_once("`torch_dtype` is deprecated! Use `dtype` instead!")
            kwargs["dtype"] = kwargs.get("dtype", torch_dtype)
        config_dict["attn_implementation"] = kwargs.pop("attn_implementation", None)
        config = cls(**config_dict)
        if hasattr(config, "pruned_heads"):
            config.pruned_heads = {int(key): value for key, value in config.pruned_heads.items()}
        if "num_labels" in kwargs and "id2label" in kwargs:
            num_labels = kwargs["num_labels"]
            id2label = kwargs["id2label"] if kwargs["id2label"] is not None else []
            if len(id2label) != num_labels:
                raise ValueError(
                    f"You passed along `num_labels={num_labels}` with an incompatible id to label map: "
                    f"{kwargs['id2label']}. Since those arguments are inconsistent with each other, you should remove "
                    "one of them."
                )
        to_remove = []
        for key, value in kwargs.items():
            if hasattr(config, key):
                current_attr = getattr(config, key)
                if isinstance(current_attr, PretrainedConfig) and isinstance(value, dict):
                    current_attr_updated = current_attr.to_dict()
                    current_attr_updated.update(value)
                    value = current_attr.__class__(**current_attr_updated)
                setattr(config, key, value)
                if key != "dtype":
                    to_remove.append(key)
        for key in to_remove:
            kwargs.pop(key, None)
        logger.info(f"Model config {config}")
        if return_unused_kwargs:
            return config, kwargs
        else:
            return config
    @classmethod
    def from_json_file(
        cls: type[SpecificPretrainedConfigType], json_file: Union[str, os.PathLike]
    ) -> SpecificPretrainedConfigType:
        config_dict = cls._dict_from_json_file(json_file)
        return cls(**config_dict)
    @classmethod
    def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
        with open(json_file, encoding="utf-8") as reader:
            text = reader.read()
        return json.loads(text)
    def __eq__(self, other):
        return isinstance(other, PretrainedConfig) and (self.__dict__ == other.__dict__)
    def __repr__(self):
        return f"{self.__class__.__name__} {self.to_json_string()}"
    def __iter__(self):
        yield from self.__dict__
    def to_diff_dict(self) -> dict[str, Any]:
        config_dict = self.to_dict()
        default_config_dict = PretrainedConfig().to_dict()
        class_config_dict = self.__class__().to_dict() if not self.has_no_defaults_at_init else {}
        serializable_config_dict = {}
        for key, value in config_dict.items():
            if (
                isinstance(getattr(self, key, None), PretrainedConfig)
                and key in class_config_dict
                and isinstance(class_config_dict[key], dict)
                or key in self.sub_configs
            ):
                diff = recursive_diff_dict(value, default_config_dict, config_obj=getattr(self, key, None))
                if "model_type" in value:
                    diff["model_type"] = value["model_type"]
                serializable_config_dict[key] = diff
            elif (
                key not in default_config_dict
                or key == "MEROAI_version"
                or key == "vocab_file"
                or value != default_config_dict[key]
                or (key in default_config_dict and value != class_config_dict.get(key, value))
            ):
                serializable_config_dict[key] = value
        self._remove_keys_not_serialized(serializable_config_dict)
        if "_name_or_path" in serializable_config_dict:
            del serializable_config_dict["_name_or_path"]
        if hasattr(self, "quantization_config"):
            serializable_config_dict["quantization_config"] = (
                self.quantization_config.to_dict()
                if not isinstance(self.quantization_config, dict)
                else self.quantization_config
            )
        self.dict_dtype_to_str(serializable_config_dict)
        return serializable_config_dict
    def to_dict(self) -> dict[str, Any]:
        output = copy.deepcopy(self.__dict__)
        if hasattr(self.__class__, "model_type"):
            output["model_type"] = self.__class__.model_type
        output["MEROAI_version"] = __version__
        for key, value in output.items():
            if isinstance(value, PretrainedConfig):
                value = value.to_dict()
                del value["MEROAI_version"]
            output[key] = value
        self._remove_keys_not_serialized(output)
        if hasattr(self, "quantization_config"):
            output["quantization_config"] = (
                self.quantization_config.to_dict()
                if not isinstance(self.quantization_config, dict)
                else self.quantization_config
            )
        self.dict_dtype_to_str(output)
        return output
    def to_json_string(self, use_diff: bool = True) -> str:
        if use_diff is True:
            config_dict = self.to_diff_dict()
        else:
            config_dict = self.to_dict()
        return json.dumps(config_dict, indent=2, sort_keys=True) + "\n"
    def to_json_file(self, json_file_path: Union[str, os.PathLike], use_diff: bool = True):
        with open(json_file_path, "w", encoding="utf-8") as writer:
            writer.write(self.to_json_string(use_diff=use_diff))
    def update(self, config_dict: dict[str, Any]):
        for key, value in config_dict.items():
            setattr(self, key, value)
    def update_from_string(self, update_str: str):
        d = dict(x.split("=") for x in update_str.split(","))
        for k, v in d.items():
            if not hasattr(self, k):
                raise ValueError(f"key {k} isn't in the original config dict")
            old_v = getattr(self, k)
            if isinstance(old_v, bool):
                if v.lower() in ["true", "1", "y", "yes"]:
                    v = True
                elif v.lower() in ["false", "0", "n", "no"]:
                    v = False
                else:
                    raise ValueError(f"can't derive true or false from {v} (key {k})")
            elif isinstance(old_v, int):
                v = int(v)
            elif isinstance(old_v, float):
                v = float(v)
            elif not isinstance(old_v, str):
                raise TypeError(
                    f"You can only update int, float, bool or string values in the config, got {v} for key {k}"
                )
            setattr(self, k, v)
    def dict_dtype_to_str(self, d: dict[str, Any]) -> None:
        if d.get("dtype") is not None:
            if isinstance(d["dtype"], dict):
                d["dtype"] = {k: str(v).split(".")[-1] for k, v in d["dtype"].items()}
            elif not isinstance(d["dtype"], (str, int)):
                d["dtype"] = str(d["dtype"]).split(".")[1]
        for value in d.values():
            if isinstance(value, dict):
                self.dict_dtype_to_str(value)
    def _remove_keys_not_serialized(self, d: dict[str, Any]) -> None:
        if hasattr(self, "quantization_config"):
            _ = d.pop("_pre_quantization_dtype", None)
        if "_auto_class" in d:
            del d["_auto_class"]
        if "_output_attentions" in d:
            d["output_attentions"] = d.pop("_output_attentions")
        if "_commit_hash" in d:
            del d["_commit_hash"]
        if "_attn_implementation_internal" in d:
            del d["_attn_implementation_internal"]
        if "base_model_tp_plan" in d:
            del d["base_model_tp_plan"]
        if "base_model_pp_plan" in d:
            del d["base_model_pp_plan"]
        for value in d.values():
            if isinstance(value, dict):
                self._remove_keys_not_serialized(value)
    @classmethod
    def register_for_auto_class(cls, auto_class="AutoConfig"):
        if not isinstance(auto_class, str):
            auto_class = auto_class.__name__
        import MEROAI.models.auto as auto_module
        if not hasattr(auto_module, auto_class):
            raise ValueError(f"{auto_class} is not a valid auto class.")
        cls._auto_class = auto_class
    @staticmethod
    def _get_global_generation_defaults() -> dict[str, Any]:
        return {
            "max_length": 20,
            "min_length": 0,
            "do_sample": False,
            "early_stopping": False,
            "num_beams": 1,
            "temperature": 1.0,
            "top_k": 50,
            "top_p": 1.0,
            "typical_p": 1.0,
            "repetition_penalty": 1.0,
            "length_penalty": 1.0,
            "no_repeat_ngram_size": 0,
            "encoder_no_repeat_ngram_size": 0,
            "bad_words_ids": None,
            "num_return_sequences": 1,
            "output_scores": False,
            "return_dict_in_generate": False,
            "forced_bos_token_id": None,
            "forced_eos_token_id": None,
            "remove_invalid_values": False,
            "exponential_decay_length_penalty": None,
            "suppress_tokens": None,
            "begin_suppress_tokens": None,
            "num_beam_groups": 1,
            "diversity_penalty": 0.0,
        }
    def _get_non_default_generation_parameters(self) -> dict[str, Any]:
        non_default_generation_parameters = {}
        decoder_attribute_name = None
        try:
            default_config = self.__class__()
        except ValueError:
            decoder_config = self.get_text_config(decoder=True)
            if decoder_config is not self:
                default_config = decoder_config.__class__()
            else:
                default_config = None
        self_decoder_config = self if decoder_attribute_name is None else getattr(self, decoder_attribute_name)
        for parameter_name, default_global_value in self._get_global_generation_defaults().items():
            if hasattr(self_decoder_config, parameter_name):
                is_default_in_config = is_default_generation_value = None
                parameter_value = getattr(self_decoder_config, parameter_name)
                if parameter_value is None:
                    continue
                if default_config is not None:
                    is_default_in_config = parameter_value == getattr(default_config, parameter_name)
                else:
                    is_default_generation_value = parameter_value == default_global_value
                is_non_default = (is_default_in_config is False) or (
                    is_default_in_config is None and is_default_generation_value is False
                )
                if is_non_default:
                    non_default_generation_parameters[parameter_name] = getattr(self_decoder_config, parameter_name)
        return non_default_generation_parameters
    def get_text_config(self, decoder=None, encoder=None) -> "PretrainedConfig":
        return_both = decoder == encoder
        decoder_possible_text_config_names = ("decoder", "generator", "text_config")
        encoder_possible_text_config_names = ("text_encoder",)
        if return_both:
            possible_text_config_names = encoder_possible_text_config_names + decoder_possible_text_config_names
        elif decoder:
            possible_text_config_names = decoder_possible_text_config_names
        else:
            possible_text_config_names = encoder_possible_text_config_names
        valid_text_config_names = []
        for text_config_name in possible_text_config_names:
            if hasattr(self, text_config_name):
                text_config = getattr(self, text_config_name, None)
                if text_config is not None:
                    valid_text_config_names += [text_config_name]
        if len(valid_text_config_names) > 1:
            raise ValueError(
                f"Multiple valid text configs were found in the model config: {valid_text_config_names}. In this "
                "case, using `get_text_config()` would be ambiguous. Please specify the desired text config directly, "
                "e.g. `text_config = config.sub_config_name`"
            )
        elif len(valid_text_config_names) == 1:
            config_to_return = getattr(self, valid_text_config_names[0])
        else:
            config_to_return = self
        if not return_both and len(valid_text_config_names) == 0 and config_to_return.is_encoder_decoder:
            config_to_return = copy.deepcopy(config_to_return)
            prefix_to_discard = "encoder" if decoder else "decoder"
            prefix_to_keep = "decoder" if decoder else "encoder"
            for key in config_to_return.to_dict():
                if key.startswith(prefix_to_discard) and key not in config_to_return.attribute_map.values():
                    delattr(config_to_return, key)
                if key.startswith(prefix_to_keep):
                    if key == prefix_to_keep + "_layers":
                        new_key = "num_hidden_layers"
                    elif key == prefix_to_keep + "_attention_heads":
                        new_key = "num_attention_heads"
                    else:
                        new_key = key[len(prefix_to_keep) + 1 :]
                    if new_key in config_to_return.attribute_map:
                        new_key = config_to_return.attribute_map[new_key]
                    value = getattr(config_to_return, key)
                    delattr(config_to_return, key)
                    setattr(config_to_return, new_key, value)
        return config_to_return
    @classmethod
    def from_text_vision_configs(cls, text_config, vision_config, **kwargs):
        warnings.warn(
            "The `from_text_vision_configs` method is deprecated and will be removed in v4.60 of MEROAI. Please instantiate "
            "the config class directly with `MyConfig(text_config=text_config, vision_config=vision_config, **kwargs)` instead.",
            FutureWarning,
        )
        return cls(text_config=text_config.to_dict(), vision_config=vision_config.to_dict(), **kwargs)
    @classmethod
    def from_text_audio_configs(cls, text_config, audio_config, **kwargs):
        warnings.warn(
            "The `from_text_audio_configs` method is deprecated and will be removed in v4.60 of MEROAI. Please instantiate "
            "the config class directly with `MyConfig(text_config=text_config, audio_config=audio_config, **kwargs)` instead.",
            FutureWarning,
        )
        return cls(text_config=text_config.to_dict(), audio_config=audio_config.to_dict(), **kwargs)
def get_configuration_file(configuration_files: list[str]) -> str:
    configuration_files_map = {}
    for file_name in configuration_files:
        if file_name.startswith("config.") and file_name.endswith(".json") and file_name != "config.json":
            v = file_name.removeprefix("config.").removesuffix(".json")
            configuration_files_map[v] = file_name
    available_versions = sorted(configuration_files_map.keys())
    configuration_file = CONFIG_NAME
    MEROAI_version = version.parse(__version__)
    for v in available_versions:
        if version.parse(v) <= MEROAI_version:
            configuration_file = configuration_files_map[v]
        else:
            break
    return configuration_file
def recursive_diff_dict(dict_a, dict_b, config_obj=None):
    diff = {}
    default = config_obj.__class__().to_dict() if config_obj is not None else {}
    for key, value in dict_a.items():
        obj_value = getattr(config_obj, str(key), None)
        if isinstance(obj_value, PretrainedConfig) and key in dict_b and isinstance(dict_b[key], dict):
            diff_value = recursive_diff_dict(value, dict_b[key], config_obj=obj_value)
            diff[key] = diff_value
        elif key not in dict_b or (value != default[key]):
            diff[key] = value
    return diff
PretrainedConfig.push_to_hub = copy_func(PretrainedConfig.push_to_hub)
if PretrainedConfig.push_to_hub.__doc__ is not None:
    PretrainedConfig.push_to_hub.__doc__ = PretrainedConfig.push_to_hub.__doc__.format(
        object="config", object_class="AutoConfig", object_files="configuration file"
    )
ALLOWED_LAYER_TYPES = (
    "full_attention",
    "sliding_attention",
    "chunked_attention",
    "linear_attention",
)
def layer_type_validation(layer_types: list[str], num_hidden_layers: Optional[int] = None):
    if not all(layer_type in ALLOWED_LAYER_TYPES for layer_type in layer_types):
        raise ValueError(f"The `layer_types` entries must be in {ALLOWED_LAYER_TYPES}")
    if num_hidden_layers is not None and num_hidden_layers != len(layer_types):
        raise ValueError(
            f"`num_hidden_layers` ({num_hidden_layers}) must be equal to the number of layer types "
            f"({len(layer_types)})"
        )