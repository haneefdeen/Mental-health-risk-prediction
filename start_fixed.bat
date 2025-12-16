@echo off
echo ========================================
echo    MindScope AI - FIXED VERSION
echo ========================================
echo.

echo [1/4] Killing any existing Python processes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Installing ultra-minimal dependencies...
pip install -r requirements_ultra_minimal.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [3/4] Starting Backend Server...
start "MindScope Backend" cmd /k "python backend_fixed.py"

echo [4/4] Waiting for backend to start...
timeout /t 3 /nobreak >nul

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
echo Features:
echo   - Professional UI with Bootstrap 5
echo   - Real-time text and image analysis
echo   - Interactive charts and dashboards
echo   - PDF/JSON report export
echo   - Dark/Light theme toggle
echo   - Responsive design
echo.
echo Press any key to exit...
pause >nul