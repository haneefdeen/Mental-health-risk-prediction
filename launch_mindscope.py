#!/usr/bin/env python3
"""
MindScope AI - Easy Launcher Script
One-click startup for the entire application
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    print("=" * 50)
    print("    MindScope AI - Easy Launcher")
    print("=" * 50)
    print()

def check_requirements():
    """Check if required tools are installed"""
    print("Checking requirements...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("❌ Python 3.8+ required")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except:
        print("❌ npm not found")
        return False
    
    print()
    return True

def setup_backend():
    """Setup and start backend"""
    print("🚀 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Create virtual environment
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            activate_script = "venv\\Scripts\\activate.bat"
            pip_path = "venv\\Scripts\\pip"
            python_path = "venv\\Scripts\\python"
        else:  # Mac/Linux
            activate_script = "venv/bin/activate"
            pip_path = "venv/bin/pip"
            python_path = "venv/bin/python"
        
        print("📥 Installing Python dependencies...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("📊 Initializing datasets...")
        subprocess.run([python_path, "datasets/dataset_manager.py"], check=True)
        
        print("🌐 Starting backend server...")
        # Start backend in background
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                "cmd", "/c", 
                f"{activate_script} && uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Mac/Linux
            subprocess.Popen([
                "bash", "-c",
                f"source {activate_script} && uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000"
            ])
        
        print("✅ Backend started successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend setup failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Backend setup error: {e}")
        return False
    finally:
        os.chdir("..")

def setup_frontend():
    """Setup and start frontend"""
    print("🎨 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    try:
        print("📥 Installing Node.js dependencies...")
        subprocess.run(["npm", "install"], check=True)
        
        print("🌐 Starting frontend server...")
        # Start frontend in background
        if os.name == 'nt':  # Windows
            subprocess.Popen([
                "cmd", "/c", 
                "npm run dev"
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Mac/Linux
            subprocess.Popen([
                "bash", "-c",
                "npm run dev"
            ])
        
        print("✅ Frontend started successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend setup failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Frontend setup error: {e}")
        return False
    finally:
        os.chdir("..")

def open_browser():
    """Open browser after servers start"""
    print("⏳ Waiting for servers to initialize...")
    time.sleep(10)
    
    print("🌐 Opening MindScope AI in browser...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened successfully!")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("🌐 Please manually open: http://localhost:3000")

def main():
    """Main launcher function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements check failed. Please install missing tools.")
        return
    
    print("🚀 Starting MindScope AI...")
    print()
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return
    
    print()
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return
    
    print()
    
    # Open browser
    open_browser()
    
    print()
    print("=" * 50)
    print("    🎉 MindScope AI is now running!")
    print("=" * 50)
    print()
    print("📱 Access Points:")
    print("   • Main App:    http://localhost:3000")
    print("   • API Docs:    http://localhost:8000/docs")
    print("   • API Health:  http://localhost:8000/health")
    print()
    print("🛑 To stop servers: Close the terminal windows or press Ctrl+C")
    print()
    
    # Keep script running
    try:
        input("Press Enter to exit...")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
