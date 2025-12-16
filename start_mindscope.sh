#!/bin/bash

echo "========================================"
echo "   MindScope AI - Quick Start Script"
echo "========================================"
echo

echo "[1/4] Starting Backend Server..."
cd backend
gnome-terminal -- bash -c "python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python datasets/dataset_manager.py && uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000; exec bash" &

echo "[2/4] Waiting for backend to initialize..."
sleep 5

echo "[3/4] Starting Frontend Server..."
cd ../frontend
gnome-terminal -- bash -c "npm install && npm run dev; exec bash" &

echo "[4/4] Opening application in browser..."
sleep 10
xdg-open http://localhost:3000

echo
echo "========================================"
echo "   MindScope AI is now running!"
echo "========================================"
echo
echo "Backend API:  http://localhost:8000"
echo "Frontend App: http://localhost:3000"
echo
echo "Press Enter to exit..."
read
