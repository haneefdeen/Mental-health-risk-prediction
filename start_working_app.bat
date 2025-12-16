@echo off
echo ========================================
echo    MindScope AI - Complete Working App
echo ========================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d D:\capstone_project\backend && python -m uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d D:\capstone_project\frontend && npm run dev"

echo Waiting for frontend to start...
timeout /t 8 /nobreak >nul

echo Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo    MindScope AI is now running!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Test Credentials:
echo   Admin: username=admin, password=admin123
echo   User:  username=user1, password=user123
echo.
echo Features Working:
echo   - Modern React UI
echo   - Login System
echo   - Dashboard with Stats
echo   - Quick Actions
echo   - Recent Activity
echo   - Responsive Design
echo.
echo Press any key to exit...
pause >nul
