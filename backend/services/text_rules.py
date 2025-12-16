"""
Rule-based emotion and stress detection for very short texts.
This provides fast, accurate predictions for simple phrases like "I'm happy", "I'm anxious".
"""

import re
from typing import Optional, Tuple
from backend.config.labels import PRIMARY_EMOTIONS, STRESS_LABELS_INTERNAL


def normalize_text(text: str) -> str:
    """Normalize text: lowercase, strip, remove punctuation."""
    text = text.lower().strip()
    # Remove punctuation but keep apostrophes for contractions
    text = re.sub(r'[^\w\s\']', '', text)
    return text


def rule_based_emotion_and_stress(text: str) -> Optional[Tuple[str, str]]:
    """
    For very short texts (like "I'm happy", "I'm anxious"),
    return a (primary_emotion, stress_label_internal) pair
    if a clear keyword match is found.
    Otherwise return None.
    
    Returns:
        Tuple[emotion, stress_label] or None
    """
    if not text or not text.strip():
        return None
    
    normalized = normalize_text(text)
    words = normalized.split()
    word_count = len(words)
    
    # Apply rules for short texts (7 words or less for better coverage)
    if word_count > 7:
        return None
    
    # Happy/positive keywords
    happy_keywords = ["happy", "good", "fine", "great", "excited", "glad", "pleased", "joyful", 
                     "grateful", "thankful", "blessed", "wonderful", "amazing", "fantastic"]
    if any(kw in normalized for kw in happy_keywords):
        return ("happy", "no_stress")
    
    # Sad/depressed keywords
    sad_keywords = ["sad", "upset", "cry", "crying", "depressed", "down", "unhappy", 
                   "miserable", "hopeless", "lonely", "empty", "worthless", "tears"]
    if any(kw in normalized for kw in sad_keywords):
        return ("sad", "moderate")
    
    # Anxious/stressed keywords
    anxious_keywords = ["anxious", "anxiety", "worried", "nervous", "stressed", "stress", 
                       "overwhelmed", "panic", "panicking", "fearful", "scared", "afraid",
                       "tense", "uneasy", "restless"]
    if any(kw in normalized for kw in anxious_keywords):
        return ("anxious", "moderate")
    
    # Angry/frustrated keywords
    angry_keywords = ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", 
                     "rage", "raging", "livid", "upset"]
    if any(kw in normalized for kw in angry_keywords):
        return ("angry", "moderate")
    
    # Fearful keywords
    fearful_keywords = ["fear", "fearful", "terrified", "scared", "afraid", "horrified", 
                       "panic", "panicking"]
    if any(kw in normalized for kw in fearful_keywords):
        return ("fearful", "high")
    
    # Neutral/okay keywords
    neutral_keywords = ["ok", "okay", "fine", "normal", "nothing", "alright", "all right",
                       "neutral", "calm", "peaceful"]
    if any(kw in normalized for kw in neutral_keywords):
        return ("neutral", "low")
    
    # If no clear match, return None to fall back to model
    return None

