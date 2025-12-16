@echo off
echo ========================================
echo    MindScope AI - ENHANCED VERSION
echo ========================================
echo.

echo [1/4] Killing any existing processes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/4] Installing enhanced dependencies...
pip install fastapi uvicorn python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv reportlab scikit-learn pandas pillow

echo [3/4] Starting Enhanced Backend Server...
start "MindScope Enhanced Backend" cmd /k "python backend_enhanced.py"

echo [4/4] Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo    MindScope AI Enhanced is running!
echo ========================================
echo Frontend: Open index_enhanced.html in your browser
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Enhanced Features:
echo   - High-risk detection for crisis intervention
echo   - Role-based admin and user features
echo   - Enhanced image analysis with varied results
echo   - Image removal option
echo   - Proper PDF/JSON report generation
echo   - Professional UI with emotion icons
echo   - Behavioral analytics and charts
echo   - Dark/Light theme toggle
echo   - Responsive design
echo.
echo Demo Credentials:
echo   Admin: username=admin, password=admin123
echo   User:  username=user1, password=user123
echo.
echo Test High-Risk Detection:
echo   Try: "I'm going to die" or "I want to kill myself"
echo.
echo Press any key to exit...
pause >nul
