from enum import Enum
from dataclasses import dataclass
from typing import Optional
import torch


class Attention(str, Enum):
    EAGER = "eager"
    PAGED_EAGER = "paged|eager"
    FLASH_ATTENTION_2 = "flash_attention_2"
    PAGED_FLASH_ATTENTION_2 = "paged|flash_attention_2"
    FLASH_ATTENTION_3 = "flash_attention_3"
    SDPA = "sdpa"
    PAGED_SDPA = "paged|sdpa"
    FLEX_ATTENTION = "flex_attention"


ATTN_META = {
    Attention.EAGER: "Reference baseline. Predictable and widely compatible.",
    Attention.PAGED_EAGER: "Eager attention with paged/continuous batching.",
    Attention.SDPA: "PyTorch scaled dot-product attention. Fast and versatile.",
    Attention.PAGED_SDPA: "SDPA with paged/continuous batching.",
    Attention.FLASH_ATTENTION_2: "Fused CUDA kernel optimized for throughput/latency.",
    Attention.PAGED_FLASH_ATTENTION_2: "FlashAttn2 with paged/continuous batching.",
    Attention.FLASH_ATTENTION_3: "Newer fused CUDA kernel (where supported).",
    Attention.FLEX_ATTENTION: "Flexible attention path; can reduce memory or improve throughput.",
}


@dataclass(frozen=True)
class AttentionOption:
    attention: Attention
    label: str
    enabled: bool
    description: str
    reason: Optional[str] = None
    paged: Optional[bool] = False


CUDA_ONLY = {
    Attention.FLASH_ATTENTION_2,
    Attention.PAGED_FLASH_ATTENTION_2,
    Attention.FLASH_ATTENTION_3,
}


def attention_options(device_choice: str) -> dict[str, AttentionOption]:
    is_cuda = device_choice.startswith("cuda")
    has_cuda = torch.cuda.is_available()

    is_map = device_choice in {"auto", "balanced"}
    cuda_effective = has_cuda and (is_cuda or is_map)

    opts: dict[str, AttentionOption] = {}
    for a in Attention:
        enabled = True
        reason = None

        if a in CUDA_ONLY and not cuda_effective:
            enabled = False
            reason = "Not available on the selected device - CUDA-only support"

        opts[a.value] = AttentionOption(
            attention=a,
            label=a.value.split("|")[-1],
            enabled=enabled,
            reason=reason,
            paged="paged" in a.value,
            description=ATTN_META[a],
        )

    return opts
