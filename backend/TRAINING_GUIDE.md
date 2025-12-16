# MindScope AI Model Training Guide

This guide explains how to train the MindScope AI models using your real datasets.

## 🎯 Overview

The training pipeline uses your real datasets to create specialized models:

- **Text Models**: DistilBERT fine-tuned on Reddit stress data and DAIC-WOZ depression data
- **Image Model**: ResNet50 fine-tuned on FER2013 facial emotion data
- **Behavioral Model**: Uses Dreaddit linguistic features for behavioral analysis

## 📊 Datasets Used

| Dataset | Purpose | Size | Model |
|---------|---------|------|-------|
| FER2013 | Facial emotion recognition | 28,000+ images | ResNet50 |
| DAIC-WOZ | Depression detection | 192 transcripts | DistilBERT |
| Reddit Stress | Stress/anxiety classification | 21,710+ posts | DistilBERT |
| Dreaddit | Behavioral analysis | 100+ features | Custom |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Train All Models

```bash
python train_models.py --model all
```

### 3. Train Specific Models

```bash
# Train only text models
python train_models.py --model text

# Train only image model
python train_models.py --model image
```

## 📝 Detailed Training Process

### Text Model Training

#### Stress Detection Model (Reddit Data)
```python
from model.text_trainer import TextAnalyzerTrainer

trainer = TextAnalyzerTrainer()
trainer.train_stress_model(
    reddit_csv_path="../datasets_archive3/stressed_anxious_cleaned.csv",
    output_dir="models/stress_model"
)
```

**Features:**
- Binary classification (stressed/not stressed)
- 21,710+ Reddit posts
- 80/20 train/validation split
- 3 epochs training
- Best model saved based on validation accuracy

#### Depression Detection Model (DAIC-WOZ Data)
```python
trainer.train_depression_model(
    daic_woz_dir="../datasets_archive2",
    output_dir="models/depression_model"
)
```

**Features:**
- Binary classification (depressed/not depressed)
- 192 conversation transcripts
- Participant responses extracted
- Conversation length as depression indicator

### Image Model Training

#### Facial Emotion Recognition (FER2013 Data)
```python
from model.image_trainer import ImageAnalyzerTrainer

trainer = ImageAnalyzerTrainer()
trainer.train_model(
    data_dir="../datasets_archive1",
    output_dir="models/emotion_model",
    epochs=10
)
```

**Features:**
- 7 emotion categories: angry, disgusted, fearful, happy, neutral, sad, surprised
- 28,000+ facial images
- Data augmentation (rotation, flipping, color jitter)
- ResNet50 backbone with custom classifier
- Best model saved based on validation accuracy

## 🔧 Training Configuration

### Text Model Settings
```python
training_args = TrainingArguments(
    output_dir=output_dir,
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=500,
    weight_decay=0.01,
    evaluation_strategy="steps",
    eval_steps=500,
    save_strategy="steps",
    save_steps=500,
    load_best_model_at_end=True,
    metric_for_best_model="eval_accuracy",
)
```

### Image Model Settings
```python
# Data augmentation
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Training parameters
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
```

## 📈 Training Monitoring

### Logs and Metrics
- Training logs saved to `models/*/logs/`
- TensorBoard support for visualization
- Validation accuracy tracking
- Best model checkpointing

### Evaluation Metrics
- **Text Models**: Accuracy, Precision, Recall, F1-Score
- **Image Model**: Accuracy, Per-class metrics, Confusion Matrix

## 🎯 Model Performance

### Expected Results
- **Stress Model**: 85-90% accuracy on Reddit data
- **Depression Model**: 80-85% accuracy on DAIC-WOZ data
- **Emotion Model**: 70-80% accuracy on FER2013 data

### Performance Optimization
- Use GPU if available (CUDA)
- Adjust batch size based on memory
- Increase epochs for better performance
- Use data augmentation for image model

## 🔄 Model Integration

After training, models are automatically integrated into the main application:

```python
# Load trained models
from model.text_analyzer import TextAnalyzer
from model.image_analyzer import ImageAnalyzer

# Models will automatically use trained weights if available
text_analyzer = TextAnalyzer()  # Uses models/stress_model or models/depression_model
image_analyzer = ImageAnalyzer()  # Uses models/emotion_model
```

## 🛠️ Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```bash
   # Reduce batch size
   python train_models.py --model image --batch_size 16
   ```

2. **Dataset Not Found**
   ```bash
   # Verify dataset paths
   ls ../datasets_archive1/
   ls ../datasets_archive2/
   ls ../datasets_archive3/
   ```

3. **Training Too Slow**
   ```bash
   # Use GPU acceleration
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

### Performance Tips

- **GPU**: Use CUDA for 5-10x faster training
- **Memory**: Adjust batch size based on available RAM
- **Data**: Ensure datasets are properly extracted
- **Epochs**: Start with fewer epochs for testing

## 📊 Dataset Statistics

### FER2013 Distribution
```
angry: 3,995 train, 958 test
disgusted: 436 train, 1 test  
fearful: 4,097 train, 1,024 test
happy: 7,215 train, 1,774 test
neutral: 4,965 train, 1,233 test
sad: 4,830 train, 1,247 test
surprised: 3,171 train, 831 test
```

### Reddit Stress Distribution
```
Not Stressed (0): ~60%
Stressed/Anxious (1): ~40%
```

### DAIC-WOZ Distribution
```
Total Transcripts: 192
Average Duration: ~15 minutes
Participants: Depression screening interviews
```

## 🎉 Next Steps

After training:

1. **Test Models**: Use the trained models in the web application
2. **Fine-tune**: Adjust hyperparameters for better performance
3. **Deploy**: Use models in production environment
4. **Monitor**: Track model performance over time

## 📚 References

- [FER2013 Dataset](https://www.kaggle.com/datasets/msambare/fer2013)
- [DAIC-WOZ Dataset](https://dcapswoz.ict.usc.edu/)
- [DistilBERT](https://huggingface.co/distilbert-base-uncased)
- [ResNet50](https://pytorch.org/hub/pytorch_vision_resnet/)
