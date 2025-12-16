# 🧠 MindScope AI - Easy Startup Guide

## 🚀 **Super Quick Start (Choose One)**

### **Option 1: One-Click Scripts**
```bash
# Windows
start_mindscope.bat

# Mac/Linux
./start_mindscope.sh

# Python (Any OS)
python launch_mindscope.py
```

### **Option 2: NPM Command**
```bash
npm start
```

### **Option 3: Manual (Step by Step)**
```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python datasets/dataset_manager.py
uvicorn empath_app:app --reload

# Terminal 2 - Frontend  
cd frontend
npm install
npm run dev
```

---

## 🌐 **Access Your App**

- **Main Application**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

---

## 🎯 **What Happens When You Start**

1. ✅ **Backend Server** starts on port 8000
2. ✅ **Frontend Server** starts on port 3000  
3. ✅ **Datasets** are initialized automatically
4. ✅ **Browser** opens to the application
5. ✅ **Ready to use!** 🎉

---

## 🛠️ **Troubleshooting**

### **Port Already in Use**
```bash
# Kill processes on ports 3000 and 8000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### **Dependencies Issues**
```bash
# Reinstall everything
npm run install-all
```

### **Reset Everything**
```bash
# Delete and reinstall
rm -rf frontend/node_modules backend/venv
npm run install-all
```

---

## 🎉 **You're All Set!**

Your MindScope AI application is now running with:
- ✅ **Real datasets** (FER2013, DAIC-WOZ, Reddit, Dreaddit)
- ✅ **Multimodal analysis** (Text + Image + Behavioral)
- ✅ **User & Doctor modes**
- ✅ **Modern UI** with dark/light themes
- ✅ **Complete features** as requested

**Happy analyzing!** 🧠✨
