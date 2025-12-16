"""
Standardized label configuration for MindScope AI.
All models and inference should use these labels for consistency.
"""

# Primary emotions supported by the platform
PRIMARY_EMOTIONS = [
    "happy",      # 😊
    "sad",        # 😢
    "anxious",    # 😟
    "fearful",    # 😨
    "neutral",    # 😐
    "surprised",  # 😲
    "disgusted",  # 😒
    "angry",      # 😠
]

# Emoji mapping for emotions
PRIMARY_EMOJI = {
    "happy": "😊",
    "sad": "😢",
    "anxious": "😟",
    "fearful": "😨",
    "neutral": "😐",
    "surprised": "😲",
    "disgusted": "😒",
    "angry": "😠",
}

# Internal stress labels (used in training and inference)
STRESS_LABELS_INTERNAL = ["no_stress", "low", "moderate", "high"]

# Display labels for stress categories
STRESS_DISPLAY = {
    "no_stress": "No Apparent Stress",
    "low": "Low Stress",
    "moderate": "Moderate Stress",
    "high": "High Stress",
}

# Mapping from DistilBERT emotion labels to platform emotions
DISTILBERT_TO_PLATFORM_EMOTION = {
    "joy": "happy",
    "surprise": "surprised",
    "sadness": "sad",
    "disgust": "disgusted",
    "anger": "angry",
    "fear": "fearful",
    "neutral": "neutral",
}

# Mapping from FER emotion labels to platform emotions
FER_TO_PLATFORM_EMOTION = {
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "fear": "fearful",
    "surprise": "surprised",
    "disgust": "disgusted",
    "neutral": "neutral",
}




