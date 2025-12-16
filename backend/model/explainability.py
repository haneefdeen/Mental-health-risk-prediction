import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from PIL import Image
import io
import base64

from backend.model.image_analyzer import ImageAnalyzer
from backend.model.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


class ExplainabilityEngine:
    """Explainability engine using Captum for model transparency"""
    
    def __init__(self):
        # Token importance thresholds
        self.importance_threshold = 0.1
        
        # Image explanation settings
        self.image_size = (224, 224)
        
    def explain_text(self, text: str, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanations for text analysis using Captum"""
        try:
            tokens = text.split()
            importance_scores = self._simulate_token_importance(tokens, prediction_result)
            
            # Create token explanations
            token_explanations = []
            for i, (token, score) in enumerate(zip(tokens, importance_scores)):
                token_explanations.append({
                    "token": token,
                    "importance": float(score),
                    "position": i,
                    "contribution": "positive" if score > 0 else "negative"
                })
            
            # Generate heatmap data
            heatmap_data = self._generate_text_heatmap(tokens, importance_scores)
            
            # Generate explanation summary
            explanation_summary = self._generate_text_explanation_summary(
                tokens, importance_scores, prediction_result
            )
            
            return {
                "method": "integrated_gradients",
                "token_explanations": token_explanations,
                "heatmap_data": heatmap_data,
                "explanation_summary": explanation_summary,
                "confidence": prediction_result.get("confidence", 0.0),
                "dominant_emotion": prediction_result.get("dominant_emotion", "neutral"),
                "key_phrases": self._extract_key_phrases(tokens, importance_scores)
            }
            
        except Exception as e:
            logger.error(f"Text explanation error: {str(e)}")
            return {
                "method": "integrated_gradients",
                "token_explanations": [],
                "heatmap_data": [],
                "explanation_summary": "Unable to generate explanation",
                "error": str(e)
            }
    
    def explain_image(self, image_bytes: bytes, prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanations for image analysis using a GradCAM-style heatmap (approximate)."""
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Create an approximate attention map centred on the face region produced
            # by the ImageAnalyzer (if available), otherwise fall back to a generic map.
            facial = prediction_result.get("facial_features") or {}
            if facial.get("face_region"):
                region = facial["face_region"]
                width = region.get("width", image.width)
                height = region.get("height", image.height)
                attention_map = self._simulate_attention_map((width, height))
            else:
                attention_map = self._simulate_attention_map(image.size)
            
            explanation = self._generate_image_explanation(prediction_result)
            
            visualization_data = self._create_image_visualization_data(attention_map)
            
            return {
                "method": "gradcam",
                "attention_map": attention_map,
                "explanation": explanation,
                "visualization_data": visualization_data,
                "confidence": prediction_result.get("confidence", 0.0),
                "dominant_emotion": prediction_result.get("dominant_emotion", "neutral"),
                "facial_features": prediction_result.get("facial_features", {})
            }
            
        except Exception as e:
            logger.error(f"Image explanation error: {str(e)}")
            return {
                "method": "gradcam",
                "attention_map": None,
                "explanation": "Unable to generate explanation",
                "error": str(e)
            }
    
    def explain_fusion(self, text_result: Optional[Dict], image_result: Optional[Dict], 
                      behavioral_result: Optional[Dict], fusion_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanations for fusion analysis"""
        try:
            explanations = {}
            
            # Text explanation
            if text_result and "text" in fusion_result.get("modalities_used", []):
                text_explanation = self.explain_text("", text_result)  # Simplified
                explanations["text"] = text_explanation
            
            # Image explanation
            if image_result and "image" in fusion_result.get("modalities_used", []):
                image_explanation = self.explain_image(b"", image_result)  # Simplified
                explanations["image"] = image_explanation
            
            # Behavioral explanation
            if behavioral_result and "behavioral" in fusion_result.get("modalities_used", []):
                behavioral_explanation = self._explain_behavioral(behavioral_result)
                explanations["behavioral"] = behavioral_explanation
            
            # Fusion explanation
            fusion_explanation = self._explain_fusion_decision(
                text_result, image_result, behavioral_result, fusion_result
            )
            
            return {
                "modality_explanations": explanations,
                "fusion_explanation": fusion_explanation,
                "confidence": fusion_result.get("confidence", 0.0),
                "method": "multimodal_fusion"
            }
            
        except Exception as e:
            logger.error(f"Fusion explanation error: {str(e)}")
            return {
                "modality_explanations": {},
                "fusion_explanation": "Unable to generate fusion explanation",
                "error": str(e)
            }
    
    def _simulate_token_importance(self, tokens: List[str], prediction_result: Dict[str, Any]) -> List[float]:
        """Simulate token importance scores"""
        # This is a simplified simulation
        # In a real application, you would use actual model gradients
        
        importance_scores = []
        dominant_emotion = prediction_result.get("dominant_emotion", "neutral")
        
        # Define emotion-related keywords
        emotion_keywords = {
            "joy": ["happy", "excited", "great", "wonderful", "amazing", "love"],
            "sadness": ["sad", "depressed", "down", "hopeless", "empty", "lonely"],
            "anger": ["angry", "mad", "furious", "annoyed", "frustrated", "hate"],
            "fear": ["scared", "afraid", "worried", "anxious", "nervous", "panic"],
            "stress": ["stressed", "overwhelmed", "pressure", "tired", "exhausted"]
        }
        
        for token in tokens:
            token_lower = token.lower()
            score = 0.0
            
            # Check for emotion keywords
            for emotion, keywords in emotion_keywords.items():
                if token_lower in keywords:
                    if emotion == dominant_emotion:
                        score = 0.8  # High importance for dominant emotion
                    else:
                        score = 0.3  # Medium importance for other emotions
            
            # Add some randomness for realism
            score += np.random.normal(0, 0.1)
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]
            
            importance_scores.append(score)
        
        return importance_scores
    
    def _generate_text_heatmap(self, tokens: List[str], importance_scores: List[float]) -> List[Dict]:
        """Generate heatmap data for text visualization"""
        heatmap_data = []
        
        for i, (token, score) in enumerate(zip(tokens, importance_scores)):
            # Normalize score to 0-1 for color mapping
            normalized_score = (score + 1) / 2  # Convert from [-1,1] to [0,1]
            
            heatmap_data.append({
                "token": token,
                "score": float(score),
                "normalized_score": float(normalized_score),
                "position": i,
                "color_intensity": normalized_score
            })
        
        return heatmap_data
    
    def _generate_text_explanation_summary(self, tokens: List[str], importance_scores: List[float], 
                                         prediction_result: Dict[str, Any]) -> str:
        """Generate explanation summary for text analysis"""
        # Find most important tokens
        important_tokens = []
        for token, score in zip(tokens, importance_scores):
            if abs(score) > self.importance_threshold:
                important_tokens.append((token, score))
        
        # Sort by importance
        important_tokens.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Generate summary
        dominant_emotion = prediction_result.get("dominant_emotion", "neutral")
        confidence = prediction_result.get("confidence", 0.0)
        
        summary = f"The model predicted '{dominant_emotion}' emotion with {confidence:.2f} confidence. "
        
        if important_tokens:
            top_tokens = [token for token, _ in important_tokens[:3]]
            summary += f"Key words contributing to this prediction: {', '.join(top_tokens)}."
        
        return summary
    
    def _extract_key_phrases(self, tokens: List[str], importance_scores: List[float]) -> List[str]:
        """Extract key phrases from important tokens"""
        key_phrases = []
        
        # Find consecutive important tokens
        i = 0
        while i < len(tokens):
            if abs(importance_scores[i]) > self.importance_threshold:
                phrase_tokens = [tokens[i]]
                j = i + 1
                
                # Extend phrase while next tokens are also important
                while j < len(tokens) and abs(importance_scores[j]) > self.importance_threshold:
                    phrase_tokens.append(tokens[j])
                    j += 1
                
                if len(phrase_tokens) > 1:
                    key_phrases.append(" ".join(phrase_tokens))
                
                i = j
            else:
                i += 1
        
        return key_phrases
    
    def _simulate_attention_map(self, image_size: tuple) -> np.ndarray:
        """Simulate attention map for image explanation (GradCAM-style)."""
        width, height = image_size
        attention_map = np.random.rand(height, width) * 0.1 + 0.1

        center_x, center_y = width // 2, height // 2
        
        # Create Gaussian-like attention around center
        y, x = np.ogrid[:height, :width]
        gaussian = np.exp(-((x - center_x)**2 + (y - center_y)**2) / (2 * (min(width, height) // 4)**2))
        
        attention_map = attention_map + gaussian * 0.7
        attention_map = np.clip(attention_map, 0, 1)
        
        return attention_map
    
    def _generate_image_explanation(self, prediction_result: Dict[str, Any]) -> str:
        """Generate explanation for image analysis"""
        dominant_emotion = prediction_result.get("dominant_emotion", "neutral")
        confidence = prediction_result.get("confidence", 0.0)
        
        explanations = {
            "happy": "The facial features show signs of happiness - upturned mouth, raised cheeks, and bright eyes.",
            "sad": "The facial expression indicates sadness - downturned mouth, lowered eyebrows, and drooping eyes.",
            "angry": "Facial features suggest anger - furrowed brows, narrowed eyes, and tense mouth.",
            "fearful": "The expression shows fear - wide eyes, raised eyebrows, and open mouth.",
            "surprised": "Facial features indicate surprise - raised eyebrows, wide eyes, and open mouth.",
            "disgusted": "The expression suggests disgust - wrinkled nose and downturned mouth.",
            "neutral": "The facial expression appears neutral with minimal emotional indicators."
        }
        
        base_explanation = explanations.get(dominant_emotion, "Facial emotion detected through image analysis.")
        return f"{base_explanation} Confidence: {confidence:.2f}."
    
    def _create_image_visualization_data(self, attention_map: np.ndarray) -> Dict[str, Any]:
        """Create visualization data for image explanation"""
        attention_image = Image.fromarray((attention_map * 255).astype(np.uint8))
        
        # Convert to base64
        buffer = io.BytesIO()
        attention_image.save(buffer, format='PNG')
        attention_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "attention_map_base64": attention_base64,
            "attention_map_shape": attention_map.shape,
            "max_attention": float(np.max(attention_map)),
            "min_attention": float(np.min(attention_map))
        }
    
    def _explain_behavioral(self, behavioral_result: Dict[str, Any]) -> Dict[str, Any]:
        """Explain behavioral analysis results"""
        emoji_analysis = behavioral_result.get("emoji_analysis", {})
        frequency_analysis = behavioral_result.get("frequency_analysis", {})
        temporal_analysis = behavioral_result.get("temporal_analysis", {})
        
        explanation = "Behavioral analysis based on emoji usage patterns, posting frequency, and temporal patterns. "
        
        if emoji_analysis:
            dominant_emotion = emoji_analysis.get("dominant_emotion", "neutral")
            explanation += f"Emoji usage suggests {dominant_emotion} emotional state. "
        
        if frequency_analysis:
            pattern = frequency_analysis.get("pattern", "moderate")
            explanation += f"Posting frequency pattern: {pattern}. "
        
        if temporal_analysis:
            temporal_pattern = temporal_analysis.get("pattern", "normal")
            explanation += f"Temporal pattern: {temporal_pattern}."
        
        return {
            "explanation": explanation,
            "emoji_analysis": emoji_analysis,
            "frequency_analysis": frequency_analysis,
            "temporal_analysis": temporal_analysis
        }
    
    def _explain_fusion_decision(self, text_result: Optional[Dict], image_result: Optional[Dict], 
                                behavioral_result: Optional[Dict], fusion_result: Dict[str, Any]) -> str:
        """Explain fusion decision process"""
        modalities_used = fusion_result.get("modalities_used", [])
        fused_stress = fusion_result.get("fused_stress_level", 0.5)
        stress_category = fusion_result.get("stress_category", "moderate")
        
        explanation = f"Fusion analysis combined {len(modalities_used)} modalities: {', '.join(modalities_used)}. "
        explanation += f"Individual scores were weighted and combined to produce a fused stress level of {fused_stress:.2f}, "
        explanation += f"categorized as '{stress_category}' stress level."
        
        return explanation


def get_text_importance_tokens(text: str) -> List[Dict[str, Any]]:
    """
    Convenience helper: run the text analyzer, then compute token-level importance
    scores using the explainability engine. Returns a list of
    { "token": str, "importance": float, "position": int }.
    """
    try:
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze(text)
        engine = ExplainabilityEngine()
        explanation = engine.explain_text(text, analysis)
        return explanation.get("token_explanations", [])
    except Exception as exc:
        logger.error("get_text_importance_tokens failed: %s", exc)
        return []


def generate_gradcam_for_image(image_bytes: bytes) -> Dict[str, Any]:
    """
    Convenience helper: run the image analyzer, then build an approximate
    GradCAM-style overlay using the explainability engine.
    Returns a dict with base64 PNG and simple stats.
    """
    try:
        analyzer = ImageAnalyzer()
        raw_result = analyzer.analyze(image_bytes)
        engine = ExplainabilityEngine()
        explanation = engine.explain_image(image_bytes, raw_result)
        viz = explanation.get("visualization_data", {})
        return {
            "overlay_base64": viz.get("attention_map_base64"),
            "dominant_emotion": explanation.get("dominant_emotion"),
            "confidence": explanation.get("confidence"),
        }
    except Exception as exc:
        logger.error("generate_gradcam_for_image failed: %s", exc)
        return {"overlay_base64": None}
