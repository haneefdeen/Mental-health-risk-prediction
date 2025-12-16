"""
Emotion to stress category mapping and combination logic.
Ensures stress_category is consistent with primary_emotion.
"""

from typing import Optional
from backend.config.labels import STRESS_DISPLAY


# Mapping from primary emotion to base stress category
PRIMARY_TO_BASE_STRESS = {
    "happy": "No Apparent Stress",
    "neutral": "Low Stress",
    "surprised": "Low Stress",
    
    "sad": "High Stress",
    "anxious": "High Stress",
    "fearful": "High Stress",
    "angry": "High Stress",
    "disgusted": "Moderate Stress",
    "depressed": "High Stress",  # if we have this label
}


def map_emotion_to_stress(primary_emotion_label: str) -> str:
    """
    Map primary emotion label to base stress category.
    
    Args:
        primary_emotion_label: Emotion label (e.g., "Happy", "Sad", "Anxious")
    
    Returns:
        Stress category string (e.g., "No Apparent Stress", "High Stress")
    """
    # Normalize to lowercase for lookup
    emotion_lower = primary_emotion_label.lower()
    return PRIMARY_TO_BASE_STRESS.get(emotion_lower, "Low Stress")


def combine_stress(model_stress: Optional[str], emotion_stress: str) -> str:
    """
    Combine model stress output with emotion-based stress.
    Priority: Use the more severe of the two, but ensure negative emotions
    don't get downgraded to low stress.
    
    Args:
        model_stress: Stress category from model (may be None)
        emotion_stress: Stress category from emotion mapping
    
    Returns:
        Final stress category string
    """
    # Order of severity (higher index = more severe)
    order = ["No Apparent Stress", "Low Stress", "Moderate Stress", "High Stress"]
    
    def get_severity_index(category: str) -> int:
        """Get severity index of a stress category."""
        try:
            return order.index(category)
        except ValueError:
            # If category not found, try to match partial strings
            category_lower = category.lower()
            if "no" in category_lower or "apparent" in category_lower:
                return 0
            elif "low" in category_lower:
                return 1
            elif "moderate" in category_lower:
                return 2
            elif "high" in category_lower or "severe" in category_lower:
                return 3
            return 1  # Default to Low Stress
    
    # If no model stress, use emotion stress
    if model_stress is None:
        return emotion_stress
    
    # Get severity indices
    model_idx = get_severity_index(model_stress)
    emotion_idx = get_severity_index(emotion_stress)
    
    # Special case: If emotion indicates high stress but model says low/no stress,
    # bump to at least moderate stress (don't let negative emotions be downgraded)
    if emotion_idx >= 3 and model_idx <= 1:  # Emotion is High, Model is Low/No
        return "Moderate Stress"  # Compromise: at least moderate
    
    # Otherwise, use the more severe of the two
    final_idx = max(model_idx, emotion_idx)
    return order[final_idx]


def stress_category_to_internal_label(stress_category: str) -> str:
    """
    Convert display stress category to internal label.
    
    Args:
        stress_category: Display category (e.g., "No Apparent Stress", "High Stress")
    
    Returns:
        Internal label (e.g., "no_stress", "high")
    """
    category_lower = stress_category.lower()
    
    if "no" in category_lower or "apparent" in category_lower:
        return "no_stress"
    elif "low" in category_lower:
        return "low"
    elif "moderate" in category_lower:
        return "moderate"
    elif "high" in category_lower or "severe" in category_lower:
        return "high"
    else:
        return "moderate"  # Default fallback


