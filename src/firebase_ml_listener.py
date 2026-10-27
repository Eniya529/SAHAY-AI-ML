from google.cloud.firestore_v1 import SERVER_TIMESTAMP

from src.firebase_config import (
    db,
    save_assessment,
    update_case_latest
)

from src.assessment import create_assessment


# --------------------------------------------------
# 1. GET PREVIOUS VICTIM CONVERSATION
# --------------------------------------------------

def get_conversation_history(case_id, current_message_id):

    messages_ref = (
        db.collection("cases")
        .document(case_id)
        .collection("messages")
    )

    history = []

    try:

        documents = messages_ref.stream()

        for doc in documents:

            if doc.id == current_message_id:
                continue

            message = doc.to_dict()

            # Only victim messages
            if message.get("sender") != "victim":
                continue

            text = message.get("text", "")

            if not isinstance(text, str):
                continue

            text = text.strip()

            if not text:
                continue

            history.append({
                "messageId": doc.id,
                "text": text,
                "timestamp": message.get("timestamp")
            })

    except Exception as error:

        print(
            "Could not retrieve conversation history:"
        )

        print(error)

        return []

    # Keep only recent messages
    MAX_HISTORY_MESSAGES = 10

    history = history[-MAX_HISTORY_MESSAGES:]

    return history


# --------------------------------------------------
# 2. GET PREVIOUS ASSESSMENT
# --------------------------------------------------

def get_previous_assessment(
    case_id,
    current_message_id
):
    """
    Retrieve the most recent previous assessment
    for this case.

    The current message is excluded.

    Returns:
        {
            "assessmentId": ...,
            "messageId": ...,
            "svi": ...,
            "riskLevel": ...,
            "createdAt": ...
        }

        or None if no previous assessment exists.
    """

    assessments_ref = (
        db.collection("cases")
        .document(case_id)
        .collection("assessments")
    )

    assessments = []

    try:

        documents = assessments_ref.stream()

        for doc in documents:

            assessment = doc.to_dict()

            # Never compare against the current message
            if (
                assessment.get("messageId")
                == current_message_id
            ):
                continue

            svi = assessment.get("svi")

            risk_level = assessment.get(
                "riskLevel"
            )

            if not isinstance(
                svi,
                (int, float)
            ):
                continue

            if not isinstance(
                risk_level,
                str
            ):
                continue

            assessments.append({
                "assessmentId": doc.id,

                "messageId": assessment.get(
                    "messageId"
                ),

                "svi": float(svi),

                "riskLevel": risk_level,

                "createdAt": assessment.get(
                    "createdAt"
                )
            })

    except Exception as error:

        print(
            "Could not retrieve previous assessments:"
        )

        print(error)

        return None

    # No previous assessments
    if not assessments:

        return None

    # --------------------------------------------------
    # Sort by assessment creation time
    # --------------------------------------------------

    assessments.sort(
        key=lambda item: item.get(
            "createdAt"
        ) or ""
    )

    # Most recent previous assessment
    return assessments[-1]


# --------------------------------------------------
# 3. PROCESS NEW MESSAGE
# --------------------------------------------------

def process_message(message_doc):

    message = message_doc.to_dict()

    # --------------------------------------------------
    # Only process victim messages
    # --------------------------------------------------

    if message.get("sender") != "victim":

        return

    # --------------------------------------------------
    # Skip already processed messages
    # --------------------------------------------------

    if message.get("processed", False):

        return

    # --------------------------------------------------
    # Get text
    # --------------------------------------------------

    text = message.get(
        "text",
        ""
    )

    if not isinstance(text, str):
        return

    text = text.strip()

    if not text:

        return

    # --------------------------------------------------
    # Get input type
    # --------------------------------------------------

    input_type = message.get(
        "inputType",
        "text"
    )

    if not isinstance(input_type, str):
        input_type = "text"

    input_type = input_type.strip().lower()

    # --------------------------------------------------
    # Get language
    # --------------------------------------------------

    language = message.get(
        "language",
        "en"
    )

    if not isinstance(language, str):
        language = "en"

    language = language.strip().lower()

    # --------------------------------------------------
    # Get case ID
    # --------------------------------------------------

    case_id = message.get("caseId")

    if not case_id:

        print(
            "Skipping message: caseId missing"
        )

        return

    message_id = message_doc.id

    print("\n================================")

    print(
        "NEW VICTIM MESSAGE"
    )

    print(
        "Case ID:",
        case_id
    )

    print(
        "Message ID:",
        message_id
    )

    print(
        "Input Type:",
        input_type
    )

    print(
        "Language:",
        language
    )

    print(
        "Text:",
        text
    )

    # --------------------------------------------------
    # 4. GET CONVERSATION HISTORY
    # --------------------------------------------------

    conversation_history = (
        get_conversation_history(
            case_id=case_id,
            current_message_id=message_id
        )
    )

    print(
        "Previous victim messages:",
        len(conversation_history)
    )

    # --------------------------------------------------
    # 5. GET PREVIOUS ASSESSMENT
    # --------------------------------------------------

    previous_assessment = (
        get_previous_assessment(
            case_id=case_id,
            current_message_id=message_id
        )
    )

    # --------------------------------------------------
    # Extract previous SVI
    # --------------------------------------------------

    previous_svi = (
        previous_assessment["svi"]
        if previous_assessment
        else None
    )

    # --------------------------------------------------
    # Extract previous Risk Level
    # --------------------------------------------------

    previous_risk_level = (
        previous_assessment["riskLevel"]
        if previous_assessment
        else None
    )

    print(
        "Previous SVI:",
        previous_svi
    )

    print(
        "Previous Risk Level:",
        previous_risk_level
    )

    # --------------------------------------------------
    # 6. RUN ML ASSESSMENT
    # --------------------------------------------------

    assessment = create_assessment(

        case_id=case_id,

        message_id=message_id,

        text=text,

        conversation_history=conversation_history,

        previous_svi=previous_svi,

        previous_risk_level=previous_risk_level,

        input_type=input_type,

        language=language
    )

    # --------------------------------------------------
    # Check assessment result
    # --------------------------------------------------

    if assessment.get("status") != "SUCCESS":

        print(
            "ML assessment failed!"
        )

        return

    # --------------------------------------------------
    # 7. SAVE ASSESSMENT
    # --------------------------------------------------

    assessment_id = (
        assessment["assessmentId"]
    )

    save_assessment(

        case_id=case_id,

        assessment_id=assessment_id,

        assessment=assessment
    )

    # --------------------------------------------------
    # 8. UPDATE CASE LATEST DATA
    # --------------------------------------------------

    update_case_latest(

        case_id=case_id,

        svi=assessment["svi"],

        risk_level=assessment["riskLevel"]
    )

    # --------------------------------------------------
    # 9. MARK MESSAGE AS PROCESSED
    # --------------------------------------------------

    message_doc.reference.update({

        "processed": True,

        "processedAt": SERVER_TIMESTAMP,

        "assessmentId": assessment_id

    })

    # --------------------------------------------------
    # 10. PRINT RESULT
    # --------------------------------------------------

    print(
        "\nASSESSMENT CREATED"
    )

    print(
        "Assessment ID:",
        assessment["assessmentId"]
    )

    print(
        "Risk Level:",
        assessment["riskLevel"]
    )

    print(
        "SVI:",
        assessment["svi"]
    )

    print(
        "Confidence:",
        assessment["confidence"]
    )

    print(
        "Confidence Level:",
        assessment.get(
            "confidenceLevel"
        )
    )

    print(
        "Input Type:",
        assessment.get(
            "inputType"
        )
    )

    print(
        "Language:",
        assessment.get(
            "language"
        )
    )

    print(
        "Previous SVI:",
        assessment["previousSvi"]
    )

    print(
        "SVI Change:",
        assessment["sviChange"]
    )

    print(
        "Risk Trend:",
        assessment["riskTrend"]
    )

    print(
        "Previous Risk Level:",
        assessment[
            "previousRiskLevel"
        ]
    )

    print(
        "Risk Escalation:",
        assessment[
            "riskEscalation"
        ]
    )

    print(
        "Previous Messages Used:",
        assessment[
            "conversationContext"
        ][
            "previousMessageCount"
        ]
    )

    print(
        "Human Review:",
        assessment[
            "requiresHumanReview"
        ]
    )

    print(
        "================================"
    )


# --------------------------------------------------
# 11. FIREBASE SNAPSHOT LISTENER
# --------------------------------------------------

def on_messages_snapshot(
    collection_snapshot,
    changes,
    read_time
):

    for change in changes:

        if change.type.name == "ADDED":

            process_message(
                change.document
            )


# --------------------------------------------------
# 12. START LISTENER
# --------------------------------------------------

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "SAHAY ML FIREBASE LISTENER"
    )

    print(
        "Listening for new victim messages..."
    )

    print(
        "Conversation context: ENABLED"
    )

    print(
        "Risk trend: ENABLED"
    )

    print(
        "Risk escalation: ENABLED"
    )

    print(
        "Input type handling: ENABLED"
    )

    print(
        "Language handling: ENABLED"
    )

    print(
        "================================"
    )

    messages_query = (
        db.collection_group("messages")
    )

    messages_query.on_snapshot(
        on_messages_snapshot
    )

    # Keep listener running
    import threading

    threading.Event().wait()