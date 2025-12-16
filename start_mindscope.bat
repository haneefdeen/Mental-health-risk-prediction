@echo off
echo ========================================
echo    MindScope AI - Quick Start Script
echo ========================================
echo.

echo [1/4] Starting Backend Server...
cd backend
start "MindScope Backend" cmd /k "python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python datasets\dataset_manager.py && uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000"

echo [2/4] Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo [3/4] Starting Frontend Server...
cd ..\frontend
start "MindScope Frontend" cmd /k "npm install && npm run dev"

echo [4/4] Opening application in browser...
timeout /t 10 /nobreak > nul
start http://localhost:3000

echo.
echo ========================================
echo    MindScope AI is now running!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend App: http://localhost:3000
echo.
echo Press any key to exit this script...
pause > nul
