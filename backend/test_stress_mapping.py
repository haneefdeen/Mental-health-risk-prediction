"""
Sanity check script for stress mapping.
Tests that stress_category is consistent with primary_emotion.
"""

from backend.services.stress_mapping import (
    map_emotion_to_stress,
    combine_stress,
    stress_category_to_internal_label
)
from backend.services.risk_utils import stress_category_to_risk_score


def test_stress_mapping():
    """Test emotion to stress mapping."""
    print("=" * 60)
    print("STRESS MAPPING SANITY CHECKS")
    print("=" * 60)
    print()
    
    test_cases = [
        ("Sad", None, "High Stress"),
        ("Anxious", None, "High Stress"),
        ("Fearful", None, "High Stress"),
        ("Angry", None, "High Stress"),
        ("Happy", None, "No Apparent Stress"),
        ("Neutral", None, "Low Stress"),
        ("Surprised", None, "Low Stress"),
        ("Disgusted", None, "Moderate Stress"),
        
        # Test combination: emotion says High, model says Low -> should be at least Moderate
        ("Sad", "Low Stress", "Moderate Stress"),
        ("Anxious", "No Apparent Stress", "Moderate Stress"),
        
        # Test combination: both agree
        ("Happy", "No Apparent Stress", "No Apparent Stress"),
        ("Sad", "High Stress", "High Stress"),
        
        # Test combination: model says High, emotion says Low -> use High (more severe)
        ("Happy", "High Stress", "High Stress"),
    ]
    
    print("1. Testing emotion → stress mapping:")
    print("-" * 60)
    for emotion, model_stress, expected in test_cases[:8]:
        emotion_stress = map_emotion_to_stress(emotion)
        status = "✅" if emotion_stress == expected else "❌"
        print(f"{status} {emotion:12} → {emotion_stress:25} (expected: {expected})")
    
    print()
    print("2. Testing stress combination:")
    print("-" * 60)
    for emotion, model_stress, expected in test_cases:
        emotion_stress = map_emotion_to_stress(emotion)
        final_stress = combine_stress(model_stress, emotion_stress)
        status = "✅" if final_stress == expected else "❌"
        model_str = model_stress or "None"
        print(f"{status} Emotion: {emotion:12} | Model: {model_str:20} → Final: {final_stress:25}")
    
    print()
    print("3. Testing risk score calculation:")
    print("-" * 60)
    stress_categories = ["No Apparent Stress", "Low Stress", "Moderate Stress", "High Stress"]
    for category in stress_categories:
        risk_score, risk_level = stress_category_to_risk_score(category)
        internal_label = stress_category_to_internal_label(category)
        print(f"   {category:25} → Risk Score: {risk_score:3} | Risk Level: {risk_level:15} | Internal: {internal_label}")
    
    print()
    print("=" * 60)
    print("KEY REQUIREMENTS CHECK:")
    print("=" * 60)
    
    # Critical checks
    sad_stress = map_emotion_to_stress("Sad")
    anxious_stress = map_emotion_to_stress("Anxious")
    happy_stress = map_emotion_to_stress("Happy")
    neutral_stress = map_emotion_to_stress("Neutral")
    
    checks = [
        (sad_stress not in ["Low Stress", "No Apparent Stress"], 
         f"Sad → {sad_stress} (should NOT be Low/No Stress)"),
        (anxious_stress not in ["Low Stress", "No Apparent Stress"], 
         f"Anxious → {anxious_stress} (should NOT be Low/No Stress)"),
        (happy_stress in ["No Apparent Stress", "Low Stress"], 
         f"Happy → {happy_stress} (should be No/Low Stress)"),
        (neutral_stress in ["Low Stress", "No Apparent Stress"], 
         f"Neutral → {neutral_stress} (should be Low/No Stress)"),
    ]
    
    all_passed = True
    for passed, message in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {message}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
    else:
        print("❌ SOME CHECKS FAILED - Please review the mapping logic.")
    
    return all_passed


if __name__ == "__main__":
    test_stress_mapping()


