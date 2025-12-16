# Real Datasets for MindScope AI

This directory manages real-world datasets for training and testing the MindScope AI models.

## Real Datasets Integrated

### 1. FER2013 Facial Emotion Recognition Dataset
- **Source**: `datasets_archive1/`
- **Content**: 28,000+ facial images across 7 emotion categories
- **Categories**: angry, disgusted, fearful, happy, neutral, sad, surprised
- **Splits**: Train/test splits with balanced distribution
- **Usage**: Training ResNet50 for facial emotion detection

### 2. DAIC-WOZ Depression Dataset
- **Source**: `datasets_archive2/`
- **Content**: 192 conversation transcripts from depression screening interviews
- **Format**: CSV files with timestamps, speakers, and conversation text
- **Usage**: Training DistilBERT for depression detection in conversations

### 3. Reddit Stress/Anxiety Dataset
- **Source**: `datasets_archive3/stressed_anxious_cleaned.csv`
- **Content**: 21,710+ Reddit posts with stress/anxiety labels
- **Labels**: Binary classification (0=not stressed, 1=stressed/anxious)
- **Usage**: Training text analysis models for stress detection

### 4. Dreaddit Stress Analysis Dataset
- **Source**: `datasets_archive11/dreaddit_StressAnalysis - Sheet1.csv`
- **Content**: Reddit posts with comprehensive linguistic features
- **Features**: 100+ linguistic features including LIWC, sentiment, syntax
- **Usage**: Advanced behavioral analysis and stress prediction

## Dataset Management

```python
from datasets.dataset_manager import DatasetManager

# Initialize dataset manager
dm = DatasetManager()

# Load all real datasets
dm.initialize_all_datasets()

# Get dataset summary
summary = dm.get_dataset_summary()
print(f"FER2013 images: {summary['fer2013']['total_images']}")
print(f"DAIC-WOZ transcripts: {summary['daic_woz']['total_transcripts']}")
print(f"Reddit posts: {summary['reddit_stress']['total_posts']}")
print(f"Dreaddit posts: {summary['dreaddit']['total_posts']}")

# Load specific datasets
fer2013_info = dm.load_fer2013_dataset()
reddit_data = dm.load_reddit_stress_dataset()
```

## Dataset Statistics

| Dataset | Type | Size | Purpose |
|---------|------|------|---------|
| FER2013 | Images | 28,000+ | Facial emotion recognition |
| DAIC-WOZ | Text | 192 transcripts | Depression detection |
| Reddit Stress | Text | 21,710+ posts | Stress/anxiety classification |
| Dreaddit | Text + Features | 100+ features | Behavioral analysis |

## Privacy & Ethics

These are publicly available research datasets used for:
- **Research purposes only**
- **Academic and educational use**
- **Model development and validation**
- **No personal data collection**

For production deployment:
- Use only anonymized data
- Obtain proper consent
- Follow GDPR/HIPAA guidelines
- Implement data protection measures
