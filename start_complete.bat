@echo off
echo ========================================
echo    MindScope AI - Complete Application
echo ========================================
echo.

echo [1/4] Installing minimal Python dependencies...
pip install -r requirements_minimal.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo [2/4] Starting Backend Server...
start "Backend" cmd /k "python backend_simple.py"

echo [3/4] Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo [4/4] Opening Web Application...
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