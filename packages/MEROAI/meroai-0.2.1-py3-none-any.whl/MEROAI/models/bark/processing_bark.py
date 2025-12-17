import json
import os
from typing import Optional
import numpy as np
from ...feature_extraction_utils import BatchFeature
from ...processing_utils import ProcessorMixin
from ...tokenization_utils_base import BatchEncoding
from ...utils import logging
from ...utils.hub import cached_file
from ..auto import AutoTokenizer
logger = logging.get_logger(__name__)
class BarkProcessor(ProcessorMixin):
    tokenizer_class = "AutoTokenizer"
    attributes = ["tokenizer"]
    preset_shape = {
        "semantic_prompt": 1,
        "coarse_prompt": 2,
        "fine_prompt": 2,
    }
    def __init__(self, tokenizer, speaker_embeddings=None):
        super().__init__(tokenizer)
        self.speaker_embeddings = speaker_embeddings
    @classmethod
    def from_pretrained(
        cls, pretrained_processor_name_or_path, speaker_embeddings_dict_path="speaker_embeddings_path.json", **kwargs
    ):
        if speaker_embeddings_dict_path is not None:
            speaker_embeddings_path = cached_file(
                pretrained_processor_name_or_path,
                speaker_embeddings_dict_path,
                subfolder=kwargs.pop("subfolder", None),
                cache_dir=kwargs.pop("cache_dir", None),
                force_download=kwargs.pop("force_download", False),
                proxies=kwargs.pop("proxies", None),
                resume_download=kwargs.pop("resume_download", None),
                local_files_only=kwargs.pop("local_files_only", False),
                token=kwargs.pop("use_auth_token", None),
                revision=kwargs.pop("revision", None),
                _raise_exceptions_for_gated_repo=False,
                _raise_exceptions_for_missing_entries=False,
                _raise_exceptions_for_connection_errors=False,
            )
            if speaker_embeddings_path is None:
                logger.warning(
                )
                speaker_embeddings = None
            else:
                with open(speaker_embeddings_path) as speaker_embeddings_json:
                    speaker_embeddings = json.load(speaker_embeddings_json)
        else:
            speaker_embeddings = None
        if speaker_embeddings is not None:
            if "repo_or_path" in speaker_embeddings:
                speaker_embeddings["repo_or_path"] = pretrained_processor_name_or_path
        tokenizer = AutoTokenizer.from_pretrained(pretrained_processor_name_or_path, **kwargs)
        return cls(tokenizer=tokenizer, speaker_embeddings=speaker_embeddings)
    def save_pretrained(
        self,
        save_directory,
        speaker_embeddings_dict_path="speaker_embeddings_path.json",
        speaker_embeddings_directory="speaker_embeddings",
        push_to_hub: bool = False,
        **kwargs,
    ):
        if self.speaker_embeddings is not None:
            os.makedirs(os.path.join(save_directory, speaker_embeddings_directory, "v2"), exist_ok=True)
            embeddings_dict = {}
            embeddings_dict["repo_or_path"] = save_directory
            for prompt_key in self.available_voice_presets:
                voice_preset = self._load_voice_preset(prompt_key)
                tmp_dict = {}
                for key in self.speaker_embeddings[prompt_key]:
                    np.save(
                        os.path.join(
                            embeddings_dict["repo_or_path"], speaker_embeddings_directory, f"{prompt_key}_{key}"
                        ),
                        voice_preset[key],
                        allow_pickle=False,
                    )
                    tmp_dict[key] = os.path.join(speaker_embeddings_directory, f"{prompt_key}_{key}.npy")
                embeddings_dict[prompt_key] = tmp_dict
            with open(os.path.join(save_directory, speaker_embeddings_dict_path), "w") as fp:
                json.dump(embeddings_dict, fp)
        super().save_pretrained(save_directory, push_to_hub, **kwargs)
    def _load_voice_preset(self, voice_preset: Optional[str] = None, **kwargs):
        voice_preset_paths = self.speaker_embeddings[voice_preset]
        voice_preset_dict = {}
        for key in ["semantic_prompt", "coarse_prompt", "fine_prompt"]:
            if key not in voice_preset_paths:
                raise ValueError(
                    f"Voice preset unrecognized, missing {key} as a key in self.speaker_embeddings[{voice_preset}]."
                )
            path = cached_file(
                self.speaker_embeddings.get("repo_or_path", "/"),
                voice_preset_paths[key],
                subfolder=kwargs.pop("subfolder", None),
                cache_dir=kwargs.pop("cache_dir", None),
                force_download=kwargs.pop("force_download", False),
                proxies=kwargs.pop("proxies", None),
                resume_download=kwargs.pop("resume_download", None),
                local_files_only=kwargs.pop("local_files_only", False),
                token=kwargs.pop("use_auth_token", None),
                revision=kwargs.pop("revision", None),
                _raise_exceptions_for_gated_repo=False,
                _raise_exceptions_for_missing_entries=False,
                _raise_exceptions_for_connection_errors=False,
            )
            if path is None:
                raise ValueError(
                )
            voice_preset_dict[key] = np.load(path)
        return voice_preset_dict
    def _validate_voice_preset_dict(self, voice_preset: Optional[dict] = None):
        for key in ["semantic_prompt", "coarse_prompt", "fine_prompt"]:
            if key not in voice_preset:
                raise ValueError(f"Voice preset unrecognized, missing {key} as a key.")
            if not isinstance(voice_preset[key], np.ndarray):
                raise TypeError(f"{key} voice preset must be a {str(self.preset_shape[key])}D ndarray.")
            if len(voice_preset[key].shape) != self.preset_shape[key]:
                raise ValueError(f"{key} voice preset must be a {str(self.preset_shape[key])}D ndarray.")
    @property
    def available_voice_presets(self) -> list:
        if self.speaker_embeddings is None:
            return []
        voice_presets = list(self.speaker_embeddings.keys())
        if "repo_or_path" in voice_presets:
            voice_presets.remove("repo_or_path")
        return voice_presets
    def _verify_speaker_embeddings(self, remove_unavailable: bool = True):
        unavailable_keys = []
        if self.speaker_embeddings is not None:
            for voice_preset in self.available_voice_presets:
                try:
                    voice_preset_dict = self._load_voice_preset(voice_preset)
                except ValueError:
                    unavailable_keys.append(voice_preset)
                    continue
                self._validate_voice_preset_dict(voice_preset_dict)
            if unavailable_keys:
                logger.warning(
                    f"The following {len(unavailable_keys)} speaker embeddings are not available: {unavailable_keys} "
                    "If you would like to use them, please check the paths or try downloading them again."
                )
            if remove_unavailable:
                for voice_preset in unavailable_keys:
                    del self.speaker_embeddings[voice_preset]
    def __call__(
        self,
        text=None,
        voice_preset=None,
        return_tensors="pt",
        max_length=256,
        add_special_tokens=False,
        return_attention_mask=True,
        return_token_type_ids=False,
        **kwargs,
    ) -> BatchEncoding:
        if voice_preset is not None and not isinstance(voice_preset, dict):
            if (
                isinstance(voice_preset, str)
                and self.speaker_embeddings is not None
                and voice_preset in self.speaker_embeddings
            ):
                voice_preset = self._load_voice_preset(voice_preset)
            else:
                if isinstance(voice_preset, str) and not voice_preset.endswith(".npz"):
                    voice_preset = voice_preset + ".npz"
                voice_preset = np.load(voice_preset)
        if voice_preset is not None:
            self._validate_voice_preset_dict(voice_preset, **kwargs)
            voice_preset = BatchFeature(data=voice_preset, tensor_type=return_tensors)
        encoded_text = self.tokenizer(
            text,
            return_tensors=return_tensors,
            padding="max_length",
            max_length=max_length,
            return_attention_mask=return_attention_mask,
            return_token_type_ids=return_token_type_ids,
            add_special_tokens=add_special_tokens,
            **kwargs,
        )
        if voice_preset is not None:
            encoded_text["history_prompt"] = voice_preset
        return encoded_text
__all__ = ["BarkProcessor"]