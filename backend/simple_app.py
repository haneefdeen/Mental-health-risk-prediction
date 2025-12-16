from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import json
import base64
from datetime import datetime
import random

# Simple mock models for demo
class MockTextAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        emotion = random.choice(emotions)
        confidence = random.uniform(0.7, 0.95)
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'stress_level': random.uniform(0.2, 0.8),
            'emoji_analysis': {
                'positive_emojis': random.randint(0, 5),
                'negative_emojis': random.randint(0, 3),
                'neutral_emojis': random.randint(0, 2)
            },
            'posting_frequency': random.uniform(0.1, 1.0)
        }

class MockImageAnalyzer:
    def analyze(self, image_data: bytes) -> Dict[str, Any]:
        emotions = ['happy', 'sad', 'angry', 'fear', 'surprise', 'disgust', 'neutral']
        emotion = random.choice(emotions)
        confidence = random.uniform(0.6, 0.9)
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'facial_landmarks': {
                'eye_contact': random.uniform(0.3, 0.9),
                'smile_intensity': random.uniform(0.1, 0.8),
                'brow_furrow': random.uniform(0.1, 0.7)
            }
        }

class MockBehavioralAnalyzer:
    def analyze(self, emoji_stats: Dict, frequency: float) -> Dict[str, Any]:
        return {
            'stress_indicator': random.uniform(0.2, 0.8),
            'anxiety_level': random.uniform(0.1, 0.7),
            'behavioral_pattern': random.choice(['stable', 'increasing', 'decreasing', 'volatile'])
        }

class MockFusionModel:
    def fuse_predictions(self, text_result: Dict, image_result: Dict, behavioral_result: Dict) -> Dict[str, Any]:
        # Simple fusion logic
        stress_score = (text_result['stress_level'] + behavioral_result['stress_indicator']) / 2
        anxiety_score = behavioral_result['anxiety_level']
        
        return {
            'final_stress_score': stress_score,
            'final_anxiety_score': anxiety_score,
            'overall_risk_level': 'low' if stress_score < 0.4 else 'medium' if stress_score < 0.7 else 'high',
            'confidence': random.uniform(0.7, 0.9)
        }

# Initialize mock models
text_analyzer = MockTextAnalyzer()
image_analyzer = MockImageAnalyzer()
behavioral_analyzer = MockBehavioralAnalyzer()
fusion_model = MockFusionModel()

# FastAPI app
app = FastAPI(title="MindScope AI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class TextAnalysisRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class ImageAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded
    user_id: Optional[str] = None

class FusionRequest(BaseModel):
    text_result: Dict[str, Any]
    image_result: Dict[str, Any]
    behavioral_result: Dict[str, Any]

class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    user_type: str = "user"  # "user" or "doctor"

class UserLogin(BaseModel):
    username: str
    password: str

# Mock user database
users_db = {
    "admin": {"password": "admin123", "email": "admin@mindscope.ai", "user_type": "doctor"},
    "user1": {"password": "user123", "email": "user1@example.com", "user_type": "user"}
}

# Mock analysis history
analysis_history = []

@app.get("/")
async def root():
    return {"message": "MindScope AI API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/analyze_text")
async def analyze_text(request: TextAnalysisRequest):
    try:
        result = text_analyzer.analyze(request.text)
        
        # Store analysis
        analysis_record = {
            "id": len(analysis_history) + 1,
            "user_id": request.user_id,
            "type": "text",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        analysis_history.append(analysis_record)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_image")
async def analyze_image(request: ImageAnalysisRequest):
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_data)
        result = image_analyzer.analyze(image_data)
        
        # Store analysis
        analysis_record = {
            "id": len(analysis_history) + 1,
            "user_id": request.user_id,
            "type": "image",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        analysis_history.append(analysis_record)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fusion")
async def fusion_analysis(request: FusionRequest):
    try:
        result = fusion_model.fuse_predictions(
            request.text_result,
            request.image_result,
            request.behavioral_result
        )
        
        # Store fusion analysis
        analysis_record = {
            "id": len(analysis_history) + 1,
            "user_id": "system",
            "type": "fusion",
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        analysis_history.append(analysis_record)
        
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/coping_guide")
async def get_coping_guide(stress_level: float):
    try:
        if stress_level < 0.3:
            guide = {
                "level": "low",
                "recommendations": [
                    "Continue your current healthy habits",
                    "Practice mindfulness meditation",
                    "Maintain regular exercise routine"
                ],
                "activities": ["Reading", "Walking", "Meditation"]
            }
        elif stress_level < 0.7:
            guide = {
                "level": "medium",
                "recommendations": [
                    "Take regular breaks throughout the day",
                    "Practice deep breathing exercises",
                    "Consider talking to a friend or family member"
                ],
                "activities": ["Yoga", "Journaling", "Music therapy"]
            }
        else:
            guide = {
                "level": "high",
                "recommendations": [
                    "Consider professional mental health support",
                    "Practice stress-reduction techniques daily",
                    "Ensure adequate sleep and nutrition"
                ],
                "activities": ["Professional counseling", "Support groups", "Stress management workshops"]
            }
        
        return {"success": True, "guide": guide}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register")
async def register_user(user: UserRegistration):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    users_db[user.username] = {
        "password": user.password,
        "email": user.email,
        "user_type": user.user_type
    }
    
    return {"success": True, "message": "User registered successfully"}

@app.post("/login")
async def login_user(user: UserLogin):
    if user.username not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if users_db[user.username]["password"] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "success": True,
        "token": f"mock_token_{user.username}",
        "user": {
            "username": user.username,
            "email": users_db[user.username]["email"],
            "user_type": users_db[user.username]["user_type"]
        }
    }

@app.get("/get_admin_summary")
async def get_admin_summary():
    try:
        # Mock aggregated data
        summary = {
            "total_users": len(users_db),
            "total_analyses": len(analysis_history),
            "average_stress_level": random.uniform(0.3, 0.6),
            "risk_distribution": {
                "low": random.randint(20, 40),
                "medium": random.randint(30, 50),
                "high": random.randint(10, 30)
            },
            "trends": {
                "stress_trend": random.choice(["increasing", "decreasing", "stable"]),
                "anxiety_trend": random.choice(["increasing", "decreasing", "stable"])
            }
        }
        
        return {"success": True, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export_report/{user_id}")
async def export_report(user_id: str):
    try:
        user_analyses = [a for a in analysis_history if a.get("user_id") == user_id]
        
        report = {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),
            "total_analyses": len(user_analyses),
            "analyses": user_analyses,
            "summary": {
                "average_stress": random.uniform(0.3, 0.7),
                "most_common_emotion": random.choice(["happy", "neutral", "sad"]),
                "risk_level": random.choice(["low", "medium", "high"])
            }
        }
        
        return {"success": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_data/{user_id}")
async def delete_user_data(user_id: str):
    try:
        # Remove user analyses
        global analysis_history
        analysis_history = [a for a in analysis_history if a.get("user_id") != user_id]
        
        return {"success": True, "message": f"Data deleted for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
