@echo off
title MindScope AI - Complete Application
color 0A

echo.
echo ========================================
echo    MindScope AI - Complete Application
echo ========================================
echo.
echo Starting your mental health analysis platform...
echo.

echo [1/4] Starting Backend Server...
start "Backend Server" cmd /k "cd /d D:\capstone_project\backend && echo Starting Backend... && python -m uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000"

echo [2/4] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [3/4] Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d D:\capstone_project\frontend && echo Starting Frontend... && npm run dev"

echo [4/4] Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ========================================
echo    🎉 MindScope AI is now running!
echo ========================================
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend:  http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 🔑 Test Credentials:
echo    Admin: username=admin, password=admin123
echo    User:  username=user1, password=user123
echo.
echo ✅ Features Working:
echo    - Modern React UI
echo    - Professional Design
echo    - Interactive Components
echo    - Responsive Layout
echo    - FastAPI Backend
echo    - Real-time Updates
echo.
echo 🚀 Opening browser...
start http://localhost:3000

echo.
echo Press any key to exit this window...
pause >nul
