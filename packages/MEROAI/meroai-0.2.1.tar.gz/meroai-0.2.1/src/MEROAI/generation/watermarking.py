import collections
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Optional, Union
import numpy as np
import torch
from torch import nn
from torch.nn import BCELoss
from ..modeling_utils import PreTrainedModel
from ..utils import ModelOutput, logging
from .configuration_utils import PretrainedConfig, WatermarkingConfig
from .logits_process import SynthIDTextWatermarkLogitsProcessor, WatermarkLogitsProcessor
logger = logging.get_logger(__name__)
@dataclass
class WatermarkDetectorOutput:
    num_tokens_scored: Optional[np.ndarray] = None
    num_green_tokens: Optional[np.ndarray] = None
    green_fraction: Optional[np.ndarray] = None
    z_score: Optional[np.ndarray] = None
    p_value: Optional[np.ndarray] = None
    prediction: Optional[np.ndarray] = None
    confidence: Optional[np.ndarray] = None
class WatermarkDetector:
    def __init__(
        self,
        model_config: PretrainedConfig,
        device: str,
        watermarking_config: Union[WatermarkingConfig, dict],
        ignore_repeated_ngrams: bool = False,
        max_cache_size: int = 128,
    ):
        if isinstance(watermarking_config, WatermarkingConfig):
            watermarking_config = watermarking_config.to_dict()
        self.bos_token_id = (
            model_config.bos_token_id if not model_config.is_encoder_decoder else model_config.decoder_start_token_id
        )
        self.greenlist_ratio = watermarking_config["greenlist_ratio"]
        self.ignore_repeated_ngrams = ignore_repeated_ngrams
        self.processor = WatermarkLogitsProcessor(
            vocab_size=model_config.vocab_size, device=device, **watermarking_config
        )
        self._get_ngram_score_cached = lru_cache(maxsize=max_cache_size)(self._get_ngram_score)
    def _get_ngram_score(self, prefix: torch.LongTensor, target: int):
        greenlist_ids = self.processor._get_greenlist_ids(prefix)
        return target in greenlist_ids
    def _score_ngrams_in_passage(self, input_ids: torch.LongTensor):
        batch_size, seq_length = input_ids.shape
        selfhash = int(self.processor.seeding_scheme == "selfhash")
        n = self.processor.context_width + 1 - selfhash
        indices = torch.arange(n).unsqueeze(0) + torch.arange(seq_length - n + 1).unsqueeze(1)
        ngram_tensors = input_ids[:, indices]
        num_tokens_scored_batch = np.zeros(batch_size)
        green_token_count_batch = np.zeros(batch_size)
        for batch_idx in range(ngram_tensors.shape[0]):
            frequencies_table = collections.Counter(ngram_tensors[batch_idx])
            ngram_to_watermark_lookup = {}
            for ngram_example in frequencies_table:
                prefix = ngram_example if selfhash else ngram_example[:-1]
                target = ngram_example[-1]
                ngram_to_watermark_lookup[ngram_example] = self._get_ngram_score_cached(prefix, target)
            if self.ignore_repeated_ngrams:
                num_tokens_scored_batch[batch_idx] = len(frequencies_table.keys())
                green_token_count_batch[batch_idx] = sum(ngram_to_watermark_lookup.values())
            else:
                num_tokens_scored_batch[batch_idx] = sum(frequencies_table.values())
                green_token_count_batch[batch_idx] = sum(
                    freq * outcome
                    for freq, outcome in zip(frequencies_table.values(), ngram_to_watermark_lookup.values())
                )
        return num_tokens_scored_batch, green_token_count_batch
    def _compute_z_score(self, green_token_count: np.ndarray, total_num_tokens: np.ndarray) -> np.ndarray:
        expected_count = self.greenlist_ratio
        numer = green_token_count - expected_count * total_num_tokens
        denom = np.sqrt(total_num_tokens * expected_count * (1 - expected_count))
        z = numer / denom
        return z
    def _compute_pval(self, x, loc=0, scale=1):
        z = (x - loc) / scale
        return 1 - (0.5 * (1 + np.sign(z) * (1 - np.exp(-2 * z**2 / np.pi))))
    def __call__(
        self,
        input_ids: torch.LongTensor,
        z_threshold: float = 3.0,
        return_dict: bool = False,
    ) -> Union[WatermarkDetectorOutput, np.ndarray]:
        if input_ids[0, 0] == self.bos_token_id:
            input_ids = input_ids[:, 1:]
        if input_ids.shape[-1] - self.processor.context_width < 1:
            raise ValueError(
                f"Must have at least `1` token to score after the first "
                f"min_prefix_len={self.processor.context_width} tokens required by the seeding scheme."
            )
        num_tokens_scored, green_token_count = self._score_ngrams_in_passage(input_ids)
        z_score = self._compute_z_score(green_token_count, num_tokens_scored)
        prediction = z_score > z_threshold
        if return_dict:
            p_value = self._compute_pval(z_score)
            confidence = 1 - p_value
            return WatermarkDetectorOutput(
                num_tokens_scored=num_tokens_scored,
                num_green_tokens=green_token_count,
                green_fraction=green_token_count / num_tokens_scored,
                z_score=z_score,
                p_value=p_value,
                prediction=prediction,
                confidence=confidence,
            )
        return prediction
class BayesianDetectorConfig(PretrainedConfig):
    def __init__(self, watermarking_depth: Optional[int] = None, base_rate: float = 0.5, **kwargs):
        self.watermarking_depth = watermarking_depth
        self.base_rate = base_rate
        self.model_name = None
        self.watermarking_config = None
        super().__init__(**kwargs)
    def set_detector_information(self, model_name, watermarking_config):
        self.model_name = model_name
        self.watermarking_config = watermarking_config
@dataclass
class BayesianWatermarkDetectorModelOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    posterior_probabilities: Optional[torch.FloatTensor] = None
class BayesianDetectorWatermarkedLikelihood(nn.Module):
    def __init__(self, watermarking_depth: int):
        super().__init__()
        self.watermarking_depth = watermarking_depth
        self.beta = torch.nn.Parameter(-2.5 + 0.001 * torch.randn(1, 1, watermarking_depth))
        self.delta = torch.nn.Parameter(0.001 * torch.randn(1, 1, self.watermarking_depth, watermarking_depth))
    def _compute_latents(self, g_values: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = torch.repeat_interleave(torch.unsqueeze(g_values, dim=-2), self.watermarking_depth, axis=-2)
        x = torch.tril(x, diagonal=-1)
        logits = (self.delta[..., None, :] @ x.type(self.delta.dtype)[..., None]).squeeze() + self.beta
        p_two_unique_tokens = torch.sigmoid(logits)
        p_one_unique_token = 1 - p_two_unique_tokens
        return p_one_unique_token, p_two_unique_tokens
    def forward(self, g_values: torch.Tensor) -> torch.Tensor:
        p_one_unique_token, p_two_unique_tokens = self._compute_latents(g_values)
        return 0.5 * ((g_values + 0.5) * p_two_unique_tokens + p_one_unique_token)
class BayesianDetectorModel(PreTrainedModel):
    config: BayesianDetectorConfig
    base_model_prefix = "model"
    def __init__(self, config):
        super().__init__(config)
        self.watermarking_depth = config.watermarking_depth
        self.base_rate = config.base_rate
        self.likelihood_model_watermarked = BayesianDetectorWatermarkedLikelihood(
            watermarking_depth=self.watermarking_depth
        )
        self.prior = torch.nn.Parameter(torch.tensor([self.base_rate]))
    def _init_weights(self, module):
        if isinstance(module, nn.Parameter):
            module.weight.data.normal_(mean=0.0, std=0.02)
    def _compute_posterior(
        self,
        likelihoods_watermarked: torch.Tensor,
        likelihoods_unwatermarked: torch.Tensor,
        mask: torch.Tensor,
        prior: float,
    ) -> torch.Tensor:
        mask = torch.unsqueeze(mask, dim=-1)
        prior = torch.clamp(prior, min=1e-5, max=1 - 1e-5)
        log_likelihoods_watermarked = torch.log(torch.clamp(likelihoods_watermarked, min=1e-30, max=float("inf")))
        log_likelihoods_unwatermarked = torch.log(torch.clamp(likelihoods_unwatermarked, min=1e-30, max=float("inf")))
        log_odds = log_likelihoods_watermarked - log_likelihoods_unwatermarked
        relative_surprisal_likelihood = torch.einsum("i...->i", log_odds * mask)
        relative_surprisal_prior = torch.log(prior) - torch.log(1 - prior)
        relative_surprisal = relative_surprisal_prior + relative_surprisal_likelihood
        return torch.sigmoid(relative_surprisal)
    def forward(
        self,
        g_values: torch.Tensor,
        mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
        loss_batch_weight=1,
        return_dict=False,
    ) -> BayesianWatermarkDetectorModelOutput:
        likelihoods_watermarked = self.likelihood_model_watermarked(g_values)
        likelihoods_unwatermarked = 0.5 * torch.ones_like(g_values)
        out = self._compute_posterior(
            likelihoods_watermarked=likelihoods_watermarked,
            likelihoods_unwatermarked=likelihoods_unwatermarked,
            mask=mask,
            prior=self.prior,
        )
        loss = None
        if labels is not None:
            loss_fct = BCELoss()
            loss_unwweight = torch.sum(self.likelihood_model_watermarked.delta**2)
            loss_weight = loss_unwweight * loss_batch_weight
            loss = loss_fct(torch.clamp(out, 1e-5, 1 - 1e-5), labels) + loss_weight
        if not return_dict:
            return (out,) if loss is None else (out, loss)
        return BayesianWatermarkDetectorModelOutput(loss=loss, posterior_probabilities=out)
class SynthIDTextWatermarkDetector:
    def __init__(
        self,
        detector_module: BayesianDetectorModel,
        logits_processor: SynthIDTextWatermarkLogitsProcessor,
        tokenizer: Any,
    ):
        self.detector_module = detector_module
        self.logits_processor = logits_processor
        self.tokenizer = tokenizer
    def __call__(self, tokenized_outputs: torch.Tensor):
        eos_token_mask = self.logits_processor.compute_eos_token_mask(
            input_ids=tokenized_outputs,
            eos_token_id=self.tokenizer.eos_token_id,
        )[:, self.logits_processor.ngram_len - 1 :]
        context_repetition_mask = self.logits_processor.compute_context_repetition_mask(
            input_ids=tokenized_outputs,
        )
        combined_mask = context_repetition_mask * eos_token_mask
        g_values = self.logits_processor.compute_g_values(
            input_ids=tokenized_outputs,
        )
        return self.detector_module(g_values, combined_mask)