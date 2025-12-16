import json
import os
from typing import List, Dict, Any
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import glob
from PIL import Image

class DatasetManager:
    """Manages real datasets for MindScope AI including FER2013, DAIC-WOZ, Reddit, and Dreaddit"""
    
    def __init__(self, data_dir: str = "datasets"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        
        # Real dataset paths
        self.fer2013_path = "../datasets_archive1"  # FER2013 facial emotion dataset
        self.daic_woz_path = "../datasets_archive2"  # DAIC-WOZ depression dataset
        self.reddit_stress_path = "../datasets_archive3/stressed_anxious_cleaned.csv"  # Reddit stress dataset
        self.dreaddit_path = "../datasets_archive11/dreaddit_StressAnalysis - Sheet1.csv"  # Dreaddit dataset
        
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/text", exist_ok=True)
        os.makedirs(f"{self.data_dir}/images", exist_ok=True)
        os.makedirs(f"{self.data_dir}/behavioral", exist_ok=True)
        
    def create_sample_text_dataset(self):
        """Create sample text dataset with emotional labels"""
        sample_texts = [
            {"text": "I'm feeling really overwhelmed with work lately. Can't seem to catch a break.", "emotion": "stress", "anxiety_level": 0.8},
            {"text": "Had a great day today! Everything went perfectly and I'm so happy.", "emotion": "joy", "anxiety_level": 0.1},
            {"text": "I don't know what to do anymore. Everything feels hopeless and pointless.", "emotion": "depression", "anxiety_level": 0.9},
            {"text": "Just finished my presentation and it went well! Feeling confident.", "emotion": "confidence", "anxiety_level": 0.2},
            {"text": "Can't sleep again. My mind keeps racing with worries about tomorrow.", "emotion": "anxiety", "anxiety_level": 0.7},
            {"text": "Spent time with friends today. It was nice to laugh and forget about stress.", "emotion": "relief", "anxiety_level": 0.3},
            {"text": "I'm so tired of pretending everything is okay when it's not.", "emotion": "exhaustion", "anxiety_level": 0.6},
            {"text": "Finally got the promotion I've been working towards! So excited!", "emotion": "excitement", "anxiety_level": 0.1},
            {"text": "Why does everyone else seem to have it figured out except me?", "emotion": "insecurity", "anxiety_level": 0.7},
            {"text": "Taking a walk in nature always helps me feel better.", "emotion": "calm", "anxiety_level": 0.2},
            {"text": "I feel like I'm drowning in responsibilities and expectations.", "emotion": "overwhelmed", "anxiety_level": 0.8},
            {"text": "Had a good therapy session today. Feeling more hopeful about the future.", "emotion": "hope", "anxiety_level": 0.3},
            {"text": "Another sleepless night. My anxiety is getting worse.", "emotion": "anxiety", "anxiety_level": 0.8},
            {"text": "Celebrated my birthday with family. Feeling loved and grateful.", "emotion": "gratitude", "anxiety_level": 0.1},
            {"text": "I can't stop worrying about what others think of me.", "emotion": "anxiety", "anxiety_level": 0.6},
            {"text": "Meditation helped me find some peace today.", "emotion": "peace", "anxiety_level": 0.2},
            {"text": "Feeling isolated and alone. No one understands what I'm going through.", "emotion": "loneliness", "anxiety_level": 0.7},
            {"text": "Completed a challenging project at work. Proud of my accomplishment!", "emotion": "pride", "anxiety_level": 0.2},
            {"text": "My heart is racing and I can't breathe properly. Having a panic attack.", "emotion": "panic", "anxiety_level": 0.9},
            {"text": "Spent quality time with my pet. They always make me feel better.", "emotion": "comfort", "anxiety_level": 0.2}
        ]
        
        with open(f"{self.data_dir}/text/sample_text_dataset.json", "w") as f:
            json.dump(sample_texts, f, indent=2)
            
        return sample_texts
    
    def create_behavioral_dataset(self):
        """Create sample behavioral dataset with emoji usage and posting patterns"""
        behavioral_data = []
        
        # Generate sample behavioral patterns
        for i in range(50):
            user_id = f"user_{i+1}"
            
            # Generate emoji usage patterns
            emoji_patterns = {
                "happy_emojis": ["😊", "😄", "😁", "🥰", "😍", "🤗", "😘", "🙂"],
                "sad_emojis": ["😢", "😭", "😔", "😞", "😟", "😕", "😰", "😨"],
                "anxious_emojis": ["😰", "😨", "😱", "😳", "😬", "😓", "😵", "🤯"],
                "neutral_emojis": ["😐", "😑", "😶", "🤔", "😏", "🙃", "😒", "😴"]
            }
            
            # Simulate different stress levels
            stress_level = random.uniform(0.1, 0.9)
            
            if stress_level > 0.7:
                # High stress users use more anxious/sad emojis
                emoji_usage = {
                    "happy": random.randint(0, 3),
                    "sad": random.randint(5, 15),
                    "anxious": random.randint(3, 10),
                    "neutral": random.randint(2, 8)
                }
                posting_frequency = random.uniform(0.8, 2.5)  # More frequent posting when stressed
            elif stress_level < 0.3:
                # Low stress users use more happy emojis
                emoji_usage = {
                    "happy": random.randint(8, 20),
                    "sad": random.randint(0, 3),
                    "anxious": random.randint(0, 2),
                    "neutral": random.randint(3, 8)
                }
                posting_frequency = random.uniform(0.3, 1.2)  # Less frequent posting when calm
            else:
                # Moderate stress users
                emoji_usage = {
                    "happy": random.randint(3, 8),
                    "sad": random.randint(2, 8),
                    "anxious": random.randint(1, 5),
                    "neutral": random.randint(4, 10)
                }
                posting_frequency = random.uniform(0.5, 1.8)
            
            # Generate posting timeline
            posts_timeline = []
            base_date = datetime.now() - timedelta(days=30)
            
            for day in range(30):
                daily_posts = random.randint(0, int(posting_frequency * 3))
                for post in range(daily_posts):
                    post_time = base_date + timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                    posts_timeline.append({
                        "timestamp": post_time.isoformat(),
                        "stress_level": stress_level + random.uniform(-0.1, 0.1),
                        "emoji_count": random.randint(0, 5)
                    })
            
            behavioral_data.append({
                "user_id": user_id,
                "emoji_usage": emoji_usage,
                "posting_frequency": posting_frequency,
                "avg_stress_level": stress_level,
                "posts_timeline": posts_timeline,
                "behavioral_score": self.calculate_behavioral_score(emoji_usage, posting_frequency)
            })
        
        with open(f"{self.data_dir}/behavioral/sample_behavioral_dataset.json", "w") as f:
            json.dump(behavioral_data, f, indent=2)
            
        return behavioral_data
    
    def calculate_behavioral_score(self, emoji_usage: Dict, posting_frequency: float) -> float:
        """Calculate behavioral stress score based on emoji usage and posting frequency"""
        # Higher sad/anxious emoji usage increases stress score
        sad_anxious_ratio = (emoji_usage["sad"] + emoji_usage["anxious"]) / sum(emoji_usage.values())
        
        # Higher posting frequency can indicate stress
        frequency_score = min(posting_frequency / 2.0, 1.0)
        
        # Combine both factors
        behavioral_score = (sad_anxious_ratio * 0.7) + (frequency_score * 0.3)
        
        return min(behavioral_score, 1.0)
    
    def create_emotion_labels(self):
        """Create emotion label mappings"""
        emotion_labels = {
            "emotions": ["joy", "sadness", "anger", "fear", "surprise", "disgust", "neutral"],
            "stress_levels": ["low", "moderate", "high", "critical"],
            "anxiety_indicators": ["worry", "panic", "restlessness", "irritability", "fatigue", "concentration_problems"],
            "coping_strategies": [
                "deep_breathing", "meditation", "exercise", "social_support", 
                "professional_help", "mindfulness", "journaling", "sleep_hygiene"
            ]
        }
        
        with open(f"{self.data_dir}/emotion_labels.json", "w") as f:
            json.dump(emotion_labels, f, indent=2)
            
        return emotion_labels
    
    def load_dataset(self, dataset_type: str) -> List[Dict]:
        """Load dataset by type"""
        if dataset_type == "text":
            with open(f"{self.data_dir}/text/sample_text_dataset.json", "r") as f:
                return json.load(f)
        elif dataset_type == "behavioral":
            with open(f"{self.data_dir}/behavioral/sample_behavioral_dataset.json", "r") as f:
                return json.load(f)
        elif dataset_type == "emotion_labels":
            with open(f"{self.data_dir}/emotion_labels.json", "r") as f:
                return json.load(f)
        else:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
    
    def load_fer2013_dataset(self) -> Dict[str, Any]:
        """Load FER2013 facial emotion recognition dataset"""
        try:
            emotion_categories = ['angry', 'disgusted', 'fearful', 'happy', 'neutral', 'sad', 'surprised']
            dataset_info = {
                'name': 'FER2013',
                'description': 'Facial Emotion Recognition Dataset',
                'emotions': emotion_categories,
                'train_images': {},
                'test_images': {},
                'total_images': 0
            }
            
            # Count images in each category
            for split in ['train', 'test']:
                split_path = os.path.join(self.fer2013_path, split)
                if os.path.exists(split_path):
                    dataset_info[f'{split}_images'] = {}
                    for emotion in emotion_categories:
                        emotion_path = os.path.join(split_path, emotion)
                        if os.path.exists(emotion_path):
                            image_files = glob.glob(os.path.join(emotion_path, '*.png'))
                            dataset_info[f'{split}_images'][emotion] = len(image_files)
                            dataset_info['total_images'] += len(image_files)
            
            return dataset_info
        except Exception as e:
            print(f"Error loading FER2013 dataset: {str(e)}")
            return {'error': str(e)}
    
    def load_daic_woz_dataset(self) -> Dict[str, Any]:
        """Load DAIC-WOZ depression dataset"""
        try:
            transcript_files = glob.glob(os.path.join(self.daic_woz_path, "*.csv"))
            dataset_info = {
                'name': 'DAIC-WOZ',
                'description': 'Depression Analysis Dataset',
                'total_transcripts': len(transcript_files),
                'sample_transcript': None
            }
            
            # Load a sample transcript
            if transcript_files:
                sample_file = transcript_files[0]
                df = pd.read_csv(sample_file, sep='\t')
                dataset_info['sample_transcript'] = {
                    'file': os.path.basename(sample_file),
                    'total_lines': len(df),
                    'speakers': df['speaker'].unique().tolist(),
                    'duration': f"{df['stop_time'].max():.2f} seconds"
                }
            
            return dataset_info
        except Exception as e:
            print(f"Error loading DAIC-WOZ dataset: {str(e)}")
            return {'error': str(e)}
    
    def load_reddit_stress_dataset(self) -> Dict[str, Any]:
        """Load Reddit stress/anxiety dataset"""
        try:
            df = pd.read_csv(self.reddit_stress_path)
            dataset_info = {
                'name': 'Reddit Stress/Anxiety',
                'description': 'Reddit posts with stress/anxiety labels',
                'total_posts': len(df),
                'stress_distribution': df['is_stressed/anxious'].value_counts().to_dict(),
                'sample_posts': df.head(3).to_dict('records')
            }
            return dataset_info
        except Exception as e:
            print(f"Error loading Reddit stress dataset: {str(e)}")
            return {'error': str(e)}
    
    def load_dreaddit_dataset(self) -> Dict[str, Any]:
        """Load Dreaddit stress analysis dataset"""
        try:
            df = pd.read_csv(self.dreaddit_path)
            dataset_info = {
                'name': 'Dreaddit',
                'description': 'Reddit posts with comprehensive linguistic features',
                'total_posts': len(df),
                'stress_distribution': df['label'].value_counts().to_dict(),
                'subreddits': df['subreddit'].value_counts().head(10).to_dict(),
                'features': list(df.columns),
                'sample_posts': df[['text', 'label', 'subreddit']].head(3).to_dict('records')
            }
            return dataset_info
        except Exception as e:
            print(f"Error loading Dreaddit dataset: {str(e)}")
            return {'error': str(e)}
    
    def get_dataset_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all real datasets"""
        return {
            'fer2013': self.load_fer2013_dataset(),
            'daic_woz': self.load_daic_woz_dataset(),
            'reddit_stress': self.load_reddit_stress_dataset(),
            'dreaddit': self.load_dreaddit_dataset(),
            'total_datasets': 4,
            'last_updated': datetime.now().isoformat()
        }
    
    def initialize_all_datasets(self):
        """Initialize all datasets (both sample and real)"""
        print("Loading real datasets...")
        
        # Load real datasets
        real_datasets = self.get_dataset_summary()
        
        # Save real dataset info
        with open(f"{self.data_dir}/real_datasets_summary.json", "w") as f:
            json.dump(real_datasets, f, indent=2)
        
        # Still create sample datasets for demo purposes
        print("Creating sample datasets for demo...")
        self.create_sample_text_dataset()
        self.create_behavioral_dataset()
        self.create_emotion_labels()
        
        print("All datasets loaded successfully!")
        print(f"Real datasets: {real_datasets['total_datasets']}")
        print(f"FER2013 images: {real_datasets['fer2013'].get('total_images', 0)}")
        print(f"DAIC-WOZ transcripts: {real_datasets['daic_woz'].get('total_transcripts', 0)}")
        print(f"Reddit posts: {real_datasets['reddit_stress'].get('total_posts', 0)}")
        print(f"Dreaddit posts: {real_datasets['dreaddit'].get('total_posts', 0)}")

if __name__ == "__main__":
    dataset_manager = DatasetManager()
    dataset_manager.initialize_all_datasets()
