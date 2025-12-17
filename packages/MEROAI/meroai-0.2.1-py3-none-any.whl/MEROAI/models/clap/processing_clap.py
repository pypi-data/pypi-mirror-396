from typing import Optional, Union
from ...audio_utils import AudioInput
from ...processing_utils import ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils_base import PreTokenizedInput, TextInput
from ...utils import logging
from ...utils.deprecation import deprecate_kwarg
logger = logging.get_logger(__name__)
class ClapProcessor(ProcessorMixin):
    feature_extractor_class = "ClapFeatureExtractor"
    tokenizer_class = ("RobertaTokenizer", "RobertaTokenizerFast")
    def __init__(self, feature_extractor, tokenizer):
        super().__init__(feature_extractor, tokenizer)
    @deprecate_kwarg("audios", version="v4.59.0", new_name="audio")
    def __call__(
        self,
        text: Optional[Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]]] = None,
        audios: Optional[AudioInput] = None,
        audio: Optional[AudioInput] = None,
        **kwargs: Unpack[ProcessingKwargs],
    ):
        if audios is not None and audio is None:
            logger.warning(
                "Using `audios` keyword argument is deprecated when calling ClapProcessor, instead use `audio`."
            )
            audio = audios
        return super().__call__(text=text, audio=audio, **kwargs)
__all__ = ["ClapProcessor"]