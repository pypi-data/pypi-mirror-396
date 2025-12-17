import subprocess
from typing import Any, Union
import numpy as np
import requests
from ..utils import add_end_docstrings, is_torch_available, is_torchaudio_available, is_torchcodec_available, logging
from .base import Pipeline, build_pipeline_init_args
if is_torch_available():
    from ..models.auto.modeling_auto import MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING_NAMES
logger = logging.get_logger(__name__)
def ffmpeg_read(bpayload: bytes, sampling_rate: int) -> np.ndarray:
    ar = f"{sampling_rate}"
    ac = "1"
    format_for_conversion = "f32le"
    ffmpeg_command = [
        "ffmpeg",
        "-i",
        "pipe:0",
        "-ac",
        ac,
        "-ar",
        ar,
        "-f",
        format_for_conversion,
        "-hide_banner",
        "-loglevel",
        "quiet",
        "pipe:1",
    ]
    try:
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise ValueError("ffmpeg was not found but is required to load audio files from filename")
    output_stream = ffmpeg_process.communicate(bpayload)
    out_bytes = output_stream[0]
    audio = np.frombuffer(out_bytes, np.float32)
    if audio.shape[0] == 0:
        raise ValueError("Malformed soundfile")
    return audio
@add_end_docstrings(build_pipeline_init_args(has_feature_extractor=True))
class AudioClassificationPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = False
    _load_feature_extractor = True
    _load_tokenizer = False
    def __init__(self, *args, **kwargs):
        if "top_k" in kwargs and kwargs["top_k"] is None:
            kwargs["top_k"] = None
        elif "top_k" not in kwargs:
            kwargs["top_k"] = 5
        super().__init__(*args, **kwargs)
        if self.framework != "pt":
            raise ValueError(f"The {self.__class__} is only available in PyTorch.")
        self.check_model_type(MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING_NAMES)
    def __call__(self, inputs: Union[np.ndarray, bytes, str, dict], **kwargs: Any) -> list[dict[str, Any]]:
        return super().__call__(inputs, **kwargs)
    def _sanitize_parameters(self, top_k=None, function_to_apply=None, **kwargs):
        postprocess_params = {}
        if top_k is None:
            postprocess_params["top_k"] = self.model.config.num_labels
        else:
            if top_k > self.model.config.num_labels:
                top_k = self.model.config.num_labels
            postprocess_params["top_k"] = top_k
        if function_to_apply is not None:
            if function_to_apply not in ["softmax", "sigmoid", "none"]:
                raise ValueError(
                    f"Invalid value for `function_to_apply`: {function_to_apply}. "
                    "Valid options are ['softmax', 'sigmoid', 'none']"
                )
            postprocess_params["function_to_apply"] = function_to_apply
        else:
            postprocess_params["function_to_apply"] = "softmax"
        return {}, {}, postprocess_params
    def preprocess(self, inputs):
        if isinstance(inputs, str):
            if inputs.startswith("http://") or inputs.startswith("https://"):
                inputs = requests.get(inputs).content
            else:
                with open(inputs, "rb") as f:
                    inputs = f.read()
        if isinstance(inputs, bytes):
            inputs = ffmpeg_read(inputs, self.feature_extractor.sampling_rate)
        if is_torch_available():
            import torch
            if isinstance(inputs, torch.Tensor):
                inputs = inputs.cpu().numpy()
        if is_torchcodec_available():
            import torch
            import torchcodec
            if isinstance(inputs, torchcodec.decoders.AudioDecoder):
                _audio_samples = inputs.get_all_samples()
                _array = _audio_samples.data
                inputs = {"array": _array, "sampling_rate": _audio_samples.sample_rate}
        if isinstance(inputs, dict):
            inputs = inputs.copy()
            if not ("sampling_rate" in inputs and ("raw" in inputs or "array" in inputs)):
                raise ValueError(
                    "When passing a dictionary to AudioClassificationPipeline, the dict needs to contain a "
                    '"raw" key containing the numpy array or torch tensor representing the audio and a "sampling_rate" key, '
                    "containing the sampling_rate associated with that array"
                )
            _inputs = inputs.pop("raw", None)
            if _inputs is None:
                inputs.pop("path", None)
                _inputs = inputs.pop("array", None)
            in_sampling_rate = inputs.pop("sampling_rate")
            inputs = _inputs
            if in_sampling_rate != self.feature_extractor.sampling_rate:
                import torch
                if is_torchaudio_available():
                    from torchaudio import functional as F
                else:
                    raise ImportError(
                        "torchaudio is required to resample audio samples in AudioClassificationPipeline. "
                        "The torchaudio package can be installed through: `pip install torchaudio`."
                    )
                inputs = F.resample(
                    torch.from_numpy(inputs) if isinstance(inputs, np.ndarray) else inputs,
                    in_sampling_rate,
                    self.feature_extractor.sampling_rate,
                ).numpy()
        if not isinstance(inputs, np.ndarray):
            raise TypeError("We expect a numpy ndarray or torch tensor as input")
        if len(inputs.shape) != 1:
            raise ValueError("We expect a single channel audio input for AudioClassificationPipeline")
        processed = self.feature_extractor(
            inputs, sampling_rate=self.feature_extractor.sampling_rate, return_tensors="pt"
        )
        if self.dtype is not None:
            processed = processed.to(dtype=self.dtype)
        return processed
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        return model_outputs
    def postprocess(self, model_outputs, top_k=5, function_to_apply="softmax"):
        if function_to_apply == "softmax":
            probs = model_outputs.logits[0].softmax(-1)
        elif function_to_apply == "sigmoid":
            probs = model_outputs.logits[0].sigmoid()
        else:
            probs = model_outputs.logits[0]
        scores, ids = probs.topk(top_k)
        scores = scores.tolist()
        ids = ids.tolist()
        labels = [{"score": score, "label": self.model.config.id2label[_id]} for score, _id in zip(scores, ids)]
        return labels