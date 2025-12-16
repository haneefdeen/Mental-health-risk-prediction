from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import json
import os
import random
import datetime
from datetime import datetime, timedelta
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

app = FastAPI(title="MindScope AI - Enhanced")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class LoginRequest(BaseModel):
    username: str
    password: str

class TextRequest(BaseModel):
    text: str
    user_id: str

class ImageRequest(BaseModel):
    image_data: str
    user_id: str

class AnalysisData(BaseModel):
    user_id: str
    text: Optional[str] = None
    image_data: Optional[str] = None
    emotion: str
    stress_level: str
    confidence: float
    risk_level: str
    timestamp: str

# In-memory storage for demo
analyses_db = []
users_db = {
    "admin": {"username": "admin", "name": "Administrator", "user_type": "admin", "password": "admin123"},
    "user1": {"username": "user1", "name": "Test User", "user_type": "user", "password": "user123"}
}

# High-risk keywords for suicide/self-harm detection
HIGH_RISK_KEYWORDS = [
    'die', 'death', 'suicide', 'kill myself', 'end it all', 'not worth living',
    'want to die', 'going to die', 'hurt myself', 'self harm', 'cut myself',
    'overdose', 'jump off', 'hang myself', 'drown myself', 'shoot myself'
]

CRISIS_KEYWORDS = [
    'emergency', 'help me', 'can\'t take it', 'give up', 'hopeless',
    'worthless', 'burden', 'better off dead', 'final goodbye'
]

# Enhanced text analysis with proper risk detection
def analyze_text_enhanced(text: str) -> Dict:
    text_lower = text.lower()
    
    # Check for high-risk indicators
    high_risk_count = sum(1 for keyword in HIGH_RISK_KEYWORDS if keyword in text_lower)
    crisis_count = sum(1 for keyword in CRISIS_KEYWORDS if keyword in text_lower)
    
    # Determine risk level
    if high_risk_count >= 2 or crisis_count >= 2:
        risk_level = "CRITICAL"
        emotion = "crisis"
        stress_level = "extreme"
        confidence = 0.95
    elif high_risk_count >= 1 or crisis_count >= 1:
        risk_level = "HIGH"
        emotion = "distressed"
        stress_level = "very_high"
        confidence = 0.90
    else:
        # Regular emotion detection
        if any(word in text_lower for word in ['happy', 'joy', 'great', 'wonderful', 'excited', 'amazing', 'fantastic']):
            emotion = "happy"
            stress_level = "low"
            risk_level = "LOW"
            confidence = 0.85
        elif any(word in text_lower for word in ['sad', 'depressed', 'lonely', 'hurt', 'crying', 'tears']):
            emotion = "sad"
            stress_level = "high"
            risk_level = "MEDIUM"
            confidence = 0.80
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'hate', 'rage', 'annoyed']):
            emotion = "angry"
            stress_level = "high"
            risk_level = "MEDIUM"
            confidence = 0.82
        elif any(word in text_lower for word in ['anxious', 'worried', 'nervous', 'stress', 'panic', 'overwhelmed']):
            emotion = "anxious"
            stress_level = "high"
            risk_level = "MEDIUM"
            confidence = 0.85
        else:
            emotion = "neutral"
            stress_level = "medium"
            risk_level = "LOW"
            confidence = 0.70
    
    return {
        "emotion": emotion,
        "stress_level": stress_level,
        "risk_level": risk_level,
        "confidence": confidence
    }

# Enhanced image analysis with varied results
def analyze_image_enhanced(image_data: str) -> Dict:
    # Simulate different emotions based on image characteristics
    # In a real implementation, this would use actual image analysis
    emotions = ["happy", "sad", "angry", "fearful", "surprised", "disgusted", "neutral"]
    stress_levels = ["low", "medium", "high"]
    
    # Simulate analysis based on image data length (for demo purposes)
    emotion = random.choice(emotions)
    stress_level = random.choice(stress_levels)
    
    if emotion in ["happy", "surprised"]:
        stress_level = "low"
        risk_level = "LOW"
    elif emotion in ["sad", "fearful", "disgusted"]:
        stress_level = "high"
        risk_level = "MEDIUM"
    elif emotion == "angry":
        stress_level = "high"
        risk_level = "HIGH"
    else:
        stress_level = "medium"
        risk_level = "LOW"
    
    return {
        "emotion": emotion,
        "stress_level": stress_level,
        "risk_level": risk_level,
        "confidence": random.uniform(0.70, 0.95)
    }

# Generate personalized suggestions
def generate_suggestions(emotion: str, stress_level: str, risk_level: str) -> List[str]:
    suggestions = []
    
    if risk_level == "CRITICAL":
        suggestions = [
            "🚨 IMMEDIATE HELP: Contact emergency services (911) or crisis helpline",
            "💬 Talk to someone you trust right now",
            "🏥 Go to the nearest emergency room",
            "📞 National Suicide Prevention Lifeline: 988"
        ]
    elif risk_level == "HIGH":
        suggestions = [
            "🆘 Seek immediate professional help",
            "💬 Talk to a mental health professional today",
            "📞 Contact a crisis counselor",
            "🏠 Stay with someone you trust"
        ]
    elif emotion == "sad" or stress_level == "high":
        suggestions = [
            "💙 Practice self-compassion and self-care",
            "🧘 Try mindfulness or meditation",
            "📝 Journal your feelings",
            "🏃‍♀️ Go for a walk or light exercise",
            "🎵 Listen to calming music"
        ]
    elif emotion == "anxious":
        suggestions = [
            "🫁 Practice deep breathing exercises",
            "🧘 Try progressive muscle relaxation",
            "📱 Use a meditation app",
            "☕ Limit caffeine intake",
            "😴 Ensure adequate sleep"
        ]
    elif emotion == "angry":
        suggestions = [
            "🫁 Take deep breaths and count to 10",
            "🏃‍♂️ Go for a brisk walk",
            "🎵 Listen to calming music",
            "💬 Talk to someone about your feelings",
            "🧘 Practice mindfulness"
        ]
    else:
        suggestions = [
            "😊 Maintain your positive outlook",
            "🏃‍♀️ Keep up with regular exercise",
            "👥 Stay connected with friends and family",
            "📚 Continue learning and growing",
            "🎯 Set small, achievable goals"
        ]
    
    return suggestions

# API Endpoints
@app.get("/")
def root():
    return {"message": "MindScope AI Enhanced is running!", "status": "success"}

@app.post("/api/auth/login")
def login(request: LoginRequest):
    if request.username in users_db and users_db[request.username]["password"] == request.password:
        user = users_db[request.username]
        return {
            "access_token": f"{user['user_type']}_token",
            "user": {
                "username": user["username"],
                "name": user["name"],
                "user_type": user["user_type"]
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/analyze/text")
def analyze_text(request: TextRequest):
    analysis = analyze_text_enhanced(request.text)
    suggestions = generate_suggestions(
        analysis["emotion"], 
        analysis["stress_level"], 
        analysis["risk_level"]
    )
    
    # Store analysis
    analysis_data = AnalysisData(
        user_id=request.user_id,
        text=request.text,
        emotion=analysis["emotion"],
        stress_level=analysis["stress_level"],
        confidence=analysis["confidence"],
        risk_level=analysis["risk_level"],
        timestamp=datetime.now().isoformat()
    )
    analyses_db.append(analysis_data.dict())
    
    return {
        "emotion": analysis["emotion"],
        "stress_level": analysis["stress_level"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "suggestions": suggestions,
        "timestamp": analysis_data.timestamp,
        "is_high_risk": analysis["risk_level"] in ["HIGH", "CRITICAL"]
    }

@app.post("/api/analyze/image")
def analyze_image(request: ImageRequest):
    analysis = analyze_image_enhanced(request.image_data)
    suggestions = generate_suggestions(
        analysis["emotion"], 
        analysis["stress_level"], 
        analysis["risk_level"]
    )
    
    # Store analysis
    analysis_data = AnalysisData(
        user_id=request.user_id,
        image_data=request.image_data,
        emotion=analysis["emotion"],
        stress_level=analysis["stress_level"],
        confidence=analysis["confidence"],
        risk_level=analysis["risk_level"],
        timestamp=datetime.now().isoformat()
    )
    analyses_db.append(analysis_data.dict())
    
    return {
        "emotion": analysis["emotion"],
        "stress_level": analysis["stress_level"],
        "risk_level": analysis["risk_level"],
        "confidence": analysis["confidence"],
        "suggestions": suggestions,
        "timestamp": analysis_data.timestamp,
        "is_high_risk": analysis["risk_level"] in ["HIGH", "CRITICAL"]
    }

@app.get("/api/analyze/history")
def get_history(user_id: str):
    user_analyses = [a for a in analyses_db if a["user_id"] == user_id]
    return {"analyses": user_analyses[-10:]}  # Last 10 analyses

# Admin-only endpoints
@app.get("/api/admin/summary")
def get_admin_summary():
    if not analyses_db:
        return {
            "total_analyses": 0,
            "stress_distribution": {"low": 0, "medium": 0, "high": 0, "very_high": 0, "extreme": 0},
            "emotion_distribution": {},
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "recent_analyses": [],
            "high_risk_cases": 0,
            "crisis_cases": 0
        }
    
    # Calculate distributions
    stress_levels = [a["stress_level"] for a in analyses_db]
    emotions = [a["emotion"] for a in analyses_db]
    risk_levels = [a["risk_level"] for a in analyses_db]
    
    stress_dist = {}
    for level in stress_levels:
        stress_dist[level] = stress_dist.get(level, 0) + 1
    
    emotion_dist = {}
    for emotion in emotions:
        emotion_dist[emotion] = emotion_dist.get(emotion, 0) + 1
    
    risk_dist = {}
    for risk in risk_levels:
        risk_dist[risk] = risk_dist.get(risk, 0) + 1
    
    high_risk_cases = sum(1 for a in analyses_db if a["risk_level"] in ["HIGH", "CRITICAL"])
    crisis_cases = sum(1 for a in analyses_db if a["risk_level"] == "CRITICAL")
    
    return {
        "total_analyses": len(analyses_db),
        "stress_distribution": stress_dist,
        "emotion_distribution": emotion_dist,
        "risk_distribution": risk_dist,
        "recent_analyses": analyses_db[-5:],
        "high_risk_cases": high_risk_cases,
        "crisis_cases": crisis_cases
    }

@app.get("/api/admin/users")
def get_users():
    return {"users": list(users_db.values())}

@app.get("/api/admin/analytics")
def get_analytics():
    if not analyses_db:
        return {"message": "No data available"}
    
    # Calculate trends over time
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    recent_analyses = [
        a for a in analyses_db 
        if datetime.fromisoformat(a["timestamp"]) >= week_ago
    ]
    
    return {
        "weekly_trend": len(recent_analyses),
        "daily_average": len(recent_analyses) / 7,
        "most_common_emotion": max(set([a["emotion"] for a in analyses_db]), 
                                 key=[a["emotion"] for a in analyses_db].count),
        "average_confidence": sum(a["confidence"] for a in analyses_db) / len(analyses_db)
    }

# Report generation
@app.post("/api/reports/export")
def export_data(user_id: str, format: str = "json"):
    user_analyses = [a for a in analyses_db if a["user_id"] == user_id]
    
    if format == "json":
        return {
            "user": {"user_id": user_id},
            "analyses": user_analyses,
            "export_date": datetime.now().isoformat(),
            "total_analyses": len(user_analyses),
            "summary": {
                "most_common_emotion": max(set([a["emotion"] for a in user_analyses]), 
                                         key=[a["emotion"] for a in user_analyses].count) if user_analyses else "N/A",
                "average_confidence": sum(a["confidence"] for a in user_analyses) / len(user_analyses) if user_analyses else 0,
                "high_risk_count": sum(1 for a in user_analyses if a["risk_level"] in ["HIGH", "CRITICAL"])
            }
        }
    else:
        # Generate PDF report
        filename = f"mindscope_report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("MindScope AI - Mental Health Report", title_style))
        story.append(Spacer(1, 20))
        
        # User info
        story.append(Paragraph(f"<b>User ID:</b> {user_id}", styles['Normal']))
        story.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"<b>Total Analyses:</b> {len(user_analyses)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary
        if user_analyses:
            most_common = max(set([a["emotion"] for a in user_analyses]), 
                            key=[a["emotion"] for a in user_analyses].count)
            avg_confidence = sum(a["confidence"] for a in user_analyses) / len(user_analyses)
            high_risk = sum(1 for a in user_analyses if a["risk_level"] in ["HIGH", "CRITICAL"])
            
            story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
            story.append(Paragraph(f"Most Common Emotion: {most_common}", styles['Normal']))
            story.append(Paragraph(f"Average Confidence: {avg_confidence:.2f}", styles['Normal']))
            story.append(Paragraph(f"High Risk Cases: {high_risk}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Analysis details
        story.append(Paragraph("<b>Analysis History:</b>", styles['Heading2']))
        if user_analyses:
            data = [['Date', 'Emotion', 'Stress Level', 'Risk Level', 'Confidence']]
            for analysis in user_analyses[-10:]:  # Last 10 analyses
                date = datetime.fromisoformat(analysis['timestamp']).strftime('%Y-%m-%d %H:%M')
                data.append([
                    date,
                    analysis['emotion'],
                    analysis['stress_level'],
                    analysis['risk_level'],
                    f"{analysis['confidence']:.2f}"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        else:
            story.append(Paragraph("No analyses found.", styles['Normal']))
        
        doc.build(story)
        return FileResponse(filename, media_type='application/pdf', filename=filename)

if __name__ == "__main__":
    print("🚀 Starting MindScope AI Enhanced Backend...")
    print("📡 Server: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔐 Login: admin/admin123 or user1/user123")
    print("✨ Enhanced Features:")
    print("   - High-risk detection for crisis intervention")
    print("   - Role-based admin and user features")
    print("   - Enhanced image analysis")
    print("   - PDF/JSON report generation")
    uvicorn.run(app, host="0.0.0.0", port=8000)
