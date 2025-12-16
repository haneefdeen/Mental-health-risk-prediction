from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import json
import re
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="MindScope AI",
    description="Mental Health Analysis Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str = "user"

class TextAnalysisRequest(BaseModel):
    text: str
    user_id: str

class ImageAnalysisRequest(BaseModel):
    image_data: str
    user_id: str

class AnalysisResponse(BaseModel):
    emotion: str
    stress_level: str
    confidence: float
    suggestions: List[str]
    timestamp: str

# Simple user database
users_db = {
    "admin": {"username": "admin", "password": "admin123", "user_type": "admin", "name": "Administrator"},
    "user1": {"username": "user1", "password": "user123", "user_type": "user", "name": "Test User"}
}

analysis_history = []

def analyze_text_emotion(text: str) -> Dict[str, Any]:
    """Simple text emotion analysis"""
    text_lower = text.lower()
    
    # Simple keyword-based emotion detection
    happy_words = ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'love', 'enjoy']
    sad_words = ['sad', 'depressed', 'lonely', 'hurt', 'cry', 'tears', 'down', 'blue']
    angry_words = ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'frustrated']
    anxious_words = ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'stress', 'panic']
    
    happy_count = sum(1 for word in happy_words if word in text_lower)
    sad_count = sum(1 for word in sad_words if word in text_lower)
    angry_count = sum(1 for word in angry_words if word in text_lower)
    anxious_count = sum(1 for word in anxious_words if word in text_lower)
    
    # Determine emotion
    if happy_count > max(sad_count, angry_count, anxious_count):
        emotion = "happy"
        stress_level = "low"
    elif sad_count > max(happy_count, angry_count, anxious_count):
        emotion = "sad"
        stress_level = "high"
    elif angry_count > max(happy_count, sad_count, anxious_count):
        emotion = "angry"
        stress_level = "high"
    elif anxious_count > max(happy_count, sad_count, angry_count):
        emotion = "anxious"
        stress_level = "high"
    else:
        emotion = "neutral"
        stress_level = "medium"
    
    # Generate suggestions
    suggestions = []
    if stress_level == "high":
        suggestions = [
            "Consider talking to a mental health professional",
            "Try deep breathing exercises",
            "Take breaks throughout your day",
            "Practice mindfulness meditation"
        ]
    elif stress_level == "medium":
        suggestions = [
            "Try some light exercise",
            "Listen to calming music",
            "Take a walk in nature",
            "Practice gratitude journaling"
        ]
    else:
        suggestions = [
            "Keep up the positive mindset!",
            "Continue your healthy habits",
            "Share your positivity with others",
            "Consider helping someone in need"
        ]
    
    return {
        "emotion": emotion,
        "stress_level": stress_level,
        "confidence": 0.85,
        "suggestions": suggestions
    }

def analyze_image_emotion(image_data: str) -> Dict[str, Any]:
    """Simple image emotion analysis (mock)"""
    # Mock analysis - in real app, you'd use proper image processing
    return {
        "emotion": "neutral",
        "stress_level": "medium",
        "confidence": 0.75,
        "suggestions": [
            "Consider your facial expressions",
            "Try to maintain a positive demeanor",
            "Practice smiling more often",
            "Take care of your mental well-being"
        ]
    }

# API Routes
@app.get("/")
async def root():
    return {"message": "MindScope AI - Mental Health Analysis Platform", "status": "running"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login endpoint"""
    user = users_db.get(request.username)
    
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate simple token
    token = f"{request.username}_token"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "name": user["name"],
            "user_type": user["user_type"]
        }
    }

@app.post("/api/analyze/text")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text for emotion and stress"""
    result = analyze_text_emotion(request.text)
    
    # Store analysis
    analysis_record = {
        "user_id": request.user_id,
        "type": "text",
        "input": request.text,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    analysis_history.append(analysis_record)
    
    return AnalysisResponse(
        emotion=result["emotion"],
        stress_level=result["stress_level"],
        confidence=result["confidence"],
        suggestions=result["suggestions"],
        timestamp=analysis_record["timestamp"]
    )

@app.post("/api/analyze/image")
async def analyze_image(request: ImageAnalysisRequest):
    """Analyze image for facial emotion"""
    result = analyze_image_emotion(request.image_data)
    
    # Store analysis
    analysis_record = {
        "user_id": request.user_id,
        "type": "image",
        "input": "image_data",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    analysis_history.append(analysis_record)
    
    return AnalysisResponse(
        emotion=result["emotion"],
        stress_level=result["stress_level"],
        confidence=result["confidence"],
        suggestions=result["suggestions"],
        timestamp=analysis_record["timestamp"]
    )

@app.get("/api/analyze/history")
async def get_analysis_history():
    """Get analysis history"""
    return {"analyses": analysis_history}

@app.get("/api/admin/summary")
async def get_admin_summary():
    """Get admin analytics summary"""
    total_analyses = len(analysis_history)
    stress_levels = [a["result"]["stress_level"] for a in analysis_history]
    emotions = [a["result"]["emotion"] for a in analysis_history]
    
    stress_distribution = {
        "low": stress_levels.count("low"),
        "medium": stress_levels.count("medium"),
        "high": stress_levels.count("high")
    }
    
    emotion_distribution = {}
    for emotion in emotions:
        emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
    
    return {
        "total_analyses": total_analyses,
        "stress_distribution": stress_distribution,
        "emotion_distribution": emotion_distribution,
        "recent_analyses": analysis_history[-10:] if analysis_history else []
    }

@app.post("/api/reports/export")
async def export_report():
    """Export data as JSON"""
    export_data = {
        "analyses": analysis_history,
        "export_date": datetime.now().isoformat(),
        "total_analyses": len(analysis_history)
    }
    
    return export_data

if __name__ == "__main__":
    print("🧠 Starting MindScope AI Backend...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔐 Demo Credentials:")
    print("   Admin: admin / admin123")
    print("   User:  user1 / user123")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
