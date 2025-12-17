from typing import Any, Union, overload
import numpy as np
from ..utils import add_end_docstrings, is_tf_available, is_torch_available, logging
from .base import GenericTensor, Pipeline, PipelineException, build_pipeline_init_args
if is_tf_available():
    import tensorflow as tf
    from ..tf_utils import stable_softmax
if is_torch_available():
    import torch
logger = logging.get_logger(__name__)
@add_end_docstrings(
    build_pipeline_init_args(has_tokenizer=True),
,
)
class FillMaskPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = False
    _load_feature_extractor = False
    _load_tokenizer = True
    def get_masked_index(self, input_ids: GenericTensor) -> np.ndarray:
        if self.framework == "tf":
            masked_index = tf.where(input_ids == self.tokenizer.mask_token_id).numpy()
        elif self.framework == "pt":
            masked_index = torch.nonzero(input_ids == self.tokenizer.mask_token_id, as_tuple=False)
        else:
            raise ValueError("Unsupported framework")
        return masked_index
    def _ensure_exactly_one_mask_token(self, input_ids: GenericTensor) -> np.ndarray:
        masked_index = self.get_masked_index(input_ids)
        numel = np.prod(masked_index.shape)
        if numel < 1:
            raise PipelineException(
                "fill-mask",
                self.model.base_model_prefix,
                f"No mask_token ({self.tokenizer.mask_token}) found on the input",
            )
    def ensure_exactly_one_mask_token(self, model_inputs: GenericTensor):
        if isinstance(model_inputs, list):
            for model_input in model_inputs:
                self._ensure_exactly_one_mask_token(model_input["input_ids"][0])
        else:
            for input_ids in model_inputs["input_ids"]:
                self._ensure_exactly_one_mask_token(input_ids)
    def preprocess(
        self, inputs, return_tensors=None, tokenizer_kwargs=None, **preprocess_parameters
    ) -> dict[str, GenericTensor]:
        if return_tensors is None:
            return_tensors = self.framework
        if tokenizer_kwargs is None:
            tokenizer_kwargs = {}
        model_inputs = self.tokenizer(inputs, return_tensors=return_tensors, **tokenizer_kwargs)
        self.ensure_exactly_one_mask_token(model_inputs)
        return model_inputs
    def _forward(self, model_inputs):
        model_outputs = self.model(**model_inputs)
        model_outputs["input_ids"] = model_inputs["input_ids"]
        return model_outputs
    def postprocess(self, model_outputs, top_k=5, target_ids=None):
        if target_ids is not None and target_ids.shape[0] < top_k:
            top_k = target_ids.shape[0]
        input_ids = model_outputs["input_ids"][0]
        outputs = model_outputs["logits"]
        if self.framework == "tf":
            masked_index = tf.where(input_ids == self.tokenizer.mask_token_id).numpy()[:, 0]
            outputs = outputs.numpy()
            logits = outputs[0, masked_index, :]
            probs = stable_softmax(logits, axis=-1)
            if target_ids is not None:
                probs = tf.gather_nd(tf.squeeze(probs, 0), target_ids.reshape(-1, 1))
                probs = tf.expand_dims(probs, 0)
            topk = tf.math.top_k(probs, k=top_k)
            values, predictions = topk.values.numpy(), topk.indices.numpy()
        else:
            masked_index = torch.nonzero(input_ids == self.tokenizer.mask_token_id, as_tuple=False).squeeze(-1)
            logits = outputs[0, masked_index, :]
            probs = logits.softmax(dim=-1)
            if target_ids is not None:
                probs = probs[..., target_ids]
            values, predictions = probs.topk(top_k)
        result = []
        single_mask = values.shape[0] == 1
        for i, (_values, _predictions) in enumerate(zip(values.tolist(), predictions.tolist())):
            row = []
            for v, p in zip(_values, _predictions):
                tokens = input_ids.numpy().copy()
                if target_ids is not None:
                    p = target_ids[p].tolist()
                tokens[masked_index[i]] = p
                tokens = tokens[np.where(tokens != self.tokenizer.pad_token_id)]
                sequence = self.tokenizer.decode(tokens, skip_special_tokens=single_mask)
                proposition = {"score": v, "token": p, "token_str": self.tokenizer.decode([p]), "sequence": sequence}
                row.append(proposition)
            result.append(row)
        if single_mask:
            return result[0]
        return result
    def get_target_ids(self, targets):
        if isinstance(targets, str):
            targets = [targets]
        try:
            vocab = self.tokenizer.get_vocab()
        except Exception:
            vocab = {}
        target_ids = []
        for target in targets:
            id_ = vocab.get(target)
            if id_ is None:
                input_ids = self.tokenizer(
                    target,
                    add_special_tokens=False,
                    return_attention_mask=False,
                    return_token_type_ids=False,
                    max_length=1,
                    truncation=True,
                )["input_ids"]
                if len(input_ids) == 0:
                    logger.warning(
                        f"The specified target token `{target}` does not exist in the model vocabulary. "
                        "We cannot replace it with anything meaningful, ignoring it"
                    )
                    continue
                id_ = input_ids[0]
                logger.warning(
                    f"The specified target token `{target}` does not exist in the model vocabulary. "
                    f"Replacing with `{self.tokenizer.convert_ids_to_tokens(id_)}`."
                )
            target_ids.append(id_)
        target_ids = list(set(target_ids))
        if len(target_ids) == 0:
            raise ValueError("At least one target must be provided when passed.")
        target_ids = np.array(target_ids)
        return target_ids
    def _sanitize_parameters(self, top_k=None, targets=None, tokenizer_kwargs=None):
        preprocess_params = {}
        if tokenizer_kwargs is not None:
            preprocess_params["tokenizer_kwargs"] = tokenizer_kwargs
        postprocess_params = {}
        if targets is not None:
            target_ids = self.get_target_ids(targets)
            postprocess_params["target_ids"] = target_ids
        if top_k is not None:
            postprocess_params["top_k"] = top_k
        if self.tokenizer.mask_token_id is None:
            raise PipelineException(
                "fill-mask", self.model.base_model_prefix, "The tokenizer does not define a `mask_token`."
            )
        return preprocess_params, {}, postprocess_params
    @overload
    def __call__(self, inputs: str, **kwargs: Any) -> list[dict[str, Any]]: ...
    @overload
    def __call__(self, inputs: list[str], **kwargs: Any) -> list[list[dict[str, Any]]]: ...
    def __call__(
        self, inputs: Union[str, list[str]], **kwargs: Any
    ) -> Union[list[dict[str, Any]], list[list[dict[str, Any]]]]:
        outputs = super().__call__(inputs, **kwargs)
        if isinstance(inputs, list) and len(inputs) == 1:
            return outputs[0]
        return outputs