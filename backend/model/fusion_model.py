import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FusionModel:
    """Softmax Fusion Layer to merge text, image, and behavioral predictions"""
    
    def __init__(self):
        # Initialize fusion weights
        self.fusion_weights = {
            "text": 0.4,      # Text analysis weight
            "image": 0.3,     # Image analysis weight
            "behavioral": 0.3  # Behavioral analysis weight
        }
        
        # Stress level thresholds
        self.stress_thresholds = {
            "low": 0.3,
            "moderate": 0.6,
            "high": 0.8,
            "critical": 0.9
        }
        
        # Coping strategies database
        self.coping_strategies = {
            "low": [
                "Continue maintaining healthy habits",
                "Practice mindfulness and gratitude",
                "Stay connected with supportive people",
                "Engage in regular physical activity"
            ],
            "moderate": [
                "Practice deep breathing exercises",
                "Try meditation or yoga",
                "Limit caffeine and alcohol intake",
                "Establish a regular sleep schedule",
                "Consider talking to a trusted friend or family member"
            ],
            "high": [
                "Practice progressive muscle relaxation",
                "Use grounding techniques (5-4-3-2-1 method)",
                "Consider professional counseling or therapy",
                "Limit social media and news consumption",
                "Focus on one task at a time",
                "Practice self-compassion and positive self-talk"
            ],
            "critical": [
                "Seek immediate professional help",
                "Contact a crisis hotline",
                "Reach out to emergency contacts",
                "Remove yourself from stressful situations",
                "Practice emergency breathing techniques",
                "Consider medication consultation with a doctor"
            ]
        }
    
    def fuse_predictions(self, text_result: Optional[Dict], image_result: Optional[Dict], behavioral_result: Optional[Dict]) -> Dict[str, Any]:
        """Fuse predictions from text, image, and behavioral analysis"""
        try:
            # Extract stress levels from each modality
            text_stress = text_result.get("stress_level", 0.5) if text_result else 0.5
            image_stress = image_result.get("stress_level", 0.5) if image_result else 0.5
            behavioral_stress = behavioral_result.get("behavioral_score", 0.5) if behavioral_result else 0.5
            
            # Calculate weighted fusion
            available_modalities = []
            weights = []
            stress_values = []
            
            if text_result:
                available_modalities.append("text")
                weights.append(self.fusion_weights["text"])
                stress_values.append(text_stress)
            
            if image_result:
                available_modalities.append("image")
                weights.append(self.fusion_weights["image"])
                stress_values.append(image_stress)
            
            if behavioral_result:
                available_modalities.append("behavioral")
                weights.append(self.fusion_weights["behavioral"])
                stress_values.append(behavioral_stress)
            
            # Normalize weights
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            # Calculate fused stress level
            fused_stress = sum(stress * weight for stress, weight in zip(stress_values, normalized_weights))
            
            # Determine stress category
            stress_category = self._determine_stress_category(fused_stress)
            
            # Calculate confidence
            confidence = self._calculate_fusion_confidence(text_result, image_result, behavioral_result)
            
            # Generate comprehensive analysis
            analysis = self._generate_fusion_analysis(text_result, image_result, behavioral_result, fused_stress)
            
            return {
                "fused_stress_level": fused_stress,
                "stress_category": stress_category,
                "confidence": confidence,
                "modalities_used": available_modalities,
                "individual_scores": {
                    "text": text_stress,
                    "image": image_stress,
                    "behavioral": behavioral_stress
                },
                "analysis": analysis,
                "risk_assessment": self._assess_risk(fused_stress),
                "recommendations": self._generate_recommendations(fused_stress, stress_category)
            }
            
        except Exception as e:
            logger.error(f"Fusion analysis error: {str(e)}")
            return {
                "fused_stress_level": 0.5,
                "stress_category": "moderate",
                "confidence": 0.0,
                "modalities_used": [],
                "individual_scores": {"text": 0.5, "image": 0.5, "behavioral": 0.5},
                "analysis": "Fusion analysis failed",
                "risk_assessment": "Unable to assess",
                "recommendations": ["Seek professional help if experiencing distress"],
                "error": str(e)
            }
    
    def _determine_stress_category(self, stress_level: float) -> str:
        """Determine stress category based on level"""
        if stress_level < self.stress_thresholds["low"]:
            return "low"
        elif stress_level < self.stress_thresholds["moderate"]:
            return "moderate"
        elif stress_level < self.stress_thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    def _calculate_fusion_confidence(self, text_result: Optional[Dict], image_result: Optional[Dict], behavioral_result: Optional[Dict]) -> float:
        """Calculate confidence in fusion prediction"""
        confidences = []
        
        if text_result:
            confidences.append(text_result.get("confidence", 0.0))
        
        if image_result:
            confidences.append(image_result.get("confidence", 0.0))
        
        if behavioral_result:
            confidences.append(behavioral_result.get("confidence", 0.0))
        
        if not confidences:
            return 0.0
        
        # Average confidence weighted by modality importance
        return sum(confidences) / len(confidences)
    
    def _generate_fusion_analysis(self, text_result: Optional[Dict], image_result: Optional[Dict], behavioral_result: Optional[Dict], fused_stress: float) -> str:
        """Generate comprehensive analysis"""
        analysis_parts = []
        
        if text_result:
            dominant_emotion = text_result.get("dominant_emotion", "neutral")
            analysis_parts.append(f"Text analysis indicates {dominant_emotion} emotional state")
        
        if image_result:
            dominant_emotion = image_result.get("dominant_emotion", "neutral")
            analysis_parts.append(f"Facial expression shows {dominant_emotion} emotion")
        
        if behavioral_result:
            pattern = behavioral_result.get("frequency_analysis", {}).get("pattern", "moderate")
            analysis_parts.append(f"Behavioral patterns suggest {pattern} posting frequency")
        
        # Overall assessment
        category = self._determine_stress_category(fused_stress)
        analysis_parts.append(f"Overall assessment: {category} stress level ({fused_stress:.2f})")
        
        return ". ".join(analysis_parts) + "."
    
    def _assess_risk(self, stress_level: float) -> Dict[str, Any]:
        """Assess risk level and provide risk indicators"""
        category = self._determine_stress_category(stress_level)
        
        risk_indicators = {
            "low": {
                "level": "minimal",
                "indicators": ["Good emotional regulation", "Healthy coping mechanisms"],
                "urgency": "low"
            },
            "moderate": {
                "level": "elevated",
                "indicators": ["Some stress indicators present", "May benefit from stress management"],
                "urgency": "medium"
            },
            "high": {
                "level": "significant",
                "indicators": ["Multiple stress indicators", "May need professional support"],
                "urgency": "high"
            },
            "critical": {
                "level": "severe",
                "indicators": ["Severe stress indicators", "Immediate professional help recommended"],
                "urgency": "critical"
            }
        }
        
        return risk_indicators.get(category, risk_indicators["moderate"])
    
    def _generate_recommendations(self, stress_level: float, category: str) -> List[str]:
        """Generate personalized recommendations"""
        base_recommendations = self.coping_strategies.get(category, self.coping_strategies["moderate"])
        
        # Add modality-specific recommendations
        additional_recommendations = []
        
        if stress_level > 0.7:
            additional_recommendations.extend([
                "Consider reducing screen time and social media usage",
                "Practice regular physical exercise",
                "Maintain a consistent sleep schedule"
            ])
        
        if stress_level > 0.8:
            additional_recommendations.extend([
                "Seek professional mental health support",
                "Consider mindfulness-based stress reduction programs",
                "Develop a crisis management plan"
            ])
        
        return base_recommendations + additional_recommendations
    
    def get_coping_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Get coping suggestions based on analysis result (emotion-aware)"""
        if isinstance(analysis_result, dict):
            stress_level = analysis_result.get("stress_level", analysis_result.get("fused_stress_level", 0.5))
            emotion = analysis_result.get("emotion") or analysis_result.get("primary_emotion") or analysis_result.get("dominant_emotion", "")
            category = self._determine_stress_category(stress_level)
            
            # Get base suggestions based on stress category
            suggestions = self.coping_strategies.get(category, self.coping_strategies["moderate"]).copy()
            
            # Customize based on emotion
            emotion_lower = str(emotion).lower()
            if emotion_lower in ["happy", "joy", "excited", "calm"]:
                # For positive emotions, add maintenance suggestions
                if stress_level < 0.3:
                    suggestions = [
                        "Continue maintaining healthy habits",
                        "Practice mindfulness and gratitude",
                        "Stay connected with supportive people",
                        "Engage in regular physical activity",
                        "Keep a gratitude journal"
                    ]
                elif stress_level < 0.5:
                    suggestions = [
                        "Practice deep breathing exercises",
                        "Try meditation or yoga",
                        "Maintain social connections",
                        "Engage in hobbies you enjoy",
                        "Get adequate sleep"
                    ]
            elif emotion_lower in ["sad", "sadness", "depressed", "lonely"]:
                # For sadness, add connection-focused suggestions
                suggestions = [
                    "Reach out to a trusted friend or family member",
                    "Engage in activities you used to enjoy",
                    "Practice self-compassion and positive self-talk",
                    "Consider talking to a counselor or therapist",
                    "Spend time in nature or with pets"
                ]
            elif emotion_lower in ["angry", "anger", "frustrated"]:
                # For anger, add calming suggestions
                suggestions = [
                    "Practice progressive muscle relaxation",
                    "Take a walk or engage in physical activity",
                    "Use grounding techniques (5-4-3-2-1 method)",
                    "Write down your feelings in a journal",
                    "Practice box breathing (inhale-4, hold-4, exhale-4)"
                ]
            elif emotion_lower in ["anxious", "fearful", "stressed", "worried"]:
                # For anxiety, add grounding suggestions
                suggestions = [
                    "Practice deep breathing exercises",
                    "Use grounding techniques (5-4-3-2-1 method)",
                    "Try meditation or yoga",
                    "Limit caffeine and alcohol intake",
                    "Consider talking to a trusted friend or professional"
                ]
            
            return suggestions
        
        # Fallback for simple stress level
        stress_level = float(analysis_result) if isinstance(analysis_result, (int, float)) else 0.5
        category = self._determine_stress_category(stress_level)
        return self.coping_strategies.get(category, self.coping_strategies["moderate"])
    
    def update_fusion_weights(self, new_weights: Dict[str, float]):
        """Update fusion weights based on performance or user preferences"""
        if sum(new_weights.values()) != 1.0:
            # Normalize weights
            total = sum(new_weights.values())
            self.fusion_weights = {k: v/total for k, v in new_weights.items()}
        else:
            self.fusion_weights = new_weights
        
        logger.info(f"Updated fusion weights: {self.fusion_weights}")
    
    def get_fusion_weights(self) -> Dict[str, float]:
        """Get current fusion weights"""
        return self.fusion_weights.copy()
