@echo off
echo ========================================
echo    MindScope AI - Easy Startup
echo ========================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d D:\capstone_project\backend && python -m uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d D:\capstone_project\frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo    MindScope AI is now running!
echo ========================================
echo.
echo Backend API:  http://localhost:8000
echo Frontend App: http://localhost:3000
echo.
echo Press any key to exit...
pause >nul
