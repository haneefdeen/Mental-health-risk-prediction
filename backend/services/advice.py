"""
Dynamic advice generation based on emotion, stress, and risk level.
Generates coping suggestions and wellness tips that vary based on predictions.
"""

from typing import List
from backend.config.labels import STRESS_DISPLAY


def generate_coping_suggestions(
    primary_emotion: str, 
    stress_label: str, 
    risk_level: str
) -> List[str]:
    """
    Generate dynamic coping suggestions based on emotion, stress, and risk.
    
    Args:
        primary_emotion: Emotion label (e.g., "happy", "sad", "anxious")
        stress_label: Internal stress label (e.g., "no_stress", "low", "moderate", "high")
        risk_level: Risk level string (e.g., "Low Risk", "Moderate Risk")
    
    Returns:
        List of coping suggestion strings
    """
    emotion_lower = primary_emotion.lower()
    stress_lower = stress_label.lower()
    
    suggestions = []
    
    # Low stress + positive emotions: maintenance and enhancement
    if stress_lower in ["no_stress", "low"] and emotion_lower in ["happy", "neutral"]:
        suggestions = [
            "Maintain your current routines and self-care practices.",
            "Continue expressing gratitude and connecting with supportive people.",
            "Engage in light physical activity or hobbies you enjoy.",
            "Keep a journal to track positive moments and patterns.",
            "Stay connected with friends and family who uplift you."
        ]
    
    # Moderate stress: active coping strategies
    elif stress_lower == "moderate":
        if emotion_lower in ["anxious", "fearful"]:
            suggestions = [
                "Practice deep breathing exercises (4-7-8 technique).",
                "Try progressive muscle relaxation or a short meditation.",
                "Write down your worries and identify what you can control.",
                "Take a short walk or do gentle stretching.",
                "Limit caffeine and ensure you're getting enough sleep."
            ]
        elif emotion_lower in ["sad", "angry"]:
            suggestions = [
                "Reach out to a trusted friend or family member.",
                "Engage in a creative activity or hobby you enjoy.",
                "Practice self-compassion and acknowledge your feelings.",
                "Take a break from social media or news if needed.",
                "Consider journaling to process your emotions."
            ]
        else:
            suggestions = [
                "Practice mindfulness or breathing exercises.",
                "Take regular breaks and stretch throughout the day.",
                "Stay connected with supportive people.",
                "Maintain regular sleep and meal times.",
                "Engage in activities that bring you joy or relaxation."
            ]
    
    # High stress: intensive support and grounding
    elif stress_lower == "high":
        if emotion_lower in ["anxious", "fearful"]:
            suggestions = [
                "Use grounding techniques: name 5 things you see, 4 you hear, 3 you feel.",
                "Practice box breathing: inhale-4, hold-4, exhale-4, hold-4.",
                "Reduce overwhelming inputs (social media, news, notifications).",
                "Reach out for support from friends, family, or a professional.",
                "Establish a simple, predictable routine for stability."
            ]
        elif emotion_lower in ["sad", "angry"]:
            suggestions = [
                "Reach out for support from someone you trust.",
                "Practice self-compassion and acknowledge it's okay to feel this way.",
                "Engage in gentle activities that provide comfort.",
                "Consider talking with a mental health professional.",
                "Focus on small, manageable steps rather than big changes."
            ]
        else:
            suggestions = [
                "Use grounding techniques to stay present.",
                "Reach out for support from trusted people.",
                "Reduce overwhelming inputs and take breaks.",
                "Establish a simple routine for stability.",
                "Consider professional support if feelings persist."
            ]
    
    # Default suggestions if no specific match
    else:
        suggestions = [
            "Practice deep breathing or mindfulness exercises.",
            "Take a break and engage in a calming activity.",
            "Stay connected with supportive people.",
            "Maintain regular sleep and meal times.",
            "Consider talking to someone you trust."
        ]
    
    # Return 3-5 suggestions
    return suggestions[:5]


def generate_wellness_tip(
    primary_emotion: str, 
    stress_label: str, 
    risk_level: str
) -> str:
    """
    Generate a dynamic wellness tip based on emotion, stress, and risk.
    
    Args:
        primary_emotion: Emotion label
        stress_label: Internal stress label
        risk_level: Risk level string
    
    Returns:
        Wellness tip string
    """
    emotion_lower = primary_emotion.lower()
    stress_lower = stress_label.lower()
    
    # Low stress + positive emotions
    if stress_lower in ["no_stress", "low"] and emotion_lower in ["happy", "neutral"]:
        tips = [
            "You're doing well — keep nurturing your emotional balance and positive connections.",
            "Maintain your current self-care practices and celebrate the progress you've made.",
            "Keep sharing gratitude and take mindful breaks to lock in the good vibes."
        ]
        return tips[0]  # Use first tip for consistency
    
    # Moderate stress
    elif stress_lower == "moderate":
        if emotion_lower in ["anxious", "fearful"]:
            return "Take a mindful 2-minute pause to check in with how you're feeling. Ground yourself in the present moment."
        elif emotion_lower in ["sad", "angry"]:
            return "Acknowledge your feelings without judgment. Reach out to someone you trust and give yourself space to process."
        else:
            return "Take a mindful break and give yourself space to process your feelings. Regular self-care practices can help manage stress levels."
    
    # High stress
    elif stress_lower == "high":
        if emotion_lower in ["anxious", "fearful", "sad", "angry"]:
            return "Your feelings are valid. Consider reaching out to a trusted friend, family member, or mental health professional if these feelings persist or feel overwhelming."
        else:
            return "Take care of yourself right now. Reach out for support if needed, and consider talking with a mental health professional if symptoms persist."
    
    # Default
    else:
        return "Take a deep breath and give yourself credit for checking in. Remember that seeking help is a sign of strength."




