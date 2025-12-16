@echo off
echo ========================================
echo    MindScope AI - Lightweight Version
echo ========================================
echo.

echo [1/3] Installing Python dependencies...
pip install fastapi uvicorn python-multipart python-jose passlib python-dotenv

echo [2/3] Starting Backend Server...
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo [3/3] Opening Web App...
timeout /t 2 /nobreak >nul
start "" "index.html"

echo.
echo ========================================
echo    MindScope AI is now running!
echo ========================================
echo Frontend: Open index.html in your browser
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Demo Credentials:
echo   Admin: username=admin, password=admin123
echo   User:  username=user1, password=user123
echo.
echo Press any key to exit...
pause >nul
