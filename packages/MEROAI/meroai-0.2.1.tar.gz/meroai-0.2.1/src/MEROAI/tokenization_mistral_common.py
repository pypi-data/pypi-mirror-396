import os
import shutil
import warnings
from collections.abc import Mapping, Sized
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union, overload
import numpy as np
from MEROAI.audio_utils import load_audio_as
from MEROAI.tokenization_utils_base import (
    LARGE_INTEGER,
    VERY_LARGE_INTEGER,
    BatchEncoding,
    EncodedInput,
    PreTokenizedInput,
    PreTrainedTokenizerBase,
    TextInput,
    TruncationStrategy,
)
from MEROAI.utils import PaddingStrategy, TensorType, add_end_docstrings, logging, to_py_obj
from MEROAI.utils.generic import is_torch_tensor
from MEROAI.utils.hub import PushToHubMixin
from MEROAI.utils.import_utils import is_mistral_common_available, is_torch_available, requires
if is_mistral_common_available():
    from mistral_common.protocol.instruct.request import ChatCompletionRequest
    from mistral_common.protocol.instruct.validator import ValidationMode
    from mistral_common.tokens.tokenizers.base import SpecialTokenPolicy, TokenizerVersion
    from mistral_common.tokens.tokenizers.image import MultiModalVersion
    from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
    from mistral_common.tokens.tokenizers.tekken import Tekkenizer
    from mistral_common.tokens.tokenizers.utils import download_tokenizer_from_hf_hub
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
class MistralTokenizerType(str, Enum):
    spm = "spm"
    tekken = "tekken"
@requires(backends=("mistral-common",))
class MistralCommonTokenizer(PushToHubMixin):
    model_input_names: list[str] = ["input_ids", "attention_mask"]
    padding_side: str = "left"
    truncation_side: str = "right"
    def __init__(
        self,
        tokenizer_path: Union[str, os.PathLike, Path],
        mode: ValidationMode = ValidationMode.test,
        model_max_length: int = VERY_LARGE_INTEGER,
        padding_side: str = "left",
        truncation_side: str = "right",
        model_input_names: Optional[list[str]] = None,
        clean_up_tokenization_spaces: bool = False,
        **kwargs,
    ):
        if kwargs:
            raise ValueError(f"Kwargs {list(kwargs.keys())} are not supported to init `MistralCommonTokenizer`.")
        self._tokenizer_path = Path(tokenizer_path)
        self.tokenizer: MistralTokenizer = MistralTokenizer.from_file(str(self._tokenizer_path), mode=mode)
        self._tokenizer_type = (
            MistralTokenizerType.tekken
            if isinstance(self.tokenizer.instruct_tokenizer.tokenizer, Tekkenizer)
            else MistralTokenizerType.spm
        )
        self.truncation_side = truncation_side
        self.padding_side = padding_side
        self.model_max_length = model_max_length
        self.cleanup_tokenization_spaces = clean_up_tokenization_spaces
        self.deprecation_warnings = {}
        if model_input_names is not None:
            if (
                not isinstance(model_input_names, (list, tuple))
                and len(model_input_names) == 0
                and not all(isinstance(i, str) for i in model_input_names)
            ):
                raise ValueError(
                    "`model_input_names` should be a non-empty list or tuple of str but got an empty value."
                )
            self.model_input_names = model_input_names
        self._cache_get_vocab: Optional[dict[str, int]] = None
    @property
    def bos_token_id(self) -> int:
        return self.tokenizer.instruct_tokenizer.tokenizer.bos_id
    @property
    def eos_token_id(self) -> int:
        return self.tokenizer.instruct_tokenizer.tokenizer.eos_id
    @property
    def unk_token_id(self) -> int:
        return self.tokenizer.instruct_tokenizer.tokenizer.unk_id
    @property
    def pad_token_id(self) -> int:
        return self.tokenizer.instruct_tokenizer.tokenizer.pad_id
    @property
    def bos_token(self) -> str:
        return self.convert_ids_to_tokens(self.bos_token_id)
    @property
    def eos_token(self) -> str:
        return self.convert_ids_to_tokens(self.eos_token_id)
    @property
    def unk_token(self) -> str:
        return self.convert_ids_to_tokens(self.unk_token_id)
    @property
    def pad_token(self) -> str:
        return self.convert_ids_to_tokens(self.pad_token_id)
    @property
    def vocab_size(self) -> int:
        return self.tokenizer.instruct_tokenizer.tokenizer.n_words
    def get_vocab(self) -> dict[str, int]:
        if self._cache_get_vocab is None:
            self._cache_get_vocab = {
                token: idx for idx, token in enumerate(self.tokenizer.instruct_tokenizer.tokenizer.vocab())
            }
        return self._cache_get_vocab
    def __len__(self):
        return self.vocab_size
    @add_end_docstrings(
        ENCODE_KWARGS_DOCSTRING,
,
,
    )
    def encode(
        self,
        text: Union[TextInput, EncodedInput],
        text_pair: None = None,
        add_special_tokens: bool = True,
        padding: Union[bool, str, PaddingStrategy] = False,
        truncation: Union[bool, str, TruncationStrategy, None] = None,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        verbose: bool = True,
        **kwargs,
    ) -> list[int]:
        if kwargs:
            raise ValueError(f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.encode`.")
        if text_pair:
            raise ValueError("`MistralCommonTokenizer.encode` does not support `text_pair`.")
        padding_strategy, truncation_strategy, max_length, _ = self._get_padding_truncation_strategies(
            padding=padding,
            truncation=truncation,
            max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            verbose=verbose,
        )
        encoded_inputs = self._encode_plus(
            text,
            add_special_tokens=add_special_tokens,
            padding_strategy=padding_strategy,
            truncation_strategy=truncation_strategy,
            max_length=max_length,
            stride=stride,
            pad_to_multiple_of=pad_to_multiple_of,
            padding_side=padding_side,
            return_tensors=return_tensors,
            return_attention_mask=False,
            return_overflowing_tokens=False,
            return_special_tokens_mask=False,
            return_length=False,
            verbose=verbose,
        )
        return encoded_inputs["input_ids"]
    def decode(
        self,
        token_ids: Union[int, list[int], np.ndarray, "torch.Tensor"],
        skip_special_tokens: bool = False,
        clean_up_tokenization_spaces: Optional[bool] = None,
        **kwargs,
    ) -> str:
        if kwargs:
            raise ValueError(f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.decode`.")
        clean_up_tokenization_spaces = clean_up_tokenization_spaces or self.cleanup_tokenization_spaces
        token_ids = to_py_obj(token_ids)
        special_token_policy = SpecialTokenPolicy.IGNORE if skip_special_tokens else SpecialTokenPolicy.KEEP
        decoded_string = self.tokenizer.decode(token_ids, special_token_policy=special_token_policy)
        if clean_up_tokenization_spaces:
            decoded_string = PreTrainedTokenizerBase.clean_up_tokenization(decoded_string)
        return decoded_string
    def batch_decode(
        self,
        sequences: Union[list[int], list[list[int]], np.ndarray, "torch.Tensor"],
        skip_special_tokens: bool = False,
        clean_up_tokenization_spaces: Optional[bool] = None,
        **kwargs,
    ) -> list[str]:
        return [
            self.decode(
                seq,
                skip_special_tokens=skip_special_tokens,
                clean_up_tokenization_spaces=clean_up_tokenization_spaces,
                **kwargs,
            )
            for seq in sequences
        ]
    def _is_control_token(self, token_id: int) -> bool:
        if self._tokenizer_type == MistralTokenizerType.spm:
            return token_id in self.tokenizer.instruct_tokenizer.tokenizer._control_tokens()
        elif self._tokenizer_type == MistralTokenizerType.tekken:
            return token_id < self.tokenizer.instruct_tokenizer.tokenizer.num_special_tokens
        else:
            raise ValueError(f"Unknown tokenizer type: {self._tokenizer_type}")
    @overload
    def convert_ids_to_tokens(self, ids: int, skip_special_tokens: bool = False) -> str: ...
    @overload
    def convert_ids_to_tokens(self, ids: list[int], skip_special_tokens: bool = False) -> list[str]: ...
    def convert_ids_to_tokens(
        self, ids: Union[int, list[int]], skip_special_tokens: bool = False
    ) -> Union[str, list[str]]:
        if isinstance(ids, int):
            one_token = True
            ids = [ids]
        else:
            one_token = False
        tokens: list[str] = []
        for token_id in ids:
            if self._is_control_token(token_id) and skip_special_tokens:
                continue
            tokens.append(self.tokenizer.instruct_tokenizer.tokenizer.id_to_piece(token_id))
        if one_token:
            if tokens == []:
                raise ValueError(f"Invalid token id {ids}.")
            return tokens[0]
        return tokens
    def _piece_to_id(self, piece: str) -> int:
        if self._tokenizer_type == MistralTokenizerType.spm:
            return self.tokenizer.instruct_tokenizer.tokenizer._model.piece_to_id(piece)
        elif self._tokenizer_type == MistralTokenizerType.tekken:
            pieces = self.tokenizer.instruct_tokenizer.tokenizer._model.encode(
                piece, allowed_special="all", disallowed_special=set()
            )
            assert len(pieces) == 1, f"Expected to decode 1 token, got {len(pieces)}"
            return pieces[0]
        else:
            raise ValueError(f"Unknown tokenizer type: {self._tokenizer_type}")
    def convert_tokens_to_ids(self, tokens: Union[str, list[str]]) -> Union[int, list[int]]:
        if isinstance(tokens, str):
            one_token = True
            tokens = [tokens]
        else:
            one_token = False
        ids: list[int] = []
        for token in tokens:
            ids.append(self._piece_to_id(token))
        if one_token:
            return ids[0]
        return ids
    def _text_to_ids(self, text: TextInput, add_special_tokens: bool) -> list[int]:
        tokens_ids = self.tokenizer.instruct_tokenizer.tokenizer.encode(
            text, bos=add_special_tokens, eos=add_special_tokens
        )
        return tokens_ids
    def tokenize(self, text: TextInput, **kwargs) -> list[str]:
        if kwargs:
            raise ValueError(f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.tokenize`.")
        return self.convert_ids_to_tokens(self._text_to_ids(text, add_special_tokens=False), skip_special_tokens=False)
    def _encode_plus(
        self,
        text: Union[TextInput, EncodedInput],
        add_special_tokens: bool = True,
        padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
        truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_attention_mask: Optional[bool] = None,
        return_overflowing_tokens: bool = False,
        return_special_tokens_mask: bool = False,
        return_length: bool = False,
        verbose: bool = True,
        **kwargs,
    ) -> BatchEncoding:
        if kwargs:
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer._encode_plus`."
            )
        def get_input_ids(text):
            if isinstance(text, str):
                return self._text_to_ids(text, add_special_tokens)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int):
                return text
            else:
                raise ValueError(f"Input {text} is not valid. Should be a string, or a list/tuple of integers.")
        ids = get_input_ids(text)
        return self.prepare_for_model(
            ids,
            add_special_tokens=add_special_tokens,
            padding=padding_strategy.value,
            truncation=truncation_strategy.value,
            max_length=max_length,
            stride=stride,
            pad_to_multiple_of=pad_to_multiple_of,
            padding_side=padding_side,
            return_tensors=return_tensors,
            prepend_batch_axis=True,
            return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask,
            return_length=return_length,
            verbose=verbose,
        )
    def _batch_encode_plus(
        self,
        batch_text: Union[
            list[TextInput],
            list[EncodedInput],
        ],
        add_special_tokens: bool = True,
        padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
        truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_attention_mask: Optional[bool] = None,
        return_overflowing_tokens: bool = False,
        return_special_tokens_mask: bool = False,
        return_offsets_mapping: bool = False,
        return_length: bool = False,
        verbose: bool = True,
        **kwargs,
    ) -> BatchEncoding:
        def get_input_ids(text):
            if isinstance(text, str):
                return self._text_to_ids(text, add_special_tokens)
            elif isinstance(text, (list, tuple)) and len(text) > 0 and isinstance(text[0], int):
                return text
            else:
                raise ValueError("Input is not valid. Should be a string or a list/tuple of integers.")
        if return_offsets_mapping:
            raise NotImplementedError(
                "return_offset_mapping is not available when using Python tokenizers. "
                "To use this feature, change your tokenizer to one deriving from "
                "MEROAI.PreTrainedTokenizerFast."
            )
        input_ids = []
        for ids in batch_text:
            input_ids.append(get_input_ids(ids))
        batch_outputs = self._batch_prepare_for_model(
            input_ids,
            add_special_tokens=add_special_tokens,
            padding_strategy=padding_strategy,
            truncation_strategy=truncation_strategy,
            max_length=max_length,
            stride=stride,
            pad_to_multiple_of=pad_to_multiple_of,
            padding_side=padding_side,
            return_attention_mask=return_attention_mask,
            return_overflowing_tokens=return_overflowing_tokens,
            return_special_tokens_mask=return_special_tokens_mask,
            return_length=return_length,
            return_tensors=return_tensors,
            verbose=verbose,
        )
        return BatchEncoding(batch_outputs)
    def _all_special_ids(self) -> set[int]:
        if self._tokenizer_type == MistralTokenizerType.tekken:
            return {t["rank"] for t in self.tokenizer.instruct_tokenizer.tokenizer._all_special_tokens}
        elif self._tokenizer_type == MistralTokenizerType.spm:
            return self.tokenizer.instruct_tokenizer.tokenizer._control_tokens()
        else:
            raise ValueError(f"Unknown tokenizer type: {self._tokenizer_type}")
    def get_special_tokens_mask(
        self, token_ids_0: list, token_ids_1: None = None, already_has_special_tokens: bool = False
    ) -> list[int]:
        if token_ids_1 is not None:
            raise ValueError(
                "`token_ids_1` is not supported by `MistralCommonTokenizer` and should be `None`, kept for compatibility."
            )
        if already_has_special_tokens:
            raise ValueError(
                "`already_has_special_tokens` is not supported by `MistralCommonTokenizer` and should be `False`."
            )
        all_special_ids = self._all_special_ids()
        special_tokens_mask = [1 if token in all_special_ids else 0 for token in token_ids_0]
        return special_tokens_mask
    def _batch_prepare_for_model(
        self,
        batch_ids: list[Union[PreTokenizedInput, list[int]]],
        add_special_tokens: bool = True,
        padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
        truncation_strategy: TruncationStrategy = TruncationStrategy.DO_NOT_TRUNCATE,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[str] = None,
        return_attention_mask: Optional[bool] = None,
        return_overflowing_tokens: bool = False,
        return_special_tokens_mask: bool = False,
        return_length: bool = False,
        verbose: bool = True,
    ) -> BatchEncoding:
        batch_outputs = {}
        for ids in batch_ids:
            outputs = self.prepare_for_model(
                ids,
                add_special_tokens=add_special_tokens,
                padding=PaddingStrategy.DO_NOT_PAD.value,
                truncation=truncation_strategy.value,
                max_length=max_length,
                stride=stride,
                pad_to_multiple_of=None,
                padding_side=None,
                return_attention_mask=False,
                return_overflowing_tokens=return_overflowing_tokens,
                return_special_tokens_mask=return_special_tokens_mask,
                return_length=return_length,
                return_tensors=None,
                prepend_batch_axis=False,
                verbose=verbose,
            )
            for key, value in outputs.items():
                if key not in batch_outputs:
                    batch_outputs[key] = []
                batch_outputs[key].append(value)
        batch_outputs = self.pad(
            batch_outputs,
            padding=padding_strategy.value,
            max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            padding_side=padding_side,
            return_attention_mask=return_attention_mask,
        )
        batch_outputs = BatchEncoding(batch_outputs, tensor_type=return_tensors)
        return batch_outputs
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def prepare_for_model(
        self,
        ids: list[int],
        pair_ids: None = None,
        add_special_tokens: bool = True,
        padding: Union[bool, str, PaddingStrategy] = False,
        truncation: Union[bool, str, TruncationStrategy, None] = None,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_attention_mask: Optional[bool] = None,
        return_overflowing_tokens: bool = False,
        return_special_tokens_mask: bool = False,
        return_length: bool = False,
        verbose: bool = True,
        prepend_batch_axis: bool = False,
        **kwargs,
    ) -> BatchEncoding:
        if pair_ids is not None:
            raise ValueError(
                "`pair_ids` is not supported by `MistralCommonTokenizer` and should be `None`, kept for compatibility."
            )
        if kwargs:
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.prepare_for_model`."
            )
        padding_strategy, truncation_strategy, max_length, _ = self._get_padding_truncation_strategies(
            padding=padding,
            truncation=truncation,
            max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            verbose=verbose,
        )
        len_ids = len(ids)
        if return_attention_mask is None:
            return_attention_mask = "attention_mask" in self.model_input_names
        encoded_inputs = {}
        overflowing_tokens = []
        if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE and max_length and len_ids > max_length:
            ids, _, overflowing_tokens = self.truncate_sequences(
                ids,
                num_tokens_to_remove=len_ids - max_length,
                truncation_strategy=truncation_strategy,
                stride=stride,
            )
        if return_overflowing_tokens:
            encoded_inputs["overflowing_tokens"] = overflowing_tokens
            encoded_inputs["num_truncated_tokens"] = len_ids - max_length
        encoded_inputs[self.model_input_names[0]] = ids
        if return_special_tokens_mask:
            if add_special_tokens:
                encoded_inputs["special_tokens_mask"] = self.get_special_tokens_mask(ids, None)
            else:
                encoded_inputs["special_tokens_mask"] = [0] * len(ids)
        if padding_strategy != PaddingStrategy.DO_NOT_PAD or return_attention_mask:
            encoded_inputs = self.pad(
                encoded_inputs,
                max_length=max_length,
                padding=padding_strategy.value,
                pad_to_multiple_of=pad_to_multiple_of,
                padding_side=padding_side,
                return_attention_mask=return_attention_mask,
            )
        if return_length:
            encoded_inputs["length"] = len(encoded_inputs["input_ids"])
        batch_outputs = BatchEncoding(
            encoded_inputs, tensor_type=return_tensors, prepend_batch_axis=prepend_batch_axis
        )
        return batch_outputs
    def _get_padding_truncation_strategies(
        self,
        padding: Union[str, PaddingStrategy, bool] = False,
        truncation: Optional[Union[str, TruncationStrategy, bool]] = None,
        max_length: Optional[int] = None,
        pad_to_multiple_of: Optional[int] = None,
        verbose: bool = True,
        **kwargs,
    ):
        if max_length is not None and padding is False and truncation is None:
            if verbose:
                if not self.deprecation_warnings.get("Truncation-not-explicitly-activated", False):
                    logger.warning(
                        "Truncation was not explicitly activated but `max_length` is provided a specific value, please"
                        " use `truncation=True` to explicitly truncate examples to max length. Defaulting to"
                        " 'longest_first' truncation strategy. If you encode pairs of sequences (GLUE-style) with the"
                        " tokenizer you can select this strategy more precisely by providing a specific strategy to"
                        " `truncation`."
                    )
                self.deprecation_warnings["Truncation-not-explicitly-activated"] = True
            truncation = "longest_first"
        if padding is not False:
            if padding is True:
                if verbose:
                    if max_length is not None and (
                        truncation is None or truncation is False or truncation == "do_not_truncate"
                    ):
                        warnings.warn(
                            "`max_length` is ignored when `padding`=`True` and there is no truncation strategy. "
                            "To pad to max length, use `padding='max_length'`."
                        )
                padding_strategy = PaddingStrategy.LONGEST
            elif not isinstance(padding, PaddingStrategy):
                padding_strategy = PaddingStrategy(padding)
            elif isinstance(padding, PaddingStrategy):
                padding_strategy = padding
        else:
            padding_strategy = PaddingStrategy.DO_NOT_PAD
        if truncation is not False and truncation is not None:
            if truncation is True:
                truncation_strategy = (
                    TruncationStrategy.LONGEST_FIRST
                )
            elif not isinstance(truncation, TruncationStrategy):
                truncation_strategy = TruncationStrategy(truncation)
            elif isinstance(truncation, TruncationStrategy):
                truncation_strategy = truncation
            if truncation in [TruncationStrategy.ONLY_FIRST, TruncationStrategy.ONLY_SECOND]:
                raise ValueError(
                    "Truncation strategy `only_first` and `only_second` are not supported by `MistralCommonTokenizer`."
                )
        else:
            truncation_strategy = TruncationStrategy.DO_NOT_TRUNCATE
        if max_length is None:
            if padding_strategy == PaddingStrategy.MAX_LENGTH:
                if self.model_max_length > LARGE_INTEGER:
                    if verbose:
                        if not self.deprecation_warnings.get("Asking-to-pad-to-max_length", False):
                            logger.warning(
                                "Asking to pad to max_length but no maximum length is provided and the model has no"
                                " predefined maximum length. Default to no padding."
                            )
                        self.deprecation_warnings["Asking-to-pad-to-max_length"] = True
                    padding_strategy = PaddingStrategy.DO_NOT_PAD
                else:
                    max_length = self.model_max_length
            if truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE:
                if self.model_max_length > LARGE_INTEGER:
                    if verbose:
                        if not self.deprecation_warnings.get("Asking-to-truncate-to-max_length", False):
                            logger.warning(
                                "Asking to truncate to max_length but no maximum length is provided and the model has"
                                " no predefined maximum length. Default to no truncation."
                            )
                        self.deprecation_warnings["Asking-to-truncate-to-max_length"] = True
                    truncation_strategy = TruncationStrategy.DO_NOT_TRUNCATE
                else:
                    max_length = self.model_max_length
        if padding_strategy != PaddingStrategy.DO_NOT_PAD and (self.pad_token is None or self.pad_token_id < 0):
            raise ValueError(
                "Asking to pad but the tokenizer does not have a padding token. "
                "Please select a token to use as `pad_token` `(tokenizer.pad_token = tokenizer.eos_token e.g.)` "
                "or add a new pad token via `tokenizer.add_special_tokens({'pad_token': '[PAD]'})`."
            )
        if (
            truncation_strategy != TruncationStrategy.DO_NOT_TRUNCATE
            and padding_strategy != PaddingStrategy.DO_NOT_PAD
            and pad_to_multiple_of is not None
            and max_length is not None
            and (max_length % pad_to_multiple_of != 0)
        ):
            raise ValueError(
                "Truncation and padding are both activated but "
                f"truncation length ({max_length}) is not a multiple of pad_to_multiple_of ({pad_to_multiple_of})."
            )
        return padding_strategy, truncation_strategy, max_length, kwargs
    def _pad(
        self,
        encoded_inputs: Union[dict[str, EncodedInput], BatchEncoding],
        max_length: Optional[int] = None,
        padding_strategy: PaddingStrategy = PaddingStrategy.DO_NOT_PAD,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_attention_mask: Optional[bool] = None,
    ) -> dict:
        if return_attention_mask is None:
            return_attention_mask = "attention_mask" in self.model_input_names
        required_input = encoded_inputs[self.model_input_names[0]]
        if padding_strategy == PaddingStrategy.LONGEST:
            max_length = len(required_input)
        if max_length is not None and pad_to_multiple_of is not None and (max_length % pad_to_multiple_of != 0):
            max_length = ((max_length // pad_to_multiple_of) + 1) * pad_to_multiple_of
        needs_to_be_padded = padding_strategy != PaddingStrategy.DO_NOT_PAD and len(required_input) != max_length
        if return_attention_mask and "attention_mask" not in encoded_inputs:
            encoded_inputs["attention_mask"] = [1] * len(required_input)
        if needs_to_be_padded:
            difference = max_length - len(required_input)
            padding_side = padding_side if padding_side is not None else self.padding_side
            if padding_side == "right":
                if return_attention_mask:
                    encoded_inputs["attention_mask"] = encoded_inputs["attention_mask"] + [0] * difference
                if "special_tokens_mask" in encoded_inputs:
                    encoded_inputs["special_tokens_mask"] = encoded_inputs["special_tokens_mask"] + [1] * difference
                encoded_inputs[self.model_input_names[0]] = required_input + [self.pad_token_id] * difference
            elif padding_side == "left":
                if return_attention_mask:
                    encoded_inputs["attention_mask"] = [0] * difference + encoded_inputs["attention_mask"]
                if "special_tokens_mask" in encoded_inputs:
                    encoded_inputs["special_tokens_mask"] = [1] * difference + encoded_inputs["special_tokens_mask"]
                encoded_inputs[self.model_input_names[0]] = [self.pad_token_id] * difference + required_input
            else:
                raise ValueError(f"Invalid padding strategy:{padding_side}")
        return encoded_inputs
    def pad(
        self,
        encoded_inputs: Union[
            BatchEncoding,
            list[BatchEncoding],
            dict[str, EncodedInput],
            dict[str, list[EncodedInput]],
            list[dict[str, EncodedInput]],
        ],
        padding: Union[bool, str, PaddingStrategy] = True,
        max_length: Optional[int] = None,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_attention_mask: Optional[bool] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        verbose: bool = True,
    ) -> BatchEncoding:
        if isinstance(encoded_inputs, (list, tuple)) and isinstance(encoded_inputs[0], Mapping):
            encoded_inputs = {key: [example[key] for example in encoded_inputs] for key in encoded_inputs[0]}
        if self.model_input_names[0] not in encoded_inputs:
            raise ValueError(
                "You should supply an encoding or a list of encodings to this method "
                f"that includes {self.model_input_names[0]}, but you provided {list(encoded_inputs.keys())}"
            )
        required_input = encoded_inputs[self.model_input_names[0]]
        if required_input is None or (isinstance(required_input, Sized) and len(required_input) == 0):
            if return_attention_mask:
                encoded_inputs["attention_mask"] = []
            return encoded_inputs
        first_element = required_input[0]
        if isinstance(first_element, (list, tuple)):
            for item in required_input:
                if len(item) != 0:
                    first_element = item[0]
                    break
        if not isinstance(first_element, (int, list, tuple)):
            if is_torch_tensor(first_element):
                return_tensors = "pt" if return_tensors is None else return_tensors
            elif isinstance(first_element, np.ndarray):
                return_tensors = "np" if return_tensors is None else return_tensors
            else:
                raise ValueError(
                    f"type of {first_element} unknown: {type(first_element)}. "
                    "Should be one of a python, numpy, pytorch or tensorflow object."
                )
            for key, value in encoded_inputs.items():
                encoded_inputs[key] = to_py_obj(value)
        padding_strategy, _, max_length, _ = self._get_padding_truncation_strategies(
            padding=padding, max_length=max_length, verbose=verbose
        )
        required_input = encoded_inputs[self.model_input_names[0]]
        if required_input and not isinstance(required_input[0], (list, tuple)):
            encoded_inputs = self._pad(
                encoded_inputs,
                max_length=max_length,
                padding_strategy=padding_strategy,
                pad_to_multiple_of=pad_to_multiple_of,
                padding_side=padding_side,
                return_attention_mask=return_attention_mask,
            )
            return BatchEncoding(encoded_inputs, tensor_type=return_tensors)
        batch_size = len(required_input)
        assert all(len(v) == batch_size for v in encoded_inputs.values()), (
            "Some items in the output dictionary have a different batch size than others."
        )
        if padding_strategy == PaddingStrategy.LONGEST:
            max_length = max(len(inputs) for inputs in required_input)
            padding_strategy = PaddingStrategy.MAX_LENGTH
        batch_outputs = {}
        for i in range(batch_size):
            inputs = {k: v[i] for k, v in encoded_inputs.items()}
            outputs = self._pad(
                inputs,
                max_length=max_length,
                padding_strategy=padding_strategy,
                pad_to_multiple_of=pad_to_multiple_of,
                padding_side=padding_side,
                return_attention_mask=return_attention_mask,
            )
            for key, value in outputs.items():
                if key not in batch_outputs:
                    batch_outputs[key] = []
                batch_outputs[key].append(value)
        return BatchEncoding(batch_outputs, tensor_type=return_tensors)
    def truncate_sequences(
        self,
        ids: list[int],
        pair_ids: None = None,
        num_tokens_to_remove: int = 0,
        truncation_strategy: Union[str, TruncationStrategy] = "longest_first",
        stride: int = 0,
        **kwargs,
    ) -> tuple[list[int], None, list[int]]:
        if kwargs:
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.truncate_sequences`."
            )
        if pair_ids:
            raise ValueError("`pair_ids` is not supported by `MistralCommonTokenizer.truncate_sequences`.")
        if num_tokens_to_remove <= 0:
            return (ids, None, [])
        if not isinstance(truncation_strategy, TruncationStrategy):
            truncation_strategy = TruncationStrategy(truncation_strategy)
        if truncation_strategy in [TruncationStrategy.ONLY_FIRST, TruncationStrategy.ONLY_SECOND]:
            raise ValueError(
                f"Only {TruncationStrategy.LONGEST_FIRST} and {TruncationStrategy.DO_NOT_TRUNCATE} are supported."
            )
        overflowing_tokens = []
        if truncation_strategy == TruncationStrategy.LONGEST_FIRST:
            if len(ids) > num_tokens_to_remove:
                window_len = min(len(ids), stride + num_tokens_to_remove)
                if self.truncation_side == "left":
                    overflowing_tokens = ids[:window_len]
                    ids = ids[num_tokens_to_remove:]
                elif self.truncation_side == "right":
                    overflowing_tokens = ids[-window_len:]
                    ids = ids[:-num_tokens_to_remove]
                else:
                    raise ValueError(f"invalid truncation strategy: {self.truncation_side}, use 'left' or 'right'.")
            else:
                error_msg = (
                    f"We need to remove {num_tokens_to_remove} to truncate the input "
                    f"but the first sequence has a length {len(ids)}. "
                )
                logger.error(error_msg)
        return (ids, None, overflowing_tokens)
    def apply_chat_template(
        self,
        conversation: Union[list[dict[str, str]], list[list[dict[str, str]]]],
        tools: Optional[list[Union[dict, Callable]]] = None,
        continue_final_message: bool = False,
        tokenize: bool = True,
        padding: Union[bool, str, PaddingStrategy] = False,
        truncation: bool = False,
        max_length: Optional[int] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_dict: bool = False,
        **kwargs,
    ) -> Union[str, list[int], list[str], list[list[int]], BatchEncoding]:
        if kwargs:
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.apply_chat_template`."
            )
        if not isinstance(truncation, bool):
            raise ValueError("`truncation` must be a boolean for `apply_chat_template` method.")
        if isinstance(conversation, (list, tuple)) and (
            isinstance(conversation[0], (list, tuple)) or hasattr(conversation[0], "messages")
        ):
            conversations = conversation
            is_batched = True
        else:
            conversations = [conversation]
            is_batched = False
        def _maybe_adapt_message(message: dict[str, Any]) -> None:
            if not isinstance(message, dict):
                return
            maybe_list_content: Optional[Union[str, list[dict[str, Union[str, dict[str, Any]]]]]] = message.get(
                "content"
            )
            if not maybe_list_content or isinstance(maybe_list_content, str):
                return
            normalized_content: list[dict[str, Union[str, dict[str, Any]]]] = []
            for content in maybe_list_content:
                content_type = content.get("type", None)
                if not content_type:
                    continue
                elif content_type == "image":
                    maybe_url: Optional[str] = content.get("url")
                    maybe_path: Optional[str] = content.get("path")
                    maybe_base64: Optional[str] = content.get("base64")
                    if maybe_url:
                        image_content = maybe_url
                    elif maybe_path:
                        if not maybe_path.startswith("file://"):
                            maybe_path = Path(maybe_path).resolve().as_uri()
                        image_content = maybe_path
                    elif maybe_base64:
                        if not maybe_base64.startswith("data:image"):
                            maybe_base64 = "data:image/unk;base64," + maybe_base64
                        image_content = maybe_base64
                    else:
                        raise ValueError("Image content must be specified.")
                    normalized_content.append({"type": "image_url", "image_url": {"url": image_content}})
                elif content_type == "audio":
                    maybe_url: Optional[str] = content.get("url")
                    maybe_path: Optional[str] = content.get("path")
                    maybe_base64: Optional[str] = content.get("base64")
                    if maybe_url or maybe_path:
                        audio_data = load_audio_as(maybe_url or maybe_path, return_format="dict", force_mono=True)
                        normalized_content.append({"type": "input_audio", "input_audio": audio_data})
                        continue
                    if not maybe_base64:
                        raise ValueError("Audio content must be specified.")
                    normalized_content.append({"type": "audio_url", "audio_url": {"url": maybe_base64}})
                else:
                    normalized_content.append(content)
            message["content"] = normalized_content
        outputs = []
        images: list[np.ndarray] = []
        audios: list[np.ndarray] = []
        for conversation in conversations:
            messages: list[dict[str, Union[str, list[dict[str, Union[str, dict[str, Any]]]]]]] = []
            for message in conversation:
                _maybe_adapt_message(message)
                messages.append(message)
            chat_request = ChatCompletionRequest.from_openai(
                messages=messages,
                tools=tools,
                continue_final_message=continue_final_message,
            )
            tokenized_request = self.tokenizer.encode_chat_completion(chat_request)
            if tokenize:
                outputs.append(tokenized_request.tokens)
            else:
                outputs.append(tokenized_request.text)
            images.extend(tokenized_request.images)
            audios.extend([el.audio_array for el in tokenized_request.audios])
        if not is_batched:
            outputs = outputs[0]
        if tokenize:
            out = self(
                outputs,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
                add_special_tokens=False,
                return_tensors=return_tensors,
            )
            if return_dict:
                if images:
                    pixel_values: Union[list[np.ndarray], np.ndarray, torch.Tensor]
                    if return_tensors == "pt":
                        if not is_torch_available():
                            raise ImportError(
                                "Unable to convert output to PyTorch tensors format, PyTorch is not installed."
                            )
                        pixel_values = torch.tensor(images)
                    elif return_tensors == "np":
                        pixel_values = np.array(images)
                    elif return_tensors is None:
                        pixel_values = images
                    else:
                        raise ValueError(f"Unsupported return_tensors type: {return_tensors}")
                    out.data["pixel_values"] = pixel_values
                if audios:
                    if return_tensors is not None:
                        raise NotImplementedError(
                            "When passing audio content in apply_chat_template, `return_tensors` must be None since we cannot batch the audio inputs. The returned audio will be a list of numpy arrays."
                        )
                    out.data["audio"] = audios
                return out
            else:
                return out["input_ids"]
        else:
            logger.warning(
                "`MistralCommonTokenizer.apply_chat_template(..., tokenize=False)` is unsafe and may lead to unexpected behavior."
                " Please consider using `tokenize=True` instead and don't encode the output manually."
            )
            return outputs
    @add_end_docstrings(ENCODE_KWARGS_DOCSTRING, ENCODE_PLUS_ADDITIONAL_KWARGS_DOCSTRING)
    def __call__(
        self,
        text: Union[TextInput, EncodedInput, list[TextInput], list[EncodedInput], None] = None,
        text_pair: None = None,
        text_target: None = None,
        text_pair_target: None = None,
        add_special_tokens: bool = True,
        padding: Union[bool, str, PaddingStrategy] = False,
        truncation: Union[bool, str, TruncationStrategy, None] = None,
        max_length: Optional[int] = None,
        stride: int = 0,
        pad_to_multiple_of: Optional[int] = None,
        padding_side: Optional[str] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_attention_mask: Optional[bool] = None,
        return_overflowing_tokens: bool = False,
        return_special_tokens_mask: bool = False,
        return_length: bool = False,
        verbose: bool = True,
        **kwargs,
    ) -> BatchEncoding:
        if kwargs:
            raise ValueError(f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.__call__`.")
        if text_pair or text_target or text_pair_target:
            raise ValueError(
                "`text_pair`, `text_target` and `text_pair_target` are not supported by `MistralCommonTokenizer`."
            )
        if return_tensors in ("tf", "jax"):
            raise ValueError(
                "`MistralCommonTokenizer` does not support `return_tensors='tf'` or `return_tensors='jax'`."
            )
        def _is_valid_text_input(t):
            if isinstance(t, str):
                return True
            elif isinstance(t, (list, tuple)):
                if len(t) == 0:
                    return True
                elif isinstance(t[0], (str, int)):
                    return True
                elif isinstance(t[0], (list, tuple)):
                    return len(t[0]) == 0 or isinstance(t[0][0], (str, int))
                else:
                    return False
            else:
                return False
        if not _is_valid_text_input(text):
            raise ValueError(
                "text input must be of type `str` (single example), `List[str]` (batch or single encoded example) "
                "or `List[List[int]]` (batch of encoded examples)."
            )
        is_batched = isinstance(text, (list, tuple)) and isinstance(text[0], (str, list, tuple))
        padding_strategy, truncation_strategy, max_length, kwargs = self._get_padding_truncation_strategies(
            padding=padding,
            truncation=truncation,
            max_length=max_length,
            pad_to_multiple_of=pad_to_multiple_of,
            verbose=verbose,
            **kwargs,
        )
        if is_batched:
            return self._batch_encode_plus(
                batch_text=text,
                add_special_tokens=add_special_tokens,
                padding_strategy=padding_strategy,
                truncation_strategy=truncation_strategy,
                max_length=max_length,
                stride=stride,
                pad_to_multiple_of=pad_to_multiple_of,
                padding_side=padding_side,
                return_tensors=return_tensors,
                return_attention_mask=return_attention_mask,
                return_overflowing_tokens=return_overflowing_tokens,
                return_special_tokens_mask=return_special_tokens_mask,
                return_length=return_length,
                verbose=verbose,
                **kwargs,
            )
        else:
            return self._encode_plus(
                text=text,
                add_special_tokens=add_special_tokens,
                padding_strategy=padding_strategy,
                truncation_strategy=truncation_strategy,
                max_length=max_length,
                stride=stride,
                pad_to_multiple_of=pad_to_multiple_of,
                padding_side=padding_side,
                return_tensors=return_tensors,
                return_attention_mask=return_attention_mask,
                return_overflowing_tokens=return_overflowing_tokens,
                return_special_tokens_mask=return_special_tokens_mask,
                return_length=return_length,
                verbose=verbose,
                **kwargs,
            )
    @classmethod
    def from_pretrained(
        cls,
        pretrained_model_name_or_path: Union[str, os.PathLike],
        *init_inputs,
        mode: ValidationMode = ValidationMode.test,
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        model_max_length: int = VERY_LARGE_INTEGER,
        padding_side: str = "left",
        truncation_side: str = "right",
        model_input_names: Optional[list[str]] = None,
        clean_up_tokenization_spaces: bool = False,
        **kwargs,
    ):
        if init_inputs:
            raise ValueError("`init_inputs` are not supported by `MistralCommonTokenizer.from_pretrained`.")
        if kwargs and not set(kwargs.keys()).issubset({"_from_auto", "trust_remote_code"}):
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.from_pretrained`."
            )
        if not os.path.isdir(pretrained_model_name_or_path):
            tokenizer_path = download_tokenizer_from_hf_hub(
                repo_id=pretrained_model_name_or_path,
                cache_dir=cache_dir,
                token=token,
                revision=revision,
                force_download=force_download,
                local_files_only=local_files_only,
            )
        else:
            valid_tokenizer_files = []
            tokenizer_file: str
            instruct_versions = list(TokenizerVersion.__members__)
            mm_versions = list(MultiModalVersion.__members__) + [""]
            sentencepiece_suffixes = [f".model.{v}{m}" for v in instruct_versions for m in mm_versions] + [".model"]
            for path in os.listdir(pretrained_model_name_or_path):
                pathlib_repo_file = Path(path)
                file_name = pathlib_repo_file.name
                suffix = "".join(pathlib_repo_file.suffixes)
                if file_name == "tekken.json" or suffix in sentencepiece_suffixes:
                    valid_tokenizer_files.append(file_name)
            if len(valid_tokenizer_files) == 0:
                raise ValueError(f"No tokenizer file found in directory: {pretrained_model_name_or_path}")
            if len(valid_tokenizer_files) > 1:
                if "tekken.json" in valid_tokenizer_files:
                    tokenizer_file = "tekken.json"
                else:
                    tokenizer_file = max(valid_tokenizer_files)
                logger.warning(
                    f"Multiple tokenizer files found in directory: {pretrained_model_name_or_path}. Using {tokenizer_file}."
                )
            else:
                tokenizer_file = valid_tokenizer_files[0]
            tokenizer_path = os.path.join(pretrained_model_name_or_path, tokenizer_file)
        return cls(
            tokenizer_path=tokenizer_path,
            mode=mode,
            model_max_length=model_max_length,
            padding_side=padding_side,
            truncation_side=truncation_side,
            model_input_names=model_input_names,
            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
        )
    def save_pretrained(
        self,
        save_directory: Union[str, os.PathLike, Path],
        push_to_hub: bool = False,
        token: Optional[Union[str, bool]] = None,
        commit_message: Optional[str] = None,
        repo_id: Optional[str] = None,
        private: Optional[bool] = None,
        repo_url: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs,
    ) -> tuple[str, ...]:
        kwargs.pop("save_jinja_files", None)
        if kwargs:
            raise ValueError(
                f"Kwargs {list(kwargs.keys())} are not supported by `MistralCommonTokenizer.save_pretrained`."
            )
        save_directory = Path(save_directory)
        save_directory.mkdir(parents=True, exist_ok=True)
        shutil.copy(self._tokenizer_path, save_directory)
        if push_to_hub:
            repo_id = repo_id or str(save_directory).split(os.path.sep)[-1]
            repo_id = self._create_repo(
                repo_id, token=token, private=private, repo_url=repo_url, organization=organization
            )
            files_timestamps = self._get_files_timestamps(save_directory)
            self._upload_modified_files(
                save_directory,
                repo_id,
                files_timestamps,
                commit_message=commit_message,
                token=token,
            )
        return (str(save_directory / self._tokenizer_path.name),)