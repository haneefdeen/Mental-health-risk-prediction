#!/usr/bin/env python
"""
Evaluate MindScope AI models (text, image, fusion) on test datasets.
Writes metrics JSON for the admin dashboard.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from backend.model.text_analyzer import TextAnalyzer
from backend.model.image_analyzer import ImageAnalyzer
from backend.model.fusion_model import FusionModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)
METRICS_PATH = MODELS_DIR / "metrics.json"


def evaluate_text_stress_model() -> dict:
    """
    Evaluate text analyzer on Reddit stress dataset.
    Uses train/test split (80/20) for evaluation.
    """
    dataset_path = BASE_DIR / "datasets_archive3" / "stressed_anxious_cleaned.csv"
    if not dataset_path.exists():
        logger.warning(f"Text dataset not found at {dataset_path}")
        return {}

    try:
        df = pd.read_csv(dataset_path)
        if "Text" not in df.columns or "is_stressed/anxious" not in df.columns:
            logger.warning("Required columns not found in dataset")
            return {}

        # Split into train/test (80/20)
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        split_idx = int(len(df) * 0.8)
        test_df = df[split_idx:]

        texts = test_df["Text"].astype(str).tolist()
        labels = test_df["is_stressed/anxious"].astype(int).tolist()

        analyzer = TextAnalyzer()
        y_true = []
        y_pred = []

        logger.info(f"Evaluating text model on {len(texts)} test samples...")
        for i, (text, label) in enumerate(zip(texts, labels)):
            if not text.strip() or len(text.split()) < 3:
                continue
            try:
                result = analyzer.analyze(text)
                stress_score = float(result.get("stress_level", 0.5))
                pred = 1 if stress_score >= 0.5 else 0
                y_true.append(label)
                y_pred.append(pred)
            except Exception as e:
                logger.warning(f"Error analyzing text {i}: {e}")
                continue

        if not y_true:
            return {}

        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)

        accuracy = float((y_true_arr == y_pred_arr).mean())
        tp = float(((y_true_arr == 1) & (y_pred_arr == 1)).sum())
        fp = float(((y_true_arr == 0) & (y_pred_arr == 1)).sum())
        fn = float(((y_true_arr == 1) & (y_pred_arr == 0)).sum())
        tn = float(((y_true_arr == 0) & (y_pred_arr == 0)).sum())

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset": "reddit_stress",
            "num_samples": int(len(y_true_arr)),
            "accuracy": accuracy,
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "confusion_matrix": {
                "tp": int(tp),
                "fp": int(fp),
                "tn": int(tn),
                "fn": int(fn)
            }
        }
    except Exception as e:
        logger.error(f"Text evaluation failed: {e}")
        return {}


def evaluate_image_model() -> dict:
    """
    Evaluate image analyzer on FER dataset (if available).
    Simplified evaluation - checks if model produces varied predictions.
    """
    try:
        analyzer = ImageAnalyzer()
        
        # Check if custom weights are loaded
        has_custom_weights = analyzer.weights_path.exists()
        
        # Try to find test images
        fer_path = BASE_DIR / "datasets_archive1"
        if not fer_path.exists():
            logger.info("FER dataset not found - skipping image evaluation")
            return {}
        
        image_files = list(fer_path.rglob("*.jpg")) + list(fer_path.rglob("*.png"))
        if not image_files:
            logger.info("No image files found in FER dataset")
            return {}
        
        # Sample a subset for evaluation
        import random
        test_images = random.sample(image_files, min(100, len(image_files)))
        
        stress_scores = []
        emotions = []
        
        logger.info(f"Evaluating image model on {len(test_images)} test images...")
        for img_path in test_images:
            try:
                with open(img_path, 'rb') as f:
                    image_bytes = f.read()
                result = analyzer.analyze(image_bytes)
                stress_scores.append(result.get('stress_level', 0.5))
                emotions.append(result.get('dominant_emotion', 'neutral'))
            except Exception as e:
                logger.warning(f"Error analyzing image {img_path.name}: {e}")
                continue
        
        if not stress_scores:
            return {}
        
        # Calculate statistics
        stress_scores_arr = np.array(stress_scores)
        unique_emotions = len(set(emotions))
        stress_std = float(np.std(stress_scores_arr))
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset": "fer2013",
            "num_samples": len(stress_scores),
            "has_custom_weights": has_custom_weights,
            "unique_emotions_detected": unique_emotions,
            "stress_score_std": stress_std,
            "stress_score_mean": float(np.mean(stress_scores_arr)),
            "stress_score_min": float(np.min(stress_scores_arr)),
            "stress_score_max": float(np.max(stress_scores_arr)),
        }
    except Exception as e:
        logger.error(f"Image evaluation failed: {e}")
        return {}


def evaluate_fusion_model() -> dict:
    """
    Evaluate fusion model by combining text and image predictions.
    """
    try:
        fusion_model = FusionModel()
        text_analyzer = TextAnalyzer()
        image_analyzer = ImageAnalyzer()
        
        # Use text dataset for fusion evaluation
        dataset_path = BASE_DIR / "datasets_archive3" / "stressed_anxious_cleaned.csv"
        if not dataset_path.exists():
            return {}
        
        df = pd.read_csv(dataset_path)
        if "Text" not in df.columns or "is_stressed/anxious" not in df.columns:
            return {}
        
        # Sample a small subset for fusion evaluation
        test_df = df.sample(n=min(50, len(df)), random_state=42)
        
        y_true = []
        y_pred = []
        
        logger.info(f"Evaluating fusion model on {len(test_df)} samples...")
        for idx, row in test_df.iterrows():
            text = str(row.get("Text", ""))
            label = int(row.get("is_stressed/anxious", 0))
            
            if not text.strip():
                continue
            
            try:
                text_result = text_analyzer.analyze(text)
                # Simulate image result (in real scenario, would use actual image)
                image_result = {"stress_level": 0.5, "dominant_emotion": "neutral"}
                
                fusion_result = fusion_model.fuse_predictions(text_result, image_result, None)
                fused_stress = fusion_result.get("fused_stress_level", 0.5)
                pred = 1 if fused_stress >= 0.5 else 0
                
                y_true.append(label)
                y_pred.append(pred)
            except Exception as e:
                logger.warning(f"Error in fusion evaluation {idx}: {e}")
                continue
        
        if not y_true:
            return {}
        
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)
        
        accuracy = float((y_true_arr == y_pred_arr).mean())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "dataset": "fusion_reddit",
            "num_samples": int(len(y_true_arr)),
            "accuracy": accuracy,
        }
    except Exception as e:
        logger.error(f"Fusion evaluation failed: {e}")
        return {}


def main() -> None:
    """Evaluate all models and save metrics"""
    logger.info("Starting model evaluation...")
    
    all_metrics = {
        "text_model": evaluate_text_stress_model(),
        "image_model": evaluate_image_model(),
        "fusion_model": evaluate_fusion_model(),
        "evaluation_timestamp": datetime.utcnow().isoformat()
    }
    
    # Calculate overall accuracy if available
    accuracies = []
    if all_metrics["text_model"]:
        accuracies.append(all_metrics["text_model"].get("accuracy", 0))
    if all_metrics["fusion_model"]:
        accuracies.append(all_metrics["fusion_model"].get("accuracy", 0))
    
    if accuracies:
        all_metrics["overall_accuracy"] = float(np.mean(accuracies))
    
    METRICS_PATH.write_text(json.dumps(all_metrics, indent=2))
    logger.info(f"Saved metrics to {METRICS_PATH}")
    print(json.dumps(all_metrics, indent=2))


if __name__ == "__main__":
    main()





