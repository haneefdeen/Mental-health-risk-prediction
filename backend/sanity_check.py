#!/usr/bin/env python3
"""
Sanity Check Script for MindScope AI Models
Tests predictions on real dataset examples to verify models are not collapsed.
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import torch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.model.text_analyzer import TextAnalyzer
from backend.model.image_analyzer import ImageAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_text_predictions():
    """Test text model on Reddit stress dataset examples"""
    logger.info("=" * 60)
    logger.info("Testing Text Model Predictions")
    logger.info("=" * 60)
    
    # Load dataset
    dataset_path = Path("../datasets_archive3/stressed_anxious_cleaned.csv")
    if not dataset_path.exists():
        logger.error(f"Dataset not found at {dataset_path}")
        return False
    
    try:
        df = pd.read_csv(dataset_path)
        logger.info(f"Loaded dataset with {len(df)} examples")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        return False
    
    # Sample examples from each class
    stressed_samples = df[df['is_stressed/anxious'] == 1].head(10)
    not_stressed_samples = df[df['is_stressed/anxious'] == 0].head(10)
    
    logger.info(f"Testing {len(stressed_samples)} stressed examples and {len(not_stressed_samples)} non-stressed examples")
    
    # Initialize analyzer
    text_analyzer = TextAnalyzer()
    
    correct_predictions = 0
    total_predictions = 0
    predictions_by_class = {"stressed": [], "not_stressed": []}
    
    # Test stressed examples
    logger.info("\n--- Testing Stressed Examples ---")
    for idx, row in stressed_samples.iterrows():
        text = str(row.get('Text', ''))
        if len(text.split()) < 5:  # Skip very short texts
            continue
        
        try:
            result = text_analyzer.analyze(text)
            stress_score = result.get('stress_level', 0.5)
            stress_prob = result.get('dataset_stress_probability', stress_score)
            
            # Consider prediction correct if stress_score > 0.5
            predicted_stressed = stress_score > 0.5 or (stress_prob and stress_prob > 0.5)
            
            predictions_by_class["stressed"].append({
                "text_id": idx,
                "true_label": "stressed",
                "predicted_stressed": predicted_stressed,
                "stress_score": stress_score,
                "stress_prob": stress_prob,
                "emotion": result.get('primary_emotion', 'unknown')
            })
            
            if predicted_stressed:
                correct_predictions += 1
            total_predictions += 1
            
            logger.info(f"  Example {idx}: stress_score={stress_score:.3f}, predicted={'stressed' if predicted_stressed else 'not_stressed'}")
        except Exception as e:
            logger.warning(f"  Failed to analyze example {idx}: {e}")
    
    # Test non-stressed examples
    logger.info("\n--- Testing Non-Stressed Examples ---")
    for idx, row in not_stressed_samples.iterrows():
        text = str(row.get('Text', ''))
        if len(text.split()) < 5:
            continue
        
        try:
            result = text_analyzer.analyze(text)
            stress_score = result.get('stress_level', 0.5)
            stress_prob = result.get('dataset_stress_probability', stress_score)
            
            predicted_stressed = stress_score > 0.5 or (stress_prob and stress_prob > 0.5)
            
            predictions_by_class["not_stressed"].append({
                "text_id": idx,
                "true_label": "not_stressed",
                "predicted_stressed": predicted_stressed,
                "stress_score": stress_score,
                "stress_prob": stress_prob,
                "emotion": result.get('primary_emotion', 'unknown')
            })
            
            if not predicted_stressed:
                correct_predictions += 1
            total_predictions += 1
            
            logger.info(f"  Example {idx}: stress_score={stress_score:.3f}, predicted={'stressed' if predicted_stressed else 'not_stressed'}")
        except Exception as e:
            logger.warning(f"  Failed to analyze example {idx}: {e}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Text Model Sanity Check Results")
    logger.info("=" * 60)
    logger.info(f"Total predictions: {total_predictions}")
    logger.info(f"Correct predictions: {correct_predictions}")
    if total_predictions > 0:
        accuracy = correct_predictions / total_predictions
        logger.info(f"Accuracy: {accuracy:.2%}")
        
        # Check if predictions are all the same
        all_stressed = all(p["predicted_stressed"] for p in predictions_by_class["stressed"] + predictions_by_class["not_stressed"])
        all_not_stressed = all(not p["predicted_stressed"] for p in predictions_by_class["stressed"] + predictions_by_class["not_stressed"])
        
        if all_stressed or all_not_stressed:
            logger.warning("⚠️  WARNING: All predictions are the same! Model may be collapsed.")
            return False
        else:
            logger.info("✅ Predictions vary across examples - model is not collapsed.")
        
        if accuracy >= 0.5:
            logger.info(f"✅ Accuracy ({accuracy:.2%}) meets minimum threshold (50%)")
            return True
        else:
            logger.warning(f"⚠️  Accuracy ({accuracy:.2%}) is below 50% threshold")
            return False
    else:
        logger.error("No predictions made!")
        return False


def test_image_predictions():
    """Test image model on FER dataset examples (if available)"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Image Model Predictions")
    logger.info("=" * 60)
    
    try:
        image_analyzer = ImageAnalyzer()
        logger.info("✅ Image analyzer initialized successfully")
        logger.info(f"   Device: {image_analyzer.device}")
        logger.info(f"   Model in eval mode: {not image_analyzer.model.training}")
        
        # Check if custom weights are loaded
        if image_analyzer.weights_path.exists():
            logger.info(f"✅ Custom FER weights found at {image_analyzer.weights_path}")
        else:
            logger.info("ℹ️  Using pre-trained ResNet50 (no fine-tuned weights)")
        
        # Try to load FER dataset images if available
        fer_path = Path("../datasets_archive1")
        if fer_path.exists():
            logger.info(f"📁 FER dataset found at {fer_path}")
            # Look for image files
            image_files = list(fer_path.rglob("*.jpg")) + list(fer_path.rglob("*.png"))
            if image_files:
                logger.info(f"   Found {len(image_files)} image files")
                # Test a few random images
                import random
                test_images = random.sample(image_files, min(5, len(image_files)))
                logger.info(f"   Testing {len(test_images)} sample images...")
                
                predictions = []
                for img_path in test_images:
                    try:
                        with open(img_path, 'rb') as f:
                            image_bytes = f.read()
                        result = image_analyzer.analyze(image_bytes)
                        stress_score = result.get('stress_level', 0.5)
                        dominant_emotion = result.get('dominant_emotion', 'unknown')
                        predictions.append({
                            'file': img_path.name,
                            'stress_score': stress_score,
                            'emotion': dominant_emotion
                        })
                        logger.info(f"   {img_path.name}: stress={stress_score:.3f}, emotion={dominant_emotion}")
                    except Exception as e:
                        logger.warning(f"   Failed to analyze {img_path.name}: {e}")
                
                if predictions:
                    avg_stress = sum(p['stress_score'] for p in predictions) / len(predictions)
                    logger.info(f"   Average stress score: {avg_stress:.3f}")
                    if len(set(p['stress_score'] for p in predictions)) > 1:
                        logger.info("✅ Predictions vary across images - model is not collapsed.")
                    else:
                        logger.warning("⚠️  All predictions have similar stress scores.")
        else:
            logger.info("ℹ️  FER dataset not found - skipping image testing")
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize image analyzer: {e}")
        return False


def main():
    """Run all sanity checks"""
    logger.info("🧪 Starting MindScope AI Sanity Checks")
    logger.info("=" * 60)
    
    results = {
        "text": False,
        "image": False,
    }
    
    # Test text model
    results["text"] = test_text_predictions()
    
    # Test image model
    results["image"] = test_image_predictions()
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("Sanity Check Summary")
    logger.info("=" * 60)
    logger.info(f"Text Model: {'✅ PASS' if results['text'] else '❌ FAIL'}")
    logger.info(f"Image Model: {'✅ PASS' if results['image'] else '❌ FAIL'}")
    
    if all(results.values()):
        logger.info("\n✅ All sanity checks passed!")
        return 0
    else:
        logger.warning("\n⚠️  Some sanity checks failed. Review the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

