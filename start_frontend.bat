@echo off
echo ========================================
echo    MindScope AI - Complete Frontend
echo ========================================
echo.

echo Installing Frontend Dependencies...
cd frontend
call npm install

echo.
echo Starting Frontend Development Server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo Waiting for frontend to start...
timeout /t 10 /nobreak >nul

echo Opening browser...
start http://localhost:3000

echo.
echo ========================================
echo    MindScope AI Frontend is Running!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo.
echo Features Available:
echo   - Modern React + TailwindCSS UI
echo   - Dark/Light theme toggle
echo   - User and Doctor login modes
echo   - Text and Image analysis
echo   - Emotional timeline charts
echo   - AI explainability features
echo   - PDF/JSON report export
echo   - Admin analytics dashboard
echo   - Privacy and ethics management
echo.
echo Test Credentials:
echo   Admin: username=admin, password=admin123
echo   User:  username=user1, password=user123
echo.
echo Press any key to exit...
pause >nul
