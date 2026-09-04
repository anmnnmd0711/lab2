from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
import torch


def load_audio_mono(path: str | Path) -> tuple[torch.Tensor, int]:
    """Load WAV/MP3/etc. as mono float32. soundfile handles modern MP3 builds.

    If libsndfile cannot decode a specific MP3, pydub/FFmpeg is used as fallback.
    """
    path = str(path)
    try:
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        mono = np.mean(data, axis=1, dtype=np.float32)
        return torch.from_numpy(mono.copy()), int(sr)
    except Exception as first_error:
        try:
            from pydub import AudioSegment

            seg = AudioSegment.from_file(path)
            seg = seg.set_channels(1)
            samples = np.array(seg.get_array_of_samples(), dtype=np.float32)
            scale = float(1 << (8 * seg.sample_width - 1))
            if scale > 0:
                samples /= scale
            return torch.from_numpy(samples), int(seg.frame_rate)
        except Exception as second_error:
            raise RuntimeError(
                "Không thể đọc file voice. Với MP3, hãy cài FFmpeg nếu soundfile không giải mã được. "
                f"soundfile={first_error}; fallback={second_error}"
            ) from second_error


def save_wav(path: str | Path, waveform: torch.Tensor | np.ndarray, sample_rate: int) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(waveform, torch.Tensor):
        arr = waveform.detach().float().cpu().numpy()
    else:
        arr = np.asarray(waveform, dtype=np.float32)
    arr = np.squeeze(arr)
    if arr.ndim != 1:
        raise ValueError(f"Expected mono waveform, got shape {arr.shape}")
    sf.write(path, arr, int(sample_rate), subtype="PCM_16")
