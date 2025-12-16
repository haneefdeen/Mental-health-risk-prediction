"""
MindScope AI - Admin API Routes
Handles admin dashboard and analytics
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any
import json
import os
from datetime import datetime, timedelta

from utils.auth import get_current_admin
from models.behavioral_analyzer import behavioral_analyzer

router = APIRouter()

# Response models
class AdminSummary(BaseModel):
    total_users: int
    active_users: int
    total_analyses: int
    stress_distribution: Dict[str, int]
    behavioral_insights: Dict[str, Any]

class UserAnalytics(BaseModel):
    user_id: str
    total_posts: int
    behavioral_score: float
    stress_trend: str
    activity_level: str

@router.get("/summary", response_model=AdminSummary)
async def get_admin_summary(current_admin: dict = Depends(get_current_admin)):
    """Get aggregated analytics for admin dashboard"""
    try:
        # Get all user data
        all_users = behavioral_analyzer.user_data
        
        total_users = len(all_users)
        active_users = len([u for u in all_users.values() if u.get("posts", [])])
        
        # Calculate total analyses
        total_analyses = sum(len(user.get("posts", [])) for user in all_users.values())
        
        # Calculate stress distribution
        stress_levels = {"low": 0, "medium": 0, "high": 0}
        for user in all_users.values():
            posts = user.get("posts", [])
            for post in posts:
                stress_score = post.get("stress_score", 0.5)
                if stress_score < 0.3:
                    stress_levels["low"] += 1
                elif stress_score < 0.7:
                    stress_levels["medium"] += 1
                else:
                    stress_levels["high"] += 1
        
        # Calculate behavioral insights
        behavioral_scores = [user.get("behavioral_score", 0.5) for user in all_users.values()]
        avg_behavioral_score = sum(behavioral_scores) / len(behavioral_scores) if behavioral_scores else 0.5
        
        # Calculate activity levels
        activity_levels = {"low": 0, "medium": 0, "high": 0}
        for user in all_users.values():
            posts = user.get("posts", [])
            if len(posts) > 5:
                activity_levels["high"] += 1
            elif len(posts) > 2:
                activity_levels["medium"] += 1
            else:
                activity_levels["low"] += 1
        
        behavioral_insights = {
            "average_behavioral_score": avg_behavioral_score,
            "activity_distribution": activity_levels,
            "users_needing_attention": len([u for u in all_users.values() if u.get("behavioral_score", 0.5) < 0.3])
        }
        
        return AdminSummary(
            total_users=total_users,
            active_users=active_users,
            total_analyses=total_analyses,
            stress_distribution=stress_levels,
            behavioral_insights=behavioral_insights
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get admin summary: {str(e)}"
        )

@router.get("/users", response_model=List[UserAnalytics])
async def get_user_analytics(current_admin: dict = Depends(get_current_admin)):
    """Get individual user analytics"""
    try:
        user_analytics = []
        
        for user_id, user_data in behavioral_analyzer.user_data.items():
            posts = user_data.get("posts", [])
            
            # Calculate stress trend
            if len(posts) >= 10:
                recent_10 = posts[-10:]
                older_10 = posts[-20:-10] if len(posts) >= 20 else posts[:-10]
                
                recent_avg = sum(p.get('stress_score', 0.5) for p in recent_10) / len(recent_10)
                older_avg = sum(p.get('stress_score', 0.5) for p in older_10) / len(older_10)
                
                if recent_avg > older_avg + 0.1:
                    stress_trend = "increasing"
                elif recent_avg < older_avg - 0.1:
                    stress_trend = "decreasing"
                else:
                    stress_trend = "stable"
            else:
                stress_trend = "insufficient_data"
            
            # Determine activity level
            if len(posts) > 5:
                activity_level = "high"
            elif len(posts) > 2:
                activity_level = "medium"
            else:
                activity_level = "low"
            
            user_analytics.append(UserAnalytics(
                user_id=user_id,
                total_posts=len(posts),
                behavioral_score=user_data.get("behavioral_score", 0.5),
                stress_trend=stress_trend,
                activity_level=activity_level
            ))
        
        return user_analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user analytics: {str(e)}"
        )

@router.get("/stress-trends")
async def get_stress_trends(days: int = 30, current_admin: dict = Depends(get_current_admin)):
    """Get stress trends over time"""
    try:
        # Calculate daily stress averages
        daily_stress = {}
        
        for user_data in behavioral_analyzer.user_data.values():
            posts = user_data.get("posts", [])
            for post in posts:
                post_date = datetime.fromisoformat(post["timestamp"]).date()
                if post_date not in daily_stress:
                    daily_stress[post_date] = []
                daily_stress[post_date].append(post.get("stress_score", 0.5))
        
        # Calculate daily averages
        trend_data = []
        for date, scores in daily_stress.items():
            avg_stress = sum(scores) / len(scores)
            trend_data.append({
                "date": date.isoformat(),
                "average_stress": avg_stress,
                "post_count": len(scores)
            })
        
        # Sort by date
        trend_data.sort(key=lambda x: x["date"])
        
        return {
            "trend_data": trend_data[-days:],  # Last N days
            "period_days": days,
            "total_data_points": len(trend_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stress trends: {str(e)}"
        )

@router.get("/flagged-users")
async def get_flagged_users(current_admin: dict = Depends(get_current_admin)):
    """Get users who may need attention"""
    try:
        flagged_users = []
        
        for user_id, user_data in behavioral_analyzer.user_data.items():
            behavioral_score = user_data.get("behavioral_score", 0.5)
            posts = user_data.get("posts", [])
            
            # Flag users with low behavioral scores or high stress
            if behavioral_score < 0.3 or len(posts) > 10:
                # Check recent stress levels
                recent_posts = posts[-5:] if len(posts) >= 5 else posts
                recent_stress = sum(p.get("stress_score", 0.5) for p in recent_posts) / len(recent_posts) if recent_posts else 0.5
                
                if recent_stress > 0.7:
                    flagged_users.append({
                        "user_id": user_id,
                        "behavioral_score": behavioral_score,
                        "recent_stress": recent_stress,
                        "total_posts": len(posts),
                        "flag_reason": "high_stress" if recent_stress > 0.7 else "low_behavioral_score"
                    })
        
        return {
            "flagged_users": flagged_users,
            "total_flagged": len(flagged_users)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get flagged users: {str(e)}"
        )

@router.get("/export-data")
async def export_admin_data(current_admin: dict = Depends(get_current_admin)):
    """Export anonymized admin data"""
    try:
        # Get summary data
        summary = await get_admin_summary(current_admin)
        user_analytics = await get_user_analytics(current_admin)
        stress_trends = await get_stress_trends(30, current_admin)
        flagged_users = await get_flagged_users(current_admin)
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "admin_id": current_admin["username"],
            "summary": summary.dict(),
            "user_analytics": [user.dict() for user in user_analytics],
            "stress_trends": stress_trends,
            "flagged_users": flagged_users
        }
        
        return export_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export admin data: {str(e)}"
        )

@router.delete("/user/{user_id}")
async def delete_user_data(user_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete user data (GDPR compliance)"""
    try:
        if user_id in behavioral_analyzer.user_data:
            del behavioral_analyzer.user_data[user_id]
            behavioral_analyzer._save_user_data()
            
            return {"message": f"User data for {user_id} has been deleted"}
        else:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete user data: {str(e)}"
        )
