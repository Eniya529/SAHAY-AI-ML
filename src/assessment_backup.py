import joblib
import re
from datetime import datetime


MODEL_PATH = "model/risk_model.pkl"


# Load trained ML model
model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# 1. RISK PREDICTION
# --------------------------------------------------

def predict_risk(text):
    """
    Predict risk level and confidence from victim message.
    """

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]
    confidence = max(probabilities)

    return prediction, round(float(confidence), 2)


# --------------------------------------------------
# 2. EMOTIONAL INDICATORS
# --------------------------------------------------

def extract_emotional_indicators(text):
    """
    Detect possible emotional indicators.
    """

    text_lower = text.lower()

    indicators = []

    emotional_patterns = {
        "fear": [
            "afraid",
            "scared",
            "fear",
            "terrified",
            "frightened"
        ],
        "distress": [
            "distressed",
            "overwhelmed",
            "can't cope",
            "cannot cope",
            "desperate"
        ],
        "anxiety": [
            "anxious",
            "anxiety",
            "nervous",
            "worried",
            "panic"
        ],
        "helplessness": [
            "helpless",
            "don't know what to do",
            "cannot do anything",
            "can't do anything"
        ]
    }

    for indicator, patterns in emotional_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


# --------------------------------------------------
# 3. CONTEXTUAL INDICATORS
# --------------------------------------------------

def extract_contextual_indicators(text):
    """
    Detect contextual risk indicators.
    """

    text_lower = text.lower()

    indicators = []

    contextual_patterns = {
        "threat": [
            "threat",
            "threatened",
            "kill",
            "harm",
            "hurt"
        ],
        "retaliation": [
            "retaliate",
            "retaliation",
            "punish me",
            "because i reported",
            "if i report"
        ],
        "intimidation": [
            "intimidate",
            "scare me",
            "pressure me",
            "forcing me"
        ],
        "repeated_contact": [
            "keep calling",
            "keeps calling",
            "repeatedly",
            "again and again",
            "keeps messaging"
        ],
        "following": [
            "following me",
            "followed me",
            "watching me",
            "tracking me"
        ]
    }

    for indicator, patterns in contextual_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


# --------------------------------------------------
# 4. SAFETY INDICATORS
# --------------------------------------------------

def extract_safety_indicators(text):
    """
    Detect immediate or personal safety concerns.
    """

    text_lower = text.lower()

    indicators = []

    safety_patterns = {
        "immediate_safety_concern": [
            "right now",
            "here right now",
            "not safe",
            "unsafe",
            "in danger"
        ],
        "family_safety_concern": [
            "my family",
            "my parents",
            "my mother",
            "my father",
            "my children",
            "family"
        ],
        "home_safety_concern": [
            "outside my house",
            "at my house",
            "near my home",
            "came to my house"
        ],
        "workplace_safety_concern": [
            "workplace",
            "office",
            "at my work"
        ]
    }

    for indicator, patterns in safety_patterns.items():
        for pattern in patterns:
            if pattern in text_lower:
                indicators.append(indicator)
                break

    return list(set(indicators))


# --------------------------------------------------
# 5. KEY EVIDENCE
# --------------------------------------------------

def extract_key_evidence(text):
    """
    For the initial prototype, preserve the victim's
    message as the evidence.
    """

    if not text.strip():
        return []

    return [text.strip()]


# --------------------------------------------------
# 6. SVI CALCULATION
# --------------------------------------------------

def calculate_svi(
    risk_level,
    emotional_indicators,
    contextual_indicators,
    safety_indicators
):
    """
    Calculate a prototype Stress Vulnerability Index.

    This is a transparent heuristic score for the prototype.
    It is NOT a clinical diagnosis.
    """

    base_scores = {
        "LOW": 20,
        "MODERATE": 40,
        "HIGH": 65,
        "CRITICAL": 85
    }

    svi = base_scores.get(risk_level, 0)

    # Additional emotional indicators
    svi += min(len(emotional_indicators) * 2, 6)

    # Additional contextual indicators
    svi += min(len(contextual_indicators) * 2, 6)

    # Safety indicators have higher weight
    svi += min(len(safety_indicators) * 3, 9)

    return min(svi, 100)


# --------------------------------------------------
# 7. ADAPTIVE QUESTION
# --------------------------------------------------

def generate_adaptive_question(
    risk_level,
    safety_indicators
):
    """
    Generate the next safety-oriented question.
    """

    if "immediate_safety_concern" in safety_indicators:
        return "Are you currently in a safe place?"

    if "family_safety_concern" in safety_indicators:
        return "Is your family currently safe?"

    if risk_level == "CRITICAL":
        return "Are you currently in immediate danger?"

    if risk_level == "HIGH":
        return "Has the person threatened or contacted you recently?"

    if risk_level == "MODERATE":
        return "Do you feel safe at the moment?"

    return "Would you like to share anything else about what happened?"


# --------------------------------------------------
# 8. RECOMMENDED ACTION
# --------------------------------------------------

def generate_recommended_action(risk_level, confidence):

    if risk_level == "CRITICAL":
        return "Priority human review recommended."

    if risk_level == "HIGH":
        return "Urgent human review recommended."

    if risk_level == "MODERATE":
        return "Human review recommended for further assessment."

    if confidence < 0.60:
        return "Low-confidence prediction; human review recommended."

    return "Continue monitoring and reassessment."


# --------------------------------------------------
# 9. HUMAN REVIEW
# --------------------------------------------------

def requires_human_review(risk_level, confidence):

    if risk_level in ["HIGH", "CRITICAL"]:
        return True

    if confidence < 0.60:
        return True

    return False


# --------------------------------------------------
# 10. REASONING
# --------------------------------------------------

def generate_reasoning(
    risk_level,
    emotional_indicators,
    contextual_indicators,
    safety_indicators
):

    reasons = []

    if emotional_indicators:
        reasons.append(
            "emotional indicators detected"
        )

    if contextual_indicators:
        reasons.append(
            "contextual risk indicators detected"
        )

    if safety_indicators:
        reasons.append(
            "safety-related indicators detected"
        )

    if not reasons:
        return "No strong risk indicators were detected in the message."

    return (
        f"The assessment was classified as {risk_level} because "
        + ", ".join(reasons)
        + "."
    )


# --------------------------------------------------
# 11. COMPLETE ASSESSMENT
# --------------------------------------------------

def create_assessment(
    case_id,
    message_id,
    text
):

    if not text or not text.strip():

        return {
            "status": "ERROR",
            "error": "Empty victim message."
        }

    # ML prediction
    risk_level, confidence = predict_risk(text)

    # Indicator extraction
    emotional_indicators = extract_emotional_indicators(text)

    contextual_indicators = extract_contextual_indicators(text)

    safety_indicators = extract_safety_indicators(text)

    # Evidence
    key_evidence = extract_key_evidence(text)

    # SVI
    svi = calculate_svi(
        risk_level,
        emotional_indicators,
        contextual_indicators,
        safety_indicators
    )

    # Adaptive question
    adaptive_question = generate_adaptive_question(
        risk_level,
        safety_indicators
    )

    # Recommended action
    recommended_action = generate_recommended_action(
        risk_level,
        confidence
    )

    # Human review
    human_review = requires_human_review(
        risk_level,
        confidence
    )

    # Reasoning
    reasoning = generate_reasoning(
        risk_level,
        emotional_indicators,
        contextual_indicators,
        safety_indicators
    )

    # Final assessment object
    assessment = {

        "status": "SUCCESS",

        "assessmentId": f"ASM-{datetime.now().strftime('%Y%m%d%H%M%S')}",

        "caseId": case_id,

        "messageId": message_id,

        "svi": svi,

        "riskLevel": risk_level,

        "confidence": confidence,

        "emotionalIndicators": emotional_indicators,

        "contextualIndicators": contextual_indicators,

        "safetyIndicators": safety_indicators,

        "keyEvidence": key_evidence,

        "reasoning": reasoning,

        "adaptiveQuestion": adaptive_question,

        "recommendedAction": recommended_action,

        "requiresHumanReview": human_review,

        "createdAt": datetime.now().isoformat()
    }

    return assessment


# --------------------------------------------------
# 12. TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_message = (
        "They threatened my family and I am scared. "
        "They said they will hurt my parents."
    )

    result = create_assessment(
        case_id="SH-1042",
        message_id="MSG-003",
        text=test_message
    )

    import json

    print("\nSAHAY ASSESSMENT")
    print("================")

    print(
        json.dumps(
            result,
            indent=4
        )
    )