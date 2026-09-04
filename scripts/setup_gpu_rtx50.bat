@echo off
setlocal
cd /d "%~dp0\.."
py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip wheel setuptools
REM RTX 50-series / Blackwell: CUDA 12.8 PyTorch wheels.
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements-app.txt
python -m pip install -e .
echo.
echo GPU setup complete. Run scripts\run.bat
pause
