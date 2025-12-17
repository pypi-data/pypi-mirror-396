import gc
import tempfile
import unittest
import numpy as np
import torch
from MEROAI.image_utils import load_image
from MEROAI.models.auto.tokenization_auto import AutoTokenizer
from MEROAI.testing_utils import require_mistral_common
from MEROAI.tokenization_mistral_common import MistralCommonTokenizer
from MEROAI.tokenization_utils_base import BatchEncoding, TruncationStrategy
from MEROAI.utils import PaddingStrategy, is_mistral_common_available
if is_mistral_common_available():
    import mistral_common.tokens.tokenizers
    from mistral_common.exceptions import InvalidMessageStructureException
    from mistral_common.protocol.instruct.request import ChatCompletionRequest
    from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
    from mistral_common.tokens.tokenizers.utils import list_local_hf_repo_files
    mistral_common.tokens.tokenizers.image.download_image = load_image
from .test_processing_common import url_to_local_path
IMG_URL = url_to_local_path(
    "https://huggingface.co/datasets/raushan-testing-hf/images_test/resolve/main/picsum_237_200x300.jpg"
)
IMG_URL = f"file://{IMG_URL}" if not IMG_URL.startswith("http") else IMG_URL
IMG_BASE_64 = 
AUDIO_NAMESPACE = "hf-internal-testing"
AUDIO_REPO_NAME = "dummy-audio-samples"
AUDIO_FILENAME = "bcn_weather.mp3"
AUDIO_URL = url_to_local_path(
    f"https://huggingface.co/datasets/{AUDIO_NAMESPACE}/{AUDIO_REPO_NAME}/resolve/main/{AUDIO_FILENAME}"
)
AUDIO_BASE_64 = 
@require_mistral_common
class TestMistralCommonTokenizer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.repo_id = "hf-internal-testing/namespace-mistralai-repo_name-Mistral-Small-3.1-24B-Instruct-2503"
        cls.local_files_only = len(list_local_hf_repo_files(cls.repo_id, revision=None)) > 0
        cls.tokenizer: MistralCommonTokenizer = AutoTokenizer.from_pretrained(
            cls.repo_id,
            tokenizer_type="mistral",
            local_files_only=cls.local_files_only,
            revision=None,
        )
        cls.ref_tokenizer: MistralTokenizer = MistralTokenizer.from_hf_hub(
            cls.repo_id, local_files_only=cls.local_files_only
        )
        repo_id = "mistralai/Voxtral-Mini-3B-2507"
        local_files_only = len(list_local_hf_repo_files(repo_id, revision=None)) > 0
        cls.tokenizer_audio: MistralCommonTokenizer = AutoTokenizer.from_pretrained(
            repo_id,
            local_files_only=local_files_only,
            revision=None,
        )
        cls.ref_tokenizer_audio: MistralCommonTokenizer = MistralTokenizer.from_hf_hub(
            repo_id, local_files_only=local_files_only
        )
        cls.fixture_conversations = [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
            ],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
                {"role": "assistant", "content": "Hello! How can I help you?"},
                {"role": "user", "content": "What is the temperature in Paris?"},
            ],
        ]
        cls.tokenized_fixture_conversations = [
            cls.ref_tokenizer.encode_chat_completion(ChatCompletionRequest.from_openai(conversation))
            for conversation in cls.fixture_conversations
        ]
        cls.ref_special_ids = {t["rank"] for t in cls.ref_tokenizer.instruct_tokenizer.tokenizer._all_special_tokens}
    @classmethod
    def tearDownClass(cls):
        del cls.tokenizer
        del cls.ref_tokenizer
        del cls.tokenizer_audio
        del cls.ref_tokenizer_audio
        del cls.fixture_conversations
        del cls.tokenized_fixture_conversations
        del cls.ref_special_ids
        gc.collect()
    def _ref_piece_to_id(self, piece: str) -> int:
        pieces = self.ref_tokenizer.instruct_tokenizer.tokenizer._model.encode(
            piece, allowed_special="all", disallowed_special=set()
        )
        assert len(pieces) == 1, f"Expected to decode 1 token, got {len(pieces)}"
        return pieces[0]
    def test_vocab_size(self):
        self.assertEqual(self.tokenizer.vocab_size, self.ref_tokenizer.instruct_tokenizer.tokenizer.n_words)
    def test_save_pretrained(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            self.tokenizer.save_pretrained(tmp_dir)
            loaded_tokenizer = MistralCommonTokenizer.from_pretrained(tmp_dir)
        self.assertIsNotNone(loaded_tokenizer)
        self.assertEqual(self.tokenizer.get_vocab(), loaded_tokenizer.get_vocab())
        self.assertEqual(
            self.tokenizer.tokenizer.instruct_tokenizer.tokenizer.version,
            loaded_tokenizer.tokenizer.instruct_tokenizer.tokenizer.version,
        )
        with self.assertRaises(
            ValueError, msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.save_pretrained`."
        ):
            with tempfile.TemporaryDirectory() as tmp_dir:
                self.tokenizer.save_pretrained(tmp_dir, unk_args="")
    def test_encode(self):
        string = "Hello, world!"
        expected_with_special = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string, bos=True, eos=True)
        tokens_with_special = self.tokenizer.encode(string, add_special_tokens=True)
        self.assertEqual(tokens_with_special, expected_with_special)
        expected_without_special = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string, bos=False, eos=False)
        tokens_without_special = self.tokenizer.encode(string, add_special_tokens=False)
        self.assertEqual(tokens_without_special, expected_without_special)
        tokens_with_return_tensors = self.tokenizer.encode(string, add_special_tokens=False, return_tensors="pt")
        self.assertIsInstance(tokens_with_return_tensors, torch.Tensor)
        self.assertEqual(tokens_with_return_tensors.tolist()[0], expected_without_special)
        tokens_with_max_length = self.tokenizer.encode(string, add_special_tokens=False, max_length=3)
        self.assertEqual(tokens_with_max_length, expected_without_special[:3])
        tokens_with_padding = self.tokenizer.encode(
            string, add_special_tokens=False, padding=True, pad_to_multiple_of=6
        )
        expected_padding = [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (
            6 - len(expected_without_special) % 6
        ) + expected_without_special
        self.assertEqual(tokens_with_padding, expected_padding)
        for padding in [
            False,
            True,
            "longest",
            "max_length",
            "do_not_pad",
            PaddingStrategy.LONGEST,
            PaddingStrategy.MAX_LENGTH,
            PaddingStrategy.DO_NOT_PAD,
        ]:
            tokens_with_padding = self.tokenizer.encode(string, add_special_tokens=False, padding=padding)
            self.assertEqual(tokens_with_padding, expected_without_special)
        string_long = (
            "Hello world! It is a beautiful day today. The sun is shining brightly and the birds are singing."
        )
        expected_long = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string_long, bos=False, eos=False)
        tokens_with_truncation = self.tokenizer.encode(
            string_long, add_special_tokens=False, truncation=True, max_length=12
        )
        self.assertEqual(tokens_with_truncation, expected_long[:12])
        tokens_with_padding_and_truncation = self.tokenizer.encode(
            string_long, add_special_tokens=False, padding=True, pad_to_multiple_of=12, truncation=True, max_length=36
        )
        expected_long_padding = [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (
            12 - len(expected_long) % 12
        ) + expected_long
        self.assertEqual(tokens_with_padding_and_truncation, expected_long_padding)
        with self.assertRaises(
            ValueError, msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.encode`."
        ):
            self.tokenizer.encode("Hello, world!", add_special_tokens=True, unk_args="")
    def test_decode(self):
        string = "Hello, world!"
        string_with_space = "Hello, world !"
        tokens_ids = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string, bos=True, eos=True)
        tokens_ids_with_space = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(
            string_with_space, bos=True, eos=True
        )
        self.assertEqual(self.tokenizer.decode(tokens_ids, skip_special_tokens=True), string)
        self.assertEqual(self.tokenizer.decode(tokens_ids, skip_special_tokens=False), "<s>" + string + "</s>")
        self.assertEqual(self.tokenizer.decode(tokens_ids_with_space, skip_special_tokens=True), string_with_space)
        self.assertEqual(
            self.tokenizer.decode(tokens_ids_with_space, skip_special_tokens=True, clean_up_tokenization_spaces=True),
            "Hello, world!",
        )
        with self.assertRaises(
            ValueError, msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.decode`."
        ):
            self.tokenizer.decode(tokens_ids, skip_special_tokens=False, unk_args="")
    def test_batch_decode(self):
        string = "Hello, world!"
        string_with_space = "Hello, world !"
        batch_tokens_ids = [
            self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string, bos=True, eos=True),
            self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string_with_space, bos=True, eos=True),
        ]
        self.assertEqual(
            self.tokenizer.batch_decode(batch_tokens_ids, skip_special_tokens=True),
            [string, string_with_space],
        )
        self.assertEqual(
            self.tokenizer.batch_decode(batch_tokens_ids, skip_special_tokens=False),
            ["<s>" + string + "</s>", "<s>" + string_with_space + "</s>"],
        )
        self.assertEqual(
            self.tokenizer.batch_decode(batch_tokens_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True),
            ["Hello, world!", "Hello, world!"],
        )
        with self.assertRaises(
            ValueError, msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.batch_decode`."
        ):
            self.tokenizer.batch_decode(batch_tokens_ids, skip_special_tokens=False, unk_args="")
    def test_convert_ids_to_tokens(self):
        ids = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode("Hello world!", bos=True, eos=True)
        expected_tokens = [self.ref_tokenizer.instruct_tokenizer.tokenizer.id_to_piece(id) for id in ids]
        tokens = self.tokenizer.convert_ids_to_tokens(ids, skip_special_tokens=False)
        self.assertEqual(tokens, expected_tokens)
        token = self.tokenizer.convert_ids_to_tokens(ids[0], skip_special_tokens=False)
        self.assertEqual(token, expected_tokens[0])
        expected_tokens = expected_tokens[1:-1]
        tokens = self.tokenizer.convert_ids_to_tokens(ids, skip_special_tokens=True)
        self.assertEqual(tokens, expected_tokens)
        with self.assertRaises(ValueError):
            self.tokenizer.convert_ids_to_tokens(ids[0], skip_special_tokens=True)
        token = self.tokenizer.convert_ids_to_tokens(ids[1], skip_special_tokens=True)
        self.assertEqual(token, expected_tokens[0])
    def test_convert_tokens_to_ids(self):
        tokens = ["Hello", "world", "!"]
        expected_ids = [self._ref_piece_to_id(token) for token in tokens]
        ids = self.tokenizer.convert_tokens_to_ids(tokens)
        self.assertEqual(ids, expected_ids)
        id = self.tokenizer.convert_tokens_to_ids(tokens[0])
        self.assertEqual(id, expected_ids[0])
        self.assertEqual(id, self.tokenizer.convert_tokens_to_ids(tokens[0]))
    def test_tokenize(self):
        string = "Hello world!"
        expected_tokens = [
            self.ref_tokenizer.instruct_tokenizer.tokenizer.id_to_piece(id)
            for id in self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(string, bos=False, eos=False)
        ]
        tokens = self.tokenizer.tokenize(string)
        self.assertEqual(tokens, expected_tokens)
        with self.assertRaises(
            ValueError, msg="Kwargs [add_special_tokens] are not supported by `MistralCommonTokenizer.tokenize`."
        ):
            self.tokenizer.tokenize(string, add_special_tokens=True)
    def test_get_special_tokens_mask(self):
        ids = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode("Hello world!", bos=True, eos=True)
        expected_mask = [1 if id in self.ref_special_ids else 0 for id in ids]
        mask = self.tokenizer.get_special_tokens_mask(ids)
        self.assertEqual(mask, expected_mask)
        with self.assertRaises(ValueError):
            self.tokenizer.get_special_tokens_mask(ids, already_has_special_tokens=True)
        with self.assertRaises(ValueError):
            self.tokenizer.get_special_tokens_mask(ids, token_ids_1=ids)
    def test_pad_batch_encoding_input(self):
        def get_batch_encoding():
            return self.tokenizer("Hello world!", return_special_tokens_mask=True)
        batch_encoding = get_batch_encoding()
        for padding in [
            False,
            True,
            "longest",
            "max_length",
            "do_not_pad",
            PaddingStrategy.LONGEST,
            PaddingStrategy.MAX_LENGTH,
            PaddingStrategy.DO_NOT_PAD,
        ]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding)
            self.assertEqual(padded_batch_encoding, batch_encoding)
        for padding in ["max_length", PaddingStrategy.MAX_LENGTH]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding, max_length=12)
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (12 - len(batch_encoding["input_ids"]))
                + batch_encoding["input_ids"],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [0] * (12 - len(batch_encoding["input_ids"])) + batch_encoding["attention_mask"],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [1] * (12 - len(batch_encoding["input_ids"])) + batch_encoding["special_tokens_mask"],
            )
        for padding in [True, "longest", PaddingStrategy.LONGEST]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding, pad_to_multiple_of=16)
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (16 - len(batch_encoding["input_ids"]))
                + batch_encoding["input_ids"],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [0] * (16 - len(batch_encoding["input_ids"])) + batch_encoding["attention_mask"],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [1] * (16 - len(batch_encoding["input_ids"])) + batch_encoding["special_tokens_mask"],
            )
        right_tokenizer = MistralCommonTokenizer.from_pretrained(
            self.repo_id,
            local_files_only=self.local_files_only,
            padding_side="right",
            revision=None,
        )
        right_paddings = [
            right_tokenizer.pad(get_batch_encoding(), padding="max_length", max_length=12),
            self.tokenizer.pad(get_batch_encoding(), padding="max_length", max_length=12, padding_side="right"),
        ]
        for padded_batch_encoding in right_paddings:
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                batch_encoding["input_ids"]
                + [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (12 - len(batch_encoding["input_ids"])),
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                batch_encoding["attention_mask"] + [0] * (12 - len(batch_encoding["input_ids"])),
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                batch_encoding["special_tokens_mask"] + [1] * (12 - len(batch_encoding["input_ids"])),
            )
        padded_batch_encoding = self.tokenizer.pad(
            get_batch_encoding(), padding="max_length", max_length=12, return_attention_mask=False
        )
        self.assertEqual(
            padded_batch_encoding["input_ids"],
            [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (12 - len(batch_encoding["input_ids"]))
            + batch_encoding["input_ids"],
        )
        self.assertEqual(padded_batch_encoding["attention_mask"], batch_encoding["attention_mask"])
        self.assertEqual(
            padded_batch_encoding["special_tokens_mask"],
            [1] * (12 - len(batch_encoding["input_ids"])) + batch_encoding["special_tokens_mask"],
        )
        for return_tensors in ["pt", "np"]:
            padded_batch_encoding = self.tokenizer.pad(
                get_batch_encoding(), padding="max_length", max_length=12, return_tensors=return_tensors
            )
            self.assertEqual(padded_batch_encoding["input_ids"].shape, torch.Size((12,)))
            self.assertEqual(padded_batch_encoding["attention_mask"].shape, torch.Size((12,)))
            self.assertEqual(padded_batch_encoding["special_tokens_mask"].shape, torch.Size((12,)))
    def test_list_batch_encoding_input(self):
        def get_batch_encoding():
            return self.tokenizer(["Hello world!", "Hello world! Longer sentence."], return_special_tokens_mask=True)
        batch_encoding = get_batch_encoding()
        for padding in [
            True,
            "longest",
            PaddingStrategy.LONGEST,
        ]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding)
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [
                    [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (len(batch_encoding["input_ids"][1]) - len(batch_encoding["input_ids"][0]))
                    + batch_encoding["input_ids"][0],
                    batch_encoding["input_ids"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [
                    [0] * (len(batch_encoding["input_ids"][1]) - len(batch_encoding["input_ids"][0]))
                    + batch_encoding["attention_mask"][0],
                    batch_encoding["attention_mask"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [
                    [1] * (len(batch_encoding["input_ids"][1]) - len(batch_encoding["input_ids"][0]))
                    + batch_encoding["special_tokens_mask"][0],
                    batch_encoding["special_tokens_mask"][1],
                ],
            )
        for padding in ["max_length", PaddingStrategy.MAX_LENGTH]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding, max_length=12)
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [
                    [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (12 - len(batch_encoding["input_ids"][0]))
                    + batch_encoding["input_ids"][0],
                    [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (12 - len(batch_encoding["input_ids"][1]))
                    + batch_encoding["input_ids"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [
                    [0] * (12 - len(batch_encoding["input_ids"][0])) + batch_encoding["attention_mask"][0],
                    [0] * (12 - len(batch_encoding["input_ids"][1])) + batch_encoding["attention_mask"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [
                    [1] * (12 - len(batch_encoding["input_ids"][0])) + batch_encoding["special_tokens_mask"][0],
                    [1] * (12 - len(batch_encoding["input_ids"][1])) + batch_encoding["special_tokens_mask"][1],
                ],
            )
        for padding in [True, "longest", PaddingStrategy.LONGEST]:
            padded_batch_encoding = self.tokenizer.pad(get_batch_encoding(), padding=padding, pad_to_multiple_of=16)
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [
                    [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (16 - len(batch_encoding["input_ids"][0]))
                    + batch_encoding["input_ids"][0],
                    [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (16 - len(batch_encoding["input_ids"][1]))
                    + batch_encoding["input_ids"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [
                    [0] * (16 - len(batch_encoding["input_ids"][0])) + batch_encoding["attention_mask"][0],
                    [0] * (16 - len(batch_encoding["input_ids"][1])) + batch_encoding["attention_mask"][1],
                ],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [
                    [1] * (16 - len(batch_encoding["input_ids"][0])) + batch_encoding["special_tokens_mask"][0],
                    [1] * (16 - len(batch_encoding["input_ids"][1])) + batch_encoding["special_tokens_mask"][1],
                ],
            )
        right_tokenizer = MistralCommonTokenizer.from_pretrained(
            self.repo_id,
            local_files_only=self.local_files_only,
            padding_side="right",
            revision=None,
        )
        right_paddings = [
            right_tokenizer.pad(get_batch_encoding(), padding="max_length", max_length=12),
            self.tokenizer.pad(get_batch_encoding(), padding="max_length", max_length=12, padding_side="right"),
        ]
        for padded_batch_encoding in right_paddings:
            self.assertEqual(
                padded_batch_encoding["input_ids"],
                [
                    batch_encoding["input_ids"][0]
                    + [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (12 - len(batch_encoding["input_ids"][0])),
                    batch_encoding["input_ids"][1]
                    + [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    * (12 - len(batch_encoding["input_ids"][1])),
                ],
            )
            self.assertEqual(
                padded_batch_encoding["attention_mask"],
                [
                    batch_encoding["attention_mask"][0] + [0] * (12 - len(batch_encoding["input_ids"][0])),
                    batch_encoding["attention_mask"][1] + [0] * (12 - len(batch_encoding["input_ids"][1])),
                ],
            )
            self.assertEqual(
                padded_batch_encoding["special_tokens_mask"],
                [
                    batch_encoding["special_tokens_mask"][0] + [1] * (12 - len(batch_encoding["input_ids"][0])),
                    batch_encoding["special_tokens_mask"][1] + [1] * (12 - len(batch_encoding["input_ids"][1])),
                ],
            )
        padded_batch_encoding = self.tokenizer.pad(
            get_batch_encoding(), padding="max_length", max_length=12, return_attention_mask=False
        )
        self.assertEqual(
            padded_batch_encoding["input_ids"],
            [
                [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (12 - len(batch_encoding["input_ids"][0]))
                + batch_encoding["input_ids"][0],
                [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id] * (12 - len(batch_encoding["input_ids"][1]))
                + batch_encoding["input_ids"][1],
            ],
        )
        self.assertEqual(padded_batch_encoding["attention_mask"], batch_encoding["attention_mask"])
        self.assertEqual(
            padded_batch_encoding["special_tokens_mask"],
            [
                [1] * (12 - len(batch_encoding["input_ids"][0])) + batch_encoding["special_tokens_mask"][0],
                [1] * (12 - len(batch_encoding["input_ids"][1])) + batch_encoding["special_tokens_mask"][1],
            ],
        )
        for return_tensors in ["pt", "np"]:
            padded_batch_encoding = self.tokenizer.pad(
                get_batch_encoding(), padding="max_length", max_length=12, return_tensors=return_tensors
            )
            self.assertEqual(padded_batch_encoding["input_ids"].shape, torch.Size((2, 12)))
            self.assertEqual(padded_batch_encoding["attention_mask"].shape, torch.Size((2, 12)))
            self.assertEqual(padded_batch_encoding["special_tokens_mask"].shape, torch.Size((2, 12)))
    def test_truncate_sequences(self):
        text = "Hello world!"
        ids = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=True, eos=True)
        for truncation in ["longest_first", TruncationStrategy.LONGEST_FIRST]:
            for num_tokens_to_remove in [0, 2]:
                tokens, none, overflowing_tokens = self.tokenizer.truncate_sequences(
                    ids, truncation_strategy=truncation, num_tokens_to_remove=num_tokens_to_remove
                )
                self.assertEqual(tokens, ids[:-num_tokens_to_remove] if num_tokens_to_remove > 0 else ids)
                self.assertIsNone(none)
                self.assertEqual(overflowing_tokens, ids[-num_tokens_to_remove:] if num_tokens_to_remove > 0 else [])
        for truncation in ["only_first", "only_second", TruncationStrategy.ONLY_FIRST, TruncationStrategy.ONLY_SECOND]:
            with self.assertRaises(ValueError):
                self.tokenizer.truncate_sequences(ids, truncation_strategy=truncation, num_tokens_to_remove=1)
        for truncation in ["do_not_truncate", TruncationStrategy.DO_NOT_TRUNCATE]:
            tokens, none, overflowing_tokens = self.tokenizer.truncate_sequences(
                ids, truncation_strategy=truncation, num_tokens_to_remove=1
            )
            self.assertEqual(tokens, ids)
            self.assertIsNone(none)
            self.assertEqual(overflowing_tokens, [])
        with self.assertRaises(ValueError):
            self.tokenizer.truncate_sequences(
                ids, pair_ids=ids, truncation_strategy="longest_first", num_tokens_to_remove=1
            )
        for stride in [0, 2]:
            tokens, none, overflowing_tokens = self.tokenizer.truncate_sequences(
                ids, truncation_strategy="longest_first", num_tokens_to_remove=2, stride=stride
            )
            self.assertEqual(tokens, ids[:-2])
            self.assertIsNone(none)
            self.assertEqual(overflowing_tokens, ids[-2 - stride :])
        left_tokenizer = MistralCommonTokenizer.from_pretrained(
            self.repo_id,
            local_files_only=self.local_files_only,
            truncation_side="left",
            revision=None,
        )
        tokens, none, overflowing_tokens = left_tokenizer.truncate_sequences(
            ids, truncation_strategy="longest_first", num_tokens_to_remove=2
        )
        self.assertEqual(tokens, ids[2:])
        self.assertIsNone(none)
        self.assertEqual(overflowing_tokens, ids[:2])
    def test_apply_chat_template_basic(self):
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hi!"},
            {"role": "assistant", "content": "Hello! How can I help you?"},
            {"role": "user", "content": "What is the capital of France?"},
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(ChatCompletionRequest.from_openai(conversation))
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tokenize=False),
            expected_tokenized.text,
        )
        self.assertEqual(self.tokenizer.apply_chat_template(conversation, tokenize=True), expected_tokenized.tokens)
        with self.assertRaises(
            ValueError, msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.apply_chat_template`."
        ):
            self.tokenizer.apply_chat_template(conversation, tokenize=True, unk_args="")
    def test_apply_chat_template_continue_final_message(self):
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hi!"},
            {"role": "assistant", "content": "Hello! How can I help you?"},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris"},
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(
            ChatCompletionRequest.from_openai(conversation, continue_final_message=True)
        )
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tokenize=False, continue_final_message=True),
            expected_tokenized.text,
        )
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tokenize=True, continue_final_message=True),
            expected_tokenized.tokens,
        )
        with self.assertRaises(InvalidMessageStructureException):
            self.tokenizer.apply_chat_template(conversation, tokenize=False, continue_final_message=False)
    def test_apply_chat_template_with_tools(self):
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hi!"},
            {"role": "assistant", "content": "Hello! How can I help you?"},
            {"role": "user", "content": "What is the temperature in Paris?"},
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "azerty123",
                        "function": {
                            "name": "get_current_weather",
                            "arguments": {"location": "Paris", "format": "text", "unit": "celsius"},
                        },
                    }
                ],
            },
            {"role": "tool", "name": "get_current_weather", "content": "22", "tool_call_id": "azerty123"},
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                                "required": ["location"],
                            },
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                            "format": {
                                "type": "string",
                                "enum": ["text", "json"],
                                "description": "The format of the response",
                                "required": ["format"],
                            },
                        },
                    },
                },
            }
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(
            ChatCompletionRequest.from_openai(conversation, tools)
        )
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tools=tools, tokenize=False),
            expected_tokenized.text,
        )
    def test_apply_chat_template_with_image(self):
        ref_conversation = conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is this?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": IMG_URL},
                    },
                ],
            },
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(
            ChatCompletionRequest.from_openai(ref_conversation)
        )
        image_contents = [
            {
                "type": "image_url",
                "image_url": {"url": IMG_URL},
            },
            {
                "type": "image",
                "url": IMG_URL,
            },
            {"type": "image", "base64": IMG_BASE_64},
        ]
        for image_content in image_contents:
            conversation = [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "What is this?"}, image_content],
                },
            ]
            output = self.tokenizer.apply_chat_template(conversation, tokenize=True)
            self.assertEqual(output, expected_tokenized.tokens)
        output_dict = self.tokenizer.apply_chat_template(conversation, tokenize=True, return_dict=True)
        self.assertEqual(output_dict["input_ids"], expected_tokenized.tokens)
        self.assertEqual(len(output_dict["pixel_values"]), len(expected_tokenized.images))
        for o, e in zip(output_dict["pixel_values"], expected_tokenized.images):
            self.assertTrue(np.allclose(o, e))
        output_dict = self.tokenizer.apply_chat_template(
            conversation, tokenize=True, return_dict=True, return_tensors="pt"
        )
        self.assertEqual(output_dict["input_ids"].tolist()[0], expected_tokenized.tokens)
        self.assertTrue(torch.allclose(output_dict["pixel_values"], torch.tensor(expected_tokenized.images)))
    def test_apply_chat_template_with_audio(self):
        ref_conversation = conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is this?"},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": AUDIO_BASE_64,
                            "format": "wav",
                        },
                    },
                ],
            },
        ]
        expected_tokenized = self.ref_tokenizer_audio.encode_chat_completion(
            ChatCompletionRequest.from_openai(ref_conversation)
        )
        audio_contents = [
            {
                "type": "audio",
                "url": AUDIO_URL,
            },
            {
                "type": "audio",
                "path": AUDIO_URL,
            },
            {"type": "audio", "base64": AUDIO_BASE_64},
        ]
        for audio_content in audio_contents:
            conversation = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "What is this?"}, audio_content],
                },
            ]
            output = self.tokenizer_audio.apply_chat_template(conversation, tokenize=True)
            self.assertEqual(output, expected_tokenized.tokens)
        output_dict = self.tokenizer_audio.apply_chat_template(conversation, tokenize=True, return_dict=True)
        self.assertEqual(output_dict["input_ids"], expected_tokenized.tokens)
        self.assertEqual(len(output_dict["audio"]), len(expected_tokenized.audios))
        for o, e in zip(output_dict["audio"], expected_tokenized.audios):
            audio_array = e.audio_array
            self.assertTrue(np.allclose(o, audio_array))
        with self.assertRaises(NotImplementedError):
            output_dict = self.tokenizer_audio.apply_chat_template(
                conversation, tokenize=True, return_dict=True, return_tensors="pt"
            )
    def test_appsly_chat_template_with_truncation(self):
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hi!"},
            {"role": "assistant", "content": "Hello! How can I help you?"},
            {"role": "user", "content": "What is the capital of France?"},
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(ChatCompletionRequest.from_openai(conversation))
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tokenize=True, truncation=True, max_length=20),
            expected_tokenized.tokens[:20],
        )
        self.assertEqual(
            self.tokenizer.apply_chat_template(conversation, tokenize=True, truncation=False, max_length=20),
            expected_tokenized.tokens,
        )
        with self.assertRaises(ValueError):
            self.tokenizer.apply_chat_template(
                conversation, tokenize=True, truncation=TruncationStrategy.LONGEST_FIRST, max_length=20
            )
    def test_batch_apply_chat_template(self):
        conversations = [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
                {"role": "assistant", "content": "Hello! How can I help you?"},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": IMG_URL},
                        },
                    ],
                },
            ],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
                {"role": "assistant", "content": "Hello! How can I help you?"},
                {"role": "user", "content": "What is the temperature in Paris?"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "azerty123",
                            "function": {
                                "name": "get_current_weather",
                                "arguments": {"location": "Paris", "format": "text", "unit": "celsius"},
                            },
                        }
                    ],
                },
                {"role": "tool", "name": "get_current_weather", "content": "22", "tool_call_id": "azerty123"},
            ],
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current weather in a given location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                                "required": ["location"],
                            },
                            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                            "format": {
                                "type": "string",
                                "enum": ["text", "json"],
                                "description": "The format of the response",
                                "required": ["format"],
                            },
                        },
                    },
                },
            }
        ]
        expected_tokenized = [
            self.ref_tokenizer.encode_chat_completion(ChatCompletionRequest.from_openai(conversation, tools=tools))
            for conversation in conversations
        ]
        text_outputs = self.tokenizer.apply_chat_template(conversations, tools=tools, tokenize=False)
        token_outputs = self.tokenizer.apply_chat_template(conversations, tools=tools, tokenize=True)
        self.assertEqual(len(text_outputs), len(token_outputs))
        self.assertEqual(len(text_outputs), len(expected_tokenized))
        for text, token, expected in zip(text_outputs, token_outputs, expected_tokenized):
            self.assertEqual(text, expected.text)
            self.assertEqual(token, expected.tokens)
        with self.assertRaises(
            ValueError,
            msg="Kwargs [unk_args] are not supported by `MistralCommonTokenizer.batch_apply_chat_template`.",
        ):
            self.tokenizer.apply_chat_template(conversations, tools=tools, tokenize=True, unk_args="")
    def test_batch_apply_images(self):
        conversations = [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": IMG_URL},
                        },
                    ],
                },
            ],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {
                            "type": "image",
                            "url": IMG_URL,
                        },
                    ],
                },
            ],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this?"},
                        {"type": "image", "base64": IMG_BASE_64},
                    ],
                },
            ],
        ]
        ref_conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is this?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": IMG_URL},
                    },
                ],
            },
        ]
        expected_tokenized = self.ref_tokenizer.encode_chat_completion(
            ChatCompletionRequest.from_openai(ref_conversation)
        )
        output = self.tokenizer.apply_chat_template(conversations, tokenize=True)
        self.assertEqual(output, [expected_tokenized.tokens] * 3)
        output = self.tokenizer.apply_chat_template(conversations, tokenize=True, return_dict=True)
        self.assertEqual(output["input_ids"], [expected_tokenized.tokens] * 3)
        self.assertEqual(len(output["pixel_values"]), len(expected_tokenized.images) * 3)
        for o, e in zip(output["pixel_values"], [expected_tokenized.images] * 3):
            self.assertTrue(np.allclose(o, e))
        output = self.tokenizer.apply_chat_template(
            conversations, tokenize=True, return_dict=True, return_tensors="pt"
        )
        self.assertEqual(output["input_ids"].tolist(), [expected_tokenized.tokens] * 3)
        self.assertEqual(output["input_ids"].shape[0], len(expected_tokenized.images) * 3)
        self.assertTrue(torch.allclose(output["pixel_values"], torch.tensor([expected_tokenized.images] * 3)))
        output = self.tokenizer.apply_chat_template(
            conversations, tokenize=True, return_dict=True, return_tensors="np"
        )
        self.assertEqual(output["input_ids"].tolist(), [expected_tokenized.tokens] * 3)
        self.assertTrue(np.allclose(output["pixel_values"], np.array([expected_tokenized.images] * 3)))
    def test_batch_apply_chat_template_with_continue_final_message(self):
        conversations = [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
                {"role": "assistant", "content": "Hello! How can "},
            ],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi!"},
                {"role": "assistant", "content": "Hello! How can I help you? Ou préférez vous "},
            ],
        ]
        expected_tokenized = [
            self.ref_tokenizer.encode_chat_completion(
                ChatCompletionRequest.from_openai(conversation, continue_final_message=True)
            )
            for conversation in conversations
        ]
        token_outputs = self.tokenizer.apply_chat_template(conversations, tokenize=True, continue_final_message=True)
        for output, expected in zip(token_outputs, expected_tokenized):
            self.assertEqual(output, expected.tokens)
        with self.assertRaises(InvalidMessageStructureException):
            self.tokenizer.apply_chat_template(
                conversations,
                tokenize=False,
                continue_final_message=False,
            )
        with self.assertRaises(InvalidMessageStructureException):
            self.tokenizer.apply_chat_template(
                conversation=[
                    [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hi!"},
                    ]
                ],
                tokenize=True,
                continue_final_message=True,
            )
    def test_batch_apply_chat_template_with_truncation(
        self,
    ):
        token_outputs = self.tokenizer.apply_chat_template(
            self.fixture_conversations, tokenize=True, truncation=True, max_length=20
        )
        for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
            self.assertEqual(output, expected.tokens[:20])
        token_outputs = self.tokenizer.apply_chat_template(
            self.fixture_conversations, tokenize=True, truncation=False, max_length=20
        )
        self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
        for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
            self.assertEqual(output, expected.tokens)
        with self.assertRaises(ValueError):
            self.tokenizer.apply_chat_template(
                self.fixture_conversations, tokenize=True, truncation=TruncationStrategy.LONGEST_FIRST, max_length=20
            )
    def test_batch_apply_chat_template_with_padding(
        self,
    ):
        for padding in [True, "max_length", PaddingStrategy.LONGEST, PaddingStrategy.MAX_LENGTH]:
            if padding == PaddingStrategy.MAX_LENGTH:
                token_outputs = self.tokenizer.apply_chat_template(self.fixture_conversations, padding=padding)
                self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
                for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                    self.assertEqual(output, expected.tokens)
            max_length = 20 if padding == PaddingStrategy.MAX_LENGTH else None
            token_outputs = self.tokenizer.apply_chat_template(
                self.fixture_conversations, tokenize=True, padding=padding, max_length=max_length
            )
            if padding != PaddingStrategy.MAX_LENGTH:
                longest = max(len(tokenized.tokens) for tokenized in self.tokenized_fixture_conversations)
                self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
                for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                    self.assertEqual(
                        output,
                        [self.tokenizer.pad_token_id] * (longest - len(expected.tokens)) + expected.tokens,
                    )
            else:
                self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
                for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                    if len(expected.tokens) < max_length:
                        self.assertEqual(
                            output,
                            [self.tokenizer.pad_token_id] * (20 - len(expected.tokens)) + expected.tokens,
                        )
                    else:
                        self.assertEqual(output, expected.tokens)
        for padding in [False, "do_not_pad", PaddingStrategy.DO_NOT_PAD]:
            token_outputs = self.tokenizer.apply_chat_template(
                self.fixture_conversations, tokenize=True, padding=padding
            )
            self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
            for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                self.assertEqual(output, expected.tokens)
    def test_batch_apply_chat_template_with_padding_and_truncation(
        self,
    ):
        max_length = 20
        for padding in [True, "max_length", PaddingStrategy.LONGEST, PaddingStrategy.MAX_LENGTH]:
            token_outputs = self.tokenizer.apply_chat_template(
                self.fixture_conversations, tokenize=True, truncation=True, padding=padding, max_length=max_length
            )
            self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
            for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                self.assertEqual(
                    output, [self.tokenizer.pad_token_id] * (20 - len(expected.tokens)) + expected.tokens[:20]
                )
        for padding in [False, "do_not_pad", PaddingStrategy.DO_NOT_PAD]:
            token_outputs = self.tokenizer.apply_chat_template(
                self.fixture_conversations, tokenize=True, truncation=True, padding=padding, max_length=max_length
            )
            self.assertEqual(len(token_outputs), len(self.tokenized_fixture_conversations))
            for output, expected in zip(token_outputs, self.tokenized_fixture_conversations):
                self.assertEqual(output, expected.tokens[:20])
    def test_batch_apply_chat_template_return_tensors(self):
        token_outputs = self.tokenizer.apply_chat_template(
            self.fixture_conversations, tokenize=True, return_tensors="pt", padding=True
        )
        self.assertIsInstance(token_outputs, torch.Tensor)
        self.assertEqual(
            token_outputs.shape,
            (len(self.fixture_conversations), max(len(t.tokens) for t in self.tokenized_fixture_conversations)),
        )
        token_outputs = self.tokenizer.apply_chat_template(
            self.fixture_conversations, tokenize=False, return_tensors="pt", padding=True
        )
        self.assertEqual(token_outputs, [t.text for t in self.tokenized_fixture_conversations])
    def test_batch_apply_chat_template_return_dict(self):
        token_outputs = self.tokenizer.apply_chat_template(self.fixture_conversations, tokenize=True, return_dict=True)
        self.assertIn("input_ids", token_outputs)
        self.assertIn("attention_mask", token_outputs)
        self.assertEqual(token_outputs["input_ids"], [t.tokens for t in self.tokenized_fixture_conversations])
        self.assertEqual(
            token_outputs["attention_mask"], [[1] * len(t.tokens) for t in self.tokenized_fixture_conversations]
        )
        token_outputs = self.tokenizer.apply_chat_template(
            self.fixture_conversations, tokenize=False, return_dict=True
        )
        self.assertNotIsInstance(token_outputs, dict)
        self.assertEqual(token_outputs, [t.text for t in self.tokenized_fixture_conversations])
    def test_call(self):
        text = "Hello world!"
        expected_tokens = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=True, eos=True)
        tokens = self.tokenizer(text)
        self.assertIsInstance(tokens, BatchEncoding)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens))
        tokens = self.tokenizer(text, return_attention_mask=False)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertNotIn("attention_mask", tokens)
        tokens = self.tokenizer(text, return_tensors="pt")
        self.assertIsInstance(tokens["input_ids"], torch.Tensor)
        self.assertTrue(torch.equal(tokens["input_ids"], torch.Tensor(expected_tokens).unsqueeze(0)))
        self.assertIsInstance(tokens["attention_mask"], torch.Tensor)
        self.assertTrue(torch.equal(tokens["attention_mask"], torch.ones(1, len(expected_tokens))))
        tokens = self.tokenizer(text, return_special_tokens_mask=True)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens))
        self.assertEqual(tokens["special_tokens_mask"], [1] + [0] * (len(expected_tokens) - 2) + [1])
        expected_tokens = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False)
        tokens = self.tokenizer(text, add_special_tokens=False, return_special_tokens_mask=True)
        self.assertIsInstance(tokens, BatchEncoding)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens))
        self.assertEqual(tokens["special_tokens_mask"], [0] * len(expected_tokens))
        with self.assertRaises(
            ValueError, msg="Kwargs [wrong_kwarg] are not supported by `MistralCommonTokenizer.__call__`."
        ):
            self.tokenizer(text, wrong_kwarg=True)
        with self.assertRaises(
            ValueError,
            msg="`text_pair`, `text_target` and `text_pair_target` are not supported by `MistralCommonTokenizer`.",
        ):
            self.tokenizer(text, text_pair="Hello world!")
        with self.assertRaises(
            ValueError,
            msg="`text_pair`, `text_target` and `text_pair_target` are not supported by `MistralCommonTokenizer`.",
        ):
            self.tokenizer(text, text_target="Hello world!")
        with self.assertRaises(
            ValueError,
            msg="`text_pair`, `text_target` and `text_pair_target` are not supported by `MistralCommonTokenizer`.",
        ):
            self.tokenizer(text, text_pair_target="Hello world!")
    def test_call_with_truncation(self):
        text = "Hello world!" * 10
        expected_tokens = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=True, eos=True)
        for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
            tokens = self.tokenizer(text, truncation=True, max_length=10, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], expected_tokens[:10])
            self.assertEqual(tokens["attention_mask"], [1] * 10)
            self.assertEqual(tokens["special_tokens_mask"], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for truncation in [False, "do_not_truncate", TruncationStrategy.DO_NOT_TRUNCATE]:
            tokens = self.tokenizer(text, truncation=truncation, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], expected_tokens)
            self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens))
            self.assertEqual(tokens["special_tokens_mask"], [1] + [0] * (len(expected_tokens) - 2) + [1])
        for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
            for stride in [0, 2]:
                tokens = self.tokenizer(
                    text,
                    truncation=truncation,
                    max_length=10,
                    return_overflowing_tokens=True,
                    return_special_tokens_mask=True,
                    stride=stride,
                )
                self.assertIsInstance(tokens, BatchEncoding)
                self.assertEqual(tokens["input_ids"], expected_tokens[:10])
                self.assertEqual(tokens["attention_mask"], [1] * 10)
                self.assertEqual(tokens["special_tokens_mask"], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                self.assertEqual(tokens["overflowing_tokens"], expected_tokens[10 - stride :])
                self.assertEqual(tokens["num_truncated_tokens"], len(expected_tokens) - 10)
        for truncation in ["only_first", TruncationStrategy.ONLY_FIRST, "only_second", TruncationStrategy.ONLY_SECOND]:
            with self.assertRaises(
                ValueError,
                msg="Truncation strategy `only_first` and `only_second` are not supported by `MistralCommonTokenizer`.",
            ):
                self.tokenizer(text, truncation=truncation)
    def test_call_with_padding(self):
        text = "Hello world!"
        expected_tokens = self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=True, eos=True)
        for padding in [False, True, "do_not_pad", PaddingStrategy.DO_NOT_PAD, "longest", PaddingStrategy.LONGEST]:
            tokens = self.tokenizer(text, padding=padding, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], expected_tokens)
            self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens))
            self.assertEqual(tokens["special_tokens_mask"], [1] + [0] * (len(expected_tokens) - 2) + [1])
        for padding in ["max_length", PaddingStrategy.MAX_LENGTH]:
            tokens = self.tokenizer(text, padding=padding, max_length=20, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            num_padding = 20 - len(expected_tokens)
            self.assertEqual(tokens["input_ids"], num_padding * [self.tokenizer.pad_token_id] + expected_tokens)
            self.assertEqual(tokens["attention_mask"], num_padding * [0] + [1] * len(expected_tokens))
            self.assertEqual(
                tokens["special_tokens_mask"], num_padding * [1] + [1] + [0] * (len(expected_tokens) - 2) + [1]
            )
        tokens = self.tokenizer(
            text, padding=True, max_length=20, pad_to_multiple_of=16, return_special_tokens_mask=True
        )
        self.assertIsInstance(tokens, BatchEncoding)
        num_padding = 16 - len(expected_tokens)
        self.assertEqual(tokens["input_ids"], num_padding * [self.tokenizer.pad_token_id] + expected_tokens)
        self.assertEqual(tokens["attention_mask"], num_padding * [0] + [1] * len(expected_tokens))
        self.assertEqual(
            tokens["special_tokens_mask"], num_padding * [1] + [1] + [0] * (len(expected_tokens) - 2) + [1]
        )
        tokens = self.tokenizer(
            text, padding="max_length", max_length=20, padding_side="right", return_special_tokens_mask=True
        )
        self.assertIsInstance(tokens, BatchEncoding)
        num_padding = 20 - len(expected_tokens)
        self.assertEqual(tokens["input_ids"], expected_tokens + num_padding * [self.tokenizer.pad_token_id])
        self.assertEqual(tokens["attention_mask"], [1] * len(expected_tokens) + num_padding * [0])
        self.assertEqual(
            tokens["special_tokens_mask"], [1] + [0] * (len(expected_tokens) - 2) + [1] + num_padding * [1]
        )
    def test_batch_call(self):
        text = ["Hello world!", "Hello world! Longer"]
        expected_tokens = [self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(t, bos=True, eos=True) for t in text]
        tokens = self.tokenizer(text)
        self.assertIsInstance(tokens, BatchEncoding)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertEqual(tokens["attention_mask"], [[1] * len(t) for t in expected_tokens])
        tokens = self.tokenizer(text, return_attention_mask=False)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertNotIn("attention_mask", tokens)
        tokens = self.tokenizer(text, return_tensors="pt", padding="longest", return_special_tokens_mask=True)
        self.assertIsInstance(tokens["input_ids"], torch.Tensor)
        self.assertEqual(tokens["input_ids"].shape, torch.Size([2, len(expected_tokens[1])]))
        self.assertTrue(
            torch.equal(
                tokens["input_ids"][0],
                torch.Tensor(
                    (len(expected_tokens[1]) - len(expected_tokens[0]))
                    * [self.ref_tokenizer.instruct_tokenizer.tokenizer.pad_id]
                    + expected_tokens[0]
                ),
            )
        )
        self.assertIsInstance(tokens["attention_mask"], torch.Tensor)
        self.assertEqual(tokens["attention_mask"].shape, torch.Size([2, len(expected_tokens[1])]))
        self.assertTrue(
            torch.equal(
                tokens["attention_mask"][0],
                torch.Tensor(
                    [0] * (len(expected_tokens[1]) - len(expected_tokens[0])) + [1] * len(expected_tokens[0])
                ),
            )
        )
        self.assertTrue(torch.equal(tokens["attention_mask"][1], torch.Tensor([1] * len(expected_tokens[1]))))
        self.assertIsInstance(tokens["special_tokens_mask"], torch.Tensor)
        self.assertEqual(tokens["special_tokens_mask"].shape, torch.Size([2, len(expected_tokens[1])]))
        self.assertTrue(
            torch.equal(
                tokens["special_tokens_mask"][0],
                torch.Tensor(
                    (len(expected_tokens[1]) - len(expected_tokens[0])) * [1]
                    + [1]
                    + [0] * (len(expected_tokens[0]) - 2)
                    + [1]
                ),
            )
        )
        self.assertTrue(
            torch.equal(
                tokens["special_tokens_mask"][1], torch.Tensor([1] + [0] * (len(expected_tokens[1]) - 2) + [1])
            )
        )
        expected_tokens = [
            self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(t, bos=False, eos=False) for t in text
        ]
        tokens = self.tokenizer(text, add_special_tokens=False, return_special_tokens_mask=True)
        self.assertIsInstance(tokens, BatchEncoding)
        self.assertEqual(tokens["input_ids"], expected_tokens)
        self.assertEqual(tokens["attention_mask"], [[1] * len(t) for t in expected_tokens])
        self.assertEqual(tokens["special_tokens_mask"], [[0] * len(t) for t in expected_tokens])
    def test_batch_call_with_truncation(self):
        text = ["Hello world!", "Hello world! Longer" * 10]
        expected_tokens = [self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(t, bos=True, eos=True) for t in text]
        for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
            tokens = self.tokenizer(text, truncation=True, max_length=10, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], [expected_tokens[0][:10], expected_tokens[1][:10]])
            self.assertEqual(tokens["attention_mask"], [[1] * min(len(t), 10) for t in expected_tokens])
            self.assertEqual(
                tokens["special_tokens_mask"],
                [[1 if id in self.ref_special_ids else 0 for id in ids[:10]] for ids in expected_tokens],
            )
        for truncation in [False, "do_not_truncate", TruncationStrategy.DO_NOT_TRUNCATE]:
            tokens = self.tokenizer(text, truncation=truncation, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], expected_tokens)
            self.assertEqual(tokens["attention_mask"], [[1] * len(t) for t in expected_tokens])
            self.assertEqual(
                tokens["special_tokens_mask"],
                [[1] + [0] * (len(t) - 2) + [1] for t in expected_tokens],
            )
        for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
            for stride in [0, 2]:
                tokens = self.tokenizer(
                    text,
                    truncation=truncation,
                    max_length=10,
                    return_overflowing_tokens=True,
                    return_special_tokens_mask=True,
                    stride=stride,
                )
                self.assertIsInstance(tokens, BatchEncoding)
                self.assertEqual(tokens["input_ids"], [expected_tokens[0][:10], expected_tokens[1][:10]])
                self.assertEqual(tokens["attention_mask"], [[1] * min(len(t), 10) for t in expected_tokens])
                self.assertEqual(
                    tokens["overflowing_tokens"],
                    [expected_tokens[0][10 - stride :], expected_tokens[1][10 - stride :]],
                )
                self.assertEqual(
                    tokens["num_truncated_tokens"], [len(expected_tokens[0]) - 10, len(expected_tokens[1]) - 10]
                )
                self.assertEqual(
                    tokens["special_tokens_mask"],
                    [[1 if id in self.ref_special_ids else 0 for id in ids[:10]] for ids in expected_tokens],
                )
    def test_batch_call_with_padding(self):
        text = ["Hello world!", "Hello world! Longer"]
        expected_tokens = [self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(t, bos=True, eos=True) for t in text]
        for padding in [False, "do_not_pad", PaddingStrategy.DO_NOT_PAD]:
            tokens = self.tokenizer(text, padding=padding, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            self.assertEqual(tokens["input_ids"], expected_tokens)
            self.assertEqual(tokens["attention_mask"], [[1] * len(t) for t in expected_tokens])
            self.assertEqual(
                tokens["special_tokens_mask"],
                [[1] + [0] * (len(t) - 2) + [1] for t in expected_tokens],
            )
        for padding in ["max_length", PaddingStrategy.MAX_LENGTH]:
            tokens = self.tokenizer(text, padding=padding, max_length=20, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            num_padding = [20 - len(t) for t in expected_tokens]
            self.assertEqual(
                tokens["input_ids"],
                [
                    num_padding[0] * [self.tokenizer.pad_token_id] + expected_tokens[0],
                    num_padding[1] * [self.tokenizer.pad_token_id] + expected_tokens[1],
                ],
            )
            self.assertEqual(
                tokens["attention_mask"],
                [
                    num_padding[0] * [0] + [1] * len(expected_tokens[0]),
                    num_padding[1] * [0] + [1] * len(expected_tokens[1]),
                ],
            )
            self.assertEqual(
                tokens["special_tokens_mask"],
                [
                    num_padding[0] * [1] + [1] + [0] * (len(expected_tokens[0]) - 2) + [1],
                    num_padding[1] * [1] + [1] + [0] * (len(expected_tokens[1]) - 2) + [1],
                ],
            )
        for padding in [True, "longest", PaddingStrategy.LONGEST]:
            tokens = self.tokenizer(text, padding=padding, return_special_tokens_mask=True)
            self.assertIsInstance(tokens, BatchEncoding)
            num_padding = [len(expected_tokens[1]) - len(t) for t in expected_tokens]
            self.assertEqual(
                tokens["input_ids"],
                [
                    num_padding[0] * [self.tokenizer.pad_token_id] + expected_tokens[0],
                    num_padding[1] * [self.tokenizer.pad_token_id] + expected_tokens[1],
                ],
            )
            self.assertEqual(
                tokens["attention_mask"],
                [
                    num_padding[0] * [0] + [1] * len(expected_tokens[0]),
                    num_padding[1] * [0] + [1] * len(expected_tokens[1]),
                ],
            )
            self.assertEqual(
                tokens["special_tokens_mask"],
                [
                    num_padding[0] * [1] + [1] + [0] * (len(expected_tokens[0]) - 2) + [1],
                    num_padding[1] * [1] + [1] + [0] * (len(expected_tokens[1]) - 2) + [1],
                ],
            )
        tokens = self.tokenizer(
            text, padding=True, max_length=32, pad_to_multiple_of=16, return_special_tokens_mask=True
        )
        self.assertIsInstance(tokens, BatchEncoding)
        num_padding = [16 - len(t) for t in expected_tokens]
        self.assertEqual(
            tokens["input_ids"],
            [
                num_padding[0] * [self.tokenizer.pad_token_id] + expected_tokens[0],
                num_padding[1] * [self.tokenizer.pad_token_id] + expected_tokens[1],
            ],
        )
        self.assertEqual(
            tokens["attention_mask"],
            [
                num_padding[0] * [0] + [1] * len(expected_tokens[0]),
                num_padding[1] * [0] + [1] * len(expected_tokens[1]),
            ],
        )
        self.assertEqual(
            tokens["special_tokens_mask"],
            [
                num_padding[0] * [1] + [1] + [0] * (len(expected_tokens[0]) - 2) + [1],
                num_padding[1] * [1] + [1] + [0] * (len(expected_tokens[1]) - 2) + [1],
            ],
        )
        for padding in ["max_length", PaddingStrategy.MAX_LENGTH]:
            tokens = self.tokenizer(
                text, padding=padding, max_length=20, padding_side="right", return_special_tokens_mask=True
            )
            self.assertIsInstance(tokens, BatchEncoding)
            num_padding = [20 - len(t) for t in expected_tokens]
            self.assertEqual(
                tokens["input_ids"],
                [
                    expected_tokens[0] + num_padding[0] * [self.tokenizer.pad_token_id],
                    expected_tokens[1] + num_padding[1] * [self.tokenizer.pad_token_id],
                ],
            )
            self.assertEqual(
                tokens["attention_mask"],
                [
                    [1] * len(expected_tokens[0]) + num_padding[0] * [0],
                    [1] * len(expected_tokens[1]) + num_padding[1] * [0],
                ],
            )
            self.assertEqual(
                tokens["special_tokens_mask"],
                [
                    [1] + [0] * (len(expected_tokens[0]) - 2) + [1] + num_padding[0] * [1],
                    [1] + [0] * (len(expected_tokens[1]) - 2) + [1] + num_padding[1] * [1],
                ],
            )
    def test_batch_call_with_padding_and_truncation(self):
        text = ["Hello world!", "Hello world! Longer" * 10]
        expected_tokens = [self.ref_tokenizer.instruct_tokenizer.tokenizer.encode(t, bos=True, eos=True) for t in text]
        for padding in [True, "longest", PaddingStrategy.LONGEST, "max_length", PaddingStrategy.MAX_LENGTH]:
            for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
                tokens = self.tokenizer(
                    text, padding=padding, truncation=truncation, max_length=10, return_special_tokens_mask=True
                )
                num_padding = [max(0, 10 - len(t)) for t in expected_tokens]
                self.assertIsInstance(tokens, BatchEncoding)
                self.assertEqual(
                    tokens["input_ids"],
                    [num_padding[i] * [self.tokenizer.pad_token_id] + t[:10] for i, t in enumerate(expected_tokens)],
                )
                self.assertEqual(
                    tokens["attention_mask"],
                    [num_padding[i] * [0] + [1] * min(len(t), 10) for i, t in enumerate(expected_tokens)],
                )
                self.assertEqual(
                    tokens["special_tokens_mask"],
                    [
                        num_padding[i] * [1] + [1 if id in self.ref_special_ids else 0 for id in ids[:10]]
                        for i, ids in enumerate(expected_tokens)
                    ],
                )
        for padding in ["longest", PaddingStrategy.LONGEST]:
            for truncation in [True, "longest_first", TruncationStrategy.LONGEST_FIRST]:
                tokens = self.tokenizer(text, padding=padding, truncation=truncation, return_special_tokens_mask=True)
                self.assertIsInstance(tokens, BatchEncoding)
                num_padding = [max(len(t) for t in expected_tokens) - len(t) for t in expected_tokens]
                self.assertEqual(
                    tokens["input_ids"],
                    [num_padding[i] * [self.tokenizer.pad_token_id] + t for i, t in enumerate(expected_tokens)],
                )
                self.assertEqual(
                    tokens["attention_mask"],
                    [num_padding[i] * [0] + [1] * len(t) for i, t in enumerate(expected_tokens)],
                )
                self.assertEqual(
                    tokens["special_tokens_mask"],
                    [
                        num_padding[i] * [1] + [1 if id in self.ref_special_ids else 0 for id in ids]
                        for i, ids in enumerate(expected_tokens)
                    ],
                )