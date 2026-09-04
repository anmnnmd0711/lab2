from __future__ import annotations

import gc
import os
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .audio_io import load_audio_mono, save_wav

# This Transformers port uses the original Higgs TTS 3 checkpoint weights unchanged,
# while exposing generate_speech() for direct local CPU/CUDA use.
DEFAULT_MODEL_ID = "multimodalart/higgs-audio-v3-tts-4b-transformers"


@dataclass(slots=True)
class GenerationSettings:
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 50
    max_new_tokens: int = 2048
    seed: int = -1


class HiggsEngine:
    def __init__(self, model_id: str = DEFAULT_MODEL_ID) -> None:
        self.model_id = model_id
        self.model = None
        self.tokenizer = None
        self.device = None
        self.sample_rate = 24000

    @staticmethod
    def resolve_device(selection: str) -> str:
        selection = selection.lower().strip()
        if selection == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        if selection.startswith("cuda"):
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA được chọn nhưng PyTorch không phát hiện NVIDIA GPU.")
            return selection
        return "cpu"

    def load(self, selection: str, cpu_threads: int | None = None) -> str:
        target = self.resolve_device(selection)
        if self.model is not None and self.device == target:
            return target

        self.unload()
        if target == "cpu":
            threads = cpu_threads or max(1, (os.cpu_count() or 4) - 1)
            torch.set_num_threads(max(1, int(threads)))
            dtype = torch.float32
        else:
            # RTX 30/40/50-class hardware handles bf16 well and this saves a lot of VRAM.
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            dtype=dtype,
            low_cpu_mem_usage=True,
        )
        self.model = self.model.to(target).eval()
        # Preload codec so first paragraph does not pay the codec startup cost.
        if hasattr(self.model, "get_audio_codec"):
            self.model.get_audio_codec()
        self.device = target
        self.sample_rate = int(getattr(self.model.config, "sample_rate", 24000))
        return target

    def unload(self) -> None:
        self.model = None
        self.tokenizer = None
        self.device = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    @torch.inference_mode()
    def synthesize(
        self,
        text: str,
        reference_path: str,
        reference_text: str,
        output_path: str | Path,
        settings: GenerationSettings,
    ) -> Path:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model chưa được load.")
        if settings.seed >= 0:
            torch.manual_seed(settings.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(settings.seed)

        ref_audio, ref_sr = load_audio_mono(reference_path)
        kwargs = {
            "reference_audio": ref_audio,
            "reference_sample_rate": ref_sr,
            "max_new_tokens": int(settings.max_new_tokens),
            "temperature": float(settings.temperature),
            "top_p": float(settings.top_p) if settings.top_p < 1.0 else None,
            "top_k": int(settings.top_k) if settings.top_k > 0 else None,
        }
        if reference_text.strip():
            kwargs["reference_text"] = reference_text.strip()

        audio = self.model.generate_speech(text, self.tokenizer, **kwargs)
        if audio is None or int(audio.numel()) == 0:
            raise RuntimeError("Model không tạo ra audio.")
        out = Path(output_path)
        save_wav(out, audio, self.sample_rate)
        return out
