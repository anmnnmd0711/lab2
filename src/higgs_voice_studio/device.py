from __future__ import annotations

import os


def device_summary() -> dict:
    summary = {
        "cuda_available": False,
        "cuda_name": None,
        "cuda_vram_gb": None,
        "cpu_threads": os.cpu_count() or 1,
    }
    try:
        import torch

        summary["cuda_available"] = bool(torch.cuda.is_available())
        if torch.cuda.is_available():
            idx = torch.cuda.current_device()
            summary["cuda_name"] = torch.cuda.get_device_name(idx)
            total = torch.cuda.get_device_properties(idx).total_memory
            summary["cuda_vram_gb"] = round(total / (1024**3), 1)
    except Exception:
        pass
    return summary
