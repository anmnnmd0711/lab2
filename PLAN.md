# Kế hoạch phát triển Higgs Voice Studio

## Mục tiêu MVP (đã có trong source)

1. Desktop app Windows bằng PySide6, theme hồng/đen.
2. Device selector: Auto / NVIDIA CUDA / CPU.
3. Voice cloning từ WAV/MP3, transcript tham chiếu tùy chọn.
4. Import TXT, tách paragraph theo dòng trống.
5. Bỏ ordinal đầu paragraph (`1.`, `2)`, `3-`, `4:`) trước khi synthesize.
6. Một paragraph → một WAV.
7. Tên WAV lấy số thứ tự + 5 từ đầu, Windows-safe.
8. Preview danh sách output trước khi chạy.
9. Batch progress, trạng thái từng file, cancel sau paragraph hiện tại.
10. Giữ model trong RAM/VRAM giữa các batch trong cùng phiên app.

## Phase 2 — ổn định production desktop

- Lưu settings bằng QSettings.
- Cache reference audio codes để không encode lại cùng voice cho từng paragraph (nếu runtime port expose public reference-code API ổn định).
- Retry từng paragraph khi CUDA OOM / generation trống.
- Resume batch: bỏ qua file đã hoàn tất.
- Audio player preview ngay trong app.
- Export MP3/FLAC bên cạnh WAV.
- Auto ASR transcript cho voice mẫu để tăng clone fidelity.
- Long paragraph policy: chia sentence nội bộ, ghép lại nhưng vẫn giữ một output file cho mỗi paragraph.
- Log file + crash report local.

## Phase 3 — installer

- PyInstaller one-folder build.
- Inno Setup/NSIS installer.
- Kiểm tra CUDA/PyTorch/driver ở first-run wizard.
- Chọn model cache folder và hiển thị dung lượng download.
- Tùy chọn offline model cache.

## Phase 4 — tối ưu GPU

- Backend interface `TransformersBackend` / `SGLangBackend`.
- RTX 5090/24–32GB: ưu tiên SGLang-Omni nếu cần throughput/streaming cao.
- CPU vẫn dùng Transformers fallback.
- Queue/concurrency cho batch rất lớn.

## Test matrix khuyến nghị

- Windows 11 + CPU 32 GB RAM.
- RTX 5070/5070 Ti: kiểm tra OOM thực tế; fallback CPU nếu không đủ VRAM.
- RTX 5080 16 GB: kiểm tra full-model VRAM.
- RTX 5090 32 GB: target GPU chính.
- Voice reference: WAV 16/24/44.1/48 kHz; mono/stereo; MP3 128/192/320 kbps.
- TXT UTF-8/UTF-8 BOM/UTF-16, tiếng Việt + English.
- 1 / 10 / 100+ paragraphs.
