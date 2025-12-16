@echo off
echo ========================================
echo    MindScope AI - Easy Startup
echo ========================================
echo.

echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo [2/4] Installing Frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Frontend dependencies
    pause
    exit /b 1
)
cd ..

echo [3/4] Starting Backend Server...
start "Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

echo [4/4] Starting Frontend Server...
timeout /t 3 /nobreak >nul
start "Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo    MindScope AI is now running!
echo ========================================
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Test Credentials:
echo   Admin: username=admin, password=admin123
echo   User:  username=user1, password=user123
echo.
echo Press any key to exit...
pause >nul
