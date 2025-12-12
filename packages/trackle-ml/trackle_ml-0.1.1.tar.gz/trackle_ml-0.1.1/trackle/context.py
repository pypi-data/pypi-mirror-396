"""
Environment and hardware context capture.
"""

from __future__ import annotations

import os
import platform
from typing import Any


def _torch_info() -> dict[str, Any]:
    try:
        import torch
    except Exception:
        return {"torch_available": False}
    info: dict[str, Any] = {"torch_available": True, "cuda_available": torch.cuda.is_available()}
    if torch.cuda.is_available():
        info["cuda_device_count"] = torch.cuda.device_count()
    return info


def capture() -> dict[str, Any]:
    data = {
        "python_version": platform.python_version(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
    }
    data.update(_torch_info())
    return data

