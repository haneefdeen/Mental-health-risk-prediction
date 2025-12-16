"""
Risk score and risk level calculation utilities.
Maps stress labels to risk scores (0-100) and risk levels.
"""

from typing import Tuple, Optional
import random
from backend.config.labels import STRESS_LABELS_INTERNAL


def stress_label_to_risk_score(
    stress_label: str, 
    model_probs: Optional[list] = None
) -> Tuple[int, str]:
    """
    Convert stress label to risk score (0-100) and risk level.
    
    Args:
        stress_label: One of "no_stress", "low", "moderate", "high"
        model_probs: Optional list of probabilities from model (for refinement)
    
    Returns:
        Tuple of (risk_score_int, risk_level_string)
    """
    # Simple mapping with ranges
    if stress_label == "no_stress":
        score = random.randint(5, 20)
        level = "Low Risk"
    elif stress_label == "low":
        score = random.randint(20, 35)
        level = "Low Risk"
    elif stress_label == "moderate":
        score = random.randint(35, 65)
        level = "Moderate Risk"
    elif stress_label == "high":
        score = random.randint(65, 90)
        level = "High Risk"
    else:
        # Default fallback
        score = 50
        level = "Moderate Risk"
    
    # If model probabilities are available, we could refine the score
    # For now, keep it simple
    return (score, level)


def stress_score_to_label(stress_score: float) -> str:
    """
    Convert a stress score (0.0-1.0) to a stress label.
    
    Args:
        stress_score: Float between 0.0 and 1.0
    
    Returns:
        Stress label string
    """
    if stress_score < 0.25:
        return "no_stress"
    elif stress_score < 0.5:
        return "low"
    elif stress_score < 0.75:
        return "moderate"
    else:
        return "high"


def stress_category_to_risk_score(stress_category: str) -> Tuple[int, str]:
    """
    Convert stress category display string to risk score (0-100) and risk level.
    This is the main function to use when you have the final stress_category.
    
    Args:
        stress_category: Display category (e.g., "No Apparent Stress", "High Stress")
    
    Returns:
        Tuple of (risk_score_int, risk_level_string)
    """
    import random
    
    category_lower = stress_category.lower()
    
    if "no" in category_lower or "apparent" in category_lower:
        base_min, base_max = 5, 30
        level = "Low Risk"
    elif "low" in category_lower:
        base_min, base_max = 5, 30
        level = "Low Risk"
    elif "moderate" in category_lower:
        base_min, base_max = 31, 60
        level = "Moderate Risk"
    elif "high" in category_lower or "severe" in category_lower:
        base_min, base_max = 61, 85
        level = "High Risk"
    else:
        # Default fallback
        base_min, base_max = 31, 60
        level = "Moderate Risk"
    
    score = random.randint(base_min, base_max)
    return (score, level)


def risk_level_from_score(score: int) -> str:
    """
    Get risk level from risk score.
    
    Args:
        score: Risk score (0-100)
    
    Returns:
        Risk level string
    """
    if score <= 30:
        return "Low Risk"
    elif score <= 60:
        return "Moderate Risk"
    elif score <= 85:
        return "High Risk"
    else:
        return "Critical Risk"



