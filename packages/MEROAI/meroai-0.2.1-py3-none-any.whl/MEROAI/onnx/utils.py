from ctypes import c_float, sizeof
from enum import Enum
from typing import TYPE_CHECKING, Optional, Union
if TYPE_CHECKING:
    from .. import AutoFeatureExtractor, AutoProcessor, AutoTokenizer
class ParameterFormat(Enum):
    Float = c_float
    @property
    def size(self) -> int:
        return sizeof(self.value)
def compute_effective_axis_dimension(dimension: int, fixed_dimension: int, num_token_to_add: int = 0) -> int:
    if dimension <= 0:
        dimension = fixed_dimension
    dimension -= num_token_to_add
    return dimension
def compute_serialized_parameters_size(num_parameters: int, dtype: ParameterFormat) -> int:
    return num_parameters * dtype.size
def get_preprocessor(model_name: str) -> Optional[Union["AutoTokenizer", "AutoFeatureExtractor", "AutoProcessor"]]:
    from .. import AutoFeatureExtractor, AutoProcessor, AutoTokenizer
    try:
        return AutoProcessor.from_pretrained(model_name)
    except (ValueError, OSError, KeyError):
        tokenizer, feature_extractor = None, None
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
        except (OSError, KeyError):
            pass
        try:
            feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        except (OSError, KeyError):
            pass
        if tokenizer is not None and feature_extractor is not None:
            raise ValueError(
                f"Couldn't auto-detect preprocessor for {model_name}. Found both a tokenizer and a feature extractor."
            )
        elif tokenizer is None and feature_extractor is None:
            return None
        elif tokenizer is not None:
            return tokenizer
        else:
            return feature_extractor