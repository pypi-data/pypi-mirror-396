from importlib import resources
import logging
from os import path

from pathlib import Path
import json
from typing import Optional

from huggingface_hub.constants import HF_HUB_CACHE
from pydantic import BaseModel

from .devices import available_devices
from .attention_implementations import attention_options, Attention, AttentionOption
from .quantizations import quantization_options, QuantOption, Precision

save_directory = Path(HF_HUB_CACHE).parent / "transformers"
local_settings_file = save_directory / "serve_settings.json"
settings_html_path = resources.files("transformers_app") / "static" / "index.html"


class QuantizationPayload(BaseModel):
    precision: str
    backend: Optional[str] = None


class SettingsPayload(BaseModel):
    device: str
    attention_method: str
    quantization_method: QuantizationPayload
    context_length: int


class Settings:
    devices: list[str]
    accelerators: list[str]
    attention_methods = dict[str, AttentionOption]
    quantization_methods = dict[str, list[QuantOption]]
    context_lengths: list[int]

    device: str
    attention_method: AttentionOption
    quantization_method: QuantOption
    context_length: int

    def __init__(self, local_file: Path = local_settings_file):
        devices = available_devices()
        self.devices = devices
        self.accelerators = [device for device in self.devices if device != "cpu"]

        chosen_device = devices[0]

        available_attention_methods = attention_options(chosen_device)
        self.attention_methods = available_attention_methods

        available_quantization_methods = quantization_options(chosen_device)
        self.quantization_methods = available_quantization_methods

        context_lengths = [2**n for n in range(8, 17)]
        self.context_lengths = context_lengths

        self.apply_default_settings()

        self.local_file = local_file
        if local_file.exists():
            self.load_settings_from_file(local_file)

    def default_device(self):
        return self.accelerators[0] if len(self.accelerators) else self.devices[0]

    def default_attention_method(self):
        return self.attention_methods[Attention.SDPA]

    def default_context_length(self):
        return 1024

    def default_quantization(self):
        return self.quantization_methods[Precision.BFLOAT16][None]

    def validate_device(self, device) -> str:
        if device not in self.devices:
            has_accelerator = len(self.accelerators) > 0
            error_message = f"Error loading settings: specified device `{device}` not available. "
            chosen_device = (
                f"Defaulting to default accelerator: `{self.accelerators[0]}`."
                if has_accelerator
                else "No accelerator available, defaulting to CPU."
            )
            logging.warning(error_message + chosen_device)
            device = self.default_device()

        return device

    def validate_attention_method(self, attention_method: str) -> AttentionOption:
        if attention_method not in [k for k, v in self.attention_methods.items() if v.enabled]:
            error_message = f"Chosen attention method not available for device {self.device}."
            chosen_attention_method = "Defaulting to SDPA."
            logging.warning(error_message + chosen_attention_method)
            attention_method = self.default_attention_method()

        return self.attention_methods[attention_method]

    def validate_quantization_method(self, precision: str, backend: str | None) -> QuantOption:
        quantization_method = self.quantization_methods[precision][backend]
        if not quantization_method.enabled:
            error_message = f"Chosen quantization method not available. Reason: {self.quantization_method.reason}"
            chosen_attention_method = "Defaulting to BF16."
            logging.warning(error_message + chosen_attention_method)
            quantization_method = self.default_quantization()

        return quantization_method

    def validate_context_length(self, context_length: int) -> int:
        if context_length not in self.context_lengths:
            error_message = f"Provided context length {context_length} not a power of 2. Defaulting to 1024."
            logging.warning(error_message)
            context_length = self.default_context_length()

        return context_length

    def load_settings_from_payload(self, payload: SettingsPayload):
        self.device = self.validate_device(payload.device)
        self.attention_method = self.validate_attention_method(payload.attention_method)
        self.context_length = self.validate_context_length(payload.context_length)
        self.quantization_method = self.validate_quantization_method(
            payload.quantization_method.precision, payload.quantization_method.backend
        )

    def load_settings_from_file(self, settings_file: Path):
        if path.exists(settings_file):
            settings = settings_file.read_text(encoding="utf-8")
            payload = SettingsPayload.model_validate_json(settings)
            self.load_settings_from_payload(payload)
        else:
            logging.warning("No settings file found.")

    def apply_default_settings(self):
        self.device = self.default_device()
        self.attention_method = self.default_attention_method()
        self.quantization_method = self.default_quantization()
        self.context_length = self.default_context_length()

    def capabilities(self):
        capabilities = {
            "capabilities": {
                "devices": self.devices,
                "attention_methods": [
                    {
                        "value": a.attention.value,
                        "label": a.label,
                        "enabled": a.enabled,
                        "reason": a.reason,
                        "paged": a.paged,
                        "description": a.description,
                    }
                    for a in self.attention_methods.values()
                ],
                "quantization_methods": [
                    {
                        quant_type: [
                            {
                                "precision": method.precision.value,
                                "enabled": method.enabled,
                                "reason": method.reason,
                                "backend": backend,
                                "description": method.description,
                            }
                            for backend, method in methods.items()
                        ]
                    }
                    for quant_type, methods in self.quantization_methods.items()
                ],
                "context_lengths": self.context_lengths,
            },
            "current_settings": {
                "device": self.device,
                "attention_method": self.attention_method.attention.value,
                "quantization_method": {
                    "precision": self.quantization_method.precision.value,
                    "backend": getattr(self.quantization_method.backend, "value", None),
                },
                "context_length": self.context_length,
            },
        }
        return capabilities

    def html(self):
        html = settings_html_path.read_text(encoding="utf-8")
        injected = json.dumps(self.capabilities(), ensure_ascii=False)
        html = html.replace("__DEFAULTS_CAPS__", injected)
        return html

    def save(self):
        if not self.local_file.exists():
            self.local_file.parent.mkdir(parents=True, exist_ok=True)
        current_settings = self.capabilities()["current_settings"]
        print("Current settings:", current_settings)
        print(f"Writing to {self.local_file}")
        self.local_file.write_text(json.dumps(current_settings, indent=2, sort_keys=True) + "\n", encoding="utf-8")
