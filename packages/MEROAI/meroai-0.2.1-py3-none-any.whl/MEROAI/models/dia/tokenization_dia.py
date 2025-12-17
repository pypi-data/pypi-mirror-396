from typing import Optional
from ...tokenization_utils import AddedToken, PreTrainedTokenizer
from ...utils import logging
logger = logging.get_logger(__name__)
class DiaTokenizer(PreTrainedTokenizer):
    model_input_names = ["input_ids", "attention_mask"]
    def __init__(
        self,
        pad_token: Optional[str] = "<pad>",
        unk_token: Optional[str] = "<pad>",
        max_length: Optional[int] = 1024,
        offset: int = 0,
        **kwargs,
    ):
        pad_token = AddedToken(pad_token) if isinstance(pad_token, str) else pad_token
        unk_token = AddedToken(unk_token) if isinstance(unk_token, str) else unk_token
        self._utf_vocab_size = 2**8
        self._added_tokens_decoder = {0: pad_token, 1: AddedToken("[S1]"), 2: AddedToken("[S2]")}
        self.offset = offset
        super().__init__(
            unk_token=unk_token,
            pad_token=pad_token,
            max_length=max_length,
            **kwargs,
        )
    @property
    def vocab_size(self):
        return self._utf_vocab_size
    def get_vocab(self):
        vocab = {self.convert_ids_to_tokens(i): i for i in range(self.vocab_size + self.offset)}
        vocab.update(self.added_tokens_encoder)
        return vocab
    def _tokenize(self, text: str) -> list[str]:
        tokens = [chr(i) for i in text.encode("utf-8")]
        return tokens
    def _convert_token_to_id(self, token):
        if len(token) != 1:
            token_id = None
        else:
            token_id = ord(token) + self.offset
        return token_id
    def _convert_id_to_token(self, index):
        token = chr(index - self.offset)
        return token
    def convert_tokens_to_string(self, tokens: list[str]) -> str:
        bstring = b""
        for token in tokens:
            if token in self.added_tokens_decoder:
                added_token_obj = self.added_tokens_decoder[token]
                tok_string = str(added_token_obj).encode("utf-8")
            elif token in self.added_tokens_encoder:
                tok_string = token.encode("utf-8")
            else:
                tok_string = token.encode("utf-8")
            bstring += tok_string
        string = bstring.decode("utf-8", errors="ignore")
        return string
    def save_vocabulary(self, save_directory: str, filename_prefix: Optional[str] = None) -> tuple[str]:
        return ()
__all__ = ["DiaTokenizer"]