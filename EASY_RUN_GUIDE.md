# MindScope AI - Easy Run Guide

## 🚀 **Super Easy Startup (One-Click)**

### **Windows Users:**
```bash
# Just double-click this file:
start_mindscope.bat
```

### **Mac/Linux Users:**
```bash
# Make executable and run:
chmod +x start_mindscope.sh
./start_mindscope.sh
```

**That's it!** The script will automatically:
- ✅ Install all dependencies
- ✅ Start the backend server
- ✅ Start the frontend server  
- ✅ Open your browser to the app

---

## 🛠️ **Manual Setup (If Needed)**

### **Step 1: Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize datasets
python datasets/dataset_manager.py

# Start backend server
uvicorn empath_app:app --reload --host 0.0.0.0 --port 8000
```

### **Step 2: Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start frontend server
npm run dev
```

### **Step 3: Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🎯 **Quick Commands**

### **Start Everything:**
```bash
# Windows
start_mindscope.bat

# Mac/Linux  
./start_mindscope.sh
```

### **Stop Everything:**
```bash
# Press Ctrl+C in both terminal windows
# Or close the terminal windows
```

### **Restart Backend Only:**
```bash
cd backend
uvicorn empath_app:app --reload
```

### **Restart Frontend Only:**
```bash
cd frontend
npm run dev
```

---

## 🔧 **Troubleshooting**

### **Port Already in Use:**
```bash
# Kill processes using ports 3000 and 8000
# Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### **Dependencies Issues:**
```bash
# Backend
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Frontend
cd frontend
npm install --force
```

### **Dataset Issues:**
```bash
cd backend
python datasets/dataset_manager.py
```

---

## 📱 **Access Points**

| Service | URL | Description |
|---------|-----|-------------|
| **Main App** | http://localhost:3000 | User interface |
| **API Docs** | http://localhost:8000/docs | Backend documentation |
| **API Health** | http://localhost:8000/health | Backend status |

---

## 🎉 **First Time Setup**

1. **Extract your datasets** (if not already done)
2. **Run the startup script**: `start_mindscope.bat` (Windows) or `./start_mindscope.sh` (Mac/Linux)
3. **Wait for both servers to start** (about 30 seconds)
4. **Open browser** to http://localhost:3000
5. **Register/Login** and start using MindScope AI!

---

## 💡 **Pro Tips**

### **Development Mode:**
- Backend auto-reloads when you change code
- Frontend hot-reloads when you change code
- Both servers restart automatically

### **Production Mode:**
```bash
# Backend (production)
cd backend
uvicorn empath_app:app --host 0.0.0.0 --port 8000

# Frontend (production build)
cd frontend
npm run build
npm run preview
```

### **Training Models (Optional):**
```bash
cd backend
python train_models.py --model all
```

---

## 🆘 **Need Help?**

### **Check Server Status:**
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000

### **View Logs:**
- Backend logs appear in the backend terminal
- Frontend logs appear in the frontend terminal

### **Reset Everything:**
```bash
# Stop all servers (Ctrl+C)
# Delete node_modules and reinstall
cd frontend
rm -rf node_modules
npm install

# Delete venv and recreate
cd ../backend  
rm -rf venv
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**Your MindScope AI is ready to go!** 🚀
