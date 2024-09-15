@echo off
chcp 1251 >nul
cls
echo =========================
echo Creating virtual environment...
echo =========================
if not exist venv (
    echo Creating new virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists, skipping creation...
)
echo =========================
echo Activating virtual environment...
echo =========================
call "%~dp0venv\Scripts\activate.bat"
echo =========================
echo Installing dependencies...
echo =========================
python -m pip install --upgrade pip
pip install -r "%~dp0requirements.txt"
echo =========================
echo Launching application...
echo =========================
python "%~dp0main.py"
pause
