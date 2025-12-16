from pathlib import Path
from typing import Dict, List, Any, Optional

import logging
import numpy as np
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from backend.config.labels import (
    DISTILBERT_TO_PLATFORM_EMOTION,
    STRESS_LABELS_INTERNAL,
    STRESS_DISPLAY
)
from backend.services.text_rules import rule_based_emotion_and_stress
from backend.services.text_keyword_override import override_emotion_from_keywords
from backend.services.risk_utils import stress_score_to_label

logger = logging.getLogger(__name__)


class TextAnalyzer:
    """Text emotion analysis using DistilBERT with optional stress detector fine-tuned on datasets."""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = "distilbert-base-uncased"
        self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_name)

        # Initialize model for emotion classification
        self.model = DistilBertForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=7,  # 7 basic emotions
            problem_type="multi_label_classification",
        )
        self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode

        # Emotion labels
        self.emotion_labels = [
            "joy",
            "sadness",
            "anger",
            "fear",
            "surprise",
            "disgust",
            "neutral",
        ]

        # Stress/anxiety keywords (expanded)
        self.stress_keywords = [
            "stressed", "stress", "stressing",
            "anxious", "anxiety", "anxiously",
            "worried", "worry", "worrying", "worries",
            "overwhelmed", "overwhelming",
            "panic", "panicking", "panicked",
            "nervous", "nervously",
            "tired", "exhausted", "exhausting",
            "burnout", "burnt out",
            "pressure", "pressured",
            "deadline", "deadlines",
            "crisis", "crises",
            "depressed", "depression", "depressing",
            "hopeless", "hopelessness",
            "lonely", "loneliness",
            "isolated", "isolation",
            "empty", "emptiness",
            "worthless", "worthlessness",
            "sad", "sadness", "sadly",
            "upset", "upsetting",
            "frustrated", "frustrating", "frustration",
            "angry", "anger", "angrily",
            "scared", "afraid", "fear", "fearful",
            "terrified", "terrifying",
            "dread", "dreading",
            "unable", "can't", "cannot",
            "struggling", "struggle",
            "difficult", "difficulty", "difficulties",
            "problem", "problems",
            "hurt", "hurting", "painful",
            "suffering", "suffer",
        ]

        self.positive_keywords = [
            "happy", "happiness", "happily",
            "excited", "exciting", "excitement",
            "grateful", "gratitude",
            "confident", "confidence",
            "proud", "pride",
            "accomplished", "accomplishment",
            "peaceful", "peace",
            "calm", "calmly", "calming",
            "relaxed", "relaxing", "relax",
            "content", "contentment",
            "optimistic", "optimism",
            "hopeful", "hope",
            "good", "great", "wonderful", "amazing", "fantastic",
            "fine", "okay", "ok", "alright",
            "glad", "pleased", "pleasure",
            "joy", "joyful", "joyfully",
            "smile", "smiling", "laugh", "laughing",
            "love", "loving", "loved",
            "blessed", "blessing",
            "thankful", "thanks", "thank you",
            "success", "successful",
            "win", "winning", "won",
            "better", "best",
            "improving", "improved", "improve",
        ]

        # Optional fine-tuned stress detector (trained via backend/train_models.py on Reddit/Dreaddit datasets)
        self.stress_model_dir = Path("models/stress_model")
        self.stress_tokenizer: Optional[DistilBertTokenizer] = None
        self.stress_model: Optional[DistilBertForSequenceClassification] = None
        self._load_stress_detector()

    def _load_stress_detector(self) -> None:
        """Load fine-tuned stress detector if available."""
        if self.stress_model_dir.exists():
            try:
                self.stress_tokenizer = DistilBertTokenizer.from_pretrained(
                    self.stress_model_dir
                )
                self.stress_model = DistilBertForSequenceClassification.from_pretrained(
                    self.stress_model_dir
                )
                self.stress_model.to(self.device)
                self.stress_model.eval()
                logger.info(
                    "Loaded fine-tuned stress detector from %s", self.stress_model_dir
                )
            except Exception as exc:
                logger.error("Failed to load custom stress detector: %s", exc)
                self.stress_model = None
                self.stress_tokenizer = None

    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for emotions and stress levels"""
        try:
            # FIRST: Check rule-based override for very short texts
            rule_result = rule_based_emotion_and_stress(text)
            if rule_result is not None:
                emotion, stress_label = rule_result
                # Convert stress label to stress level (0.0-1.0)
                stress_level_map = {
                    "no_stress": 0.1,
                    "low": 0.3,
                    "moderate": 0.6,
                    "high": 0.85
                }
                stress_level = stress_level_map.get(stress_label, 0.5)
                
                # Map DistilBERT emotion format for consistency
                distilbert_emotion = {
                    "happy": "joy",
                    "sad": "sadness",
                    "anxious": "fear",
                    "angry": "anger",
                    "fearful": "fear",
                    "neutral": "neutral",
                    "surprised": "surprise",
                    "disgusted": "disgust"
                }.get(emotion, "neutral")
                
                return {
                    "emotions": {distilbert_emotion: 0.9, "neutral": 0.1},
                    "dominant_emotion": distilbert_emotion,
                    "primary_emotion": emotion,
                    "stress_level": stress_level,
                    "stress_label": stress_label,
                    "dataset_stress_probability": None,
                    "confidence": 0.9,
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "has_stress_keywords": stress_label in ["moderate", "high"],
                    "has_positive_keywords": emotion == "happy",
                    "used_rule_based": True,
                }
            
            # For longer texts, use the trained model
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)

            # Extract emotion scores
            emotion_scores = probabilities[0].cpu().numpy()
            emotion_dict = {
                label: float(score)
                for label, score in zip(self.emotion_labels, emotion_scores)
            }

            # Calculate stress level based on keywords and emotions
            keyword_stress = self._calculate_stress_level(text, emotion_dict)
            dataset_stress = self._predict_dataset_stress(text)

            if dataset_stress is not None:
                stress_level = self._blend_stress_scores(keyword_stress, dataset_stress)
            else:
                stress_level = keyword_stress
            
            # Convert stress level to label
            stress_label = stress_score_to_label(stress_level)

            # Determine dominant emotion - prioritize based on scores and keywords
            dominant_emotion = max(emotion_dict, key=emotion_dict.get)
            max_emotion_score = emotion_dict[dominant_emotion]
            
            # Override with keyword-based detection if strong positive/negative signals
            text_lower = text.lower()
            positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
            stress_count = sum(1 for kw in self.stress_keywords if kw in text_lower)
            
            # Strong keyword-based overrides (higher priority than model if keywords are clear)
            keyword_emotion = None
            
            # Check for positive emotions first
            if positive_count >= 2 or (positive_count >= 1 and any(kw in text_lower for kw in ["happy", "great", "wonderful", "amazing", "excited"])):
                if "happy" in text_lower or "joy" in text_lower or "glad" in text_lower:
                    keyword_emotion = "joy"
                elif "excited" in text_lower:
                    keyword_emotion = "joy"  # Excitement maps to joy
                elif "grateful" in text_lower or "thankful" in text_lower:
                    keyword_emotion = "joy"
            
            # Check for negative emotions
            if keyword_emotion is None and stress_count >= 1:
                if any(kw in text_lower for kw in ["anxious", "anxiety", "worried", "nervous", "panic", "scared", "afraid"]):
                    keyword_emotion = "fear"
                elif any(kw in text_lower for kw in ["sad", "depressed", "hopeless", "lonely", "empty", "worthless"]):
                    keyword_emotion = "sadness"
                elif any(kw in text_lower for kw in ["angry", "mad", "furious", "irritated", "frustrated"]):
                    keyword_emotion = "anger"
                elif any(kw in text_lower for kw in ["fear", "fearful", "terrified", "horrified"]):
                    keyword_emotion = "fear"
            
            # Apply keyword override if confidence is high enough
            if keyword_emotion:
                # If keyword emotion matches model prediction, boost confidence
                if keyword_emotion == dominant_emotion:
                    # Already correct, keep it
                    pass
                elif emotion_dict.get(keyword_emotion, 0) > 0.15:  # Model also detected it somewhat
                    dominant_emotion = keyword_emotion
                elif max_emotion_score < 0.4:  # Model is uncertain, trust keywords
                    dominant_emotion = keyword_emotion
                elif stress_count >= 3 or positive_count >= 3:  # Very strong keyword signals
                    dominant_emotion = keyword_emotion
            
            # Map to platform emotion using standardized mapping
            mapped_emotion = DISTILBERT_TO_PLATFORM_EMOTION.get(dominant_emotion, "neutral")
            
            # Apply keyword override for obvious phrases (even for longer texts)
            mapped_emotion = override_emotion_from_keywords(text, mapped_emotion)

            # Calculate confidence
            confidence = float(max(emotion_dict.values()))

            return {
                "emotions": emotion_dict,
                "dominant_emotion": dominant_emotion,
                "primary_emotion": mapped_emotion,
                "stress_level": stress_level,
                "stress_label": stress_label,
                "dataset_stress_probability": dataset_stress,
                "confidence": confidence,
                "text_length": len(text),
                "word_count": len(text.split()),
                "has_stress_keywords": any(
                    keyword in text.lower() for keyword in self.stress_keywords
                ),
                "has_positive_keywords": any(
                    keyword in text.lower() for keyword in self.positive_keywords
                ),
                "used_rule_based": False,
            }

        except Exception as e:
            logger.error(f"Text analysis error: {str(e)}")
            return {
                "emotions": {"neutral": 1.0},
                "dominant_emotion": "neutral",
                "primary_emotion": "neutral",
                "stress_level": 0.5,
                "stress_label": "moderate",
                "confidence": 0.0,
                "error": str(e),
                "used_rule_based": False,
            }

    def _predict_dataset_stress(self, text: str) -> Optional[float]:
        """Predict stress probability using fine-tuned dataset model."""
        if not self.stress_model or not self.stress_tokenizer:
            return None

        try:
            inputs = self.stress_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=256,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.stress_model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                # Binary classifier -> stressed class index = 1
                stress_probability = float(probabilities[0][1].cpu().item())
            return stress_probability
        except Exception as exc:
            logger.error("Stress detector inference failed: %s", exc)
            return None

    def _blend_stress_scores(self, keyword_score: float, dataset_score: float) -> float:
        """Blend heuristic stress score with dataset-derived probability."""
        blended = (keyword_score * 0.35) + (dataset_score * 0.65)
        return max(0.0, min(1.0, blended))

    def _map_emotion(self, emotion: str) -> str:
        """Map DistilBERT emotion to core platform emotions."""
        # Use standardized mapping from config
        return DISTILBERT_TO_PLATFORM_EMOTION.get(emotion, "neutral")

    def _calculate_stress_level(self, text: str, emotions: Dict[str, float]) -> float:
        """Calculate stress level from text and emotions with improved heuristics"""
        text_lower = text.lower()

        # Base stress from negative emotions (weighted by intensity)
        negative_emotions = {
            "sadness": 0.7,
            "anger": 0.75,
            "fear": 0.85,  # Fear/anxiety is a strong stress indicator
            "disgust": 0.5
        }
        negative_score = sum(emotions.get(emotion, 0.0) * weight 
                            for emotion, weight in negative_emotions.items())
        
        # Positive emotions reduce stress (weighted)
        positive_emotions = {
            "joy": 0.6,      # Strong stress reduction
            "surprise": 0.2  # Mild reduction (surprise can be positive or negative)
        }
        positive_score = sum(emotions.get(emotion, 0.0) * weight 
                           for emotion, weight in positive_emotions.items())

        # Keyword-based stress (improved counting)
        stress_count = sum(1 for keyword in self.stress_keywords if keyword in text_lower)
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)

        # Calculate keyword stress (normalize based on text length)
        word_count = len(text.split())
        if word_count > 0:
            # Stress density: more stress keywords per word = higher stress
            stress_density = min(stress_count / max(word_count / 10, 1), 1.0)
            keyword_stress = stress_density * 0.8  # Cap at 0.8 from keywords alone
        else:
            keyword_stress = 0.0
        
        # Positive keywords reduce stress
        if word_count > 0:
            positive_density = min(positive_count / max(word_count / 8, 1), 1.0)
            keyword_positive = positive_density * 0.5  # Can reduce stress by up to 0.5
        else:
            keyword_positive = 0.0

        # Combine factors with improved weighting
        # Negative emotions contribute most, then keywords, positive reduces
        stress_level = (negative_score * 0.6) + (keyword_stress * 0.4) - (
            keyword_positive * 0.3
        ) - (positive_score * 0.2)

        # Special cases: very strong signals
        if stress_count >= 5:  # Many stress keywords
            stress_level = max(stress_level, 0.7)
        if positive_count >= 4 and stress_count == 0:  # Very positive, no stress
            stress_level = min(stress_level, 0.2)
        
        # If dominant emotion is very clear, adjust stress accordingly
        max_emotion = max(emotions, key=emotions.get)
        max_emotion_score = emotions[max_emotion]
        if max_emotion_score > 0.6:  # High confidence
            if max_emotion in negative_emotions:
                stress_level = max(stress_level, 0.5)  # Ensure minimum stress for negative
            elif max_emotion in positive_emotions:
                stress_level = min(stress_level, 0.4)  # Cap stress for positive

        # Ensure within bounds
        return max(0.0, min(1.0, stress_level))

    def get_emotion_explanation(self, text: str, emotions: Dict[str, float]) -> Dict[str, Any]:
        """Get explanation for emotion predictions"""
        explanations = {}

        for emotion, score in emotions.items():
            if score > 0.3:  # Only explain significant emotions
                explanations[emotion] = {
                    "score": score,
                    "explanation": self._get_emotion_explanation(emotion, text),
                }

        return explanations

    def _get_emotion_explanation(self, emotion: str, text: str) -> str:
        """Get explanation for specific emotion"""
        explanations = {
            "joy": "The text contains positive language and expressions of happiness.",
            "sadness": "The text indicates feelings of sadness, loss, or melancholy.",
            "anger": "The text shows signs of frustration, irritation, or anger.",
            "fear": "The text expresses anxiety, worry, or fear about future events.",
            "surprise": "The text contains unexpected or surprising elements.",
            "disgust": "The text shows aversion or disgust towards something.",
            "neutral": "The text appears to be emotionally neutral or factual.",
        }
        return explanations.get(emotion, "Emotion detected based on text analysis.")
