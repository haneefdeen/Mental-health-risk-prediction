"""
Keyword-based emotion override for obvious text phrases.
This fixes clear misclassifications like "I'm happy" -> Sad.
"""

import re
from typing import Optional


def override_emotion_from_keywords(user_text: str, current_emotion: str) -> str:
    """
    Override emotion prediction based on obvious keywords in the text.
    This is a safety net for clear misclassifications.
    
    Args:
        user_text: User input text
        current_emotion: Current emotion predicted by model (lowercase)
    
    Returns:
        Overridden emotion (lowercase) or current_emotion if no override needed
    """
    if not user_text or not user_text.strip():
        return current_emotion
    
    text_lower = user_text.lower()
    
    # Obvious positive phrases (high priority)
    positive_phrases = [
        "i am happy", "i'm happy", "im happy",
        "very happy", "so happy", "really happy",
        "feeling great", "i feel great", "feeling good", "i feel good",
        "i'm feeling great", "im feeling great",
        "excited", "so excited", "very excited",
        "awesome", "amazing", "wonderful",
        "feeling wonderful", "feeling amazing",
        "i'm great", "im great", "i am great",
        "feeling awesome", "feeling fantastic",
    ]
    
    for phrase in positive_phrases:
        if phrase in text_lower:
            return "happy"
    
    # Anxious/stressed phrases
    anxious_phrases = [
        "i am anxious", "i'm anxious", "im anxious",
        "feeling anxious", "i feel anxious",
        "nervous", "so nervous", "very nervous",
        "worried", "so worried", "very worried",
        "panic", "panicking", "panicked",
        "so tense", "very tense", "feeling tense",
        "overwhelmed", "feeling overwhelmed",
        "stressed", "so stressed", "very stressed", "feeling stressed",
        "can't relax", "cannot relax", "cant relax",
    ]
    
    for phrase in anxious_phrases:
        if phrase in text_lower:
            return "anxious"
    
    # Sad/depressed phrases
    sad_phrases = [
        "i am sad", "i'm sad", "im sad",
        "feeling sad", "i feel sad",
        "depressed", "feeling depressed", "i feel depressed",
        "feeling low", "feeling down",
        "lonely", "feeling lonely",
        "worthless", "feeling worthless",
        "hopeless", "feeling hopeless",
        "empty", "feeling empty",
        "crying", "i'm crying", "im crying",
    ]
    
    for phrase in sad_phrases:
        if phrase in text_lower:
            return "sad"
    
    # Angry phrases
    angry_phrases = [
        "i am angry", "i'm angry", "im angry",
        "feeling angry", "i feel angry",
        "mad", "so mad", "very mad", "i'm mad", "im mad",
        "furious", "so furious",
        "irritated", "feeling irritated",
        "annoyed", "so annoyed",
        "frustrated", "feeling frustrated",
    ]
    
    for phrase in angry_phrases:
        if phrase in text_lower:
            return "angry"
    
    # Fearful phrases
    fearful_phrases = [
        "i am afraid", "i'm afraid", "im afraid",
        "feeling afraid", "i feel afraid",
        "scared", "so scared", "very scared", "feeling scared",
        "terrified", "feeling terrified",
        "horrified", "feeling horrified",
    ]
    
    for phrase in fearful_phrases:
        if phrase in text_lower:
            return "fearful"
    
    # If no clear override, keep model prediction
    return current_emotion


