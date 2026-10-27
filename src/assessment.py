import joblib
from datetime import datetime

from src.indicators import (
    extract_emotional_indicators,
    extract_contextual_indicators,
    extract_safety_indicators,
    extract_key_evidence
)


MODEL_PATH = "model/risk_model.pkl"


# --------------------------------------------------
# 1. LOAD TRAINED ML MODEL
# --------------------------------------------------

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# 2. RISK PREDICTION
# --------------------------------------------------

def predict_risk(text):
    """
    Predict risk level and confidence from the
    current victim message.

    The ML model remains message-level.
    Conversation history is handled separately.
    """

    prediction = model.predict([text])[0]

    probabilities = model.predict_proba([text])[0]

    confidence = max(probabilities)

    return prediction, round(float(confidence), 2)


# --------------------------------------------------
# 3. CONFIDENCE-AWARE RISK HANDLING
# --------------------------------------------------

def calculate_confidence_level(confidence):
    """
    Convert model confidence into a human-readable
    confidence category.

    Thresholds:

        >= 0.80 -> HIGH_CONFIDENCE
        >= 0.60 -> MEDIUM_CONFIDENCE
        <  0.60 -> LOW_CONFIDENCE

    Note:
    This is a threshold-based interpretation of the
    model probability. It is not a formally calibrated
    probability.
    """

    if confidence is None:
        return "LOW_CONFIDENCE"

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        return "LOW_CONFIDENCE"

    if confidence >= 0.80:
        return "HIGH_CONFIDENCE"

    if confidence >= 0.60:
        return "MEDIUM_CONFIDENCE"

    return "LOW_CONFIDENCE"


# --------------------------------------------------
# 4. INPUT TYPE & LANGUAGE HANDLING
# --------------------------------------------------

def normalize_input_metadata(
    input_type,
    language
):
    """
    Normalize message input metadata.

    inputType examples:
        text
        voice
        image
        other

    language examples:
        en
        ta
        hi
    """

    # ------------------------------
    # Input type
    # ------------------------------

    if not isinstance(input_type, str):
        input_type = "text"

    input_type = input_type.strip().lower()

    if not input_type:
        input_type = "text"

    # ------------------------------
    # Language
    # ------------------------------

    if not isinstance(language, str):
        language = "en"

    language = language.strip().lower()

    if not language:
        language = "en"

    return input_type, language


# --------------------------------------------------
# 5. CONVERSATION CONTEXT
# --------------------------------------------------

def normalize_conversation_history(
    conversation_history,
    current_message_id=None
):
    """
    Normalize previous conversation messages.
    """

    if not conversation_history:
        return []

    normalized = []

    for message in conversation_history:

        if not isinstance(message, dict):
            continue

        message_id = message.get("messageId")

        if (
            current_message_id
            and message_id == current_message_id
        ):
            continue

        text = message.get("text", "")

        if not isinstance(text, str):
            continue

        text = text.strip()

        if not text:
            continue

        normalized.append({
            "messageId": message_id,
            "text": text
        })

    return normalized


def analyze_conversation_context(
    conversation_history,
    current_text
):
    """
    Analyze previous victim messages together with
    the current message.
    """

    messages = []

    for message in conversation_history:
        messages.append(message["text"])

    messages.append(current_text)

    emotional_indicators = set()
    contextual_indicators = set()
    safety_indicators = set()

    evidence = []

    for text in messages:

        emotional = extract_emotional_indicators(text)

        contextual = extract_contextual_indicators(text)

        safety = extract_safety_indicators(text)

        emotional_indicators.update(
            emotional
        )

        contextual_indicators.update(
            contextual
        )

        safety_indicators.update(
            safety
        )

        if (
            emotional
            or contextual
            or safety
        ):
            evidence.append(text)

    if current_text not in evidence:
        evidence.append(current_text)

    return {
        "emotionalIndicators": sorted(
            emotional_indicators
        ),

        "contextualIndicators": sorted(
            contextual_indicators
        ),

        "safetyIndicators": sorted(
            safety_indicators
        ),

        "evidence": evidence
    }


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
    Calculate a transparent prototype Stress
    Vulnerability Index.

    This is a heuristic risk-support score.
    It is NOT a clinical diagnosis or autonomous decision.
    """

    base_scores = {
        "LOW": 20,
        "MODERATE": 40,
        "HIGH": 65,
        "CRITICAL": 85
    }

    svi = base_scores.get(
        risk_level,
        0
    )

    # Emotional contribution
    svi += min(
        len(emotional_indicators) * 2,
        6
    )

    # Contextual contribution
    svi += min(
        len(contextual_indicators) * 2,
        6
    )

    # Safety contribution
    safety_weights = {

        "immediate_safety_concern": 6,

        "family_safety_concern": 3,

        "home_safety_concern": 4,

        "workplace_safety_concern": 3,

        "extreme_vulnerability": 4,

        "isolation": 4,

        "dependency_or_inability_to_seek_help": 5,

        "possible_self_harm_indicator": 8
    }

    safety_score = 0

    for indicator in safety_indicators:

        safety_score += safety_weights.get(
            indicator,
            0
        )

    svi += min(
        safety_score,
        20
    )

    return min(
        svi,
        100
    )


# --------------------------------------------------
# 7. RISK TREND
# --------------------------------------------------

def calculate_risk_trend(
    previous_svi,
    current_svi
):
    """
    Calculate the SVI trend compared with
    the previous assessment.
    """

    if previous_svi is None:

        return {
            "riskTrend": "NO_HISTORY",
            "previousSvi": None,
            "sviChange": 0
        }

    svi_change = current_svi - previous_svi

    if svi_change >= 10:

        trend = "RISING"

    elif svi_change <= -10:

        trend = "FALLING"

    else:

        trend = "STABLE"

    return {
        "riskTrend": trend,
        "previousSvi": previous_svi,
        "sviChange": svi_change
    }


# --------------------------------------------------
# 8. RISK ESCALATION
# --------------------------------------------------

def calculate_risk_escalation(
    previous_risk_level,
    current_risk_level
):
    """
    Detect whether the current risk category
    has escalated compared with the previous assessment.

    Risk order:

    LOW < MODERATE < HIGH < CRITICAL
    """

    risk_order = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    # No previous assessment
    if previous_risk_level is None:

        return {
            "riskEscalation": False,
            "previousRiskLevel": None
        }

    previous_score = risk_order.get(
        previous_risk_level
    )

    current_score = risk_order.get(
        current_risk_level
    )

    # Unknown risk level
    if (
        previous_score is None
        or current_score is None
    ):

        return {
            "riskEscalation": False,
            "previousRiskLevel": previous_risk_level
        }

    escalation = (
        current_score > previous_score
    )

    return {
        "riskEscalation": escalation,
        "previousRiskLevel": previous_risk_level
    }


# --------------------------------------------------
# 9. ADAPTIVE QUESTION INTELLIGENCE
# --------------------------------------------------

def generate_adaptive_question(
    risk_level,
    safety_indicators,
    contextual_indicators=None,
    emotional_indicators=None,
    conversation_history=None
):
    """
    Generate a context-aware, safety-oriented
    follow-up question.
    """

    if safety_indicators is None:
        safety_indicators = []

    if contextual_indicators is None:
        contextual_indicators = []

    if emotional_indicators is None:
        emotional_indicators = []

    if conversation_history is None:
        conversation_history = []

    safety = set(
        safety_indicators
    )

    contextual = set(
        contextual_indicators
    )

    emotional = set(
        emotional_indicators
    )

    # --------------------------------------------------
    # PRIORITY 1: IMMEDIATE SAFETY
    # --------------------------------------------------

    if "immediate_safety_concern" in safety:

        return (
            "Are you currently in a safe place?"
        )

    # --------------------------------------------------
    # PRIORITY 2: POSSIBLE SELF-HARM
    # --------------------------------------------------

    if "possible_self_harm_indicator" in safety:

        return (
            "Are you currently in immediate danger "
            "or at risk of hurting yourself?"
        )

    # --------------------------------------------------
    # PRIORITY 3: CANNOT SEEK HELP / ESCAPE
    # --------------------------------------------------

    if (
        "dependency_or_inability_to_seek_help"
        in safety
    ):

        return (
            "Is there someone you trust who can help "
            "you stay safe right now?"
        )

    # --------------------------------------------------
    # PRIORITY 4: HOME SAFETY
    # --------------------------------------------------

    if "home_safety_concern" in safety:

        return (
            "Are you currently away from the person "
            "or situation causing the concern?"
        )

    # --------------------------------------------------
    # PRIORITY 5: FAMILY SAFETY
    # --------------------------------------------------

    if "family_safety_concern" in safety:

        return (
            "Is your family currently safe?"
        )

    # --------------------------------------------------
    # PRIORITY 6: WORKPLACE SAFETY
    # --------------------------------------------------

    if "workplace_safety_concern" in safety:

        return (
            "Do you feel safe at your workplace right now?"
        )

    # --------------------------------------------------
    # PRIORITY 7: FOLLOWING / TRACKING
    # --------------------------------------------------

    if "following" in contextual:

        return (
            "Do you know where the person is currently, "
            "or are they still following or tracking you?"
        )

    # --------------------------------------------------
    # PRIORITY 8: REPEATED CONTACT
    # --------------------------------------------------

    if "repeated_contact" in contextual:

        return (
            "Are they still contacting or approaching "
            "you now?"
        )

    # --------------------------------------------------
    # PRIORITY 9: THREAT
    # --------------------------------------------------

    if "threat" in contextual:

        return (
            "Has the person made any recent threats "
            "toward you or your family?"
        )

    # --------------------------------------------------
    # PRIORITY 10: INTIMIDATION
    # --------------------------------------------------

    if "intimidation" in contextual:

        return (
            "Are they currently pressuring or intimidating "
            "you to do something?"
        )

    # --------------------------------------------------
    # PRIORITY 11: EXTREME VULNERABILITY
    # --------------------------------------------------

    if "extreme_vulnerability" in safety:

        return (
            "Do you have a safe person or place "
            "you can reach right now?"
        )

    # --------------------------------------------------
    # PRIORITY 12: ISOLATION
    # --------------------------------------------------

    if "isolation" in safety:

        return (
            "Is there someone you trust that you can "
            "contact for support?"
        )

    # --------------------------------------------------
    # PRIORITY 13: FEAR / DISTRESS / ANXIETY
    # --------------------------------------------------

    if (
        "fear" in emotional
        or "distress" in emotional
        or "anxiety" in emotional
    ):

        return (
            "What is making you feel most unsafe "
            "or worried right now?"
        )

    # --------------------------------------------------
    # PRIORITY 14: CRITICAL RISK
    # --------------------------------------------------

    if risk_level == "CRITICAL":

        return (
            "Are you currently in immediate danger?"
        )

    # --------------------------------------------------
    # PRIORITY 15: HIGH RISK
    # --------------------------------------------------

    if risk_level == "HIGH":

        return (
            "Has the person threatened, contacted, "
            "or approached you recently?"
        )

    # --------------------------------------------------
    # PRIORITY 16: MODERATE RISK
    # --------------------------------------------------

    if risk_level == "MODERATE":

        return (
            "Do you feel safe at the moment?"
        )

    # --------------------------------------------------
    # PRIORITY 17: LOW / GENERAL
    # --------------------------------------------------

    return (
        "Would you like to share anything else "
        "about what happened?"
    )


# --------------------------------------------------
# 10. RECOMMENDED ACTION
# --------------------------------------------------

def generate_recommended_action(
    risk_level,
    confidence,
    safety_indicators
):
    """
    Generate a human-review-oriented recommendation.
    """

    if (
        "possible_self_harm_indicator"
        in safety_indicators
    ):

        return (
            "Priority human review recommended due to "
            "a possible self-harm safety indicator."
        )

    if (
        "immediate_safety_concern"
        in safety_indicators
    ):

        return (
            "Priority human review recommended due to "
            "an immediate safety concern."
        )

    advanced_safety_indicators = {
        "extreme_vulnerability",
        "isolation",
        "dependency_or_inability_to_seek_help"
    }

    if any(
        indicator in safety_indicators
        for indicator in advanced_safety_indicators
    ):

        return (
            "Human review recommended due to advanced "
            "safety or vulnerability indicators."
        )

    if risk_level == "CRITICAL":

        return (
            "Priority human review recommended."
        )

    if risk_level == "HIGH":

        return (
            "Urgent human review recommended."
        )

    if risk_level == "MODERATE":

        return (
            "Human review recommended for further assessment."
        )

    if confidence < 0.60:

        return (
            "Low-confidence prediction; human review recommended."
        )

    return (
        "Continue monitoring and reassessment."
    )


# --------------------------------------------------
# 11. HUMAN REVIEW
# --------------------------------------------------

def requires_human_review(
    risk_level,
    confidence,
    safety_indicators
):
    """
    Determine whether human review is required.
    """

    if risk_level in [
        "HIGH",
        "CRITICAL"
    ]:

        return True

    if confidence < 0.60:

        return True

    review_indicators = {

        "immediate_safety_concern",

        "extreme_vulnerability",

        "isolation",

        "dependency_or_inability_to_seek_help",

        "possible_self_harm_indicator"
    }

    if any(
        indicator in safety_indicators
        for indicator in review_indicators
    ):

        return True

    return False


# --------------------------------------------------
# 12. EXPLAINABLE REASONING
# --------------------------------------------------

def generate_reasoning(
    risk_level,
    emotional_indicators,
    contextual_indicators,
    safety_indicators,
    previous_message_count=0
):
    """
    Generate transparent reasoning based on
    detected indicators and conversation context.
    """

    reasons = []

    if emotional_indicators:

        reasons.append(
            "emotional indicators detected: "
            + ", ".join(emotional_indicators)
        )

    if contextual_indicators:

        reasons.append(
            "contextual risk indicators detected: "
            + ", ".join(contextual_indicators)
        )

    if safety_indicators:

        reasons.append(
            "safety indicators detected: "
            + ", ".join(safety_indicators)
        )

    if previous_message_count > 0:

        reasons.append(
            f"conversation context included "
            f"{previous_message_count} previous victim message(s)"
        )

    if not reasons:

        return (
            "No strong risk indicators were detected "
            "in the message."
        )

    return (
        f"The assessment was classified as {risk_level} "
        "based on "
        + "; ".join(reasons)
        + "."
    )


# --------------------------------------------------
# 13. COMPLETE ASSESSMENT
# --------------------------------------------------

def create_assessment(
    case_id,
    message_id,
    text,
    conversation_history=None,
    previous_svi=None,
    previous_risk_level=None,
    input_type="text",
    language="en"
):
    """
    Create the complete SAHAY ML assessment.

    input_type:
        Source of the victim message, such as
        text or voice.

    language:
        Language code associated with the message.

    previous_svi and previous_risk_level are optional
    values supplied by the Firebase layer.
    """

    # --------------------------------------------------
    # Validate current message
    # --------------------------------------------------

    if not text or not text.strip():

        return {
            "status": "ERROR",
            "error": "Empty victim message."
        }

    text = text.strip()

    # --------------------------------------------------
    # Normalize input metadata
    # --------------------------------------------------

    input_type, language = normalize_input_metadata(
        input_type,
        language
    )

    # --------------------------------------------------
    # Normalize conversation history
    # --------------------------------------------------

    conversation_history = normalize_conversation_history(
        conversation_history,
        current_message_id=message_id
    )

    # --------------------------------------------------
    # ML risk prediction
    # --------------------------------------------------

    risk_level, confidence = predict_risk(
        text
    )

    # --------------------------------------------------
    # Confidence level
    # --------------------------------------------------

    confidence_level = calculate_confidence_level(
        confidence
    )

    # --------------------------------------------------
    # Conversation analysis
    # --------------------------------------------------

    conversation_analysis = (
        analyze_conversation_context(
            conversation_history,
            text
        )
    )

    emotional_indicators = (
        conversation_analysis[
            "emotionalIndicators"
        ]
    )

    contextual_indicators = (
        conversation_analysis[
            "contextualIndicators"
        ]
    )

    safety_indicators = (
        conversation_analysis[
            "safetyIndicators"
        ]
    )

    # --------------------------------------------------
    # Key evidence
    # --------------------------------------------------

    key_evidence = conversation_analysis[
        "evidence"
    ]

    # --------------------------------------------------
    # SVI
    # --------------------------------------------------

    svi = calculate_svi(
        risk_level,
        emotional_indicators,
        contextual_indicators,
        safety_indicators
    )

    # --------------------------------------------------
    # Risk trend
    # --------------------------------------------------

    risk_trend = calculate_risk_trend(
        previous_svi,
        svi
    )

    # --------------------------------------------------
    # Risk escalation
    # --------------------------------------------------

    risk_escalation = calculate_risk_escalation(
        previous_risk_level,
        risk_level
    )

    # --------------------------------------------------
    # Adaptive question
    # --------------------------------------------------

    adaptive_question = generate_adaptive_question(
        risk_level,
        safety_indicators,
        contextual_indicators,
        emotional_indicators,
        conversation_history
    )

    # --------------------------------------------------
    # Recommended action
    # --------------------------------------------------

    recommended_action = (
        generate_recommended_action(
            risk_level,
            confidence,
            safety_indicators
        )
    )

    # --------------------------------------------------
    # Human review
    # --------------------------------------------------

    human_review = requires_human_review(
        risk_level,
        confidence,
        safety_indicators
    )

    # --------------------------------------------------
    # Explainability
    # --------------------------------------------------

    reasoning = generate_reasoning(
        risk_level,
        emotional_indicators,
        contextual_indicators,
        safety_indicators,
        previous_message_count=len(
            conversation_history
        )
    )

    # --------------------------------------------------
    # Conversation metadata
    # --------------------------------------------------

    conversation_context = {

        "historyConsidered": (
            len(conversation_history) > 0
        ),

        "previousMessageCount": (
            len(conversation_history)
        ),

        "previousMessageIds": [
            message.get("messageId")
            for message in conversation_history
            if message.get("messageId")
        ]
    }

    # --------------------------------------------------
    # Final assessment
    # --------------------------------------------------

    assessment = {

        "status": "SUCCESS",

        "assessmentId": (
            f"ASM-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        ),

        "caseId": case_id,

        "messageId": message_id,

        # Input metadata
        "inputType": input_type,

        "language": language,

        # Risk
        "svi": svi,

        "riskLevel": risk_level,

        # Confidence
        "confidence": confidence,

        "confidenceLevel": confidence_level,

        # Risk trend
        "riskTrend": risk_trend["riskTrend"],

        "previousSvi": risk_trend["previousSvi"],

        "sviChange": risk_trend["sviChange"],

        # Risk escalation
        "riskEscalation": (
            risk_escalation["riskEscalation"]
        ),

        "previousRiskLevel": (
            risk_escalation["previousRiskLevel"]
        ),

        # Indicators
        "emotionalIndicators": emotional_indicators,

        "contextualIndicators": contextual_indicators,

        "safetyIndicators": safety_indicators,

        # Evidence
        "keyEvidence": key_evidence,

        # Explainability
        "reasoning": reasoning,

        # Officer support
        "adaptiveQuestion": adaptive_question,

        "recommendedAction": recommended_action,

        "requiresHumanReview": human_review,

        # Conversation
        "conversationContext": conversation_context,

        # Timestamp
        "createdAt": datetime.now().isoformat()
    }

    return assessment


# --------------------------------------------------
# 14. LOCAL TEST
# --------------------------------------------------

if __name__ == "__main__":

    import json

    # --------------------------------------------------
    # Risk escalation tests
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "RISK ESCALATION TESTS"
    )

    print(
        "========================================"
    )

    escalation_tests = [

        ("LOW", "MODERATE"),

        ("MODERATE", "HIGH"),

        ("HIGH", "CRITICAL"),

        ("CRITICAL", "HIGH"),

        ("HIGH", "HIGH")
    ]

    for previous, current in escalation_tests:

        result = calculate_risk_escalation(
            previous,
            current
        )

        print(
            previous,
            "->",
            current,
            ":",
            result
        )

    # --------------------------------------------------
    # Risk trend test
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "RISK TREND TEST"
    )

    print(
        "========================================"
    )

    trend_result = calculate_risk_trend(
        previous_svi=95,
        current_svi=84
    )

    print(
        json.dumps(
            trend_result,
            indent=4
        )
    )

    # --------------------------------------------------
    # Confidence level tests
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "CONFIDENCE LEVEL TESTS"
    )

    print(
        "========================================"
    )

    confidence_tests = [
        0.95,
        0.84,
        0.72,
        0.60,
        0.59,
        0.42
    ]

    for confidence in confidence_tests:

        print(
            confidence,
            "->",
            calculate_confidence_level(
                confidence
            )
        )

    # --------------------------------------------------
    # Input metadata tests
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "INPUT TYPE / LANGUAGE TESTS"
    )

    print(
        "========================================"
    )

    metadata_tests = [

        ("text", "en"),

        ("voice", "en"),

        ("voice", "ta"),

        (None, None),

        ("", "")
    ]

    for input_type, language in metadata_tests:

        normalized_type, normalized_language = (
            normalize_input_metadata(
                input_type,
                language
            )
        )

        print(
            input_type,
            language,
            "->",
            normalized_type,
            normalized_language
        )

    # --------------------------------------------------
    # Adaptive question tests
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "ADAPTIVE QUESTION TESTS"
    )

    print(
        "========================================"
    )

    adaptive_tests = [

        {
            "name": "Immediate safety",
            "risk": "CRITICAL",
            "safety": [
                "immediate_safety_concern"
            ],
            "contextual": [],
            "emotional": [
                "fear"
            ]
        },

        {
            "name": "Family safety",
            "risk": "HIGH",
            "safety": [
                "family_safety_concern"
            ],
            "contextual": [
                "threat"
            ],
            "emotional": [
                "fear"
            ]
        },

        {
            "name": "Repeated contact",
            "risk": "HIGH",
            "safety": [],
            "contextual": [
                "repeated_contact"
            ],
            "emotional": []
        },

        {
            "name": "Emotional distress",
            "risk": "MODERATE",
            "safety": [],
            "contextual": [],
            "emotional": [
                "distress"
            ]
        }
    ]

    for test in adaptive_tests:

        question = generate_adaptive_question(

            risk_level=test["risk"],

            safety_indicators=test["safety"],

            contextual_indicators=test["contextual"],

            emotional_indicators=test["emotional"],

            conversation_history=[]
        )

        print(
            "\nTest:",
            test["name"]
        )

        print(
            "Question:",
            question
        )

    # --------------------------------------------------
    # Conversation test
    # --------------------------------------------------

    print(
        "\n========================================"
    )

    print(
        "CONVERSATION CONTEXT TEST"
    )

    print(
        "========================================"
    )

    conversation_history = [

        {
            "messageId": "MSG-001",
            "text": "They keep contacting me."
        },

        {
            "messageId": "MSG-002",
            "text": "I told them to stop."
        }
    ]

    current_message = (
        "They are outside my house now."
    )

    conversation_result = create_assessment(

        case_id="SH-TEST",

        message_id="MSG-003",

        text=current_message,

        conversation_history=conversation_history,

        previous_svi=72,

        previous_risk_level="HIGH",

        input_type="voice",

        language="en"
    )

    print(
        json.dumps(
            conversation_result,
            indent=4
        )
    )