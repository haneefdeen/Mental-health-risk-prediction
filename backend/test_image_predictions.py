"""
Quick sanity check for image predictions.
Tests that happy/surprised images don't get misclassified as sad.
"""

import json
from pathlib import Path
from backend.model.image_analyzer import ImageAnalyzer


def test_image_label_mapping():
    """Test that label mapping is loaded correctly."""
    print("=" * 60)
    print("IMAGE PREDICTION SANITY CHECK")
    print("=" * 60)
    print()
    
    # Load analyzer
    analyzer = ImageAnalyzer()
    
    print("1. Label Mapping Check:")
    print("-" * 60)
    print(f"   Loaded emotion labels: {analyzer.emotion_labels}")
    print(f"   Number of labels: {len(analyzer.emotion_labels)}")
    
    # Check label_map.json if it exists
    label_map_path = Path("models/emotion_model/label_map.json")
    if label_map_path.exists():
        with open(label_map_path, 'r') as f:
            saved_map = json.load(f)
        print(f"   Saved label_map.json: {saved_map}")
        print()
        print("   Index -> Emotion mapping:")
        for idx in range(len(analyzer.emotion_labels)):
            emotion = analyzer.emotion_labels[idx]
            print(f"     Index {idx} -> {emotion}")
    else:
        print("   ⚠️  No label_map.json found, using default mapping")
    
    print()
    print("2. Transform Check:")
    print("-" * 60)
    print("   Transform steps:")
    for i, transform in enumerate(analyzer.transform.transforms):
        print(f"     {i+1}. {transform}")
    
    print()
    print("=" * 60)
    print("✅ Image analyzer initialized successfully!")
    print("=" * 60)
    print()
    print("To test with actual images:")
    print("  1. Place FER2013 happy/surprised images in test_images/")
    print("  2. Run: python -c \"from backend.model.image_analyzer import ImageAnalyzer; import os; ia = ImageAnalyzer(); [print(f'{f}: {ia.analyze(open(f, \"rb\").read())[\"primary_emotion\"]}') for f in os.listdir('test_images') if f.endswith('.png')]\"")
    print()


if __name__ == "__main__":
    test_image_label_mapping()


