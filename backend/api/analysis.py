"""
MindScope AI - Analysis API Routes
Handles text, image, and multimodal analysis
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import numpy as np
import cv2
from PIL import Image
import io

from utils.auth import get_current_user
from models.text_analyzer import text_analyzer
from models.image_analyzer import image_analyzer
from models.behavioral_analyzer import behavioral_analyzer
from models.fusion_model import fusion_model
from utils.explainability import explainability_analyzer

router = APIRouter()

# Request/Response models
class TextAnalysisRequest(BaseModel):
    text: str

class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image

class MultimodalAnalysisRequest(BaseModel):
    text: Optional[str] = ""
    image_data: Optional[str] = ""  # Base64 encoded image

class AnalysisResponse(BaseModel):
    analysis: Dict[str, Any]
    explainability: Optional[Dict[str, Any]] = None

@router.post("/text", response_model=AnalysisResponse)
async def analyze_text(request: TextAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Analyze text for emotion and stress"""
    try:
        # Perform text analysis
        text_analysis = text_analyzer.analyze_emotion(request.text)
        
        # Analyze emoji usage
        emoji_analysis = behavioral_analyzer.analyze_emoji_usage(request.text, current_user["username"])
        
        # Get token importance for explainability
        token_importance = text_analyzer.get_token_importance(request.text)
        
        # Combine results
        analysis_result = {
            **text_analysis,
            "emoji_analysis": emoji_analysis,
            "token_importance": token_importance,
            "user_id": current_user["username"],
            "analysis_type": "text"
        }
        
        # Add to behavioral data
        behavioral_analyzer.add_post(
            current_user["username"],
            request.text,
            text_analysis.get('stress_level', 'low')
        )
        
        return AnalysisResponse(
            analysis=analysis_result,
            explainability={
                "token_heatmap": token_importance,
                "text_explanation": f"Analysis based on {len(request.text.split())} words with {text_analysis.get('emoji_count', 0)} emojis"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text analysis failed: {str(e)}"
        )

@router.post("/image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Analyze image for facial emotion"""
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Convert to BGR for OpenCV
        if len(image_array.shape) == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Perform image analysis
        image_analysis = image_analyzer.analyze_emotion(image_array)
        
        # Generate Grad-CAM for explainability
        gradcam_data = image_analyzer.generate_gradcam(image_array)
        
        # Combine results
        analysis_result = {
            **image_analysis,
            "user_id": current_user["username"],
            "analysis_type": "image"
        }
        
        return AnalysisResponse(
            analysis=analysis_result,
            explainability={
                "gradcam": gradcam_data,
                "image_explanation": f"Analysis of {image_analysis.get('face_count', 0)} detected faces"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}"
        )

@router.post("/multimodal", response_model=AnalysisResponse)
async def analyze_multimodal(request: MultimodalAnalysisRequest, current_user: dict = Depends(get_current_user)):
    """Perform multimodal analysis combining text, image, and behavioral data"""
    try:
        text_analysis = {}
        image_analysis = {}
        behavioral_analysis = {}
        
        # Analyze text if provided
        if request.text:
            text_analysis = text_analyzer.analyze_emotion(request.text)
            emoji_analysis = behavioral_analyzer.analyze_emoji_usage(request.text, current_user["username"])
            text_analysis["emoji_analysis"] = emoji_analysis
        
        # Analyze image if provided
        if request.image_data:
            # Decode base64 image
            import base64
            image_data = base64.b64decode(request.image_data)
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            image_analysis = image_analyzer.analyze_emotion(image_array)
        
        # Get behavioral analysis
        behavioral_analysis = behavioral_analyzer.get_behavioral_insights(current_user["username"])
        
        # Perform fusion analysis
        fusion_analysis = fusion_model.fuse_analysis(text_analysis, image_analysis, behavioral_analysis)
        
        # Generate explainability
        explainability = explainability_analyzer.generate_explainability_report(
            text_analysis, image_analysis, behavioral_analysis, fusion_analysis
        )
        
        # Combine all results
        comprehensive_analysis = {
            "text_analysis": text_analysis,
            "image_analysis": image_analysis,
            "behavioral_analysis": behavioral_analysis,
            "fusion_analysis": fusion_analysis,
            "user_id": current_user["username"],
            "analysis_type": "multimodal"
        }
        
        # Add to behavioral data if text was provided
        if request.text:
            behavioral_analyzer.add_post(
                current_user["username"],
                request.text,
                fusion_analysis.get('risk_score', 0.5)
            )
        
        return AnalysisResponse(
            analysis=comprehensive_analysis,
            explainability=explainability
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multimodal analysis failed: {str(e)}"
        )

@router.get("/coping-guide")
async def get_coping_guide(stress_level: str = "low", current_user: dict = Depends(get_current_user)):
    """Get AI-powered coping suggestions"""
    try:
        coping_suggestions = {
            "low": [
                "Maintain your current healthy habits",
                "Continue practicing mindfulness and relaxation techniques",
                "Stay connected with friends and family",
                "Engage in activities that bring you joy",
                "Consider helping others who might be struggling"
            ],
            "medium": [
                "Practice stress management techniques like deep breathing",
                "Consider regular exercise or physical activity",
                "Maintain a consistent sleep schedule",
                "Try mindfulness meditation or yoga",
                "Stay connected with your support network"
            ],
            "high": [
                "Take a break and practice deep breathing exercises",
                "Consider speaking with a mental health professional",
                "Try mindfulness meditation or yoga to reduce stress",
                "Engage in activities that bring you joy and relaxation",
                "Consider professional mental health support when needed"
            ]
        }
        
        return {
            "stress_level": stress_level,
            "suggestions": coping_suggestions.get(stress_level, coping_suggestions["low"]),
            "timestamp": behavioral_analyzer._save_user_data()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get coping guide: {str(e)}"
        )

@router.get("/user-history")
async def get_user_history(current_user: dict = Depends(get_current_user)):
    """Get user's analysis history"""
    try:
        user_data = behavioral_analyzer.user_data.get(current_user["username"], {})
        
        return {
            "user_id": current_user["username"],
            "total_posts": len(user_data.get("posts", [])),
            "behavioral_score": user_data.get("behavioral_score", 0.5),
            "recent_analyses": user_data.get("posts", [])[-10:],  # Last 10 analyses
            "emoji_history": user_data.get("emoji_history", [])[-10:]  # Last 10 emoji analyses
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user history: {str(e)}"
        )
