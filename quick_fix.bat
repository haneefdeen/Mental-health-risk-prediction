@echo off
echo ========================================
echo    MindScope AI - SUPER SIMPLE FIX
echo ========================================
echo.

echo Fixing dependency conflicts...
pip install numpy==1.24.3 torch==2.0.1 torchvision==0.15.2 transformers==4.30.0

echo Starting MindScope AI...
python main.py

echo.
echo Press any key to exit...
pause >nul
