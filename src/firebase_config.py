import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate("./serviceAccountKey.json")

firebase_admin.initialize_app(cred)

db = firestore.client()


def get_message(case_id, message_id):
    message_ref = (
        db.collection("cases")
        .document(case_id)
        .collection("messages")
        .document(message_id)
    )

    message = message_ref.get()

    if not message.exists:
        return None

    return message.to_dict()


def save_assessment(case_id, assessment_id, assessment):
    assessment_ref = (
        db.collection("cases")
        .document(case_id)
        .collection("assessments")
        .document(assessment_id)
    )

    assessment_ref.set(assessment)


def update_case_latest(case_id, svi, risk_level):
    case_ref = db.collection("cases").document(case_id)

    case_ref.update({
        "latestSvi": svi,
        "latestRiskLevel": risk_level,
        "updatedAt": firestore.SERVER_TIMESTAMP
    })