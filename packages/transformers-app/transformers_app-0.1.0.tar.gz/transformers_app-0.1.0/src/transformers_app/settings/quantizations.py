from dataclasses import dataclass
from enum import Enum
from typing import Optional, OrderedDict
import importlib.util
import torch


class Precision(str, Enum):
    FLOAT32 = "float32"
    BFLOAT16 = "bfloat16"
    INT8 = "8-bit"
    INT4 = "4-bit"


class QuantBackend(str, Enum):
    BITSANDBYTES = "bitsandbytes"
    TORCHAO = "torchao"


PRECISION_META = {
    Precision.FLOAT32: "Full precision. Highest memory use, best compatibility.",
    Precision.BFLOAT16: "16-bit. Good speed/memory tradeoff on supported accelerators.",
    Precision.INT8: "Lower memory. Can be faster; backend/device dependent.",
    Precision.INT4: "Lowest memory. Best for fitting large models; backend/device dependent.",
}


@dataclass(frozen=True)
class QuantOption:
    precision: Precision
    description: str
    backend: QuantBackend | None = None
    label: str | None = None
    enabled: bool = True
    reason: str | None = None

    def as_string(self) -> str:
        return f"{self.backend}-{self.precision}"


def _has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def quantization_options(device_choice: str) -> dict[str, dict[str | None, QuantOption]]:
    is_cuda = device_choice.startswith("cuda")
    has_cuda = torch.cuda.is_available()

    is_map = device_choice in {"auto", "balanced"}
    cuda_effective = has_cuda and (is_cuda or is_map)

    has_bnb = _has_module("bitsandbytes")
    has_torchao = _has_module("torchao")

    opts: dict[str, dict[str | None, QuantOption]] = OrderedDict(
        {
            Precision.FLOAT32.value: {
                None: QuantOption(Precision.FLOAT32, PRECISION_META[Precision.FLOAT32], label=Precision.FLOAT32.value)
            },
            Precision.BFLOAT16.value: {
                None: QuantOption(
                    Precision.BFLOAT16, PRECISION_META[Precision.BFLOAT16], label=Precision.BFLOAT16.value
                )
            },
        }
    )

    # Quantized: backend-specific rows
    for precision in [Precision.INT8, Precision.INT4]:
        for backend in (QuantBackend.BITSANDBYTES, QuantBackend.TORCHAO):
            enabled = True
            reason: Optional[str] = None

            # Backend must be installed
            if backend is QuantBackend.BITSANDBYTES and not has_bnb:
                enabled = False
                reason = "bitsandbytes not installed"
            if backend is QuantBackend.TORCHAO and not has_torchao:
                enabled = False
                reason = "torchao not installed"

            # Simple first-pass device rule (you can refine later):
            # bitsandbytes quant is typically CUDA-only; torchao can be more flexible depending on implementation.
            if enabled and backend is QuantBackend.BITSANDBYTES and not cuda_effective:
                enabled = False
                reason = "bitsandbytes quantization requires CUDA"

            label = f"{precision.value} ({backend.value})"

            if precision.value not in opts:
                opts[precision.value] = {
                    str(backend.value): QuantOption(
                        precision, PRECISION_META[precision], backend, label, enabled, reason
                    )
                }
            else:
                opts[precision.value][str(backend.value)] = QuantOption(
                    precision, PRECISION_META[precision], backend, label, enabled, reason
                )

    return opts
