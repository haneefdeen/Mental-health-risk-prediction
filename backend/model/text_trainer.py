import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Shared label configuration for text models (kept in one place)
# ---------------------------------------------------------------------------

# Reddit stress dataset is binary (0 = not stressed/anxious, 1 = stressed/anxious)
STRESS_LABELS = ["no_stress", "high"]  # Maps dataset labels 0 -> no_stress, 1 -> high stress
STRESS_LABEL2ID = {name: i for i, name in enumerate(STRESS_LABELS)}
STRESS_ID2LABEL = {i: name for name, i in STRESS_LABEL2ID.items()}

# DAIC‑WOZ depression labels (0 = not depressed, 1 = depressed)
DEPRESSION_LABELS = ["no_depression", "depression"]
DEPRESSION_LABEL2ID = {name: i for i, name in enumerate(DEPRESSION_LABELS)}
DEPRESSION_ID2LABEL = {i: name for name, i in DEPRESSION_LABEL2ID.items()}

class RedditStressDataset(Dataset):
    """Dataset class for Reddit stress/anxiety data"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class DAICWOZDataset(Dataset):
    """Dataset class for DAIC-WOZ depression data"""
    
    def __init__(self, texts, labels, tokenizer, max_length=512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class TextAnalyzerTrainer:
    """Trainer for text analysis models using real datasets"""
    
    def __init__(self, model_name="distilbert-base-uncased"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def load_reddit_stress_data(self, csv_path: str) -> tuple:
        """Load Reddit stress/anxiety dataset"""
        try:
            df = pd.read_csv(csv_path)
            
            # Clean and prepare data
            texts = df['Text'].fillna('').astype(str).tolist()
            labels = df['is_stressed/anxious'].astype(int).tolist()
            
            # Filter out very short texts
            filtered_texts = []
            filtered_labels = []
            for text, label in zip(texts, labels):
                if len(text.split()) >= 5:  # At least 5 words
                    filtered_texts.append(text)
                    filtered_labels.append(label)
            
            logger.info(f"Loaded {len(filtered_texts)} Reddit posts")
            logger.info(f"Stress distribution: {np.bincount(filtered_labels)}")
            
            return filtered_texts, filtered_labels
            
        except Exception as e:
            logger.error(f"Error loading Reddit data: {str(e)}")
            return [], []
    
    def load_daic_woz_data(self, data_dir: str) -> tuple:
        """Load DAIC-WOZ depression dataset"""
        try:
            import glob
            
            texts = []
            labels = []
            
            # Load all transcript files
            transcript_files = glob.glob(os.path.join(data_dir, "*.csv"))
            
            for file_path in transcript_files:
                df = pd.read_csv(file_path, sep='\t')
                
                # Combine participant responses
                participant_texts = df[df['speaker'] == 'Participant']['value'].fillna('').astype(str)
                
                # Create depression labels (simplified - you might want to use actual depression scores)
                # For now, we'll use conversation length as a proxy
                combined_text = ' '.join(participant_texts)
                if len(combined_text.split()) > 50:  # Longer conversations might indicate depression
                    label = 1
                else:
                    label = 0
                
                if len(combined_text.split()) >= 10:  # At least 10 words
                    texts.append(combined_text)
                    labels.append(label)
            
            logger.info(f"Loaded {len(texts)} DAIC-WOZ conversations")
            logger.info(f"Depression distribution: {np.bincount(labels)}")
            
            return texts, labels
            
        except Exception as e:
            logger.error(f"Error loading DAIC-WOZ data: {str(e)}")
            return [], []
    
    def train_stress_model(self, reddit_csv_path: str, output_dir: str = "models/stress_model", 
                          quick_mode: bool = True, max_samples: int = 2000):
        """Train DistilBERT on Reddit stress data - lightweight mode by default"""
        try:
            # Load data
            texts, labels = self.load_reddit_stress_data(reddit_csv_path)
            
            if len(texts) == 0:
                logger.error("No data loaded for training")
                return None
            
            # Quick mode: sample limited data
            if quick_mode and len(texts) > max_samples:
                logger.info(f"Quick mode: Sampling {max_samples} from {len(texts)} examples")
                indices = np.random.choice(len(texts), max_samples, replace=False)
                texts = [texts[i] for i in indices]
                labels = [labels[i] for i in indices]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Create datasets
            train_dataset = RedditStressDataset(train_texts, train_labels, self.tokenizer)
            val_dataset = RedditStressDataset(val_texts, val_labels, self.tokenizer)
            
            # Initialize model (binary stress classification)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=len(STRESS_LABELS),
                problem_type="single_label_classification",
                id2label=STRESS_ID2LABEL,
                label2id=STRESS_LABEL2ID,
            )
            
            # Freeze backbone in quick mode (only train classification head)
            if quick_mode:
                logger.info("Quick mode: Freezing transformer layers, training only classification head")
                for param in model.distilbert.parameters():
                    param.requires_grad = False
                # Only train classification head
                for param in model.classifier.parameters():
                    param.requires_grad = True
            
            # Training arguments - lightweight vs full mode
            num_epochs = 1 if quick_mode else 3
            batch_size = 16
            warmup_steps = min(100, len(train_dataset) // batch_size // 4)  # Adaptive warmup
            
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                warmup_steps=warmup_steps,
                weight_decay=0.01,
                logging_dir=f"{output_dir}/logs",
                logging_steps=50,
                evaluation_strategy="epoch",
                save_strategy="no",  # avoid best-model bookkeeping to keep things simple/CPU-friendly
                load_best_model_at_end=False,
                fp16=False,  # CPU-friendly
                dataloader_num_workers=0,  # CPU-friendly
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=self.tokenizer,
            )
            
            # Train model
            logger.info("Starting training...")
            trainer.train()
            
            # Ensure output directory exists and save model/tokenizer
            os.makedirs(output_dir, exist_ok=True)
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            
            # Evaluate
            eval_results = trainer.evaluate()
            acc = eval_results.get("eval_accuracy")
            logger.info(f"Training evaluation metrics: {eval_results}")
            if acc is not None:
                logger.info(f"Training completed. Final accuracy: {acc:.4f}")
            
            return trainer
            
        except Exception as e:
            logger.error(f"Error training stress model: {str(e)}")
            return None
    
    def train_depression_model(self, daic_woz_dir: str, output_dir: str = "models/depression_model",
                              quick_mode: bool = True, max_samples: int = 2000):
        """Train DistilBERT on DAIC-WOZ depression data - lightweight mode by default"""
        try:
            # Load data
            texts, labels = self.load_daic_woz_data(daic_woz_dir)
            
            if len(texts) == 0:
                logger.error("No data loaded for training")
                return None
            
            # Quick mode: sample limited data
            if quick_mode and len(texts) > max_samples:
                logger.info(f"Quick mode: Sampling {max_samples} from {len(texts)} examples")
                indices = np.random.choice(len(texts), max_samples, replace=False)
                texts = [texts[i] for i in indices]
                labels = [labels[i] for i in indices]
            
            # Split data
            train_texts, val_texts, train_labels, val_labels = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Create datasets
            train_dataset = DAICWOZDataset(train_texts, train_labels, self.tokenizer)
            val_dataset = DAICWOZDataset(val_texts, val_labels, self.tokenizer)
            
            # Initialize model (binary depression classification)
            model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=len(DEPRESSION_LABELS),
                problem_type="single_label_classification",
                id2label=DEPRESSION_ID2LABEL,
                label2id=DEPRESSION_LABEL2ID,
            )
            
            # Freeze backbone in quick mode
            if quick_mode:
                logger.info("Quick mode: Freezing transformer layers, training only classification head")
                for param in model.distilbert.parameters():
                    param.requires_grad = False
                for param in model.classifier.parameters():
                    param.requires_grad = True
            
            # Training arguments - lightweight settings
            num_epochs = 1 if quick_mode else 3
            batch_size = 16
            warmup_steps = min(100, len(train_dataset) // batch_size // 4)
            
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                warmup_steps=warmup_steps,
                weight_decay=0.01,
                logging_dir=f"{output_dir}/logs",
                logging_steps=50,
                evaluation_strategy="epoch",
                save_strategy="no",
                load_best_model_at_end=False,
                fp16=False,  # CPU-friendly
                dataloader_num_workers=0,  # CPU-friendly
            )
            
            # Create trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=self.tokenizer,
            )
            
            # Train model
            logger.info("Starting depression model training...")
            trainer.train()
            
            # Ensure output directory exists and save model/tokenizer
            os.makedirs(output_dir, exist_ok=True)
            trainer.save_model()
            self.tokenizer.save_pretrained(output_dir)
            
            # Evaluate
            eval_results = trainer.evaluate()
            acc = eval_results.get("eval_accuracy")
            logger.info(f"Depression evaluation metrics: {eval_results}")
            if acc is not None:
                logger.info(f"Depression model training completed. Final accuracy: {acc:.4f}")
            
            return trainer
            
        except Exception as e:
            logger.error(f"Error training depression model: {str(e)}")
            return None

if __name__ == "__main__":
    # Example usage
    trainer = TextAnalyzerTrainer()
    
    # Train stress model on Reddit data
    reddit_path = "../datasets_archive3/stressed_anxious_cleaned.csv"
    if os.path.exists(reddit_path):
        print("Training stress model on Reddit data...")
        trainer.train_stress_model(reddit_path)
    
    # Train depression model on DAIC-WOZ data
    daic_woz_path = "../datasets_archive2"
    if os.path.exists(daic_woz_path):
        print("Training depression model on DAIC-WOZ data...")
        trainer.train_depression_model(daic_woz_path)
