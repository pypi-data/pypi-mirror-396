from typing import Any, Union, overload
from ..generation import GenerationConfig
from ..utils import is_torch_available
from .base import Pipeline
if is_torch_available():
    import torch
    from ..models.auto.modeling_auto import MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING
    from ..models.speecht5.modeling_speecht5 import SpeechT5HifiGan
DEFAULT_VOCODER_ID = "microsoft/speecht5_hifigan"
class TextToAudioPipeline(Pipeline):
    _load_processor = True
    _pipeline_calls_generate = True
    _load_processor = False
    _load_image_processor = False
    _load_feature_extractor = False
    _load_tokenizer = True
    _default_generation_config = GenerationConfig(
        max_new_tokens=256,
    )
    def __init__(self, *args, vocoder=None, sampling_rate=None, no_processor=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.no_processor = no_processor
        if self.framework == "tf":
            raise ValueError("The TextToAudioPipeline is only available in PyTorch.")
        self.vocoder = None
        if self.model.__class__ in MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING.values():
            self.vocoder = (
                SpeechT5HifiGan.from_pretrained(DEFAULT_VOCODER_ID).to(self.model.device)
                if vocoder is None
                else vocoder
            )
        self.sampling_rate = sampling_rate
        if self.vocoder is not None:
            self.sampling_rate = self.vocoder.config.sampling_rate
        if self.sampling_rate is None:
            config = self.model.config
            gen_config = self.model.__dict__.get("generation_config", None)
            if gen_config is not None:
                config.update(gen_config.to_dict())
            for sampling_rate_name in ["sample_rate", "sampling_rate"]:
                sampling_rate = getattr(config, sampling_rate_name, None)
                if sampling_rate is not None:
                    self.sampling_rate = sampling_rate
                elif getattr(config, "codec_config", None) is not None:
                    sampling_rate = getattr(config.codec_config, sampling_rate_name, None)
                    if sampling_rate is not None:
                        self.sampling_rate = sampling_rate
        if self.sampling_rate is None and not self.no_processor and hasattr(self.processor, "feature_extractor"):
            self.sampling_rate = self.processor.feature_extractor.sampling_rate
    def preprocess(self, text, **kwargs):
        if isinstance(text, str):
            text = [text]
        if self.model.config.model_type == "bark":
            new_kwargs = {
                "max_length": self.generation_config.semantic_config.get("max_input_semantic_length", 256),
                "add_special_tokens": False,
                "return_attention_mask": True,
                "return_token_type_ids": False,
                "padding": "max_length",
            }
            new_kwargs.update(kwargs)
            kwargs = new_kwargs
        preprocessor = self.tokenizer if self.no_processor else self.processor
        output = preprocessor(text, **kwargs, return_tensors="pt")
        return output
    def _forward(self, model_inputs, **kwargs):
        kwargs = self._ensure_tensor_on_device(kwargs, device=self.device)
        forward_params = kwargs["forward_params"]
        generate_kwargs = kwargs["generate_kwargs"]
        if self.model.can_generate():
            generate_kwargs = self._ensure_tensor_on_device(generate_kwargs, device=self.device)
            if "generation_config" not in generate_kwargs:
                generate_kwargs["generation_config"] = self.generation_config
            forward_params.update(generate_kwargs)
            output = self.model.generate(**model_inputs, **forward_params)
        else:
            if len(generate_kwargs):
                raise ValueError(
                    "You're using the `TextToAudioPipeline` with a forward-only model, but `generate_kwargs` is non "
                    "empty. For forward-only TTA models, please use `forward_params` instead of `generate_kwargs`. "
                    f"For reference, the `generate_kwargs` used here are: {generate_kwargs.keys()}"
                )
            output = self.model(**model_inputs, **forward_params)[0]
        if self.vocoder is not None:
            output = self.vocoder(output)
        return output
    @overload
    def __call__(self, text_inputs: str, **forward_params: Any) -> dict[str, Any]: ...
    @overload
    def __call__(self, text_inputs: list[str], **forward_params: Any) -> list[dict[str, Any]]: ...
    def __call__(
        self, text_inputs: Union[str, list[str]], **forward_params
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        return super().__call__(text_inputs, **forward_params)
    def _sanitize_parameters(
        self,
        preprocess_params=None,
        forward_params=None,
        generate_kwargs=None,
    ):
        if getattr(self, "assistant_model", None) is not None:
            generate_kwargs["assistant_model"] = self.assistant_model
        if getattr(self, "assistant_tokenizer", None) is not None:
            generate_kwargs["tokenizer"] = self.tokenizer
            generate_kwargs["assistant_tokenizer"] = self.assistant_tokenizer
        params = {
            "forward_params": forward_params if forward_params else {},
            "generate_kwargs": generate_kwargs if generate_kwargs else {},
        }
        if preprocess_params is None:
            preprocess_params = {}
        postprocess_params = {}
        return preprocess_params, params, postprocess_params
    def postprocess(self, audio):
        output_dict = {}
        if self.model.config.model_type == "csm":
            waveform_key = "audio"
        else:
            waveform_key = "waveform"
        if self.no_processor:
            if isinstance(audio, dict):
                waveform = audio[waveform_key]
            elif isinstance(audio, tuple):
                waveform = audio[0]
            else:
                waveform = audio
        else:
            waveform = self.processor.decode(audio)
        if isinstance(audio, list):
            output_dict["audio"] = [el.to(device="cpu", dtype=torch.float).numpy() for el in waveform]
        else:
            output_dict["audio"] = waveform.to(device="cpu", dtype=torch.float).numpy()
        output_dict["sampling_rate"] = self.sampling_rate
        return output_dict