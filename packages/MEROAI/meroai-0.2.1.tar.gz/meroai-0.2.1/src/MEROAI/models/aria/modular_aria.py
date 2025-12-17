from collections.abc import Iterable
from typing import Optional, Union
import numpy as np
import torch
from torch import nn
from ...activations import ACT2FN
from ...cache_utils import Cache
from ...configuration_utils import PretrainedConfig
from ...image_processing_utils import BaseImageProcessor, BatchFeature, get_patch_output_size, select_best_resolution
from ...image_transforms import PaddingMode, convert_to_rgb, pad, resize, to_channel_dimension_format
from ...image_utils import (
    ChannelDimension,
    ImageInput,
    PILImageResampling,
    get_image_size,
    infer_channel_dimension_format,
    is_scaled_image,
    make_flat_list_of_images,
    to_numpy_array,
    valid_images,
    validate_preprocess_arguments,
)
from ...modeling_flash_attention_utils import FlashAttentionKwargs
from ...modeling_utils import PreTrainedModel
from ...processing_utils import MultiModalData, ProcessingKwargs, ProcessorMixin, Unpack
from ...tokenization_utils import PreTokenizedInput, TextInput
from ...utils import TensorType, MEROAIKwargs, auto_docstring, can_return_tuple, logging
from ..auto import CONFIG_MAPPING, AutoConfig, AutoTokenizer
from ..llama.configuration_llama import LlamaConfig
from ..llama.modeling_llama import (
    LlamaAttention,
    LlamaDecoderLayer,
    LlamaForCausalLM,
    LlamaMLP,
    LlamaModel,
    LlamaPreTrainedModel,
    LlamaRMSNorm,
)
from ..llava.modeling_llava import (
    LlavaCausalLMOutputWithPast,
    LlavaForConditionalGeneration,
    LlavaModel,
    LlavaModelOutputWithPast,
)
from ..llava_next.image_processing_llava_next import divide_to_patches
logger = logging.get_logger(__name__)
def sequential_experts_gemm(token_states, expert_weights, tokens_per_expert):
    num_tokens = token_states.shape[0]
    out_features = expert_weights.shape[-1]
    output = torch.zeros(num_tokens, out_features, dtype=token_states.dtype, device=token_states.device)
    cumsum_num_tokens = torch.cumsum(tokens_per_expert, dim=0)
    zero_tensor = torch.zeros(1, dtype=torch.long, device=cumsum_num_tokens.device)
    cumsum_num_tokens = torch.cat((zero_tensor, cumsum_num_tokens))
    for expert_num in range(expert_weights.shape[0]):
        start = cumsum_num_tokens[expert_num]
        end = cumsum_num_tokens[expert_num + 1]
        tokens = token_states[start:end]
        out = torch.matmul(tokens, expert_weights[expert_num])
        output[start:end] = out
    return output
class AriaTextConfig(LlamaConfig):
    model_type = "aria_text"
    base_config_key = "text_config"
    def __init__(
        self,
        intermediate_size: int = 4096,
        moe_num_experts: int = 8,
        moe_topk: int = 2,
        moe_num_shared_experts: int = 2,
        pad_token_id=2,
        **super_kwargs,
    ):
        super().__init__(pad_token_id=pad_token_id, **super_kwargs)
        self.intermediate_size = intermediate_size
        self.moe_num_experts = moe_num_experts
        self.moe_topk = moe_topk
        self.moe_num_shared_experts = moe_num_shared_experts
class AriaConfig(PretrainedConfig):
    model_type = "aria"
    attribute_map = {
        "image_token_id": "image_token_index",
    }
    sub_configs = {"text_config": AriaTextConfig, "vision_config": AutoConfig}
    def __init__(
        self,
        vision_config=None,
        vision_feature_layer: int = -1,
        text_config: AriaTextConfig = None,
        projector_patch_to_query_dict: Optional[dict] = None,
        image_token_index: int = 9,
        initializer_range: float = 0.02,
        **kwargs,
    ):
        self.image_token_index = image_token_index
        if projector_patch_to_query_dict is None:
            projector_patch_to_query_dict = {
                1225: 128,
                4900: 256,
            }
        self.projector_patch_to_query_dict = {int(k): int(v) for k, v in projector_patch_to_query_dict.items()}
        self.max_value_projector_patch_to_query_dict = max(self.projector_patch_to_query_dict.values())
        self.vision_feature_layer = vision_feature_layer
        if isinstance(vision_config, dict):
            vision_config["model_type"] = "idefics3_vision"
            vision_config = CONFIG_MAPPING[vision_config["model_type"]](**vision_config)
        elif vision_config is None:
            vision_config = CONFIG_MAPPING["idefics3_vision"]()
        self.vision_config = vision_config
        self.initializer_range = initializer_range
        if isinstance(text_config, dict) and "model_type" in text_config:
            text_config = AriaTextConfig(**text_config)
        elif text_config is None:
            text_config = AriaTextConfig()
        self.text_config = text_config
        super().__init__(**kwargs)
class AriaTextRMSNorm(LlamaRMSNorm):
    pass
class AriaProjectorMLP(nn.Module):
    def __init__(self, in_features, hidden_features, output_dim):
        super().__init__()
        self.linear_in = nn.Linear(in_features, hidden_features, bias=False)
        self.linear_out = nn.Linear(hidden_features, output_dim, bias=False)
        self.act = ACT2FN["gelu_new"]
    def forward(self, hidden_states):
        hidden_states = self.act(self.linear_in(hidden_states))
        hidden_states = self.linear_out(hidden_states)
        return hidden_states
class AriaCrossAttention(nn.Module):
    def __init__(self, config: AriaConfig, dropout_rate: float = 0):
        super().__init__()
        hidden_size = config.vision_config.hidden_size
        num_heads = config.vision_config.num_attention_heads
        self.num_heads = num_heads
        self.q_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.k_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.v_proj = nn.Linear(hidden_size, hidden_size, bias=False)
        self.multihead_attn = nn.MultiheadAttention(hidden_size, num_heads, batch_first=True)
        self.linear = nn.Linear(hidden_size, hidden_size)
        self.dropout = nn.Dropout(dropout_rate)
        self.layer_norm = nn.LayerNorm(hidden_size)
        self.layer_norm_kv = nn.LayerNorm(hidden_size)
    def forward(self, key_value_states, hidden_states, attn_mask=None):
        query = self.q_proj(self.layer_norm(hidden_states))
        key_value_states = self.layer_norm_kv(key_value_states)
        key = self.k_proj(key_value_states)
        value = self.v_proj(key_value_states)
        attn_output, _ = self.multihead_attn(query, key, value, attn_mask=attn_mask)
        attn_output = self.dropout(self.linear(attn_output))
        return attn_output
class AriaProjector(nn.Module):
    def __init__(
        self,
        config: AriaConfig,
    ):
        super().__init__()
        self.patch_to_query_dict = config.projector_patch_to_query_dict
        self.in_features = config.vision_config.hidden_size
        self.num_heads = config.vision_config.num_attention_heads
        self.kv_dim = config.vision_config.hidden_size
        self.hidden_features = config.text_config.hidden_size
        self.output_dim = config.text_config.hidden_size
        self.query = nn.Parameter(torch.zeros(config.max_value_projector_patch_to_query_dict, self.in_features))
        self.cross_attn = AriaCrossAttention(config)
        self.layer_norm = nn.LayerNorm(self.in_features)
        self.feed_forward = AriaProjectorMLP(self.in_features, self.hidden_features, self.output_dim)
    def forward(self, key_value_states: torch.Tensor, attn_mask: Optional[torch.Tensor] = None):
        batch_size, num_patches = key_value_states.shape[0], key_value_states.shape[1]
        if num_patches not in self.patch_to_query_dict:
            raise KeyError(
                f"Number of patches {num_patches} not found in patch_to_query_dict amongst possible values {self.patch_to_query_dict.keys()}."
            )
        query_num = self.patch_to_query_dict[num_patches]
        queries = self.query[:query_num].unsqueeze(0).repeat(batch_size, 1, 1)
        if attn_mask is not None:
            attn_mask = attn_mask.repeat_interleave(self.num_heads, 0)
            attn_mask = attn_mask.unsqueeze(1).expand(-1, queries.size(1), -1)
        attention_out = self.cross_attn(key_value_states, queries, attn_mask=attn_mask)
        out = self.feed_forward(self.layer_norm(attention_out))
        return out
class AriaImageProcessor(BaseImageProcessor):
    model_input_names = ["pixel_values", "pixel_mask", "num_crops"]
    def __init__(
        self,
        image_mean: Optional[list[float]] = None,
        image_std: Optional[list[float]] = None,
        max_image_size: int = 980,
        min_image_size: int = 336,
        split_resolutions: Optional[list[tuple[int, int]]] = None,
        split_image: Optional[bool] = False,
        do_convert_rgb: Optional[bool] = True,
        do_rescale: bool = True,
        rescale_factor: Union[int, float] = 1 / 255,
        do_normalize: Optional[bool] = True,
        resample: PILImageResampling = PILImageResampling.BICUBIC,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if image_mean is None:
            image_mean = [0.5, 0.5, 0.5]
        if image_std is None:
            image_std = [0.5, 0.5, 0.5]
        self.max_image_size = max_image_size
        self.min_image_size = min_image_size
        self.image_mean = image_mean
        self.image_std = image_std
        self.split_image = split_image
        if split_resolutions is None:
            split_resolutions = [(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (2, 4), (2, 3), (2, 2), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (6, 1), (7, 1), (8, 1)]
            split_resolutions = [(el[0] * 490, el[1] * 490) for el in split_resolutions]
        self.split_resolutions = split_resolutions
        self.do_convert_rgb = do_convert_rgb
        self.do_rescale = do_rescale
        self.rescale_factor = rescale_factor
        self.do_normalize = do_normalize
        self.resample = resample
    def preprocess(
        self,
        images: Union[ImageInput, list[ImageInput]],
        image_mean: Optional[Union[float, list[float]]] = None,
        image_std: Optional[Union[float, list[float]]] = None,
        max_image_size: Optional[int] = None,
        min_image_size: Optional[int] = None,
        split_image: Optional[bool] = None,
        do_convert_rgb: Optional[bool] = None,
        do_rescale: Optional[bool] = None,
        rescale_factor: Optional[float] = None,
        do_normalize: Optional[bool] = None,
        resample: Optional[PILImageResampling] = None,
        return_tensors: Optional[Union[str, TensorType]] = "pt",
        data_format: Optional[ChannelDimension] = ChannelDimension.FIRST,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ):
        image_mean = image_mean if image_mean is not None else self.image_mean
        image_std = image_std if image_std is not None else self.image_std
        max_image_size = max_image_size if max_image_size is not None else self.max_image_size
        min_image_size = min_image_size if min_image_size is not None else self.min_image_size
        split_image = split_image if split_image is not None else self.split_image
        do_convert_rgb = do_convert_rgb if do_convert_rgb is not None else self.do_convert_rgb
        do_rescale = do_rescale if do_rescale is not None else self.do_rescale
        rescale_factor = rescale_factor if rescale_factor is not None else self.rescale_factor
        do_normalize = do_normalize if do_normalize is not None else self.do_normalize
        resample = resample if resample is not None else self.resample
        if max_image_size not in [490, 980]:
            raise ValueError("max_image_size must be either 490 or 980")
        images = self.fetch_images(images)
        images = make_flat_list_of_images(images)
        if not valid_images(images):
            raise ValueError(
                "Invalid image type. Must be of type PIL.Image.Image, numpy.ndarray, "
                "torch.Tensor, tf.Tensor or jax.ndarray."
            )
        validate_preprocess_arguments(
            do_normalize=do_normalize,
            image_mean=image_mean,
            image_std=image_std,
            resample=resample,
            do_rescale=do_rescale,
            rescale_factor=rescale_factor,
        )
        if do_convert_rgb:
            images = [convert_to_rgb(image) for image in images]
        images = [to_numpy_array(image) for image in images]
        if do_rescale and is_scaled_image(images[0]):
            logger.warning_once(
                "It looks like you are trying to rescale already rescaled images. If the input"
                " images have pixel values between 0 and 1, set `do_rescale=False` to avoid rescaling them again."
            )
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(images[0])
        pixel_values = []
        pixel_masks = []
        num_crops = None
        for image in images:
            if split_image:
                crop_images = self.get_image_patches(
                    image,
                    self.split_resolutions,
                    max_image_size,
                    resample,
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
            else:
                crop_images = [image]
            if num_crops is None or len(crop_images) > num_crops:
                num_crops = len(crop_images)
            for crop_image in crop_images:
                h, w = get_image_size(crop_image)
                scale = max_image_size / max(h, w)
                if w >= h:
                    new_size = (max(int(h * scale), min_image_size), max_image_size)
                else:
                    new_size = (max_image_size, max(int(w * scale), min_image_size))
                crop_image_resized = resize(
                    crop_image,
                    new_size,
                    resample=resample,
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
                padding_bottom, padding_right = max_image_size - new_size[0], max_image_size - new_size[1]
                crop_image_padded = pad(
                    crop_image_resized,
                    ((0, padding_bottom), (0, padding_right)),
                    data_format=input_data_format,
                    input_data_format=input_data_format,
                )
                pixel_mask = np.zeros((max_image_size, max_image_size), dtype=bool)
                pixel_mask[: new_size[0], : new_size[1]] = 1
                pixel_masks.append(pixel_mask)
                if do_rescale:
                    crop_image_padded = self.rescale(
                        image=crop_image_padded, scale=rescale_factor, input_data_format=input_data_format
                    )
                if do_normalize:
                    crop_image_padded = self.normalize(
                        crop_image_padded,
                        self.image_mean,
                        self.image_std,
                        data_format=input_data_format,
                        input_data_format=input_data_format,
                    )
                    crop_image_padded = (
                        to_channel_dimension_format(crop_image_padded, data_format, input_data_format)
                        if data_format is not None
                        else crop_image_padded
                    )
                pixel_values.append(crop_image_padded)
        return BatchFeature(
            data={
                "pixel_values": np.stack(pixel_values, axis=0),
                "pixel_mask": np.stack(pixel_masks, axis=0),
                "num_crops": num_crops,
            },
            tensor_type=return_tensors,
        )
    def _resize_for_patching(
        self, image: np.ndarray, target_resolution: tuple, resample, input_data_format: ChannelDimension
    ) -> np.ndarray:
        new_height, new_width = get_patch_output_size(image, target_resolution, input_data_format)
        resized_image = resize(image, (new_height, new_width), resample=resample, input_data_format=input_data_format)
        return resized_image
    def _get_padding_size(self, original_resolution: tuple, target_resolution: tuple):
        original_height, original_width = original_resolution
        target_height, target_width = target_resolution
        paste_x, r_x = divmod(target_width - original_width, 2)
        paste_y, r_y = divmod(target_height - original_height, 2)
        return (paste_y, paste_y + r_y), (paste_x, paste_x + r_x)
    def _pad_for_patching(
        self, image: np.ndarray, target_resolution: tuple, input_data_format: ChannelDimension
    ) -> np.ndarray:
        new_resolution = get_patch_output_size(image, target_resolution, input_data_format)
        padding = self._get_padding_size(new_resolution, target_resolution)
        padded_image = self.pad(image, padding=padding)
        return padded_image
    def pad(
        self,
        image: np.ndarray,
        padding: Union[int, tuple[int, int], Iterable[tuple[int, int]]],
        mode: PaddingMode = PaddingMode.CONSTANT,
        constant_values: Union[float, Iterable[float]] = 0.0,
        data_format: Optional[Union[str, ChannelDimension]] = None,
        input_data_format: Optional[Union[str, ChannelDimension]] = None,
    ) -> np.ndarray:
        if isinstance(padding, int) or len(padding) != 4:
            return pad(image, padding, mode, constant_values, data_format, input_data_format)
        if input_data_format is None:
            input_data_format = infer_channel_dimension_format(image)
        padding_mode_mapping = {
            PaddingMode.CONSTANT: "constant",
            PaddingMode.REFLECT: "reflect",
            PaddingMode.REPLICATE: "edge",
            PaddingMode.SYMMETRIC: "symmetric",
        }
        image = np.pad(image, padding, mode=padding_mode_mapping[mode], constant_values=constant_values)
        image = (
            to_channel_dimension_format(image, data_format, input_data_format) if data_format is not None else image
        )
        return image
    def get_image_patches(
        self,
        image: np.ndarray,
        grid_pinpoints: list[tuple[int, int]],
        patch_size: int,
        resample: PILImageResampling,
        data_format: ChannelDimension,
        input_data_format: ChannelDimension,
    ) -> list[np.ndarray]:
        if not isinstance(grid_pinpoints, list):
            raise TypeError("grid_pinpoints must be a list of possible resolutions.")
        possible_resolutions = grid_pinpoints
        image_size = get_image_size(image, channel_dim=input_data_format)
        best_resolution = select_best_resolution(image_size, possible_resolutions)
        resized_image = self._resize_for_patching(
            image, best_resolution, resample=resample, input_data_format=input_data_format
        )
        padded_image = self._pad_for_patching(resized_image, best_resolution, input_data_format=input_data_format)
        patches = divide_to_patches(padded_image, patch_size=patch_size, input_data_format=input_data_format)
        patches = [
            to_channel_dimension_format(patch, channel_dim=data_format, input_channel_dim=input_data_format)
            for patch in patches
        ]
        return patches
    def get_number_of_image_patches(self, height: int, width: int, images_kwargs=None):
        split_image = images_kwargs.get("split_image", self.split_image)
        max_image_size = images_kwargs.get("max_image_size", self.max_image_size)
        resized_height, resized_width = select_best_resolution((height, width), self.split_resolutions)
        num_patches = 1 if not split_image else resized_height // max_image_size * resized_width // max_image_size
        return num_patches
class AriaProcessorKwargs(ProcessingKwargs, total=False):
    _defaults = {
        "text_kwargs": {
            "padding": False,
            "return_mm_token_type_ids": False,
        },
        "images_kwargs": {
            "max_image_size": 980,
            "split_image": False,
        },
        "return_tensors": TensorType.PYTORCH,
    }
class AriaProcessor(ProcessorMixin):
    attributes = ["image_processor", "tokenizer"]
    image_processor_class = "AriaImageProcessor"
    tokenizer_class = "AutoTokenizer"
    def __init__(
        self,
        image_processor=None,
        tokenizer: Union[AutoTokenizer, str] = None,
        chat_template: Optional[str] = None,
        size_conversion: Optional[dict[Union[float, int], int]] = None,
    ):
        if size_conversion is None:
            size_conversion = {490: 128, 980: 256}
        self.size_conversion = {int(k): v for k, v in size_conversion.items()}
        self.image_token = tokenizer.image_token
        self.image_token_id = tokenizer.image_token_id
        if tokenizer is not None and tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.unk_token
        super().__init__(image_processor, tokenizer, chat_template=chat_template)
    def __call__(
        self,
        text: Union[TextInput, PreTokenizedInput, list[TextInput], list[PreTokenizedInput]],
        images: Optional[ImageInput] = None,
        audio=None,
        videos=None,
        **kwargs: Unpack[AriaProcessorKwargs],
    ) -> BatchFeature:
        output_kwargs = self._merge_kwargs(
            AriaProcessorKwargs,
            tokenizer_init_kwargs=self.tokenizer.init_kwargs,
            **kwargs,
        )
        if isinstance(text, str):
            text = [text]
        elif not isinstance(text, list) and not isinstance(text[0], str):
            raise TypeError("Invalid input text. Please provide a string, or a list of strings")
        if images is not None:
            image_inputs = self.image_processor(images, **output_kwargs["images_kwargs"])
            tokens_per_image = self.size_conversion[image_inputs.pixel_values.shape[2]]
            prompt_strings = []
            num_crops = image_inputs.pop("num_crops") * tokens_per_image
            for sample in text:
                sample = sample.replace(self.tokenizer.image_token, self.tokenizer.image_token * num_crops)
                prompt_strings.append(sample)
        else:
            image_inputs = {}
            prompt_strings = text
        return_tensors = output_kwargs["text_kwargs"].pop("return_tensors", None)
        return_mm_token_type_ids = output_kwargs["text_kwargs"].pop("return_mm_token_type_ids", False)
        text_inputs = self.tokenizer(prompt_strings, **output_kwargs["text_kwargs"], return_tensors=None)
        self._check_special_mm_tokens(prompt_strings, text_inputs, modalities=["image"])
        if return_mm_token_type_ids:
            array_ids = np.array(text_inputs["input_ids"])
            mm_token_type_ids = np.zeros_like(text_inputs["input_ids"])
            mm_token_type_ids[array_ids == self.image_token_id] = 1
            text_inputs["mm_token_type_ids"] = mm_token_type_ids.tolist()
        return BatchFeature(data={**text_inputs, **image_inputs}, tensor_type=return_tensors)
    def _get_num_multimodal_tokens(self, image_sizes=None, **kwargs):
        vision_data = {}
        if image_sizes is not None:
            images_kwargs = AriaProcessorKwargs._defaults.get("images_kwargs", {})
            images_kwargs.update(kwargs)
            max_size = images_kwargs.get("max_image_size", None) or self.image_processor.max_image_size
            num_image_patches = [
                self.image_processor.get_number_of_image_patches(*image_size, images_kwargs)
                for image_size in image_sizes
            ]
            num_image_tokens = [self.size_conversion[max_size] * num_patches for num_patches in num_image_patches]
            vision_data.update({"num_image_tokens": num_image_tokens, "num_image_patches": num_image_patches})
        return MultiModalData(**vision_data)
    @property
    def model_input_names(self):
        tokenizer_input_names = self.tokenizer.model_input_names
        image_processor_input_names = self.image_processor.model_input_names
        image_processor_input_names = [name for name in image_processor_input_names if name != "num_crops"]
        return list(dict.fromkeys(tokenizer_input_names + image_processor_input_names))
class AriaSharedExpertsMLP(LlamaMLP):
    def __init__(self, config: AriaTextConfig):
        super().__init__(config)
        self.intermediate_size = config.intermediate_size * config.moe_num_shared_experts
class AriaGroupedExpertsGemm(nn.Module):
    def __init__(self, in_features, out_features, groups):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.groups = groups
        self.weight = nn.Parameter(torch.empty(groups, in_features, out_features))
    def forward(self, input, tokens_per_expert):
        return sequential_experts_gemm(
            input,
            self.weight,
            tokens_per_expert.cpu(),
        )
class AriaGroupedExpertsMLP(nn.Module):
    def __init__(self, config: AriaTextConfig) -> None:
        super().__init__()
        self.config = config
        self.fc1 = AriaGroupedExpertsGemm(config.hidden_size, config.intermediate_size * 2, config.moe_num_experts)
        self.fc2 = AriaGroupedExpertsGemm(config.intermediate_size, config.hidden_size, config.moe_num_experts)
    def forward(self, permuted_tokens, tokens_per_expert):
        fc1_output = self.fc1(permuted_tokens, tokens_per_expert)
        projection, gate = torch.chunk(fc1_output, 2, dim=-1)
        fc1_output = nn.functional.silu(projection) * gate
        fc2_output = self.fc2(fc1_output, tokens_per_expert)
        return fc2_output
class AriaTextMoELayer(nn.Module):
    def __init__(self, config: AriaTextConfig):
        super().__init__()
        self.router = nn.Linear(config.hidden_size, config.moe_num_experts, bias=False)
        self.experts = AriaGroupedExpertsMLP(config)
        self.shared_experts = AriaSharedExpertsMLP(config)
        self.config = config
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        original_shape = hidden_states.shape
        hidden_states = hidden_states.view(-1, hidden_states.size(-1))
        logits = self.router(hidden_states)
        top_logits, top_indices = torch.topk(logits, k=self.config.moe_topk, dim=1)
        scores = nn.functional.softmax(top_logits, dim=-1)
        original_dtype = top_indices.dtype
        tokens_per_expert = torch.histc(
            top_indices.flatten().to(torch.float32),
            bins=self.config.moe_num_experts,
            min=0,
            max=self.config.moe_num_experts - 1,
        ).to(original_dtype)
        indices = top_indices
        flatten_indices = indices.view(-1)
        sorted_indices = torch.argsort(flatten_indices)
        permuted_tokens = hidden_states.index_select(0, sorted_indices // self.config.moe_topk)
        expert_output = self.experts(permuted_tokens, tokens_per_expert)
        unpermuted_tokens = torch.zeros(
            (scores.shape[0] * self.config.moe_topk, expert_output.size(1)),
            dtype=expert_output.dtype,
            device=expert_output.device,
        )
        unpermuted_tokens.index_copy_(0, sorted_indices, expert_output)
        unpermuted_tokens = unpermuted_tokens.view(-1, self.config.moe_topk, expert_output.size(1))
        output = (unpermuted_tokens * scores.unsqueeze(-1)).sum(dim=1).view(original_shape)
        shared_expert_output = self.shared_experts(hidden_states.view(original_shape))
        return output + shared_expert_output
class AriaTextAttention(LlamaAttention):
    pass
class AriaTextDecoderLayer(LlamaDecoderLayer):
    def __init__(self, config: AriaTextConfig, layer_idx: int):
        super().__init__(config, layer_idx)
        self.mlp = AriaTextMoELayer(config)
@auto_docstring
class AriaTextPreTrainedModel(PreTrainedModel):
    config: AriaTextConfig
    base_model_prefix = "model"
    _no_split_modules = ["AriaTextDecoderLayer", "AriaGroupedExpertsGemm"]
    supports_gradient_checkpointing = True
    _skip_keys_device_placement = "past_key_values"
    _supports_flash_attn = True
    _supports_sdpa = True
    _supports_attention_backend = True
    _can_record_outputs = {
        "hidden_states": AriaTextDecoderLayer,
        "attentions": AriaTextAttention,
    }
    def _init_weights(self, module):
        super()._init_weights(module)
        if isinstance(module, AriaGroupedExpertsGemm):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
class AriaPreTrainedModel(LlamaPreTrainedModel):
    config: AriaConfig
    base_model_prefix = ""
    _can_compile_fullgraph = False
    _supports_attention_backend = True
    def _init_weights(self, module):
        PreTrainedModel._init_weights(self, module)
        if isinstance(module, AriaProjector):
            nn.init.trunc_normal_(module.query, std=self.config.initializer_range)
class AriaTextModel(LlamaModel):
    def __init__(self, config: AriaTextConfig):
        super().__init__(config)
        self.layers = nn.ModuleList(
            [AriaTextDecoderLayer(config, layer_idx) for layer_idx in range(config.num_hidden_layers)]
        )
        self.gradient_checkpointing = False
        self.post_init()
class AriaTextForCausalLM(AriaTextPreTrainedModel, LlamaForCausalLM):
    _tied_weights_keys = ["lm_head.weight"]
    def __init__(self, config: AriaTextConfig):
        super().__init__(config)
        self.model = AriaTextModel(config)
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.post_init()
    @auto_docstring
    def forward(self, **super_kwargs):
        super().forward(self, **super_kwargs)
class AriaCausalLMOutputWithPast(LlavaCausalLMOutputWithPast):
    pass
class AriaModelOutputWithPast(LlavaModelOutputWithPast):
    pass
class AriaModel(LlavaModel):
    def __init__(self, config: AriaConfig):
        super().__init__(config)
        self.multi_modal_projector = AriaProjector(config)
    def _create_patch_attention_mask(self, pixel_mask):
        if pixel_mask is None:
            return None
        patches_subgrid = pixel_mask.unfold(
            dimension=1,
            size=self.vision_tower.config.patch_size,
            step=self.vision_tower.config.patch_size,
        )
        patches_subgrid = patches_subgrid.unfold(
            dimension=2,
            size=self.vision_tower.config.patch_size,
            step=self.vision_tower.config.patch_size,
        )
        return (patches_subgrid.sum(dim=(-1, -2)) > 0).bool()
    def get_image_features(
        self,
        pixel_values: torch.FloatTensor,
        pixel_mask: Optional[torch.FloatTensor] = None,
        vision_feature_layer: int = -1,
    ):
        vision_feature_layer = (
            vision_feature_layer if vision_feature_layer is not None else self.config.vision_feature_layer
        )
        patch_attention_mask = self._create_patch_attention_mask(pixel_mask)
        image_outputs = self.vision_tower(
            pixel_values, patch_attention_mask=patch_attention_mask, output_hidden_states=True
        )
        image_attn_mask = None
        if patch_attention_mask is not None:
            flattened_mask = patch_attention_mask.flatten(1)
            image_attn_mask = torch.logical_not(flattened_mask)
        selected_image_feature = image_outputs.hidden_states[vision_feature_layer]
        image_features = self.multi_modal_projector(selected_image_feature, attn_mask=image_attn_mask)
        return image_features
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        pixel_mask: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[FlashAttentionKwargs],
    ) -> Union[tuple, AriaModelOutputWithPast]:
        if inputs_embeds is None:
            inputs_embeds = self.get_input_embeddings()(input_ids)
        if pixel_values is not None and inputs_embeds.shape[1] != 1:
            image_features = self.get_image_features(
                pixel_values=pixel_values,
                pixel_mask=pixel_mask,
                vision_feature_layer=self.config.vision_feature_layer,
            )
            image_features = image_features.to(inputs_embeds.device, inputs_embeds.dtype)
            special_image_mask = self.get_placeholder_mask(
                input_ids, inputs_embeds=inputs_embeds, image_features=image_features
            )
            inputs_embeds = inputs_embeds.masked_scatter(special_image_mask, image_features)
        outputs = self.language_model(
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        return AriaModelOutputWithPast(
            last_hidden_state=outputs.last_hidden_state,
            past_key_values=outputs.past_key_values if use_cache else None,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
            image_hidden_states=image_features if pixel_values is not None else None,
        )
@auto_docstring(
)
class AriaForConditionalGeneration(LlavaForConditionalGeneration):
    def get_image_features(
        self,
        pixel_values: torch.FloatTensor,
        pixel_mask: Optional[torch.FloatTensor] = None,
        vision_feature_layer: int = -1,
    ):
        return self.model.get_image_features(
            pixel_values=pixel_values,
            pixel_mask=pixel_mask,
            vision_feature_layer=vision_feature_layer,
        )
    @can_return_tuple
    @auto_docstring
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        pixel_mask: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Cache] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        logits_to_keep: Union[int, torch.Tensor] = 0,
        cache_position: Optional[torch.LongTensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> Union[tuple, AriaCausalLMOutputWithPast]:
        outputs = self.model(
            input_ids=input_ids,
            pixel_values=pixel_values,
            pixel_mask=pixel_mask,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            cache_position=cache_position,
            **kwargs,
        )
        hidden_states = outputs[0]
        slice_indices = slice(-logits_to_keep, None) if isinstance(logits_to_keep, int) else logits_to_keep
        logits = self.lm_head(hidden_states[:, slice_indices, :])
        loss = None
        if labels is not None:
            loss = self.loss_function(
                logits=logits, labels=labels, vocab_size=self.config.text_config.vocab_size, **kwargs
            )
        return AriaCausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
    def prepare_inputs_for_generation(
        self,
        input_ids,
        past_key_values=None,
        inputs_embeds=None,
        pixel_values=None,
        pixel_mask=None,
        attention_mask=None,
        cache_position=None,
        logits_to_keep=None,
        **kwargs,
    ):
        model_inputs = super().prepare_inputs_for_generation(
            input_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            attention_mask=attention_mask,
            cache_position=cache_position,
            logits_to_keep=logits_to_keep,
            **kwargs,
        )
        if cache_position[0] == 0:
            model_inputs["pixel_values"] = pixel_values
            model_inputs["pixel_mask"] = pixel_mask
        return model_inputs
__all__ = [
    "AriaConfig",
    "AriaTextConfig",
    "AriaImageProcessor",
    "AriaProcessor",
    "AriaForConditionalGeneration",
    "AriaPreTrainedModel",
    "AriaTextPreTrainedModel",
    "AriaTextModel",
    "AriaModel",
    "AriaTextForCausalLM",
]