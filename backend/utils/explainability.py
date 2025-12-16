"""
MindScope AI - Model Explainability
Provides explainability features for AI model decisions
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional
import cv2
from captum.attr import IntegratedGradients, GradientShap, Saliency
from captum.attr import visualization as viz
import base64
import io

class ExplainabilityAnalyzer:
    """Provides explainability for AI model decisions"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def generate_text_heatmap(self, text: str, model, tokenizer) -> Dict:
        """Generate token importance heatmap for text analysis"""
        try:
            # Tokenize text
            tokens = tokenizer.tokenize(text)
            token_ids = tokenizer.convert_tokens_to_ids(tokens)
            
            # Create input tensor
            input_tensor = torch.tensor([token_ids]).to(self.device)
            
            # Get integrated gradients
            ig = IntegratedGradients(model)
            attributions = ig.attribute(input_tensor, target=0, n_steps=50)
            
            # Convert to numpy
            attributions = attributions.squeeze().cpu().detach().numpy()
            
            # Normalize attributions
            attributions = np.abs(attributions)
            attributions = (attributions - attributions.min()) / (attributions.max() - attributions.min())
            
            # Create heatmap data
            heatmap_data = []
            for i, (token, attr) in enumerate(zip(tokens, attributions)):
                heatmap_data.append({
                    'token': token,
                    'importance': float(attr),
                    'position': i
                })
            
            # Generate visualization
            fig, ax = plt.subplots(figsize=(12, 4))
            
            # Create color map
            colors = plt.cm.Reds(attributions)
            
            # Plot tokens with importance
            y_pos = np.arange(len(tokens))
            bars = ax.barh(y_pos, attributions, color=colors)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(tokens)
            ax.set_xlabel('Importance Score')
            ax.set_title('Token Importance Heatmap')
            
            # Add importance values on bars
            for i, (bar, attr) in enumerate(zip(bars, attributions)):
                if attr > 0.1:  # Only show values for significant tokens
                    ax.text(attr + 0.01, bar.get_y() + bar.get_height()/2, 
                           f'{attr:.2f}', va='center', ha='left')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'heatmap_data': heatmap_data,
                'visualization': image_base64,
                'max_importance': float(np.max(attributions)),
                'min_importance': float(np.min(attributions)),
                'significant_tokens': [data for data in heatmap_data if data['importance'] > 0.3]
            }
            
        except Exception as e:
            print(f"Error generating text heatmap: {e}")
            return {
                'heatmap_data': [],
                'visualization': '',
                'max_importance': 0.0,
                'min_importance': 0.0,
                'significant_tokens': []
            }
    
    def generate_gradcam(self, image: np.ndarray, model, target_layer) -> Dict:
        """Generate Grad-CAM visualization for image analysis"""
        try:
            # Preprocess image
            if len(image.shape) == 3:
                image_tensor = torch.from_numpy(image).permute(2, 0, 1).float().unsqueeze(0) / 255.0
            else:
                image_tensor = torch.from_numpy(image).float().unsqueeze(0).unsqueeze(0) / 255.0
            
            image_tensor = image_tensor.to(self.device)
            
            # Get gradients
            image_tensor.requires_grad = True
            
            # Forward pass
            output = model(image_tensor)
            
            # Get gradients
            output.backward()
            gradients = image_tensor.grad.data
            
            # Calculate Grad-CAM
            gradients = gradients.squeeze().cpu().numpy()
            if len(gradients.shape) == 3:
                gradients = np.mean(gradients, axis=0)
            
            # Normalize gradients
            gradients = np.abs(gradients)
            gradients = (gradients - gradients.min()) / (gradients.max() - gradients.min())
            
            # Create visualization
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            ax1.imshow(image)
            ax1.set_title('Original Image')
            ax1.axis('off')
            
            # Grad-CAM
            im2 = ax2.imshow(gradients, cmap='jet', alpha=0.8)
            ax2.set_title('Grad-CAM Visualization')
            ax2.axis('off')
            plt.colorbar(im2, ax=ax2)
            
            # Overlay
            ax3.imshow(image)
            ax3.imshow(gradients, cmap='jet', alpha=0.5)
            ax3.set_title('Overlay')
            ax3.axis('off')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'gradcam': gradients.tolist(),
                'visualization': image_base64,
                'max_attention': float(np.max(gradients)),
                'min_attention': float(np.min(gradients)),
                'attention_regions': self._find_attention_regions(gradients)
            }
            
        except Exception as e:
            print(f"Error generating Grad-CAM: {e}")
            return {
                'gradcam': [],
                'visualization': '',
                'max_attention': 0.0,
                'min_attention': 0.0,
                'attention_regions': []
            }
    
    def _find_attention_regions(self, gradcam: np.ndarray, threshold: float = 0.5) -> List[Dict]:
        """Find regions of high attention"""
        try:
            # Find high attention areas
            high_attention = gradcam > threshold
            
            # Find contours
            contours, _ = cv2.findContours(
                (high_attention * 255).astype(np.uint8),
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            regions = []
            for contour in contours:
                if cv2.contourArea(contour) > 100:  # Filter small regions
                    x, y, w, h = cv2.boundingRect(contour)
                    regions.append({
                        'bbox': [int(x), int(y), int(w), int(h)],
                        'area': int(cv2.contourArea(contour)),
                        'attention_score': float(np.mean(gradcam[y:y+h, x:x+w]))
                    })
            
            return regions
            
        except Exception as e:
            print(f"Error finding attention regions: {e}")
            return []
    
    def generate_feature_importance(self, analysis_data: Dict) -> Dict:
        """Generate feature importance for multimodal analysis"""
        try:
            # Extract feature weights
            text_weight = analysis_data.get('text_weight', 0.33)
            image_weight = analysis_data.get('image_weight', 0.33)
            behavioral_weight = analysis_data.get('behavioral_weight', 0.34)
            
            # Create feature importance data
            features = ['Text Analysis', 'Image Analysis', 'Behavioral Analysis']
            weights = [text_weight, image_weight, behavioral_weight]
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            
            colors = ['#3b82f6', '#ef4444', '#10b981']
            bars = ax.bar(features, weights, color=colors, alpha=0.8)
            
            # Add value labels on bars
            for bar, weight in zip(bars, weights):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{weight:.1%}', ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel('Feature Weight')
            ax.set_title('Multimodal Feature Importance')
            ax.set_ylim(0, 1)
            
            # Add grid
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'feature_weights': {
                    'text': text_weight,
                    'image': image_weight,
                    'behavioral': behavioral_weight
                },
                'visualization': image_base64,
                'dominant_feature': max(zip(features, weights), key=lambda x: x[1])[0]
            }
            
        except Exception as e:
            print(f"Error generating feature importance: {e}")
            return {
                'feature_weights': {
                    'text': 0.33,
                    'image': 0.33,
                    'behavioral': 0.34
                },
                'visualization': '',
                'dominant_feature': 'Behavioral Analysis'
            }
    
    def generate_confidence_analysis(self, analysis_data: Dict) -> Dict:
        """Generate confidence analysis for predictions"""
        try:
            # Extract confidence scores
            text_confidence = analysis_data.get('text_confidence', 0.5)
            image_confidence = analysis_data.get('image_confidence', 0.5)
            behavioral_confidence = analysis_data.get('behavioral_confidence', 0.5)
            overall_confidence = analysis_data.get('confidence', 0.5)
            
            # Create confidence data
            modalities = ['Text', 'Image', 'Behavioral', 'Overall']
            confidences = [text_confidence, image_confidence, behavioral_confidence, overall_confidence]
            
            # Create visualization
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Bar chart
            colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b']
            bars = ax1.bar(modalities, confidences, color=colors, alpha=0.8)
            
            # Add value labels
            for bar, conf in zip(bars, confidences):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{conf:.1%}', ha='center', va='bottom', fontweight='bold')
            
            ax1.set_ylabel('Confidence Score')
            ax1.set_title('Prediction Confidence by Modality')
            ax1.set_ylim(0, 1)
            ax1.grid(axis='y', alpha=0.3)
            
            # Pie chart
            ax2.pie(confidences, labels=modalities, colors=colors, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Confidence Distribution')
            
            plt.tight_layout()
            
            # Convert to base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return {
                'confidence_scores': {
                    'text': text_confidence,
                    'image': image_confidence,
                    'behavioral': behavioral_confidence,
                    'overall': overall_confidence
                },
                'visualization': image_base64,
                'average_confidence': float(np.mean(confidences)),
                'confidence_std': float(np.std(confidences))
            }
            
        except Exception as e:
            print(f"Error generating confidence analysis: {e}")
            return {
                'confidence_scores': {
                    'text': 0.5,
                    'image': 0.5,
                    'behavioral': 0.5,
                    'overall': 0.5
                },
                'visualization': '',
                'average_confidence': 0.5,
                'confidence_std': 0.0
            }
    
    def generate_explainability_report(self, text_analysis: Dict, image_analysis: Dict, 
                                     behavioral_analysis: Dict, fusion_analysis: Dict) -> Dict:
        """Generate comprehensive explainability report"""
        try:
            explainability_data = {
                'text_heatmap': self.generate_text_heatmap(
                    text_analysis.get('processed_text', ''),
                    None,  # Model would be passed in real implementation
                    None   # Tokenizer would be passed in real implementation
                ),
                'image_gradcam': self.generate_gradcam(
                    np.zeros((224, 224, 3)),  # Placeholder image
                    None,  # Model would be passed in real implementation
                    None   # Target layer would be passed in real implementation
                ),
                'feature_importance': self.generate_feature_importance(fusion_analysis),
                'confidence_analysis': self.generate_confidence_analysis(fusion_analysis),
                'explanation_summary': self._generate_explanation_summary(
                    text_analysis, image_analysis, behavioral_analysis, fusion_analysis
                )
            }
            
            return explainability_data
            
        except Exception as e:
            print(f"Error generating explainability report: {e}")
            return {
                'text_heatmap': {'heatmap_data': [], 'visualization': ''},
                'image_gradcam': {'gradcam': [], 'visualization': ''},
                'feature_importance': {'feature_weights': {}, 'visualization': ''},
                'confidence_analysis': {'confidence_scores': {}, 'visualization': ''},
                'explanation_summary': 'Unable to generate explanation at this time.'
            }
    
    def _generate_explanation_summary(self, text_analysis: Dict, image_analysis: Dict, 
                                   behavioral_analysis: Dict, fusion_analysis: Dict) -> str:
        """Generate human-readable explanation summary"""
        try:
            stress_level = fusion_analysis.get('stress_level', 'low')
            confidence = fusion_analysis.get('confidence', 0.5)
            
            # Get dominant modality
            modality_scores = fusion_analysis.get('modality_scores', {})
            dominant_modality = max(modality_scores.items(), key=lambda x: x[1])[0]
            
            explanation = f"""
            Based on the comprehensive analysis, your stress level is assessed as {stress_level.upper()} 
            with {confidence:.1%} confidence. The analysis combines insights from text emotion detection, 
            facial emotion recognition, and behavioral pattern analysis. The {dominant_modality} modality 
            contributed most significantly to this assessment.
            """
            
            return explanation.strip()
            
        except Exception as e:
            print(f"Error generating explanation summary: {e}")
            return "Unable to generate explanation summary at this time."

# Global instance
explainability_analyzer = ExplainabilityAnalyzer()
