@echo off
setlocal
cd /d "%~dp0\.."
py -3.12 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip wheel setuptools
python -m pip install torch torchaudio
python -m pip install -r requirements-app.txt
python -m pip install -e .
echo.
echo CPU setup complete. Run scripts\run.bat
pause
