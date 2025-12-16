#!/usr/bin/env python3
"""
MindScope AI Training Script
Trains models using real datasets: FER2013, DAIC-WOZ, Reddit, Dreaddit
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model.text_trainer import TextAnalyzerTrainer
from model.image_trainer import ImageAnalyzerTrainer
# Import local datasets module (not HuggingFace datasets)
import importlib.util
dataset_manager_path = os.path.join(os.path.dirname(__file__), 'datasets', 'dataset_manager.py')
if os.path.exists(dataset_manager_path):
    spec = importlib.util.spec_from_file_location("dataset_manager", dataset_manager_path)
    dataset_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dataset_manager_module)
    DatasetManager = dataset_manager_module.DatasetManager
else:
    DatasetManager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_all_models(quick: bool = True, max_samples: int = 2000, epochs: int = 1):
    """Train all models using real datasets.

    quick: when True, use CPU‑friendly lightweight training settings.
    max_samples: maximum samples per dataset in quick mode.
    epochs: number of epochs (quick mode usually 1).
    """
    logger.info("🚀 Starting MindScope AI Model Training")
    logger.info("=" * 50)
    
    # Initialize dataset manager (optional - for summary only)
    if DatasetManager:
        try:
            dataset_manager = DatasetManager()
            dataset_summary = dataset_manager.get_dataset_summary()
            logger.info(f"✅ FER2013: {dataset_summary['fer2013'].get('total_images', 0)} images")
            logger.info(f"✅ DAIC-WOZ: {dataset_summary['daic_woz'].get('total_transcripts', 0)} transcripts")
            logger.info(f"✅ Reddit Stress: {dataset_summary['reddit_stress'].get('total_posts', 0)} posts")
            logger.info(f"✅ Dreaddit: {dataset_summary['dreaddit'].get('total_posts', 0)} posts")
        except Exception as e:
            logger.warning(f"Could not load dataset summary: {e}")
    else:
        logger.info("📊 Starting training with direct dataset loading...")
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # 1. Train Text Models
    logger.info("\n🧠 Training Text Analysis Models...")
    logger.info("-" * 30)
    
    text_trainer = TextAnalyzerTrainer()
    
    # Train stress model on Reddit data
    reddit_path = "datasets_archive3/stressed_anxious_cleaned.csv"
    if os.path.exists(reddit_path):
        if quick:
            logger.info("📝 Training stress detection model on Reddit data (QUICK MODE)...")
        else:
            logger.info("📝 Training stress detection model on Reddit data (full mode)...")
        stress_trainer = text_trainer.train_stress_model(
            reddit_path,
            "models/stress_model",
            quick_mode=quick,
            max_samples=max_samples,
        )
        if stress_trainer:
            logger.info("✅ Stress model training completed!")
        else:
            logger.error("❌ Stress model training failed!")
    else:
        logger.error(f"❌ Reddit dataset not found at {reddit_path}")
    
    # Train depression model on DAIC-WOZ data
    daic_woz_path = "datasets_archive2"
    if os.path.exists(daic_woz_path):
        if quick:
            logger.info("📝 Training depression detection model on DAIC-WOZ data (QUICK MODE)...")
        else:
            logger.info("📝 Training depression detection model on DAIC-WOZ data (full mode)...")
        depression_trainer = text_trainer.train_depression_model(
            daic_woz_path,
            "models/depression_model",
            quick_mode=quick,
            max_samples=max_samples,
        )
        if depression_trainer:
            logger.info("✅ Depression model training completed!")
        else:
            logger.error("❌ Depression model training failed!")
    else:
        logger.error(f"❌ DAIC-WOZ dataset not found at {daic_woz_path}")
    
    # 2. Train Image Model
    logger.info("\n🖼️ Training Image Analysis Model...")
    logger.info("-" * 30)
    
    image_trainer = ImageAnalyzerTrainer()
    
    # Train emotion model on FER2013 data
    fer2013_path = "datasets_archive1"
    if os.path.exists(fer2013_path):
        if quick:
            logger.info("🖼️ Training facial emotion recognition model on FER2013 data (QUICK MODE)...")
        else:
            logger.info("🖼️ Training facial emotion recognition model on FER2013 data (full mode)...")
        emotion_model = image_trainer.train_model(
            fer2013_path,
            "models/emotion_model",
            epochs=epochs,
            quick_mode=quick,
            max_samples=max_samples,
        )
        if emotion_model:
            logger.info("✅ Emotion model training completed!")
        else:
            logger.error("❌ Emotion model training failed!")
    else:
        logger.error(f"❌ FER2013 dataset not found at {fer2013_path}")
    
    # 3. Create Model Summary
    logger.info("\n📋 Training Summary...")
    logger.info("-" * 30)
    
    models_created = []
    model_dirs = ["models/stress_model", "models/depression_model", "models/emotion_model"]
    
    for model_dir in model_dirs:
        if os.path.exists(model_dir):
            models_created.append(model_dir)
            logger.info(f"✅ {model_dir} - Ready")
        else:
            logger.warning(f"⚠️ {model_dir} - Not found")
    
    logger.info(f"\n🎉 Training completed! {len(models_created)} models ready for use.")
    logger.info("=" * 50)
    
    return models_created


def train_specific_model(model_type: str, quick: bool = True, max_samples: int = 2000, epochs: int = 1):
    """Train a specific model type."""
    
    if model_type == "text":
        logger.info("🧠 Training text models only...")
        if quick:
            logger.info("Quick mode enabled: limited samples, 1 epoch, frozen backbone.")
        text_trainer = TextAnalyzerTrainer()
        
        # Train stress model
        reddit_path = "datasets_archive3/stressed_anxious_cleaned.csv"
        if os.path.exists(reddit_path):
            text_trainer.train_stress_model(
                reddit_path,
                "models/stress_model",
                quick_mode=quick,
                max_samples=max_samples,
            )
        
        # Train depression model
        daic_woz_path = "datasets_archive2"
        if os.path.exists(daic_woz_path):
            text_trainer.train_depression_model(
                daic_woz_path,
                "models/depression_model",
                quick_mode=quick,
                max_samples=max_samples,
            )
    
    elif model_type == "image":
        logger.info("🖼️ Training image model only...")
        if quick:
            logger.info("Quick mode enabled: limited samples, frozen ResNet backbone.")
        image_trainer = ImageAnalyzerTrainer()
        
        fer2013_path = "datasets_archive1"
        if os.path.exists(fer2013_path):
            image_trainer.train_model(
                fer2013_path,
                "models/emotion_model",
                epochs=epochs,
                quick_mode=quick,
                max_samples=max_samples,
            )
    
    elif model_type == "fusion":
        # Current FusionModel is rule-based; no heavy training implemented yet.
        logger.info("🔗 Fusion model currently uses rule-based fusion; no training performed.")
    else:
        logger.error(f"Unknown model type: {model_type}")

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train MindScope AI models using real datasets")
    parser.add_argument(
        "--model",
        choices=["all", "text", "image", "fusion"],
        default="all",
        help="Which model(s) to train",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use quick CPU‑friendly training mode (small subsets, 1 epoch, frozen backbones)",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=2000,
        help="Maximum samples to use per dataset in quick mode",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=1,
        help="Number of training epochs (quick mode usually 1)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.model == "all":
            train_all_models(quick=args.quick, max_samples=args.max_samples, epochs=args.epochs)
        else:
            train_specific_model(
                args.model,
                quick=args.quick,
                max_samples=args.max_samples,
                epochs=args.epochs,
            )
            
    except KeyboardInterrupt:
        logger.info("\n⏹️ Training interrupted by user")
    except Exception as e:
        logger.error(f"❌ Training failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
