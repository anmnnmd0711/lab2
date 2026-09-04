from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from .engine import GenerationSettings, HiggsEngine
from .parsing import ParagraphItem


class GenerationService(QObject):
    log = Signal(str)
    progress = Signal(int, int, str)
    item_done = Signal(int, str)
    failed = Signal(str)
    finished = Signal(bool, str)

    def __init__(self) -> None:
        super().__init__()
        self.engine = HiggsEngine()
        self.cancel_requested = False
        self.busy = False

    def request_cancel(self) -> None:
        self.cancel_requested = True

    @Slot(dict)
    def generate_batch(self, job: dict) -> None:
        if self.busy:
            self.failed.emit("Đang có một tác vụ khác chạy.")
            return
        self.busy = True
        self.cancel_requested = False
        started = time.time()
        try:
            items: list[ParagraphItem] = job["items"]
            output_dir = Path(job["output_dir"])
            output_dir.mkdir(parents=True, exist_ok=True)
            reference_path = job["reference_path"]
            reference_text = job.get("reference_text", "")
            device = job.get("device", "auto")
            cpu_threads = int(job.get("cpu_threads", 0) or 0) or None
            settings = GenerationSettings(**job["settings"])

            self.log.emit(f"Đang load Higgs TTS 3 trên {device} …")
            actual = self.engine.load(device, cpu_threads=cpu_threads)
            self.log.emit(f"Model sẵn sàng trên {actual.upper()} | sample rate {self.engine.sample_rate} Hz")

            total = len(items)
            for idx, item in enumerate(items, start=1):
                if self.cancel_requested:
                    self.finished.emit(False, "Đã dừng theo yêu cầu.")
                    return
                self.progress.emit(idx - 1, total, f"Đang tạo {item.filename}")
                out = output_dir / item.filename
                self.engine.synthesize(
                    text=item.spoken_text,
                    reference_path=reference_path,
                    reference_text=reference_text,
                    output_path=out,
                    settings=settings,
                )
                self.item_done.emit(idx - 1, str(out))
                self.progress.emit(idx, total, f"Hoàn tất {item.filename}")

            elapsed = time.time() - started
            self.finished.emit(True, f"Hoàn tất {len(items)} file trong {elapsed:.1f}s.")
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
            self.finished.emit(False, "Tạo audio thất bại.")
        finally:
            self.busy = False
