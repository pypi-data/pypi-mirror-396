from pathlib import Path
from typing import Any
from MEROAI.convert_slow_tokenizer import TikTokenConverter
from MEROAI.tokenization_utils_fast import TIKTOKEN_VOCAB_FILE, TOKENIZER_FILE
def convert_tiktoken_to_fast(encoding: Any, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    save_file = output_dir / "tiktoken" / TIKTOKEN_VOCAB_FILE
    tokenizer_file = output_dir / TOKENIZER_FILE
    save_file_absolute = str(save_file.absolute())
    output_file_absolute = str(tokenizer_file.absolute())
    try:
        from tiktoken import get_encoding
        from tiktoken.load import dump_tiktoken_bpe
        if isinstance(encoding, str):
            encoding = get_encoding(encoding)
        dump_tiktoken_bpe(encoding._mergeable_ranks, save_file_absolute)
    except ImportError:
        raise ValueError("`tiktoken` is required to save a `tiktoken` file. Install it with `pip install tiktoken`.")
    tokenizer = TikTokenConverter(
        vocab_file=save_file_absolute, pattern=encoding._pat_str, additional_special_tokens=encoding._special_tokens
    ).converted()
    tokenizer.save(output_file_absolute)