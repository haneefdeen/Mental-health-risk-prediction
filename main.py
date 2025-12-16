#!/usr/bin/env python3
"""
MindScope AI - Main Application Runner
Single command to start the complete mental health analysis platform
"""

import os
import sys
import subprocess
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print the MindScope AI banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║  🧠 MindScope AI - Mental Health Analysis Platform           ║
    ║                                                              ║
    ║  Multimodal Emotion Detection & AI Coping Suggestions       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check Python packages
    try:
        import fastapi
        import torch
        import transformers
        import uvicorn
        print("✅ Python dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check Node.js and npm
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✅ Node.js and npm found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js or npm not found")
        print("Please install Node.js from https://nodejs.org/")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies if needed"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            print("✅ Frontend dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    try:
        # Start backend in a separate thread
        def run_backend():
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "backend.main:app", 
                "--reload", 
                "--host", "0.0.0.0", 
                "--port", "8000"
            ])
        
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        time.sleep(3)  # Give backend time to start
        print("✅ Backend server started on http://localhost:8000")
        return True
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the React frontend server"""
    print("🎨 Starting frontend server...")
    try:
        # Start frontend in a separate thread
        def run_frontend():
            subprocess.run(["npm", "run", "dev"], cwd="frontend")
        
        frontend_thread = threading.Thread(target=run_frontend, daemon=True)
        frontend_thread.start()
        time.sleep(5)  # Give frontend time to start
        print("✅ Frontend server started on http://localhost:3000")
        return True
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def open_browser():
    """Open the application in the default browser"""
    print("🌐 Opening application in browser...")
    time.sleep(2)  # Wait for servers to be ready
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("Please manually open http://localhost:3000")

def print_status():
    """Print application status and URLs"""
    status = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🎉 MindScope AI is Running!              ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  🌐 Frontend:     http://localhost:3000                     ║
    ║  🔧 Backend API:  http://localhost:8000                      ║
    ║  📚 API Docs:     http://localhost:8000/docs                ║
    ║                                                              ║
    ║  🔐 Test Credentials:                                        ║
    ║     Admin: admin@mindscope.ai / admin123                    ║
    ║     User:  user@mindscope.ai / user123                      ║
    ║                                                              ║
    ║  🎯 Features Available:                                      ║
    ║     • Multimodal emotion detection                          ║
    ║     • AI-powered coping suggestions                         ║
    ║     • Behavioral pattern analysis                            ║
    ║     • Admin analytics dashboard                             ║
    ║     • Explainable AI with Grad-CAM                          ║
    ║     • PDF report generation                                  ║
    ║                                                              ║
    ║  Press Ctrl+C to stop the application                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(status)

def main():
    """Main application entry point"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Start backend
    if not start_backend():
        sys.exit(1)
    
    # Start frontend
    if not start_frontend():
        sys.exit(1)
    
    # Open browser
    open_browser()
    
    # Print status
    print_status()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down MindScope AI...")
        print("Thank you for using MindScope AI! 🧠")

if __name__ == "__main__":
    main()
