"""
MindScope AI - Reports API Routes
Handles PDF report generation and data export
"""

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

from utils.auth import get_current_user, get_current_admin
from utils.report_generator import report_generator
from models.behavioral_analyzer import behavioral_analyzer

router = APIRouter()

# Request models
class ReportRequest(BaseModel):
    report_type: str  # "user", "admin", "comprehensive"
    include_explainability: bool = True
    include_behavioral: bool = True

class DataExportRequest(BaseModel):
    export_format: str  # "json", "csv"
    include_analyses: bool = True
    include_behavioral: bool = True

@router.post("/generate-pdf")
async def generate_pdf_report(request: ReportRequest, current_user: dict = Depends(get_current_user)):
    """Generate PDF report for user"""
    try:
        # Get user data
        user_data = {
            "username": current_user["username"],
            "email": current_user.get("email", ""),
            "full_name": current_user.get("full_name", "")
        }
        
        # Get analysis data
        user_behavioral_data = behavioral_analyzer.user_data.get(current_user["username"], {})
        
        # Create analysis data structure
        analysis_data = {
            "stress_level": "low",
            "confidence": 0.5,
            "risk_score": 0.3,
            "behavioral_score": user_behavioral_data.get("behavioral_score", 0.5),
            "modality_scores": {
                "text": "low",
                "image": "low",
                "behavioral": "low"
            },
            "fusion_weights": {
                "text": 0.33,
                "image": 0.33,
                "behavioral": 0.34
            },
            "recommendations": [
                "Maintain your current healthy habits",
                "Continue practicing mindfulness and relaxation techniques",
                "Stay connected with friends and family"
            ],
            "behavioral_analysis": {
                "emoji_analysis": {
                    "total_emojis": 0,
                    "positive_emojis": 0,
                    "negative_emojis": 0,
                    "stress_emojis": 0,
                    "emoji_diversity": 0.0
                },
                "frequency_analysis": {
                    "posts_per_day": 0.0,
                    "activity_level": "low",
                    "posting_consistency": 0.0,
                    "trend": "stable"
                }
            }
        }
        
        # Generate PDF report
        report_path = report_generator.generate_report(user_data, analysis_data)
        
        if os.path.exists(report_path):
            return FileResponse(
                path=report_path,
                filename=f"mindscope_report_{current_user['username']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                media_type="application/pdf"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF report"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

@router.post("/export-data")
async def export_user_data(request: DataExportRequest, current_user: dict = Depends(get_current_user)):
    """Export user data in JSON or CSV format"""
    try:
        user_id = current_user["username"]
        user_data = behavioral_analyzer.user_data.get(user_id, {})
        
        # Prepare export data
        export_data = {
            "user_id": user_id,
            "export_timestamp": datetime.now().isoformat(),
            "data_type": "user_export"
        }
        
        if request.include_analyses:
            export_data["analyses"] = user_data.get("posts", [])
        
        if request.include_behavioral:
            export_data["behavioral_data"] = {
                "behavioral_score": user_data.get("behavioral_score", 0.5),
                "emoji_history": user_data.get("emoji_history", []),
                "posting_frequency": user_data.get("posting_frequency", [])
            }
        
        if request.export_format == "json":
            return export_data
        elif request.export_format == "csv":
            # Convert to CSV format (simplified)
            csv_data = f"user_id,export_timestamp,behavioral_score,total_posts\n"
            csv_data += f"{user_id},{datetime.now().isoformat()},{user_data.get('behavioral_score', 0.5)},{len(user_data.get('posts', []))}\n"
            
            return Response(
                content=csv_data,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=user_data_{user_id}.csv"}
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid export format. Use 'json' or 'csv'"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data export failed: {str(e)}"
        )

@router.delete("/delete-data")
async def delete_user_data(current_user: dict = Depends(get_current_user)):
    """Delete all user data (GDPR compliance)"""
    try:
        user_id = current_user["username"]
        
        if user_id in behavioral_analyzer.user_data:
            del behavioral_analyzer.user_data[user_id]
            behavioral_analyzer._save_user_data()
            
            return {
                "message": "All user data has been deleted",
                "user_id": user_id,
                "deletion_timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "message": "No user data found to delete",
                "user_id": user_id
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data deletion failed: {str(e)}"
        )

@router.get("/data-consent")
async def get_data_consent_info(current_user: dict = Depends(get_current_user)):
    """Get data consent and privacy information"""
    try:
        user_id = current_user["username"]
        user_data = behavioral_analyzer.user_data.get(user_id, {})
        
        return {
            "user_id": user_id,
            "data_collected": {
                "text_analyses": len(user_data.get("posts", [])),
                "emoji_analyses": len(user_data.get("emoji_history", [])),
                "behavioral_score": user_data.get("behavioral_score", 0.5)
            },
            "data_retention": "Data is retained for analysis purposes and can be deleted at any time",
            "data_sharing": "No personal data is shared with third parties",
            "consent_status": "Consent is assumed for analysis purposes",
            "rights": [
                "Right to access your data",
                "Right to export your data",
                "Right to delete your data",
                "Right to withdraw consent"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get consent info: {str(e)}"
        )

@router.post("/update-consent")
async def update_data_consent(consent: bool, current_user: dict = Depends(get_current_user)):
    """Update data consent preferences"""
    try:
        user_id = current_user["username"]
        
        # Update consent in user data
        if user_id in behavioral_analyzer.user_data:
            behavioral_analyzer.user_data[user_id]["consent"] = consent
            behavioral_analyzer.user_data[user_id]["consent_timestamp"] = datetime.now().isoformat()
            behavioral_analyzer._save_user_data()
        
        return {
            "message": f"Data consent updated to {consent}",
            "user_id": user_id,
            "consent": consent,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update consent: {str(e)}"
        )

@router.get("/admin-export")
async def export_admin_data(current_admin: dict = Depends(get_current_admin)):
    """Export anonymized admin data"""
    try:
        # Get all user data (anonymized)
        all_users = behavioral_analyzer.user_data
        
        # Create anonymized export
        anonymized_data = {
            "export_timestamp": datetime.now().isoformat(),
            "admin_id": current_admin["username"],
            "total_users": len(all_users),
            "user_statistics": []
        }
        
        for user_id, user_data in all_users.items():
            # Anonymize user ID
            anonymized_id = f"user_{hash(user_id) % 10000}"
            
            user_stats = {
                "anonymized_id": anonymized_id,
                "total_posts": len(user_data.get("posts", [])),
                "behavioral_score": user_data.get("behavioral_score", 0.5),
                "activity_level": "high" if len(user_data.get("posts", [])) > 5 else "low"
            }
            
            anonymized_data["user_statistics"].append(user_stats)
        
        return anonymized_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Admin data export failed: {str(e)}"
        )
