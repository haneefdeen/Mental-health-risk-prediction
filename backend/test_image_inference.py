"""
Test image inference with debug output.
Helps verify that happy images are correctly predicted as happy.
"""

import json
import numpy as np
from pathlib import Path
from backend.model.image_analyzer import ImageAnalyzer


def test_image_inference_debug():
    """Test image inference with detailed debug output."""
    print("=" * 70)
    print("IMAGE INFERENCE DEBUG TEST")
    print("=" * 70)
    print()
    
    # Load analyzer
    print("1. Loading ImageAnalyzer...")
    analyzer = ImageAnalyzer()
    print(f"   ✅ Loaded {len(analyzer.emotion_labels)} emotion labels")
    print(f"   Labels: {analyzer.emotion_labels}")
    print()
    
    # Show label mapping
    print("2. Label Index Mapping:")
    print("-" * 70)
    for idx, emotion in enumerate(analyzer.emotion_labels):
        print(f"   Index {idx} → {emotion}")
    print()
    
    # Check label_map.json
    label_map_path = Path("models/emotion_model/label_map.json")
    if label_map_path.exists():
        print("3. Saved label_map.json:")
        print("-" * 70)
        with open(label_map_path, 'r') as f:
            saved_map = json.load(f)
        for idx_str, emotion in saved_map.items():
            idx = int(idx_str)
            print(f"   Index {idx} → {emotion}")
            if idx < len(analyzer.emotion_labels):
                if analyzer.emotion_labels[idx] != emotion:
                    print(f"      ⚠️  MISMATCH! Loaded: {analyzer.emotion_labels[idx]}")
        print()
    
    print("4. Expected Behavior:")
    print("-" * 70)
    print("   Happy images should predict index 3 → 'happy'")
    print("   Angry images should predict index 0 → 'angry'")
    print("   Sad images should predict index 5 → 'sad'")
    print()
    
    print("=" * 70)
    print("To test with actual images:")
    print("=" * 70)
    print("1. Place test images in a folder (e.g., test_images/)")
    print("2. Run:")
    print("   python -c \"")
    print("   from backend.model.image_analyzer import ImageAnalyzer")
    print("   import os")
    print("   ia = ImageAnalyzer()")
    print("   for f in os.listdir('test_images'):")
    print("       if f.endswith('.png'):")
    print("           result = ia.analyze(open(f'test_images/{f}', 'rb').read())")
    print("           print(f'{f}: {result[\\\"primary_emotion\\\"]} (conf: {result[\\\"confidence\\\"]:.2f})')\"")
    print()


if __name__ == "__main__":
    test_image_inference_debug()


