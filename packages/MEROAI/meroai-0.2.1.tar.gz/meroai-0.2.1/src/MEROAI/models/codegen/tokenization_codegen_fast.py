import re
from typing import TYPE_CHECKING, Optional, Union
import numpy as np
from ...utils import is_tf_available, is_torch_available, logging
if TYPE_CHECKING:
    if is_torch_available():
        import torch
    if is_tf_available():
        import tensorflow as tf
from ...tokenization_utils_base import BatchEncoding
from ...tokenization_utils_fast import PreTrainedTokenizerFast
from .tokenization_codegen import CodeGenTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.json", "merges_file": "merges.txt", "tokenizer_file": "tokenizer.json"}
class CodeGenTokenizerFast(PreTrainedTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = CodeGenTokenizer
    def __init__(
        self,
        vocab_file=None,
        merges_file=None,
        tokenizer_file=None,
        unk_token="<|endoftext|>",
        bos_token="<|endoftext|>",
        eos_token="<|endoftext|>",
        add_prefix_space=False,
        return_token_type_ids=False,
        **kwargs,
    ):
        self.return_token_type_ids = return_token_type_ids
        if self.return_token_type_ids:
            self.model_input_names.append("token_type_ids")
        super().__init__(
            vocab_file,
            merges_file,
            tokenizer_file=tokenizer_file,
            unk_token=unk_token,
            bos_token=bos_token,
            eos_token=eos_token,
            add_prefix_space=add_prefix_space,
            return_token_type_ids=return_token_type_ids,
            **kwargs,
        )
        if kwargs.pop("add_bos_token", False):
            model_id = kwargs.pop("name_or_path", "")
            raise ValueError(
                "Currently GPT2's fast tokenizer does NOT support adding a BOS token. "
                "Instead you should use GPT2's slow tokenizer class `CodeGenTokenizer` as follows: \n"
                f"`CodeGenTokenizer.from_pretrained('{model_id}')`\nor\n"
                f"`AutoTokenizer.from_pretrained('{model_id}', use_fast=False)`\n"
                "This issue will be fixed soon, see: https://github.com/huggingface/tokenizers/pull/1005."
                " so that the fast tokenizer works correctly."
            )
    def _batch_encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        assert self.add_prefix_space or not is_split_into_words, (
            f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True "
            "to use it with pretokenized inputs."
        )
        return super()._batch_encode_plus(*args, **kwargs)
    def _encode_plus(self, *args, **kwargs) -> BatchEncoding:
        is_split_into_words = kwargs.get("is_split_into_words", False)
        assert self.add_prefix_space or not is_split_into_words, (
            f"You need to instantiate {self.__class__.__name__} with add_prefix_space=True "
            "to use it with pretokenized inputs."
        )
        return super()._encode_plus(*args, **kwargs)
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> tuple[str]:
        files = self._tokenizer.model.save(save_directory, name=filename_prefix)
        return tuple(files)
    def decode(
        self,
        token_ids: Union[int, list[int], "np.ndarray", "torch.Tensor", "tf.Tensor"],
        skip_special_tokens: bool = False,
        clean_up_tokenization_spaces: Optional[bool] = None,
        truncate_before_pattern: Optional[list[str]] = None,
        **kwargs,
    ) -> str:
        decoded_text = super().decode(
            token_ids=token_ids,
            skip_special_tokens=skip_special_tokens,
            clean_up_tokenization_spaces=clean_up_tokenization_spaces,
            **kwargs,
        )
        if truncate_before_pattern is not None and len(truncate_before_pattern) > 0:
            decoded_text = self.truncate(decoded_text, truncate_before_pattern)
        return decoded_text
    def truncate(self, completion, truncate_before_pattern):
        def find_re(string, pattern, start_pos):
            m = pattern.search(string, start_pos)
            return m.start() if m else -1
        terminals = [re.compile(pattern, re.MULTILINE) for pattern in truncate_before_pattern]
        prints = list(re.finditer("^print", completion, re.MULTILINE))
        if len(prints) > 1:
            completion = completion[: prints[1].start()]
        defs = list(re.finditer("^def", completion, re.MULTILINE))
        if len(defs) > 1:
            completion = completion[: defs[1].start()]
        start_pos = 0
        terminals_pos = [
            pos for pos in [find_re(completion, terminal, start_pos) for terminal in terminals] if pos != -1
        ]
        if len(terminals_pos) > 0:
            return completion[: min(terminals_pos)]
        else:
            return completion
__all__ = ["CodeGenTokenizerFast"]