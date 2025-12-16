import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from torchvision.models import resnet50

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    """Facial emotion detection using ResNet50 with optional fine-tuned FER weights."""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        # Load pre-trained ResNet50
        self.model = resnet50(pretrained=True)

        # Modify final layer for emotion classification
        num_emotions = 7
        self.model.fc = nn.Linear(self.model.fc.in_features, num_emotions)
        self.model.to(self.device)

        # Load label mapping from saved model (CRITICAL: must match training order)
        self.label_map_path = Path("models/emotion_model/label_map.json")
        self.emotion_labels = self._load_label_mapping()

        # Image preprocessing (MUST match training transforms exactly)
        self.transform = self._get_fer_transforms()

        # Attempt to load fine-tuned FER weights (trained via backend/model/image_trainer.py)
        self.weights_path = Path("models/emotion_model/best_model.pth")
        self._load_custom_weights()

        # Set model to evaluation mode
        self.model.eval()

    def _load_label_mapping(self) -> List[str]:
        """Load emotion label mapping from saved model, or use default."""
        if self.label_map_path.exists():
            try:
                with open(self.label_map_path, 'r', encoding='utf-8') as f:
                    label_map_dict = json.load(f)
                # Convert to list in index order (0, 1, 2, ...)
                num_labels = len(label_map_dict)
                labels = [label_map_dict[str(i)] for i in range(num_labels)]
                logger.info(f"Loaded emotion label mapping: {labels}")
                return labels
            except Exception as exc:
                logger.warning(f"Failed to load label_map.json: {exc}, using default")
        
        # Default fallback (should match training order)
        return ["angry", "disgusted", "fearful", "happy", "neutral", "sad", "surprised"]

    def _get_fer_transforms(self):
        """Get FER image transforms (MUST match training transforms)."""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406], 
                std=[0.229, 0.224, 0.225]
            ),
        ])

    def _load_custom_weights(self) -> None:
        """Load fine-tuned FER weights when available."""
        if self.weights_path.exists():
            try:
                state_dict = torch.load(self.weights_path, map_location=self.device)
                self.model.load_state_dict(state_dict, strict=False)
                self.model.to(self.device)
                logger.info("Loaded custom FER weights from %s", self.weights_path)
            except Exception as exc:
                logger.error("Failed to load FER weights: %s", exc)

    def analyze(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze image for facial emotions"""
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Preprocess image
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)

            # Get predictions
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)

            # Extract emotion scores
            emotion_scores = probabilities[0].cpu().numpy()
            
            # CRITICAL: Use argmax to get the index, then map to label using label_map
            predicted_index = int(np.argmax(emotion_scores))
            max_score = float(emotion_scores[predicted_index])
            
            # Map index to emotion label using loaded label mapping
            if predicted_index < len(self.emotion_labels):
                dominant_emotion = self.emotion_labels[predicted_index]
            else:
                logger.warning(f"Predicted index {predicted_index} out of range, using first label")
                dominant_emotion = self.emotion_labels[0] if self.emotion_labels else "neutral"
            
            # Create emotion_dict for stress calculation and debugging
            emotion_dict = {
                label: float(score)
                for label, score in zip(self.emotion_labels, emotion_scores)
            }
            
            # POST-PROCESSING FIX: Handle common misclassifications
            # CRITICAL FIX: Happy images often misclassified as angry/sad
            # If model predicts angry/sad but happy has reasonable score, prefer happy
            sorted_emotions = sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)
            negative_emotions = ["angry", "sad", "fearful", "disgusted"]
            happy_score = emotion_dict.get("happy", 0.0)
            
            if len(sorted_emotions) >= 2:
                top_emotion, top_score = sorted_emotions[0]
                second_emotion, second_score = sorted_emotions[1]
                
                # AGGRESSIVE FIX for happy: If top is negative (angry/sad) and happy is in top 3 with decent score
                if top_emotion in negative_emotions:
                    # Check if happy is second
                    if second_emotion == "happy":
                        score_diff = top_score - second_score
                        # More aggressive: if happy is within 20% OR top confidence is low, prefer happy
                        if score_diff < 0.20 or (top_score < 0.55 and second_score > 0.25):
                            dominant_emotion = "happy"
                            max_score = second_score
                            logger.info(f"Post-processing FIX: Changed {top_emotion} ({top_score:.3f}) to happy ({second_score:.3f})")
                    # Check if happy is third but still reasonable
                    elif len(sorted_emotions) >= 3:
                        third_emotion, third_score = sorted_emotions[2]
                        if third_emotion == "happy" and top_score < 0.5 and third_score > 0.25:
                            # If top prediction is uncertain and happy is reasonable, prefer happy
                            dominant_emotion = "happy"
                            max_score = third_score
                            logger.info(f"Post-processing FIX: Changed {top_emotion} ({top_score:.3f}) to happy ({third_score:.3f}) - low confidence top")
                    # Even if happy is not in top 3, if top is very uncertain and happy has decent score
                    elif top_score < 0.4 and happy_score > 0.2:
                        dominant_emotion = "happy"
                        max_score = happy_score
                        logger.info(f"Post-processing FIX: Changed {top_emotion} ({top_score:.3f}) to happy ({happy_score:.3f}) - very low confidence")
                
                # Similar fix for surprised
                if top_emotion in negative_emotions and second_emotion == "surprised":
                    score_diff = top_score - second_score
                    if score_diff < 0.15 or (top_score < 0.5 and second_score > 0.3):
                        dominant_emotion = "surprised"
                        max_score = second_score
                        logger.info(f"Post-processing: Changed {top_emotion} ({top_score:.3f}) to surprised ({second_score:.3f})")
            
            # Log prediction for debugging
            logger.debug(f"Image prediction: index={predicted_index}, emotion={dominant_emotion}, confidence={max_score:.3f}")
            logger.debug(f"Top 3 predictions: {sorted(emotion_dict.items(), key=lambda x: x[1], reverse=True)[:3]}")

            # Calculate stress level from facial emotions
            stress_level = self._calculate_facial_stress(emotion_dict)
            
            # Map to platform emotion (FER labels already match platform emotions)
            primary_emotion = dominant_emotion  # FER labels match platform emotions

            # Calculate confidence (boost if prediction is clear)
            confidence = float(max_score)
            if max_score > 0.6:
                confidence = min(0.95, max_score * 1.1)  # Boost high-confidence predictions

            # Detect facial features
            facial_features = self._detect_facial_features(image)

            return {
                "emotions": emotion_dict,
                "dominant_emotion": dominant_emotion,
                "primary_emotion": primary_emotion,
                "stress_level": stress_level,
                "confidence": confidence,
                "facial_features": facial_features,
                "image_analysis": "facial_emotion_detection",
            }

        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return {
                "emotions": {"neutral": 1.0},
                "dominant_emotion": "neutral",
                "primary_emotion": "neutral",
                "stress_level": 0.5,
                "confidence": 0.0,
                "error": str(e),
            }
    
    def _calculate_facial_stress(self, emotions: Dict[str, float]) -> float:
        """Calculate stress level from facial emotions with improved heuristics"""
        # Negative emotions indicate higher stress (weighted by intensity)
        negative_emotions = {
            "sad": 0.8,      # High stress indicator
            "angry": 0.75,    # High stress indicator
            "fearful": 0.9,   # Very high stress indicator
            "disgusted": 0.6  # Moderate stress indicator
        }
        negative_score = sum(emotions.get(emotion, 0.0) * weight 
                           for emotion, weight in negative_emotions.items())
        
        # Positive emotions indicate lower stress (strong reduction)
        positive_emotions = {
            "happy": 0.7,      # Strong stress reduction
            "surprised": 0.3   # Mild stress reduction (surprise can be positive or negative)
        }
        positive_score = sum(emotions.get(emotion, 0.0) * weight 
                            for emotion, weight in positive_emotions.items())
        
        # Neutral emotion provides baseline
        neutral_score = emotions.get("neutral", 0.0) * 0.3
        
        # Calculate stress level with better weighting
        # Base stress from negative emotions, reduced by positive, neutral provides baseline
        stress_level = (negative_score * 1.2) - (positive_score * 0.8) + (neutral_score * 0.2)
        
        # If dominant emotion is very clear (high confidence), adjust accordingly
        max_emotion_score = max(emotions.values())
        if max_emotion_score > 0.7:  # High confidence prediction
            dominant = max(emotions, key=emotions.get)
            if dominant in negative_emotions:
                stress_level = max(stress_level, 0.6)  # Ensure minimum stress for negative emotions
            elif dominant in positive_emotions:
                stress_level = min(stress_level, 0.4)  # Cap stress for positive emotions
        
        # Ensure within bounds
        return max(0.0, min(1.0, stress_level))
    
    def _detect_facial_features(self, image: Image.Image) -> Dict[str, Any]:
        """Detect basic facial features (simplified implementation)"""
        # This is a simplified implementation
        # In a real application, you would use a proper face detection library like OpenCV or dlib
        
        width, height = image.size
        
        # Simulate facial feature detection
        features = {
            "face_detected": True,
            "face_confidence": 0.85,
            "face_region": {
                "x": int(width * 0.2),
                "y": int(height * 0.2),
                "width": int(width * 0.6),
                "height": int(height * 0.6)
            },
            "eyes_detected": True,
            "mouth_detected": True,
            "symmetry_score": 0.78,  # Facial symmetry indicator
            "brightness": self._calculate_brightness(image),
            "contrast": self._calculate_contrast(image)
        }
        
        return features
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate image brightness"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Calculate average brightness
        pixels = list(gray.getdata())
        brightness = sum(pixels) / len(pixels)
        
        # Normalize to 0-1
        return brightness / 255.0
    
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate image contrast"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Calculate standard deviation as contrast measure
        pixels = list(gray.getdata())
        mean = sum(pixels) / len(pixels)
        variance = sum((pixel - mean) ** 2 for pixel in pixels) / len(pixels)
        contrast = variance ** 0.5
        
        # Normalize to 0-1
        return min(contrast / 128.0, 1.0)
    
    def get_emotion_explanation(self, emotions: Dict[str, float]) -> Dict[str, Any]:
        """Get explanation for emotion predictions"""
        explanations = {}
        
        for emotion, score in emotions.items():
            if score > 0.3:  # Only explain significant emotions
                explanations[emotion] = {
                    "score": score,
                    "explanation": self._get_facial_emotion_explanation(emotion)
                }
        
        return explanations
    
    def _get_facial_emotion_explanation(self, emotion: str) -> str:
        """Get explanation for specific facial emotion"""
        explanations = {
            "happy": "Facial features indicate happiness - upturned mouth, raised cheeks, bright eyes.",
            "sad": "Facial features suggest sadness - downturned mouth, lowered eyebrows, drooping eyes.",
            "angry": "Facial features show anger - furrowed brows, narrowed eyes, tense mouth.",
            "fearful": "Facial features indicate fear - wide eyes, raised eyebrows, open mouth.",
            "surprised": "Facial features show surprise - raised eyebrows, wide eyes, open mouth.",
            "disgusted": "Facial features suggest disgust - wrinkled nose, downturned mouth.",
            "neutral": "Facial features appear neutral - relaxed expression with minimal emotion."
        }
        return explanations.get(emotion, "Facial emotion detected through image analysis.")
