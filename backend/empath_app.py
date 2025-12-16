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
import logging

# Import our custom modules
from model.text_analyzer import TextAnalyzer
from model.image_analyzer import ImageAnalyzer
from model.behavioral_analyzer import BehavioralAnalyzer
from model.fusion_model import FusionModel
from model.explainability import ExplainabilityEngine
from utils.auth import AuthManager
from utils.report_generator import ReportGenerator
from datasets.dataset_manager import DatasetManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MindScope AI",
    description="Multimodal Mental Health Analysis API",
    version="1.0.0"
)

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

# Initialize components
text_analyzer = TextAnalyzer()
image_analyzer = ImageAnalyzer()
behavioral_analyzer = BehavioralAnalyzer()
fusion_model = FusionModel()
explainability_engine = ExplainabilityEngine()
auth_manager = AuthManager()
report_generator = ReportGenerator()
dataset_manager = DatasetManager()

# Initialize datasets
dataset_manager.initialize_all_datasets()

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str
    user_type: str  # "user" or "doctor"

class UserRegister(BaseModel):
    username: str
    password: str
    email: str
    user_type: str
    full_name: str

class TextAnalysisRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class ImageAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded image
    user_id: Optional[str] = None

class FusionAnalysisRequest(BaseModel):
    text: Optional[str] = None
    image_data: Optional[str] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None

class AnalysisResponse(BaseModel):
    prediction: Dict[str, Any]
    confidence: float
    explainability: Optional[Dict[str, Any]] = None
    coping_suggestions: List[str]
    timestamp: str

class AdminSummaryResponse(BaseModel):
    total_users: int
    avg_stress_level: float
    flagged_users: List[Dict[str, Any]]
    trend_data: Dict[str, Any]
    alerts: List[str]

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user = auth_manager.verify_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Routes
@app.get("/")
async def root():
    return {"message": "MindScope AI API", "version": "1.0.0", "status": "running"}

@app.post("/login")
async def login(user_data: UserLogin):
    """Authenticate user or doctor"""
    try:
        token = auth_manager.authenticate_user(
            user_data.username, 
            user_data.password, 
            user_data.user_type
        )
        return {"access_token": token, "token_type": "bearer", "user_type": user_data.user_type}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/register")
async def register(user_data: UserRegister):
    """Register new user or doctor"""
    try:
        user_id = auth_manager.register_user(
            user_data.username,
            user_data.password,
            user_data.email,
            user_data.user_type,
            user_data.full_name
        )
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze_text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Analyze text for emotional content and stress levels"""
    try:
        # Analyze text
        text_result = text_analyzer.analyze(request.text)
        
        # Get explainability
        explainability = explainability_engine.explain_text(request.text, text_result)
        
        # Generate coping suggestions
        coping_suggestions = fusion_model.get_coping_suggestions(text_result)
        
        return AnalysisResponse(
            prediction=text_result,
            confidence=text_result.get("confidence", 0.0),
            explainability=explainability,
            coping_suggestions=coping_suggestions,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Text analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")

@app.post("/analyze_image", response_model=AnalysisResponse)
async def analyze_image(request: ImageAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Analyze uploaded image for facial emotions"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(request.image_data)
        
        # Analyze image
        image_result = image_analyzer.analyze(image_bytes)
        
        # Get explainability
        explainability = explainability_engine.explain_image(image_bytes, image_result)
        
        # Generate coping suggestions
        coping_suggestions = fusion_model.get_coping_suggestions(image_result)
        
        return AnalysisResponse(
            prediction=image_result,
            confidence=image_result.get("confidence", 0.0),
            explainability=explainability,
            coping_suggestions=coping_suggestions,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.post("/fusion", response_model=AnalysisResponse)
async def fusion_analysis(request: FusionAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Combine text, image, and behavioral data for comprehensive analysis"""
    try:
        # Prepare inputs
        text_result = None
        image_result = None
        behavioral_result = None
        
        if request.text:
            text_result = text_analyzer.analyze(request.text)
        
        if request.image_data:
            image_bytes = base64.b64decode(request.image_data)
            image_result = image_analyzer.analyze(image_bytes)
        
        if request.behavioral_data:
            behavioral_result = behavioral_analyzer.analyze(request.behavioral_data)
        
        # Fusion analysis
        fusion_result = fusion_model.fuse_predictions(
            text_result, image_result, behavioral_result
        )
        
        # Get explainability
        explainability = explainability_engine.explain_fusion(
            text_result, image_result, behavioral_result, fusion_result
        )
        
        # Generate coping suggestions
        coping_suggestions = fusion_model.get_coping_suggestions(fusion_result)
        
        return AnalysisResponse(
            prediction=fusion_result,
            confidence=fusion_result.get("confidence", 0.0),
            explainability=explainability,
            coping_suggestions=coping_suggestions,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Fusion analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fusion analysis failed: {str(e)}")

@app.get("/coping_guide")
async def get_coping_guide(stress_level: float, current_user: dict = Depends(get_current_user)):
    """Get personalized coping suggestions based on stress level"""
    try:
        suggestions = fusion_model.get_coping_suggestions({"stress_level": stress_level})
        return {"suggestions": suggestions, "stress_level": stress_level}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get coping guide: {str(e)}")

@app.get("/export_report/{user_id}")
async def export_report(user_id: str, current_user: dict = Depends(get_current_user)):
    """Export user's analysis report as PDF"""
    try:
        if current_user["user_type"] != "user" and current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        report_data = auth_manager.get_user_analyses(user_id)
        pdf_content = report_generator.generate_pdf_report(report_data, user_id)
        
        return {
            "pdf_content": base64.b64encode(pdf_content).decode(),
            "filename": f"mindscope_report_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@app.delete("/delete_data/{user_id}")
async def delete_user_data(user_id: str, current_user: dict = Depends(get_current_user)):
    """Delete all user data for ethical compliance"""
    try:
        if current_user["user_type"] != "user" and current_user["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        auth_manager.delete_user_data(user_id)
        return {"message": "User data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data deletion failed: {str(e)}")

@app.get("/admin_summary", response_model=AdminSummaryResponse)
async def get_admin_summary(current_user: dict = Depends(get_current_user)):
    """Get aggregated analytics for doctor/admin view"""
    try:
        if current_user["user_type"] != "doctor":
            raise HTTPException(status_code=403, detail="Doctor access required")
        
        summary = auth_manager.get_admin_summary()
        return AdminSummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Admin summary failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "text_analyzer": "ready",
            "image_analyzer": "ready",
            "behavioral_analyzer": "ready",
            "fusion_model": "ready"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
