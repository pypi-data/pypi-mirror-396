from ...modeling_outputs import CausalLMOutputWithPast
from ...processing_utils import Unpack
from ...utils import logging
from ..deepseek_v3.modeling_deepseek_v3 import (
    DeepseekV3DecoderLayer,
    DeepseekV3MLP,
    DeepseekV3MoE,
    DeepseekV3PreTrainedModel,
    DeepseekV3TopkRouter,
)
from ..qwen3.modeling_qwen3 import (
    Qwen3Attention,
    Qwen3ForCausalLM,
    Qwen3Model,
    Qwen3RMSNorm,
    Qwen3RotaryEmbedding,
    MEROAIKwargs,
)
from .configuration_dots1 import Dots1Config
logger = logging.get_logger(__name__)
class Dots1RMSNorm(Qwen3RMSNorm):
    pass
class Dots1RotaryEmbedding(Qwen3RotaryEmbedding):
    pass
class Dots1Attention(Qwen3Attention):
    pass
class Dots1MLP(DeepseekV3MLP):
    pass
class Dots1MoE(DeepseekV3MoE):
    pass
class Dots1TopkRouter(DeepseekV3TopkRouter):
    pass
class Dots1DecoderLayer(DeepseekV3DecoderLayer):
    def __init__(self, config: Dots1Config, layer_idx: int):
        super().__init__(config, layer_idx)
        self.attention_type = config.layer_types[layer_idx]
class Dots1PreTrainedModel(DeepseekV3PreTrainedModel):
    pass
class Dots1Model(Qwen3Model):
    pass
class Dots1ForCausalLM(Qwen3ForCausalLM):
    def forward(
        self,
        **super_kwargs: Unpack[MEROAIKwargs],
    ) -> CausalLMOutputWithPast:
        return super().forward(**super_kwargs)
__all__ = [
    "Dots1PreTrainedModel",
    "Dots1Model",
    "Dots1ForCausalLM",
]