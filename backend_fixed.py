from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import base64
from PIL import Image
import io
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import re

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

# Security
security = HTTPBearer()

# Data models
class User(BaseModel):
    username: str
    password: str
    user_type: str = "user"
    name: str = ""

class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str = "user"

class TextAnalysisRequest(BaseModel):
    text: str
    user_id: str

class ImageAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded
    user_id: str

class AnalysisResponse(BaseModel):
    emotion: str
    stress_level: str
    confidence: float
    suggestions: List[str]
    timestamp: str

# In-memory storage (for demo)
users_db = {
    "admin": {
        "username": "admin",
        "password_hash": "admin123",  # Simplified for demo
        "user_type": "admin",
        "name": "Administrator"
    },
    "user1": {
        "username": "user1", 
        "password_hash": "user123",  # Simplified for demo
        "user_type": "user",
        "name": "Test User"
    }
}

analysis_history = []

# Simple ML models
text_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
emotion_classifier = LogisticRegression()

# Initialize with sample data
sample_texts = [
    "I feel so happy today! Everything is going great.",
    "I'm really stressed about work and can't sleep.",
    "Feeling anxious about the upcoming exam.",
    "I love spending time with my family.",
    "I'm feeling depressed and lonely.",
    "Excited about my vacation next week!",
    "Worried about my health condition.",
    "Grateful for all the support I've received."
]

sample_labels = [
    "happy", "stressed", "anxious", "happy", 
    "sad", "excited", "worried", "grateful"
]

# Train the model
X = text_vectorizer.fit_transform(sample_texts)
emotion_classifier.fit(X, sample_labels)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Simple token validation (in real app, use JWT)
    if token in ["admin_token", "user_token"]:
        return {"username": "admin" if token == "admin_token" else "user1"}
    raise HTTPException(status_code=401, detail="Invalid token")

def analyze_text_emotion(text: str) -> Dict[str, Any]:
    """Analyze text for emotion and stress level"""
    # Clean and preprocess text
    text_clean = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    
    # Vectorize text
    text_vector = text_vectorizer.transform([text_clean])
    
    # Predict emotion
    emotion = emotion_classifier.predict(text_vector)[0]
    confidence = max(emotion_classifier.predict_proba(text_vector)[0])
    
    # Determine stress level based on keywords
    stress_keywords = ['stressed', 'anxious', 'worried', 'depressed', 'sad', 'angry', 'frustrated']
    stress_count = sum(1 for word in stress_keywords if word in text_clean)
    
    if stress_count >= 2:
        stress_level = "high"
    elif stress_count == 1:
        stress_level = "medium"
    else:
        stress_level = "low"
    
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
        "confidence": float(confidence),
        "suggestions": suggestions
    }

def analyze_image_emotion(image_data: str) -> Dict[str, Any]:
    """Analyze image for facial emotion (simplified)"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Simple analysis based on image properties
        # In a real app, you'd use a proper facial emotion recognition model
        width, height = image.size
        brightness = np.mean(np.array(image))
        
        # Mock emotion detection based on image properties
        if brightness > 150:
            emotion = "happy"
            stress_level = "low"
        elif brightness < 100:
            emotion = "sad"
            stress_level = "high"
        else:
            emotion = "neutral"
            stress_level = "medium"
        
        confidence = 0.75  # Mock confidence
        
        suggestions = [
            "Consider your facial expressions",
            "Try to maintain a positive demeanor",
            "Practice smiling more often",
            "Take care of your mental well-being"
        ]
        
        return {
            "emotion": emotion,
            "stress_level": stress_level,
            "confidence": confidence,
            "suggestions": suggestions
        }
        
    except Exception as e:
        return {
            "emotion": "neutral",
            "stress_level": "medium",
            "confidence": 0.5,
            "suggestions": ["Unable to analyze image properly"]
        }

# API Routes
@app.get("/")
async def root():
    return {"message": "MindScope AI - Mental Health Analysis Platform"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """User login endpoint"""
    user = users_db.get(request.username)
    
    if not user or user["password_hash"] != request.password:
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

@app.post("/api/auth/register")
async def register(request: User):
    """User registration endpoint"""
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users_db[request.username] = {
        "username": request.username,
        "password_hash": request.password,  # In real app, hash this
        "user_type": request.user_type,
        "name": request.name
    }
    
    return {"message": "User registered successfully"}

@app.post("/api/analyze/text")
async def analyze_text(request: TextAnalysisRequest, current_user: dict = Depends(get_current_user)):
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
async def analyze_image(request: ImageAnalysisRequest, current_user: dict = Depends(get_current_user)):
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
async def get_analysis_history(current_user: dict = Depends(get_current_user)):
    """Get user's analysis history"""
    user_analyses = [a for a in analysis_history if a["user_id"] == current_user["username"]]
    return {"analyses": user_analyses}

@app.get("/api/admin/summary")
async def get_admin_summary(current_user: dict = Depends(get_current_user)):
    """Get admin analytics summary"""
    if current_user["username"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Calculate summary statistics
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
async def export_report(current_user: dict = Depends(get_current_user)):
    """Export user data as JSON"""
    user_analyses = [a for a in analysis_history if a["user_id"] == current_user["username"]]
    
    export_data = {
        "user": current_user,
        "analyses": user_analyses,
        "export_date": datetime.now().isoformat(),
        "total_analyses": len(user_analyses)
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
