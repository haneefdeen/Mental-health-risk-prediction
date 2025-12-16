"""
Canonical FER2013 label mapping.
Standard FER2013 order: 0=Angry, 1=Disgust, 2=Fear, 3=Happy, 4=Sad, 5=Surprise, 6=Neutral
"""

# Standard FER2013 label order (index -> emotion)
FER_EMOTION_LABELS = [
    "angry",      # 0
    "disgusted",  # 1 (FER uses "disgust", we use "disgusted" for consistency)
    "fearful",    # 2 (FER uses "fear", we use "fearful" for consistency)
    "happy",      # 3
    "sad",        # 4
    "surprised",  # 5 (FER uses "surprise", we use "surprised" for consistency)
    "neutral",    # 6
]

# FER folder names (as they appear in dataset folders)
FER_FOLDER_NAMES = {
    "angry": "angry",
    "disgusted": "disgust",  # Folder might be named "disgust"
    "fearful": "fear",       # Folder might be named "fear"
    "happy": "happy",
    "sad": "sad",
    "surprised": "surprise",  # Folder might be named "surprise"
    "neutral": "neutral",
}

# Mapping from FER index to platform emotion (lowercase)
FER_INDEX_TO_PLATFORM = {
    0: "angry",
    1: "disgusted",
    2: "fearful",
    3: "happy",
    4: "sad",
    5: "surprised",
    6: "neutral",
}

# Reverse mapping: platform emotion -> FER index
PLATFORM_TO_FER_INDEX = {v: k for k, v in FER_INDEX_TO_PLATFORM.items()}


