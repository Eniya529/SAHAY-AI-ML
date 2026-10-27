from src.indicators import (
    extract_emotional_indicators,
    extract_contextual_indicators,
    extract_safety_indicators
)


EMOTIONAL_FEATURES = [
    "fear",
    "distress",
    "anxiety",
    "helplessness"
]

CONTEXTUAL_FEATURES = [
    "threat",
    "retaliation",
    "intimidation",
    "repeated_contact",
    "following"
]

SAFETY_FEATURES = [
    "immediate_safety_concern",
    "family_safety_concern",
    "home_safety_concern",
    "workplace_safety_concern"
]


def extract_ml_features(text):
    emotional = extract_emotional_indicators(text)
    contextual = extract_contextual_indicators(text)
    safety = extract_safety_indicators(text)

    features = {}

    for feature in EMOTIONAL_FEATURES:
        features[f"emotion_{feature}"] = int(feature in emotional)

    for feature in CONTEXTUAL_FEATURES:
        features[f"context_{feature}"] = int(feature in contextual)

    for feature in SAFETY_FEATURES:
        features[f"safety_{feature}"] = int(feature in safety)

    return features