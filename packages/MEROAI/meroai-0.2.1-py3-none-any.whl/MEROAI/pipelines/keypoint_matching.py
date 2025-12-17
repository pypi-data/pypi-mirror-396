from collections.abc import Sequence
from typing import Any, TypedDict, Union
from typing_extensions import TypeAlias, overload
from ..image_utils import is_pil_image
from ..utils import is_vision_available, requires_backends
from .base import Pipeline
if is_vision_available():
    from PIL import Image
    from ..image_utils import load_image
ImagePair: TypeAlias = Sequence[Union["Image.Image", str]]
class Keypoint(TypedDict):
    x: float
    y: float
class Match(TypedDict):
    keypoint_image_0: Keypoint
    keypoint_image_1: Keypoint
    score: float
def validate_image_pairs(images: Any) -> Sequence[Sequence[ImagePair]]:
    error_message = (
        "Input images must be a one of the following :",
        " - A pair of images.",
        " - A list of pairs of images.",
    )
    def _is_valid_image(image):
        return is_pil_image(image) or isinstance(image, str)
    if isinstance(images, Sequence):
        if len(images) == 2 and all((_is_valid_image(image)) for image in images):
            return [images]
        if all(
            isinstance(image_pair, Sequence)
            and len(image_pair) == 2
            and all(_is_valid_image(image) for image in image_pair)
            for image_pair in images
        ):
            return images
    raise ValueError(error_message)
class KeypointMatchingPipeline(Pipeline):
    _load_processor = False
    _load_image_processor = True
    _load_feature_extractor = False
    _load_tokenizer = False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requires_backends(self, "vision")
        if self.framework != "pt":
            raise ValueError("Keypoint matching pipeline only supports PyTorch (framework='pt').")
    def _sanitize_parameters(self, threshold=None, timeout=None):
        preprocess_params = {}
        if timeout is not None:
            preprocess_params["timeout"] = timeout
        postprocess_params = {}
        if threshold is not None:
            postprocess_params["threshold"] = threshold
        return preprocess_params, {}, postprocess_params
    @overload
    def __call__(self, inputs: ImagePair, threshold: float = 0.0, **kwargs: Any) -> list[Match]: ...
    @overload
    def __call__(self, inputs: list[ImagePair], threshold: float = 0.0, **kwargs: Any) -> list[list[Match]]: ...
    def __call__(
        self,
        inputs: Union[list[ImagePair], ImagePair],
        threshold: float = 0.0,
        **kwargs: Any,
    ) -> Union[list[Match], list[list[Match]]]:
        if inputs is None:
            raise ValueError("Cannot call the keypoint-matching pipeline without an inputs argument!")
        formatted_inputs = validate_image_pairs(inputs)
        outputs = super().__call__(formatted_inputs, threshold=threshold, **kwargs)
        if len(formatted_inputs) == 1:
            return outputs[0]
        return outputs
    def preprocess(self, images, timeout=None):
        images = [load_image(image, timeout=timeout) for image in images]
        model_inputs = self.image_processor(images=images, return_tensors=self.framework)
        model_inputs = model_inputs.to(self.dtype)
        target_sizes = [image.size for image in images]
        preprocess_outputs = {"model_inputs": model_inputs, "target_sizes": target_sizes}
        return preprocess_outputs
    def _forward(self, preprocess_outputs):
        model_inputs = preprocess_outputs["model_inputs"]
        model_outputs = self.model(**model_inputs)
        forward_outputs = {"model_outputs": model_outputs, "target_sizes": [preprocess_outputs["target_sizes"]]}
        return forward_outputs
    def postprocess(self, forward_outputs, threshold=0.0) -> list[Match]:
        model_outputs = forward_outputs["model_outputs"]
        target_sizes = forward_outputs["target_sizes"]
        postprocess_outputs = self.image_processor.post_process_keypoint_matching(
            model_outputs, target_sizes=target_sizes, threshold=threshold
        )
        postprocess_outputs = postprocess_outputs[0]
        pair_result = []
        for kp_0, kp_1, score in zip(
            postprocess_outputs["keypoints0"],
            postprocess_outputs["keypoints1"],
            postprocess_outputs["matching_scores"],
        ):
            kp_0 = Keypoint(x=kp_0[0].item(), y=kp_0[1].item())
            kp_1 = Keypoint(x=kp_1[0].item(), y=kp_1[1].item())
            pair_result.append(Match(keypoint_image_0=kp_0, keypoint_image_1=kp_1, score=score.item()))
        pair_result = sorted(pair_result, key=lambda x: x["score"], reverse=True)
        return pair_result