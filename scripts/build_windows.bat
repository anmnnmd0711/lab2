@echo off
setlocal
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name HiggsVoiceStudio ^
  --paths src ^
  --collect-all PySide6 ^
  --collect-all transformers ^
  --collect-all huggingface_hub ^
  app.py

echo.
echo Build finished under dist\HiggsVoiceStudio
pause
