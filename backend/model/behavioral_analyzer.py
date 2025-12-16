import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class BehavioralAnalyzer:
    """Behavioral fingerprinting system for emoji usage and posting frequency"""
    
    def __init__(self):
        # Emoji categories for emotion analysis
        self.emoji_categories = {
            "happy": ["😊", "😄", "😁", "🥰", "😍", "🤗", "😘", "🙂", "😃", "😆", "🤩", "😇"],
            "sad": ["😢", "😭", "😔", "😞", "😟", "😕", "😰", "😨", "💔", "😿", "😥", "😪"],
            "anxious": ["😰", "😨", "😱", "😳", "😬", "😓", "😵", "🤯", "😵‍💫", "😮‍💨", "😰", "😨"],
            "angry": ["😠", "😡", "🤬", "😤", "😾", "👿", "💢", "🔥", "😈", "👹"],
            "neutral": ["😐", "😑", "😶", "🤔", "😏", "🙃", "😒", "😴", "🤨", "🧐"],
            "excited": ["🤩", "😆", "😃", "🎉", "🎊", "✨", "🌟", "💫", "🚀", "⚡"]
        }
        
        # Posting frequency patterns
        self.frequency_patterns = {
            "low": {"min": 0.1, "max": 0.5},      # Less than 0.5 posts per day
            "moderate": {"min": 0.5, "max": 1.5},  # 0.5-1.5 posts per day
            "high": {"min": 1.5, "max": 3.0},      # 1.5-3.0 posts per day
            "excessive": {"min": 3.0, "max": 10.0} # More than 3 posts per day
        }
        
        # Time-based patterns
        self.time_patterns = {
            "early_morning": {"start": 5, "end": 9},    # 5 AM - 9 AM
            "morning": {"start": 9, "end": 12},         # 9 AM - 12 PM
            "afternoon": {"start": 12, "end": 17},      # 12 PM - 5 PM
            "evening": {"start": 17, "end": 21},        # 5 PM - 9 PM
            "night": {"start": 21, "end": 24},          # 9 PM - 12 AM
            "late_night": {"start": 0, "end": 5}        # 12 AM - 5 AM
        }
    
    def analyze(self, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavioral patterns for stress/anxiety indicators"""
        try:
            # Extract components
            emoji_usage = behavioral_data.get("emoji_usage", {})
            posting_frequency = behavioral_data.get("posting_frequency", 0.0)
            posts_timeline = behavioral_data.get("posts_timeline", [])
            
            # Analyze emoji patterns
            emoji_analysis = self._analyze_emoji_patterns(emoji_usage)
            
            # Analyze posting frequency
            frequency_analysis = self._analyze_posting_frequency(posting_frequency)
            
            # Analyze temporal patterns
            temporal_analysis = self._analyze_temporal_patterns(posts_timeline)
            
            # Calculate behavioral stress score
            behavioral_score = self._calculate_behavioral_stress_score(
                emoji_analysis, frequency_analysis, temporal_analysis
            )
            
            # Generate insights
            insights = self._generate_behavioral_insights(
                emoji_analysis, frequency_analysis, temporal_analysis
            )
            
            return {
                "emoji_analysis": emoji_analysis,
                "frequency_analysis": frequency_analysis,
                "temporal_analysis": temporal_analysis,
                "behavioral_score": behavioral_score,
                "insights": insights,
                "confidence": self._calculate_confidence(emoji_analysis, frequency_analysis),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Behavioral analysis error: {str(e)}")
            return {
                "emoji_analysis": {"dominant_emotion": "neutral", "stress_indicator": 0.5},
                "frequency_analysis": {"pattern": "moderate", "stress_indicator": 0.5},
                "temporal_analysis": {"pattern": "normal", "stress_indicator": 0.5},
                "behavioral_score": 0.5,
                "insights": ["Unable to analyze behavioral patterns"],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _analyze_emoji_patterns(self, emoji_usage: Dict[str, int]) -> Dict[str, Any]:
        """Analyze emoji usage patterns"""
        total_emojis = sum(emoji_usage.values())
        
        if total_emojis == 0:
            return {
                "dominant_emotion": "neutral",
                "stress_indicator": 0.5,
                "emoji_diversity": 0.0,
                "analysis": "No emoji usage detected"
            }
        
        # Calculate emotion ratios
        emotion_ratios = {}
        for emotion, emojis in self.emoji_categories.items():
            emotion_count = emoji_usage.get(emotion, 0)
            emotion_ratios[emotion] = emotion_count / total_emojis
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_ratios, key=emotion_ratios.get)
        
        # Calculate stress indicator
        negative_emotions = ["sad", "anxious", "angry"]
        stress_indicator = sum(emotion_ratios[emotion] for emotion in negative_emotions)
        
        # Calculate emoji diversity
        emoji_diversity = len([ratio for ratio in emotion_ratios.values() if ratio > 0]) / len(emotion_ratios)
        
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_ratios": emotion_ratios,
            "stress_indicator": stress_indicator,
            "emoji_diversity": emoji_diversity,
            "total_emojis": total_emojis,
            "analysis": f"Dominant emotion: {dominant_emotion}, Stress level: {stress_indicator:.2f}"
        }
    
    def _analyze_posting_frequency(self, frequency: float) -> Dict[str, Any]:
        """Analyze posting frequency patterns"""
        # Determine frequency pattern
        pattern = "moderate"
        stress_indicator = 0.5
        
        if frequency < self.frequency_patterns["low"]["max"]:
            pattern = "low"
            stress_indicator = 0.3  # Low frequency might indicate withdrawal
        elif frequency < self.frequency_patterns["moderate"]["max"]:
            pattern = "moderate"
            stress_indicator = 0.5
        elif frequency < self.frequency_patterns["high"]["max"]:
            pattern = "high"
            stress_indicator = 0.7  # High frequency might indicate stress
        else:
            pattern = "excessive"
            stress_indicator = 0.9  # Excessive posting might indicate crisis
        
        return {
            "pattern": pattern,
            "frequency": frequency,
            "stress_indicator": stress_indicator,
            "analysis": f"Posting pattern: {pattern} ({frequency:.2f} posts/day)"
        }
    
    def _analyze_temporal_patterns(self, posts_timeline: List[Dict]) -> Dict[str, Any]:
        """Analyze temporal posting patterns"""
        if not posts_timeline:
            return {
                "pattern": "normal",
                "stress_indicator": 0.5,
                "analysis": "No temporal data available"
            }
        
        # Analyze posting times
        time_distribution = {period: 0 for period in self.time_patterns.keys()}
        
        for post in posts_timeline:
            timestamp = datetime.fromisoformat(post["timestamp"])
            hour = timestamp.hour
            
            for period, times in self.time_patterns.items():
                if times["start"] <= hour < times["end"] or (times["start"] > times["end"] and (hour >= times["start"] or hour < times["end"])):
                    time_distribution[period] += 1
        
        # Determine pattern
        total_posts = len(posts_timeline)
        if total_posts == 0:
            return {"pattern": "normal", "stress_indicator": 0.5}
        
        # Check for concerning patterns
        late_night_ratio = time_distribution["late_night"] / total_posts
        early_morning_ratio = time_distribution["early_morning"] / total_posts
        
        stress_indicator = 0.5
        pattern = "normal"
        
        if late_night_ratio > 0.3:
            pattern = "late_night_posting"
            stress_indicator = 0.8  # Late night posting indicates sleep issues/stress
        elif early_morning_ratio > 0.4:
            pattern = "early_morning_posting"
            stress_indicator = 0.6  # Early morning posting might indicate anxiety
        
        return {
            "pattern": pattern,
            "time_distribution": time_distribution,
            "stress_indicator": stress_indicator,
            "analysis": f"Temporal pattern: {pattern}"
        }
    
    def _calculate_behavioral_stress_score(self, emoji_analysis: Dict, frequency_analysis: Dict, temporal_analysis: Dict) -> float:
        """Calculate overall behavioral stress score"""
        # Weighted combination of different factors
        emoji_stress = emoji_analysis.get("stress_indicator", 0.5)
        frequency_stress = frequency_analysis.get("stress_indicator", 0.5)
        temporal_stress = temporal_analysis.get("stress_indicator", 0.5)
        
        # Weighted average
        behavioral_score = (emoji_stress * 0.4) + (frequency_stress * 0.3) + (temporal_stress * 0.3)
        
        return min(1.0, max(0.0, behavioral_score))
    
    def _generate_behavioral_insights(self, emoji_analysis: Dict, frequency_analysis: Dict, temporal_analysis: Dict) -> List[str]:
        """Generate behavioral insights"""
        insights = []
        
        # Emoji insights
        dominant_emotion = emoji_analysis.get("dominant_emotion", "neutral")
        if dominant_emotion in ["sad", "anxious", "angry"]:
            insights.append(f"Emoji usage suggests {dominant_emotion} emotional state")
        
        # Frequency insights
        pattern = frequency_analysis.get("pattern", "moderate")
        if pattern == "excessive":
            insights.append("High posting frequency may indicate stress or crisis")
        elif pattern == "low":
            insights.append("Low posting frequency might indicate social withdrawal")
        
        # Temporal insights
        temporal_pattern = temporal_analysis.get("pattern", "normal")
        if temporal_pattern == "late_night_posting":
            insights.append("Late night posting patterns suggest sleep disturbances")
        
        return insights
    
    def _calculate_confidence(self, emoji_analysis: Dict, frequency_analysis: Dict) -> float:
        """Calculate confidence in behavioral analysis"""
        # Higher confidence with more data
        emoji_diversity = emoji_analysis.get("emoji_diversity", 0.0)
        total_emojis = emoji_analysis.get("total_emojis", 0)
        
        # Confidence based on data availability
        if total_emojis > 10:
            confidence = 0.8
        elif total_emojis > 5:
            confidence = 0.6
        elif total_emojis > 0:
            confidence = 0.4
        else:
            confidence = 0.2
        
        return confidence
