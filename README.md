# Higgs Voice Studio — Desktop batch voice cloning

Desktop app tone **hồng / đen** dùng Higgs TTS 3 để clone giọng từ WAV/MP3 và tạo hàng loạt file WAV từ file TXT.

## Chức năng đã có

- Desktop UI bằng PySide6, không cần browser.
- Chọn **Auto / NVIDIA CUDA / CPU**.
- Clone giọng từ `.wav`, `.mp3` (và nhiều định dạng khác nếu decoder hỗ trợ).
- Transcript voice mẫu là **tùy chọn**; nếu có sẽ tăng cloning fidelity.
- Chọn file `.txt` có nhiều đoạn, **mỗi đoạn cách nhau bằng dòng trống**.
- Mỗi đoạn → một file WAV riêng.
- Tự bỏ số thứ tự đầu đoạn trước khi đưa vào TTS: `1.`, `2.`, `3)`, `4-`, ...
- Tên file = số thứ tự + 5 từ đầu của nội dung đã làm sạch.
  - `1. Xin chào mọi người hôm nay...` → `001_Xin_chao_moi_nguoi_hom.wav`
- Preview toàn bộ đoạn và tên file trước khi chạy.
- Progress, trạng thái từng file, nút dừng sau đoạn hiện tại.
- Model được giữ trong RAM/VRAM trong suốt phiên app để lần chạy tiếp theo không phải load lại nếu thiết bị không đổi.

## Model runtime

App dùng `multimodalart/higgs-audio-v3-tts-4b-transformers`, một Transformers `trust_remote_code` port dùng **weights Higgs TTS 3 gốc không thay đổi** và cung cấp `generate_speech()` với reference audio. Điều này cho phép cùng một desktop code chạy trên CUDA hoặc CPU mà không cần SGLang server.

Model khoảng 4B và output 24 kHz. Lần đầu chạy sẽ tải nhiều GB model vào Hugging Face cache.

## Cài nhanh trên Windows

### NVIDIA RTX 50-series — khuyến nghị

Yêu cầu: Python 3.12, NVIDIA driver mới, internet trong lần tải model đầu tiên.

Chạy:

```bat
scripts\setup_gpu_rtx50.bat
scripts\run.bat
```

Script cài PyTorch CUDA 12.8 (`cu128`) trước, sau đó cài app.

### CPU

```bat
scripts\setup_cpu.bat
scripts\run.bat
```

**Lưu ý:** CPU mode chạy được theo implementation này nhưng 4B TTS rất nặng. Float32 có thể cần trên 20 GB RAM và tốc độ chậm đáng kể. CPU mode phù hợp làm fallback/test, không phải lựa chọn tối ưu cho batch lớn.

## Kiểm tra GPU

Sau khi setup:

```bat
.venv\Scripts\python scripts\check_hardware.py
```

## MP3

`python-soundfile` hiện có thể đọc MP3 trên nhiều wheel hiện đại. Nếu MP3 của bạn không đọc được, app fallback sang `pydub`, lúc đó hãy cài FFmpeg và thêm `ffmpeg.exe` vào PATH.

## Cấu trúc file TXT

Ví dụ:

```text
1. Đây là đoạn đầu tiên. Số một sẽ không được đọc.

2. Đây là đoạn thứ hai và sẽ trở thành một file riêng.

3. This paragraph can be English while using the same cloned voice.
```

App tạo:

```text
001_Day_la_doan_dau_tien.wav
002_Day_la_doan_thu_hai.wav
003_This_paragraph_can_be_English.wav
```

Nếu đoạn không có số ở đầu, app dùng thứ tự xuất hiện trong file.

## Build desktop folder / EXE launcher

Sau khi môi trường chạy ổn:

```bat
scripts\build_windows.bat
```

Kết quả nằm trong `dist\HiggsVoiceStudio`. Model weights **không** được nhúng vào EXE; máy đích vẫn tải/cache model ở lần chạy đầu.

> PyTorch/Transformers là stack lớn. Với production installer, nên dùng one-folder installer (Inno Setup/NSIS) thay vì cố làm một file EXE duy nhất.

## License quan trọng

Đọc `LICENSE_NOTICE.md` trước khi phân phối app. Higgs TTS 3 không dùng một license thương mại tự do kiểu Apache-2.0 cho model weights. App source này không kèm weights.
