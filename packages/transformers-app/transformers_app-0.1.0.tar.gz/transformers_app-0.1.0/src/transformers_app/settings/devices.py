from typing import List, Literal
import torch

DeviceStr = str
DeviceMapStr = Literal["auto", "balanced"]  # extend if you want


def available_devices() -> List[DeviceStr]:
    devs: List[DeviceStr] = ["cpu"]

    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        devs.append("mps")

    if torch.cuda.is_available():
        devs.extend([f"cuda:{i}" for i in range(torch.cuda.device_count())])

    return devs


def available_device_maps() -> List[DeviceMapStr]:
    maps: List[DeviceMapStr] = []

    if torch.cuda.is_available():
        maps.extend(["auto", "balanced"])

    return maps
