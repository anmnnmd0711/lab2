@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe (
  echo .venv not found. Run setup_cpu.bat or setup_gpu_rtx50.bat first.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python app.py
