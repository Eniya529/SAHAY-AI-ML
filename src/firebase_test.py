from src.firebase_config import db


case_id = "SH-3177"
message_id = "MSG-001"

message_ref = (
    db.collection("cases")
      .document(case_id)
      .collection("messages")
      .document(message_id)
)

message = message_ref.get()

if message.exists:
    data = message.to_dict()

    print("Message found!")
    print("Case ID:", data.get("caseId"))
    print("Message ID:", data.get("messageId"))
    print("Sender:", data.get("sender"))
    print("Text:", data.get("text"))
    print("Input Type:", data.get("inputType"))
    print("Language:", data.get("language"))
else:
    print("Message not found!")