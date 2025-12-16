import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
import numpy as np
import os
import glob
import json
from typing import Dict, List, Any
import logging
from sklearn.metrics import accuracy_score, classification_report

logger = logging.getLogger(__name__)

class FER2013Dataset(Dataset):
    """Dataset class for FER2013 facial emotion recognition"""
    
    def __init__(self, data_dir, split='train', transform=None):
        self.data_dir = data_dir
        self.split = split
        self.transform = transform
        
        # Emotion categories matching FER2013
        self.emotion_categories = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        self.emotion_to_idx = {emotion: idx for idx, emotion in enumerate(self.emotion_categories)}
        
        # Load image paths and labels
        self.image_paths = []
        self.labels = []
        
        split_path = os.path.join(data_dir, split)
        if os.path.exists(split_path):
            for emotion in self.emotion_categories:
                emotion_path = os.path.join(split_path, emotion)
                if os.path.exists(emotion_path):
                    image_files = glob.glob(os.path.join(emotion_path, '*.png'))
                    self.image_paths.extend(image_files)
                    self.labels.extend([self.emotion_to_idx[emotion]] * len(image_files))
        
        logger.info(f"Loaded {len(self.image_paths)} images for {split} split")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        return image, torch.tensor(label, dtype=torch.long)

class ImageAnalyzerTrainer:
    """Trainer for facial emotion recognition using FER2013 dataset"""
    
    def __init__(self, num_classes=7):
        self.num_classes = num_classes
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Data transforms
        self.train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Shared inference transform (same as val_transform for consistency)
        self.inference_transform = self.val_transform
    
    def load_fer2013_data(self, data_dir: str):
        """Load FER2013 dataset"""
        try:
            # Create datasets
            train_dataset = FER2013Dataset(data_dir, split='train', transform=self.train_transform)
            test_dataset = FER2013Dataset(data_dir, split='test', transform=self.val_transform)
            
            logger.info(f"FER2013 dataset loaded:")
            logger.info(f"  Train images: {len(train_dataset)}")
            logger.info(f"  Test images: {len(test_dataset)}")
            
            return train_dataset, test_dataset
            
        except Exception as e:
            logger.error(f"Error loading FER2013 data: {str(e)}")
            return None, None
    
    def create_model(self, freeze_backbone: bool = True):
        """Create ResNet50 model for emotion classification"""
        # Load pre-trained ResNet50 using current weights API
        model = resnet50(weights=ResNet50_Weights.DEFAULT)
        
        # Modify final layer for emotion classification
        model.fc = nn.Linear(model.fc.in_features, self.num_classes)
        
        # Freeze backbone in quick mode
        if freeze_backbone:
            logger.info("Freezing ResNet50 backbone, training only classification head")
            for param in model.parameters():
                param.requires_grad = False
            # Only train final classification layer
            for param in model.fc.parameters():
                param.requires_grad = True
        
        return model.to(self.device)
    
    def train_model(self, data_dir: str, output_dir: str = "models/emotion_model", 
                   epochs: int = 1, quick_mode: bool = True, max_samples: int = 2000):
        """Train ResNet50 on FER2013 data - lightweight mode by default"""
        try:
            # Ensure output directory exists before any saving
            os.makedirs(output_dir, exist_ok=True)

            # Load data
            train_dataset, test_dataset = self.load_fer2013_data(data_dir)
            
            if train_dataset is None or test_dataset is None:
                logger.error("Failed to load FER2013 data")
                return None
            
            # Quick mode: subsample dataset
            if quick_mode and len(train_dataset) > max_samples:
                logger.info(f"Quick mode: Sampling {max_samples} from {len(train_dataset)} training images")
                indices = np.random.choice(len(train_dataset), max_samples, replace=False)
                train_dataset = torch.utils.data.Subset(train_dataset, indices)
            
            # Create data loaders - CPU-friendly (num_workers=0)
            train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True, num_workers=0)
            test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0)
            
            # Create model with frozen backbone in quick mode
            model = self.create_model(freeze_backbone=quick_mode)
            
            # Loss and optimizer
            criterion = nn.CrossEntropyLoss()
            optimizer = optim.Adam(model.parameters(), lr=0.001)
            scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
            
            # Training loop
            best_accuracy = 0.0
            
            for epoch in range(epochs):
                # Training phase
                model.train()
                train_loss = 0.0
                train_correct = 0
                train_total = 0
                
                for batch_idx, (data, target) in enumerate(train_loader):
                    data, target = data.to(self.device), target.to(self.device)
                    
                    optimizer.zero_grad()
                    output = model(data)
                    loss = criterion(output, target)
                    loss.backward()
                    optimizer.step()
                    
                    train_loss += loss.item()
                    _, predicted = torch.max(output.data, 1)
                    train_total += target.size(0)
                    train_correct += (predicted == target).sum().item()
                    
                    if batch_idx % 100 == 0:
                        logger.info(f'Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}')
                
                # Validation phase
                model.eval()
                val_loss = 0.0
                val_correct = 0
                val_total = 0
                
                with torch.no_grad():
                    for data, target in test_loader:
                        data, target = data.to(self.device), target.to(self.device)
                        output = model(data)
                        loss = criterion(output, target)
                        
                        val_loss += loss.item()
                        _, predicted = torch.max(output.data, 1)
                        val_total += target.size(0)
                        val_correct += (predicted == target).sum().item()
                
                # Calculate metrics
                train_accuracy = 100.0 * train_correct / train_total
                val_accuracy = 100.0 * val_correct / val_total
                
                logger.info(f'Epoch {epoch}:')
                logger.info(f'  Train Loss: {train_loss/len(train_loader):.4f}, Train Acc: {train_accuracy:.2f}%')
                logger.info(f'  Val Loss: {val_loss/len(test_loader):.4f}, Val Acc: {val_accuracy:.2f}%')
                
                # Save best model
                if val_accuracy > best_accuracy:
                    best_accuracy = val_accuracy
                    torch.save(model.state_dict(), os.path.join(output_dir, 'best_model.pth'))
                    logger.info(f'New best model saved with accuracy: {best_accuracy:.2f}%')
                
                scheduler.step()
            
            # Save final model and label mapping for inference
            torch.save(model.state_dict(), os.path.join(output_dir, 'final_model.pth'))

            # Save emotion label mapping (index -> emotion name)
            # Handle both full dataset and Subset cases
            try:
                # Get emotion categories from original dataset
                if isinstance(train_dataset, torch.utils.data.Subset):
                    emotion_categories = train_dataset.dataset.emotion_categories
                else:
                    emotion_categories = train_dataset.emotion_categories
                
                label_map = {idx: emotion for idx, emotion in enumerate(emotion_categories)}
                label_map_path = os.path.join(output_dir, "label_map.json")
                with open(label_map_path, "w", encoding="utf-8") as f:
                    json.dump(label_map, f, ensure_ascii=False, indent=2)
                logger.info(f"Saved emotion label mapping to {label_map_path}")
            except Exception as lm_err:
                logger.warning(f"Could not save label_map.json: {lm_err}")

            # Evaluate model on test set
            logger.info("Evaluating model on test set...")
            test_accuracy, test_report = self.evaluate_model(model, test_loader)
            
            logger.info(f'Training completed. Best validation accuracy: {best_accuracy:.2f}%')
            logger.info(f'Test set accuracy: {test_accuracy*100:.2f}%')
            return model
            
        except Exception as e:
            logger.error(f"Error training emotion model: {str(e)}")
            return None
    
    def evaluate_model(self, model, test_loader):
        """Evaluate trained model"""
        model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                _, predicted = torch.max(output, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(target.cpu().numpy())
        
        # Calculate metrics
        accuracy = accuracy_score(all_targets, all_predictions)
        
        # Emotion categories for classification report
        emotion_categories = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
        
        report = classification_report(all_targets, all_predictions, 
                                    target_names=emotion_categories, 
                                    output_dict=True)
        
        logger.info(f"Model Evaluation:")
        logger.info(f"  Overall Accuracy: {accuracy:.4f}")
        logger.info(f"  Classification Report:")
        for emotion in emotion_categories:
            if emotion in report:
                logger.info(f"    {emotion}: Precision={report[emotion]['precision']:.3f}, "
                           f"Recall={report[emotion]['recall']:.3f}, "
                           f"F1={report[emotion]['f1-score']:.3f}")
        
        return accuracy, report

if __name__ == "__main__":
    # Example usage
    trainer = ImageAnalyzerTrainer()
    
    # Train emotion model on FER2013 data
    fer2013_path = "../datasets_archive1"
    if os.path.exists(fer2013_path):
        print("Training emotion model on FER2013 data...")
        model = trainer.train_model(fer2013_path, epochs=5)
        
        if model:
            print("Model training completed successfully!")
        else:
            print("Model training failed!")
    else:
        print(f"FER2013 dataset not found at {fer2013_path}")
