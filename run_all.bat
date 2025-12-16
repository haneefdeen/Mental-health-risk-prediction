@echo off
cd /d %~dp0

REM Activate virtual environment if it exists
IF EXIST "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

start "" python -m mindscope_flask.app
timeout /t 3 >nul
start "" http://localhost:5000












