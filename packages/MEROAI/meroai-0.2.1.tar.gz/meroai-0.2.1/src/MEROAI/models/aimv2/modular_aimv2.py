import math
from typing import Optional
import torch
import torch.nn.functional as F
from torch import nn
from ...masking_utils import create_causal_mask
from ...modeling_layers import GradientCheckpointingLayer
from ...modeling_outputs import BaseModelOutput, BaseModelOutputWithPooling
from ...modeling_utils import PreTrainedModel
from ...processing_utils import Unpack
from ...utils import (
    MEROAIKwargs,
    auto_docstring,
    can_return_tuple,
)
from ...utils.deprecation import deprecate_kwarg
from ...utils.generic import check_model_inputs
from ..clip.modeling_clip import CLIPModel, CLIPTextEmbeddings, _get_vector_norm
from ..llama.modeling_llama import LlamaMLP, LlamaRMSNorm
from ..siglip.configuration_siglip import SiglipConfig, SiglipTextConfig, SiglipVisionConfig
from ..siglip.modeling_siglip import SiglipAttention, SiglipEncoder, SiglipOutput
class Aimv2VisionConfig(SiglipVisionConfig):
    def __init__(
        self,
        hidden_size: int = 1024,
        intermediate_size: int = 2816,
        num_hidden_layers: int = 24,
        num_attention_heads: int = 8,
        num_channels: int = 3,
        image_size: int = 224,
        patch_size: int = 14,
        rms_norm_eps: float = 1e-5,
        attention_dropout: float = 0.0,
        qkv_bias: bool = False,
        mlp_bias: bool = False,
        hidden_act: str = "silu",
        initializer_range: float = 0.02,
        use_head: bool = True,
        is_native: bool = False,
        **kwargs,
    ):
        super().__init__(
            hidden_size=hidden_size,
            intermediate_size=intermediate_size,
            num_hidden_layers=num_hidden_layers,
            num_attention_heads=num_attention_heads,
            hidden_act=hidden_act,
            num_channels=num_channels,
            image_size=image_size,
            patch_size=patch_size,
            qkv_bias=qkv_bias,
            **kwargs,
        )
        self.use_head = use_head
        self.initializer_range = initializer_range
        self.attention_dropout = attention_dropout
        self.mlp_bias = mlp_bias
        self.qkv_bias = qkv_bias
        self.rms_norm_eps = rms_norm_eps
        self.is_native = is_native
        del self.layer_norm_eps
class Aimv2TextConfig(SiglipTextConfig):
    def __init__(
        self,
        vocab_size: int = 49408,
        hidden_size: int = 768,
        intermediate_size: int = 2048,
        num_hidden_layers: int = 12,
        num_attention_heads: int = 6,
        rms_norm_eps: float = 1e-5,
        attention_dropout: float = 0.0,
        qkv_bias: bool = False,
        mlp_bias: bool = False,
        hidden_act: str = "silu",
        pad_token_id: Optional[int] = None,
        bos_token_id: Optional[int] = None,
        eos_token_id: int = 49407,
        max_position_embeddings: int = 77,
        initializer_range: bool = 0.02,
        **kwargs,
    ):
        super().__init__(
            vocab_size=vocab_size,
            hidden_size=hidden_size,
            intermediate_size=intermediate_size,
            num_hidden_layers=num_hidden_layers,
            num_attention_heads=num_attention_heads,
            hidden_act=hidden_act,
            max_position_embeddings=max_position_embeddings,
            pad_token_id=pad_token_id,
            bos_token_id=bos_token_id,
            eos_token_id=eos_token_id,
            **kwargs,
        )
        self.initializer_range = initializer_range
        self.attention_dropout = attention_dropout
        self.mlp_bias = mlp_bias
        self.qkv_bias = qkv_bias
        self.rms_norm_eps = rms_norm_eps
        del self.bos_token_id
        del self.pad_token_id
        del self.projection_size
        del self.layer_norm_eps
class Aimv2Config(SiglipConfig):
    def __init__(
        self, text_config=None, vision_config=None, projection_dim=512, logit_scale_init_value=2.6592, **kwargs
    ):
        super().__init__(text_config, vision_config, **kwargs)
        self.projection_dim = projection_dim
        self.logit_scale_init_value = logit_scale_init_value
        self.max_logit_scale = 100.0
        del self.initializer_factor
class Aimv2Output(SiglipOutput):
    pass
class Aimv2RMSNorm(LlamaRMSNorm):
    pass
class Aimv2MLP(LlamaMLP):
    pass
class Aimv2VisionEmbeddings(nn.Module):
    def __init__(self, config: Aimv2VisionConfig):
        super().__init__()
        self.config = config
        self.patch_size = config.patch_size
        self.patch_embed = nn.Conv2d(
            config.num_channels, config.hidden_size, kernel_size=config.patch_size, stride=config.patch_size
        )
        self.rms_norm = Aimv2RMSNorm(config.hidden_size, config.rms_norm_eps)
        num_patches = (config.image_size // config.patch_size) ** 2
        if not self.config.is_native:
            self.position_embedding = nn.Embedding(num_patches, config.hidden_size)
        self.register_buffer("position_ids", torch.arange(num_patches).expand((1, -1)), persistent=False)
    @staticmethod
    def build_2d_sincos_position_embedding(
        height, width, embed_dim=256, temperature=10000.0, device="cpu", dtype=torch.float32
    ) -> torch.Tensor:
        grid_w = torch.arange(int(width), dtype=dtype, device=device)
        grid_h = torch.arange(int(height), dtype=dtype, device=device)
        grid_h, grid_w = torch.meshgrid(grid_w, grid_h, indexing="xy")
        pos_dim = embed_dim // 4
        omega = torch.arange(pos_dim, dtype=dtype, device=device) / pos_dim
        omega = 1.0 / (temperature**omega)
        out_h = grid_h.flatten()[..., None] @ omega[None, :]
        out_w = grid_w.flatten()[..., None] @ omega[None, :]
        return torch.concat([out_h.sin(), out_h.cos(), out_w.sin(), out_w.cos()], dim=1)[None, :, :]
    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        _, _, height, width = pixel_values.size()
        hidden_states = self.patch_embed(pixel_values).flatten(2).transpose(1, 2)
        hidden_states = self.rms_norm(hidden_states)
        if self.config.is_native:
            pos_embed = self.build_2d_sincos_position_embedding(
                height // self.patch_size,
                width // self.patch_size,
                embed_dim=self.config.hidden_size,
                device=hidden_states.device,
                dtype=hidden_states.dtype,
            )
        else:
            pos_embed = self.position_embedding(self.position_ids)
        hidden_states = hidden_states + pos_embed
        return hidden_states
class Aimv2TextEmbeddings(CLIPTextEmbeddings):
    pass
class Aimv2Attention(SiglipAttention):
    def __init__(self, config):
        super().__init__(config)
        self.k_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=config.qkv_bias)
        self.v_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=config.qkv_bias)
        self.q_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=config.qkv_bias)
        self.out_proj = nn.Linear(self.embed_dim, self.embed_dim, bias=config.qkv_bias)
class Aimv2EncoderLayer(GradientCheckpointingLayer):
    def __init__(self, config: Aimv2VisionConfig):
        super().__init__()
        self.attention = Aimv2Attention(config)
        self.ffn = Aimv2MLP(config)
        self.rms_norm1 = Aimv2RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.rms_norm2 = Aimv2RMSNorm(config.hidden_size, config.rms_norm_eps)
    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> torch.Tensor:
        norm_hidden_states = self.rms_norm1(hidden_states)
        attn_output, _ = self.attention(hidden_states=norm_hidden_states, attention_mask=attention_mask, **kwargs)
        hidden_states = hidden_states + attn_output
        norm_hidden_states = self.rms_norm2(hidden_states)
        mlp_output = self.ffn(norm_hidden_states)
        hidden_states = hidden_states + mlp_output
        return hidden_states
class Aimv2Encoder(SiglipEncoder):
    pass
class Aimv2AttentionPoolingHead(nn.Module):
    def __init__(self, config: Aimv2VisionConfig):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.k_proj = nn.Linear(self.hidden_size, self.hidden_size, bias=config.qkv_bias)
        self.v_proj = nn.Linear(self.hidden_size, self.hidden_size, bias=config.qkv_bias)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, self.hidden_size))
        self.output_proj = nn.Linear(self.hidden_size, self.hidden_size, bias=True)
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        batch_size, seq_len, hidden_dim = hidden_states.shape
        cls_token = self.cls_token.expand(batch_size, -1, -1)
        key = self.k_proj(hidden_states).reshape(batch_size, seq_len, self.num_heads, hidden_dim // self.num_heads)
        value = self.v_proj(hidden_states).reshape(batch_size, seq_len, self.num_heads, hidden_dim // self.num_heads)
        query = cls_token.reshape(batch_size, 1, self.num_heads, hidden_dim // self.num_heads)
        key = key.permute(0, 2, 1, 3)
        value = value.permute(0, 2, 1, 3)
        query = query.permute(0, 2, 1, 3)
        attn_output = F.scaled_dot_product_attention(query, key, value)
        attn_output = attn_output.transpose(1, 2).reshape(batch_size, 1, hidden_dim)
        attn_output = attn_output.mean(dim=1)
        output = self.output_proj(attn_output)
        return output
@auto_docstring
class Aimv2PreTrainedModel(PreTrainedModel):
    config: Aimv2Config
    base_model_prefix = "aimv2"
    supports_gradient_checkpointing = True
    _no_split_modules = [
        "Aimv2EncoderLayer",
        "Aimv2AttentionPoolingHead",
        "Aimv2VisionEmbeddings",
        "Aimv2TextEmbeddings",
    ]
    _supports_sdpa = True
    _supports_flash_attn = True
    _supports_flex_attn = True
    def _init_weights(self, module):
        super()._init_weights(module)
        if hasattr(module, "logit_scale"):
            if isinstance(module.logit_scale, nn.Parameter):
                module.logit_scale.data.fill_(math.log(1 / 0.07))
        elif isinstance(module, Aimv2AttentionPoolingHead):
            module.cls_token.data.normal_(mean=0.0, std=self.config.initializer_range)
@auto_docstring(
)
class Aimv2VisionModel(Aimv2PreTrainedModel):
    config: Aimv2VisionConfig
    main_input_name = "pixel_values"
    _can_record_outputs = {
        "hidden_states": Aimv2EncoderLayer,
        "attentions": Aimv2Attention,
    }
    def __init__(self, config: Aimv2VisionConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = Aimv2VisionEmbeddings(config)
        self.encoder = Aimv2Encoder(config)
        self.rms_norm = Aimv2RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.use_head = config.use_head
        if self.use_head:
            self.head = Aimv2AttentionPoolingHead(config)
        self.post_init()
    def get_input_embeddings(self) -> nn.Module:
        return self.embeddings.patch_embed
    @deprecate_kwarg("attention_mask", version="v4.58.0")
    @check_model_inputs(tie_last_hidden_states=False)
    @auto_docstring
    def forward(
        self,
        pixel_values,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> BaseModelOutputWithPooling:
        hidden_states = self.embeddings(pixel_values)
        encoder_outputs: BaseModelOutput = self.encoder(
            inputs_embeds=hidden_states,
            **kwargs,
        )
        last_hidden_state = encoder_outputs.last_hidden_state
        last_hidden_state = self.rms_norm(last_hidden_state)
        pooler_output = self.head(last_hidden_state) if self.use_head else None
        return BaseModelOutputWithPooling(
            last_hidden_state=last_hidden_state,
            pooler_output=pooler_output,
        )
@auto_docstring(
)
class Aimv2TextModel(Aimv2PreTrainedModel):
    main_input_name = "input_ids"
    _can_record_outputs = {
        "hidden_states": Aimv2EncoderLayer,
        "attentions": Aimv2Attention,
    }
    def __init__(self, config: Aimv2TextConfig):
        super().__init__(config)
        self.config = config
        self.embeddings = Aimv2TextEmbeddings(config)
        self.encoder = Aimv2Encoder(config)
        self.rms_norm = Aimv2RMSNorm(config.hidden_size, config.rms_norm_eps)
        self.eos_token_id = config.eos_token_id
        self.post_init()
    def get_input_embeddings(self) -> nn.Module:
        return self.embeddings.token_embedding
    def set_input_embeddings(self, value):
        self.embeddings.token_embedding = value
    @check_model_inputs(tie_last_hidden_states=False)
    @auto_docstring
    def forward(
        self,
        input_ids,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> BaseModelOutputWithPooling:
        hidden_states = self.embeddings(input_ids)
        batch_size, seq_len, _ = hidden_states.shape
        cache_position = torch.arange(seq_len, dtype=torch.long, device=hidden_states.device)
        position_ids = cache_position.unsqueeze(0).expand(batch_size, -1)
        if attention_mask is not None:
            attention_mask = create_causal_mask(
                config=self.config,
                input_embeds=hidden_states,
                position_ids=position_ids,
                attention_mask=attention_mask,
                cache_position=cache_position,
                past_key_values=None,
            )
        encoder_outputs = self.encoder(
            inputs_embeds=hidden_states,
            attention_mask=attention_mask,
            **kwargs,
        )
        last_hidden_state = encoder_outputs.last_hidden_state
        last_hidden_state = self.rms_norm(last_hidden_state)
        pooled_output = last_hidden_state[
            torch.arange(last_hidden_state.shape[0], device=last_hidden_state.device),
            (input_ids.to(dtype=torch.int, device=last_hidden_state.device) == self.eos_token_id).int().argmax(dim=-1),
        ]
        return BaseModelOutputWithPooling(
            last_hidden_state=last_hidden_state,
            pooler_output=pooled_output,
        )
@auto_docstring
class Aimv2Model(CLIPModel):
    _supports_flash_attn = True
    def __init__(self, config: Aimv2Config):
        PreTrainedModel.__init__(self, config)
        self.projection_dim = config.projection_dim
        self.vision_embed_dim = config.vision_config.hidden_size
        self.text_embed_dim = config.text_config.hidden_size
        self.vision_model = Aimv2VisionModel._from_config(config.vision_config)
        self.text_model = Aimv2TextModel._from_config(config.text_config)
        self.visual_projection = nn.Linear(self.vision_embed_dim, self.projection_dim, bias=False)
        self.text_projection = nn.Linear(self.text_embed_dim, self.projection_dim, bias=False)
        self.logit_scale = nn.Parameter(torch.tensor(self.config.logit_scale_init_value))
        self.max_log_logit_scale = math.log(config.max_logit_scale)
        self.post_init()
    @auto_docstring
    @can_return_tuple
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        pixel_values: Optional[torch.FloatTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs: Unpack[MEROAIKwargs],
    ) -> Aimv2Output:
        vision_outputs: BaseModelOutputWithPooling = self.vision_model(
            pixel_values=pixel_values,
            **kwargs,
        )
        text_outputs: BaseModelOutputWithPooling = self.text_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            **kwargs,
        )
        image_embeds = vision_outputs.pooler_output
        image_embeds = self.visual_projection(image_embeds)
        text_embeds = text_outputs.pooler_output
        text_embeds = self.text_projection(text_embeds)
        image_embeds = image_embeds / _get_vector_norm(image_embeds)
        text_embeds = text_embeds / _get_vector_norm(text_embeds)
        logit_scale = self.logit_scale.clamp(0.0, self.max_log_logit_scale).exp().to(text_embeds.device)
        logits_per_text = (logit_scale * text_embeds) @ image_embeds.t()
        logits_per_image = logits_per_text.t()
        return Aimv2Output(
            logits_per_image=logits_per_image,
            logits_per_text=logits_per_text,
            text_embeds=text_embeds,
            image_embeds=image_embeds,
            text_model_output=text_outputs,
            vision_model_output=vision_outputs,
        )
__all__ = [
    "Aimv2Config",
    "Aimv2VisionConfig",
    "Aimv2TextConfig",
    "Aimv2VisionModel",
    "Aimv2Model",
    "Aimv2PreTrainedModel",
    "Aimv2TextModel",
]