# MindScope AI - Complete Setup Guide

## 🎉 **Backend is Running Successfully!**

Your backend is now running at: **http://localhost:8000**

## 🚀 **How to Use Your App:**

### **Step 1: Open the Frontend**
Simply open `index.html` in your web browser (Chrome, Firefox, Edge, etc.)

### **Step 2: Login**
Use these credentials:
- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`user1`, password=`user123`

### **Step 3: Start Analyzing!**
- Click on "Analyze" in the navigation
- Enter text or upload an image
- Get instant AI-powered mental health insights!

## 📡 **Backend Endpoints:**

- **Root**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Login**: POST http://localhost:8000/api/auth/login
- **Text Analysis**: POST http://localhost:8000/api/analyze/text
- **Image Analysis**: POST http://localhost:8000/api/analyze/image

## 🔧 **If Backend Stops:**

Run this command to restart:
```bash
python backend_working.py
```

Or use the batch file:
```bash
start_clean.bat
```

## ✨ **Features Available:**

✅ **Dashboard** - Real-time stats and charts
✅ **Text Analysis** - AI emotion detection
✅ **Image Analysis** - Facial emotion recognition
✅ **Timeline** - Emotional progress tracking
✅ **Reports** - PDF/JSON export
✅ **Theme Toggle** - Dark/light mode
✅ **Responsive Design** - Mobile-friendly
✅ **Professional UI** - Modern, sleek design

## 🎯 **Quick Test:**

1. Open `index.html` in your browser
2. Login with `admin` / `admin123`
3. Go to "Analyze" section
4. Type: "I feel happy today!"
5. Click "Analyze Text"
6. See your results! 🎉

## 📞 **Troubleshooting:**

**Problem**: Backend port already in use
**Solution**: Run `taskkill /f /im python.exe` then restart

**Problem**: Can't login
**Solution**: Make sure backend is running at http://localhost:8000

**Problem**: Frontend not loading
**Solution**: Open `index.html` directly in browser (not through a server)

---

**Your MindScope AI is ready to use!** 🧠✨
