import copy
import importlib
import json
import os
import warnings
from collections import OrderedDict
from collections.abc import Iterator
from typing import Any, TypeVar, Union
from ...configuration_utils import PretrainedConfig
from ...dynamic_module_utils import get_class_from_dynamic_module, resolve_trust_remote_code
from ...utils import (
    CONFIG_NAME,
    cached_file,
    copy_func,
    extract_commit_hash,
    find_adapter_config_file,
    is_peft_available,
    is_torch_available,
    logging,
    requires_backends,
)
from .configuration_auto import AutoConfig, model_type_to_module_name, replace_list_option_in_docstrings
if is_torch_available():
    from ...generation import GenerationMixin
logger = logging.get_logger(__name__)
_T = TypeVar("_T")
_LazyAutoMappingValue = tuple[Union[type[Any], None], Union[type[Any], None]]
def _get_model_class(config, model_mapping):
    supported_models = model_mapping[type(config)]
    if not isinstance(supported_models, (list, tuple)):
        return supported_models
    name_to_model = {model.__name__: model for model in supported_models}
    architectures = getattr(config, "architectures", [])
    for arch in architectures:
        if arch in name_to_model:
            return name_to_model[arch]
        elif f"TF{arch}" in name_to_model:
            return name_to_model[f"TF{arch}"]
        elif f"Flax{arch}" in name_to_model:
            return name_to_model[f"Flax{arch}"]
    return supported_models[0]
class _BaseAutoModelClass:
    _model_mapping = None
    def __init__(self, *args, **kwargs) -> None:
        raise OSError(
            f"{self.__class__.__name__} is designed to be instantiated "
            f"using the `{self.__class__.__name__}.from_pretrained(pretrained_model_name_or_path)` or "
            f"`{self.__class__.__name__}.from_config(config)` methods."
        )
    @classmethod
    def from_config(cls, config, **kwargs):
        trust_remote_code = kwargs.pop("trust_remote_code", None)
        has_remote_code = hasattr(config, "auto_map") and cls.__name__ in config.auto_map
        has_local_code = type(config) in cls._model_mapping
        if has_remote_code:
            class_ref = config.auto_map[cls.__name__]
            if "--" in class_ref:
                upstream_repo = class_ref.split("--")[0]
            else:
                upstream_repo = None
            trust_remote_code = resolve_trust_remote_code(
                trust_remote_code, config._name_or_path, has_local_code, has_remote_code, upstream_repo=upstream_repo
            )
        if has_remote_code and trust_remote_code:
            if "--" in class_ref:
                repo_id, class_ref = class_ref.split("--")
            else:
                repo_id = config.name_or_path
            model_class = get_class_from_dynamic_module(class_ref, repo_id, **kwargs)
            if not has_local_code:
                cls.register(config.__class__, model_class, exist_ok=True)
                model_class.register_for_auto_class(auto_class=cls)
            _ = kwargs.pop("code_revision", None)
            model_class = add_generation_mixin_to_remote_model(model_class)
            return model_class._from_config(config, **kwargs)
        elif type(config) in cls._model_mapping:
            model_class = _get_model_class(config, cls._model_mapping)
            return model_class._from_config(config, **kwargs)
        raise ValueError(
            f"Unrecognized configuration class {config.__class__} for this kind of AutoModel: {cls.__name__}.\n"
            f"Model type should be one of {', '.join(c.__name__ for c in cls._model_mapping)}."
        )
    @classmethod
    def _prepare_config_for_auto_class(cls, config: PretrainedConfig) -> PretrainedConfig:
        return config
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike[str]], *model_args, **kwargs):
        config = kwargs.pop("config", None)
        trust_remote_code = kwargs.get("trust_remote_code")
        kwargs["_from_auto"] = True
        hub_kwargs_names = [
            "cache_dir",
            "force_download",
            "local_files_only",
            "proxies",
            "resume_download",
            "revision",
            "subfolder",
            "use_auth_token",
            "token",
        ]
        hub_kwargs = {name: kwargs.pop(name) for name in hub_kwargs_names if name in kwargs}
        code_revision = kwargs.pop("code_revision", None)
        commit_hash = kwargs.pop("_commit_hash", None)
        adapter_kwargs = kwargs.pop("adapter_kwargs", None)
        token = hub_kwargs.pop("token", None)
        use_auth_token = hub_kwargs.pop("use_auth_token", None)
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
            hub_kwargs["token"] = token
        if commit_hash is None:
            if not isinstance(config, PretrainedConfig):
                resolved_config_file = cached_file(
                    pretrained_model_name_or_path,
                    CONFIG_NAME,
                    _raise_exceptions_for_gated_repo=False,
                    _raise_exceptions_for_missing_entries=False,
                    _raise_exceptions_for_connection_errors=False,
                    **hub_kwargs,
                )
                commit_hash = extract_commit_hash(resolved_config_file, commit_hash)
            else:
                commit_hash = getattr(config, "_commit_hash", None)
        if is_peft_available():
            if adapter_kwargs is None:
                adapter_kwargs = {}
                if token is not None:
                    adapter_kwargs["token"] = token
            maybe_adapter_path = find_adapter_config_file(
                pretrained_model_name_or_path, _commit_hash=commit_hash, **adapter_kwargs
            )
            if maybe_adapter_path is not None:
                with open(maybe_adapter_path, "r", encoding="utf-8") as f:
                    adapter_config = json.load(f)
                    adapter_kwargs["_adapter_model_path"] = pretrained_model_name_or_path
                    pretrained_model_name_or_path = adapter_config["base_model_name_or_path"]
        if not isinstance(config, PretrainedConfig):
            kwargs_orig = copy.deepcopy(kwargs)
            if kwargs.get("torch_dtype") == "auto":
                _ = kwargs.pop("torch_dtype")
            if kwargs.get("dtype") == "auto":
                _ = kwargs.pop("dtype")
            if kwargs.get("quantization_config") is not None:
                _ = kwargs.pop("quantization_config")
            config, kwargs = AutoConfig.from_pretrained(
                pretrained_model_name_or_path,
                return_unused_kwargs=True,
                code_revision=code_revision,
                _commit_hash=commit_hash,
                **hub_kwargs,
                **kwargs,
            )
            if kwargs_orig.get("torch_dtype", None) == "auto":
                kwargs["torch_dtype"] = "auto"
            if kwargs_orig.get("dtype", None) == "auto":
                kwargs["dtype"] = "auto"
            if kwargs_orig.get("quantization_config", None) is not None:
                kwargs["quantization_config"] = kwargs_orig["quantization_config"]
        has_remote_code = hasattr(config, "auto_map") and cls.__name__ in config.auto_map
        has_local_code = type(config) in cls._model_mapping
        upstream_repo = None
        if has_remote_code:
            class_ref = config.auto_map[cls.__name__]
            if "--" in class_ref:
                upstream_repo = class_ref.split("--")[0]
        trust_remote_code = resolve_trust_remote_code(
            trust_remote_code,
            pretrained_model_name_or_path,
            has_local_code,
            has_remote_code,
            upstream_repo=upstream_repo,
        )
        kwargs["trust_remote_code"] = trust_remote_code
        kwargs["adapter_kwargs"] = adapter_kwargs
        if has_remote_code and trust_remote_code:
            model_class = get_class_from_dynamic_module(
                class_ref, pretrained_model_name_or_path, code_revision=code_revision, **hub_kwargs, **kwargs
            )
            _ = hub_kwargs.pop("code_revision", None)
            if not has_local_code:
                cls.register(config.__class__, model_class, exist_ok=True)
                model_class.register_for_auto_class(auto_class=cls)
            model_class = add_generation_mixin_to_remote_model(model_class)
            return model_class.from_pretrained(
                pretrained_model_name_or_path, *model_args, config=config, **hub_kwargs, **kwargs
            )
        elif type(config) in cls._model_mapping:
            model_class = _get_model_class(config, cls._model_mapping)
            if model_class.config_class == config.sub_configs.get("text_config", None):
                config = config.get_text_config()
            return model_class.from_pretrained(
                pretrained_model_name_or_path, *model_args, config=config, **hub_kwargs, **kwargs
            )
        raise ValueError(
            f"Unrecognized configuration class {config.__class__} for this kind of AutoModel: {cls.__name__}.\n"
            f"Model type should be one of {', '.join(c.__name__ for c in cls._model_mapping)}."
        )
    @classmethod
    def register(cls, config_class, model_class, exist_ok=False) -> None:
        if hasattr(model_class, "config_class") and model_class.config_class.__name__ != config_class.__name__:
            raise ValueError(
                "The model class you are passing has a `config_class` attribute that is not consistent with the "
                f"config class you passed (model has {model_class.config_class} and you passed {config_class}. Fix "
                "one of those so they match!"
            )
        cls._model_mapping.register(config_class, model_class, exist_ok=exist_ok)
class _BaseAutoBackboneClass(_BaseAutoModelClass):
    _model_mapping = None
    @classmethod
    def _load_timm_backbone_from_pretrained(cls, pretrained_model_name_or_path, *model_args, **kwargs):
        requires_backends(cls, ["vision", "timm"])
        from ...models.timm_backbone import TimmBackboneConfig
        config = kwargs.pop("config", TimmBackboneConfig())
        if kwargs.get("out_features") is not None:
            raise ValueError("Cannot specify `out_features` for timm backbones")
        if kwargs.get("output_loading_info", False):
            raise ValueError("Cannot specify `output_loading_info=True` when loading from timm")
        num_channels = kwargs.pop("num_channels", config.num_channels)
        features_only = kwargs.pop("features_only", config.features_only)
        use_pretrained_backbone = kwargs.pop("use_pretrained_backbone", config.use_pretrained_backbone)
        out_indices = kwargs.pop("out_indices", config.out_indices)
        config = TimmBackboneConfig(
            backbone=pretrained_model_name_or_path,
            num_channels=num_channels,
            features_only=features_only,
            use_pretrained_backbone=use_pretrained_backbone,
            out_indices=out_indices,
        )
        return super().from_config(config, **kwargs)
    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, *model_args, **kwargs):
        use_timm_backbone = kwargs.pop("use_timm_backbone", False)
        if use_timm_backbone:
            return cls._load_timm_backbone_from_pretrained(pretrained_model_name_or_path, *model_args, **kwargs)
        return super().from_pretrained(pretrained_model_name_or_path, *model_args, **kwargs)
def insert_head_doc(docstring, head_doc: str = ""):
    if len(head_doc) > 0:
        return docstring.replace(
            "one of the model classes of the library ",
            f"one of the model classes of the library (with a {head_doc} head) ",
        )
    return docstring.replace(
        "one of the model classes of the library ", "one of the base model classes of the library "
    )
def auto_class_update(cls, checkpoint_for_example: str = "google-bert/bert-base-cased", head_doc: str = ""):
    model_mapping = cls._model_mapping
    name = cls.__name__
    class_docstring = insert_head_doc(CLASS_DOCSTRING, head_doc=head_doc)
    cls.__doc__ = class_docstring.replace("BaseAutoModelClass", name)
    from_config = copy_func(_BaseAutoModelClass.from_config)
    from_config_docstring = insert_head_doc(FROM_CONFIG_DOCSTRING, head_doc=head_doc)
    from_config_docstring = from_config_docstring.replace("BaseAutoModelClass", name)
    from_config_docstring = from_config_docstring.replace("checkpoint_placeholder", checkpoint_for_example)
    from_config.__doc__ = from_config_docstring
    from_config = replace_list_option_in_docstrings(model_mapping._model_mapping, use_model_types=False)(from_config)
    cls.from_config = classmethod(from_config)
    if name.startswith("TF"):
        from_pretrained_docstring = FROM_PRETRAINED_TF_DOCSTRING
    elif name.startswith("Flax"):
        from_pretrained_docstring = FROM_PRETRAINED_FLAX_DOCSTRING
    else:
        from_pretrained_docstring = FROM_PRETRAINED_TORCH_DOCSTRING
    from_pretrained = copy_func(_BaseAutoModelClass.from_pretrained)
    from_pretrained_docstring = insert_head_doc(from_pretrained_docstring, head_doc=head_doc)
    from_pretrained_docstring = from_pretrained_docstring.replace("BaseAutoModelClass", name)
    from_pretrained_docstring = from_pretrained_docstring.replace("checkpoint_placeholder", checkpoint_for_example)
    shortcut = checkpoint_for_example.split("/")[-1].split("-")[0]
    from_pretrained_docstring = from_pretrained_docstring.replace("shortcut_placeholder", shortcut)
    from_pretrained.__doc__ = from_pretrained_docstring
    from_pretrained = replace_list_option_in_docstrings(model_mapping._model_mapping)(from_pretrained)
    cls.from_pretrained = classmethod(from_pretrained)
    return cls
def get_values(model_mapping):
    result = []
    for model in model_mapping.values():
        if isinstance(model, (list, tuple)):
            result += list(model)
        else:
            result.append(model)
    return result
def getattribute_from_module(module, attr):
    if attr is None:
        return None
    if isinstance(attr, tuple):
        return tuple(getattribute_from_module(module, a) for a in attr)
    if hasattr(module, attr):
        return getattr(module, attr)
    MEROAI_module = importlib.import_module("MEROAI")
    if module != MEROAI_module:
        try:
            return getattribute_from_module(MEROAI_module, attr)
        except ValueError:
            raise ValueError(f"Could not find {attr} neither in {module} nor in {MEROAI_module}!")
    else:
        raise ValueError(f"Could not find {attr} in {MEROAI_module}!")
def add_generation_mixin_to_remote_model(model_class):
    if "torch.nn.modules.module.Module" not in str(model_class.__mro__):
        return model_class
    if "GenerationMixin" in str(model_class.__bases__):
        return model_class
    has_custom_generate_in_class = hasattr(model_class, "generate") and "GenerationMixin" not in str(
        getattr(model_class, "generate")
    )
    has_custom_prepare_inputs = hasattr(model_class, "prepare_inputs_for_generation") and "GenerationMixin" not in str(
        getattr(model_class, "prepare_inputs_for_generation")
    )
    if has_custom_generate_in_class or has_custom_prepare_inputs:
        model_class_with_generation_mixin = type(
            model_class.__name__, (model_class, GenerationMixin), {**model_class.__dict__}
        )
        return model_class_with_generation_mixin
    return model_class
class _LazyAutoMapping(OrderedDict[type[PretrainedConfig], _LazyAutoMappingValue]):
    def __init__(self, config_mapping, model_mapping) -> None:
        self._config_mapping = config_mapping
        self._reverse_config_mapping = {v: k for k, v in config_mapping.items()}
        self._model_mapping = model_mapping
        self._model_mapping._model_mapping = self
        self._extra_content = {}
        self._modules = {}
    def __len__(self) -> int:
        common_keys = set(self._config_mapping.keys()).intersection(self._model_mapping.keys())
        return len(common_keys) + len(self._extra_content)
    def __getitem__(self, key: type[PretrainedConfig]) -> _LazyAutoMappingValue:
        if key in self._extra_content:
            return self._extra_content[key]
        model_type = self._reverse_config_mapping[key.__name__]
        if model_type in self._model_mapping:
            model_name = self._model_mapping[model_type]
            return self._load_attr_from_module(model_type, model_name)
        model_types = [k for k, v in self._config_mapping.items() if v == key.__name__]
        for mtype in model_types:
            if mtype in self._model_mapping:
                model_name = self._model_mapping[mtype]
                return self._load_attr_from_module(mtype, model_name)
        raise KeyError(key)
    def _load_attr_from_module(self, model_type, attr):
        module_name = model_type_to_module_name(model_type)
        if module_name not in self._modules:
            self._modules[module_name] = importlib.import_module(f".{module_name}", "MEROAI.models")
        return getattribute_from_module(self._modules[module_name], attr)
    def keys(self) -> list[type[PretrainedConfig]]:
        mapping_keys = [
            self._load_attr_from_module(key, name)
            for key, name in self._config_mapping.items()
            if key in self._model_mapping
        ]
        return mapping_keys + list(self._extra_content.keys())
    def get(self, key: type[PretrainedConfig], default: _T) -> Union[_LazyAutoMappingValue, _T]:
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    def __bool__(self) -> bool:
        return bool(self.keys())
    def values(self) -> list[_LazyAutoMappingValue]:
        mapping_values = [
            self._load_attr_from_module(key, name)
            for key, name in self._model_mapping.items()
            if key in self._config_mapping
        ]
        return mapping_values + list(self._extra_content.values())
    def items(self) -> list[tuple[type[PretrainedConfig], _LazyAutoMappingValue]]:
        mapping_items = [
            (
                self._load_attr_from_module(key, self._config_mapping[key]),
                self._load_attr_from_module(key, self._model_mapping[key]),
            )
            for key in self._model_mapping
            if key in self._config_mapping
        ]
        return mapping_items + list(self._extra_content.items())
    def __iter__(self) -> Iterator[type[PretrainedConfig]]:
        return iter(self.keys())
    def __contains__(self, item: type) -> bool:
        if item in self._extra_content:
            return True
        if not hasattr(item, "__name__") or item.__name__ not in self._reverse_config_mapping:
            return False
        model_type = self._reverse_config_mapping[item.__name__]
        return model_type in self._model_mapping
    def register(self, key: type[PretrainedConfig], value: _LazyAutoMappingValue, exist_ok=False) -> None:
        if hasattr(key, "__name__") and key.__name__ in self._reverse_config_mapping:
            model_type = self._reverse_config_mapping[key.__name__]
            if model_type in self._model_mapping and not exist_ok:
                raise ValueError(f"'{key}' is already used by a MEROAI model.")
        self._extra_content[key] = value
__all__ = ["get_values"]