from src.firebase_config import (
    db,
    save_assessment,
    update_case_latest
)

from src.assessment import create_assessment


def process_new_messages():
    cases_ref = db.collection("cases")
    cases = cases_ref.stream()

    for case in cases:
        case_id = case.id

        messages_ref = (
            cases_ref
            .document(case_id)
            .collection("messages")
        )

        messages = messages_ref.stream()

        for message_doc in messages:
            message = message_doc.to_dict()

            # Only process victim messages
            if message.get("sender") != "victim":
                continue

            # Skip already processed messages
            if message.get("processed", False):
                continue

            message_id = message_doc.id
            text = message.get("text", "").strip()

            if not text:
                continue

            print("\n--------------------------------")
            print("Processing message")
            print("Case ID:", case_id)
            print("Message ID:", message_id)
            print("Text:", text)

            # Run ML assessment
            assessment = create_assessment(
                case_id=case_id,
                message_id=message_id,
                text=text
            )

            # Check assessment status
            if assessment.get("status") != "SUCCESS":
                print("Assessment failed!")
                continue

            # Save assessment to Firebase
            assessment_id = assessment["assessmentId"]

            save_assessment(
                case_id=case_id,
                assessment_id=assessment_id,
                assessment=assessment
            )

            # Update latest case information
            update_case_latest(
                case_id=case_id,
                svi=assessment["svi"],
                risk_level=assessment["riskLevel"]
            )

            # Mark message as processed
            message_doc.reference.update({
                "processed": True
            })

            print("Assessment saved!")
            print("Assessment ID:", assessment_id)
            print("Risk Level:", assessment["riskLevel"])
            print("SVI:", assessment["svi"])


if __name__ == "__main__":
    process_new_messages()