import collections
from typing import Optional, Union
from ...tokenization_utils_base import BatchEncoding
from ...utils import TensorType, add_end_docstrings, add_start_docstrings, logging
from ..bert.tokenization_bert_fast import BertTokenizerFast
from .tokenization_dpr import DPRContextEncoderTokenizer, DPRQuestionEncoderTokenizer, DPRReaderTokenizer
logger = logging.get_logger(__name__)
VOCAB_FILES_NAMES = {"vocab_file": "vocab.txt", "tokenizer_file": "tokenizer.json"}
class DPRContextEncoderTokenizerFast(BertTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = DPRContextEncoderTokenizer
class DPRQuestionEncoderTokenizerFast(BertTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    slow_tokenizer_class = DPRQuestionEncoderTokenizer
DPRSpanPrediction = collections.namedtuple(
    "DPRSpanPrediction", ["span_score", "relevance_score", "doc_id", "start_index", "end_index", "text"]
)
DPRReaderOutput = collections.namedtuple("DPRReaderOutput", ["start_logits", "end_logits", "relevance_logits"])
@add_start_docstrings(CUSTOM_DPR_READER_DOCSTRING)
class CustomDPRReaderTokenizerMixin:
    def __call__(
        self,
        questions,
        titles: Optional[str] = None,
        texts: Optional[str] = None,
        padding: Union[bool, str] = False,
        truncation: Union[bool, str] = False,
        max_length: Optional[int] = None,
        return_tensors: Optional[Union[str, TensorType]] = None,
        return_attention_mask: Optional[bool] = None,
        **kwargs,
    ) -> BatchEncoding:
        if titles is None and texts is None:
            return super().__call__(
                questions,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
                return_tensors=return_tensors,
                return_attention_mask=return_attention_mask,
                **kwargs,
            )
        elif titles is None or texts is None:
            text_pair = titles if texts is None else texts
            return super().__call__(
                questions,
                text_pair,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
                return_tensors=return_tensors,
                return_attention_mask=return_attention_mask,
                **kwargs,
            )
        titles = titles if not isinstance(titles, str) else [titles]
        texts = texts if not isinstance(texts, str) else [texts]
        n_passages = len(titles)
        questions = questions if not isinstance(questions, str) else [questions] * n_passages
        assert len(titles) == len(texts), (
            f"There should be as many titles than texts but got {len(titles)} titles and {len(texts)} texts."
        )
        encoded_question_and_titles = super().__call__(questions, titles, padding=False, truncation=False)["input_ids"]
        encoded_texts = super().__call__(texts, add_special_tokens=False, padding=False, truncation=False)["input_ids"]
        encoded_inputs = {
            "input_ids": [
                (encoded_question_and_title + encoded_text)[:max_length]
                if max_length is not None and truncation
                else encoded_question_and_title + encoded_text
                for encoded_question_and_title, encoded_text in zip(encoded_question_and_titles, encoded_texts)
            ]
        }
        if return_attention_mask is not False:
            attention_mask = []
            for input_ids in encoded_inputs["input_ids"]:
                attention_mask.append([int(input_id != self.pad_token_id) for input_id in input_ids])
            encoded_inputs["attention_mask"] = attention_mask
        return self.pad(encoded_inputs, padding=padding, max_length=max_length, return_tensors=return_tensors)
    def decode_best_spans(
        self,
        reader_input: BatchEncoding,
        reader_output: DPRReaderOutput,
        num_spans: int = 16,
        max_answer_length: int = 64,
        num_spans_per_passage: int = 4,
    ) -> list[DPRSpanPrediction]:
        input_ids = reader_input["input_ids"]
        start_logits, end_logits, relevance_logits = reader_output[:3]
        n_passages = len(relevance_logits)
        sorted_docs = sorted(range(n_passages), reverse=True, key=relevance_logits.__getitem__)
        nbest_spans_predictions: list[DPRReaderOutput] = []
        for doc_id in sorted_docs:
            sequence_ids = list(input_ids[doc_id])
            passage_offset = sequence_ids.index(self.sep_token_id, 2) + 1
            if sequence_ids[-1] == self.pad_token_id:
                sequence_len = sequence_ids.index(self.pad_token_id)
            else:
                sequence_len = len(sequence_ids)
            best_spans = self._get_best_spans(
                start_logits=start_logits[doc_id][passage_offset:sequence_len],
                end_logits=end_logits[doc_id][passage_offset:sequence_len],
                max_answer_length=max_answer_length,
                top_spans=num_spans_per_passage,
            )
            for start_index, end_index in best_spans:
                start_index += passage_offset
                end_index += passage_offset
                nbest_spans_predictions.append(
                    DPRSpanPrediction(
                        span_score=start_logits[doc_id][start_index] + end_logits[doc_id][end_index],
                        relevance_score=relevance_logits[doc_id],
                        doc_id=doc_id,
                        start_index=start_index,
                        end_index=end_index,
                        text=self.decode(sequence_ids[start_index : end_index + 1]),
                    )
                )
            if len(nbest_spans_predictions) >= num_spans:
                break
        return nbest_spans_predictions[:num_spans]
    def _get_best_spans(
        self,
        start_logits: list[int],
        end_logits: list[int],
        max_answer_length: int,
        top_spans: int,
    ) -> list[DPRSpanPrediction]:
        scores = []
        for start_index, start_score in enumerate(start_logits):
            for answer_length, end_score in enumerate(end_logits[start_index : start_index + max_answer_length]):
                scores.append(((start_index, start_index + answer_length), start_score + end_score))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        chosen_span_intervals = []
        for (start_index, end_index), score in scores:
            assert start_index <= end_index, f"Wrong span indices: [{start_index}:{end_index}]"
            length = end_index - start_index + 1
            assert length <= max_answer_length, f"Span is too long: {length} > {max_answer_length}"
            if any(
                start_index <= prev_start_index <= prev_end_index <= end_index
                or prev_start_index <= start_index <= end_index <= prev_end_index
                for (prev_start_index, prev_end_index) in chosen_span_intervals
            ):
                continue
            chosen_span_intervals.append((start_index, end_index))
            if len(chosen_span_intervals) == top_spans:
                break
        return chosen_span_intervals
@add_end_docstrings(CUSTOM_DPR_READER_DOCSTRING)
class DPRReaderTokenizerFast(CustomDPRReaderTokenizerMixin, BertTokenizerFast):
    vocab_files_names = VOCAB_FILES_NAMES
    model_input_names = ["input_ids", "attention_mask"]
    slow_tokenizer_class = DPRReaderTokenizer
__all__ = ["DPRContextEncoderTokenizerFast", "DPRQuestionEncoderTokenizerFast", "DPRReaderTokenizerFast"]