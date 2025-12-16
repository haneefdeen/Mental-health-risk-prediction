from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

app = FastAPI(title="MindScope AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class TextRequest(BaseModel):
    text: str
    user_id: str

@app.get("/")
def root():
    return {"message": "MindScope AI is running!", "status": "success"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    if request.username == "admin" and request.password == "admin123":
        return {"access_token": "admin_token", "user": {"username": "admin", "name": "Administrator", "user_type": "admin"}}
    elif request.username == "user1" and request.password == "user123":
        return {"access_token": "user_token", "user": {"username": "user1", "name": "Test User", "user_type": "user"}}
    else:
        return {"error": "Invalid credentials"}

@app.post("/api/analyze/text")
def analyze_text(request: TextRequest):
    text = request.text.lower()
    
    # Simple emotion detection
    if any(word in text for word in ['happy', 'joy', 'great', 'wonderful', 'excited']):
        emotion = "happy"
        stress_level = "low"
    elif any(word in text for word in ['sad', 'depressed', 'lonely', 'hurt']):
        emotion = "sad"
        stress_level = "high"
    elif any(word in text for word in ['angry', 'mad', 'furious', 'hate']):
        emotion = "angry"
        stress_level = "high"
    elif any(word in text for word in ['anxious', 'worried', 'nervous', 'stress']):
        emotion = "anxious"
        stress_level = "high"
    else:
        emotion = "neutral"
        stress_level = "medium"
    
    suggestions = [
        "Practice deep breathing exercises",
        "Take regular breaks",
        "Maintain a positive mindset",
        "Consider professional help if needed"
    ]
    
    return {
        "emotion": emotion,
        "stress_level": stress_level,
        "confidence": 0.85,
        "suggestions": suggestions,
        "timestamp": "2024-01-15T10:30:00"
    }

@app.post("/api/analyze/image")
def analyze_image(request: dict):
    return {
        "emotion": "neutral",
        "stress_level": "medium",
        "confidence": 0.75,
        "suggestions": [
            "Maintain positive facial expressions",
            "Practice smiling more often",
            "Take care of your mental well-being"
        ],
        "timestamp": "2024-01-15T10:30:00"
    }

@app.get("/api/analyze/history")
def get_history():
    return {"analyses": []}

@app.get("/api/admin/summary")
def get_summary():
    return {
        "total_analyses": 0,
        "stress_distribution": {"low": 0, "medium": 0, "high": 0},
        "emotion_distribution": {},
        "recent_analyses": []
    }

@app.post("/api/reports/export")
def export_data():
    return {
        "user": {"username": "user1", "name": "Test User"},
        "analyses": [],
        "export_date": "2024-01-15T10:30:00",
        "total_analyses": 0
    }

if __name__ == "__main__":
    print("🚀 Starting MindScope AI Backend...")
    print("📡 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔐 Login: admin/admin123 or user1/user123")
    uvicorn.run(app, host="0.0.0.0", port=8000)
