from src.assessment import create_assessment


# ============================================================
# SAHAY - COMPLETE AI / ML DEMONSTRATION
# ============================================================

CASE_ID = "SH-DEMO-1042"

# ------------------------------------------------------------
# FICTIONAL VICTIM CONVERSATION
# ------------------------------------------------------------
#
# The conversation is intentionally designed to demonstrate
# the different vulnerability indicators supported by SAHAY.
#
# Emotional:
#   fear, distress, anxiety, helplessness
#
# Contextual:
#   threat, retaliation, intimidation,
#   repeated contact, following
#
# Safety:
#   immediate safety, family safety, home safety,
#   workplace safety, extreme vulnerability,
#   isolation, inability to seek help
#
# ------------------------------------------------------------

conversation = [

    {
        "messageId": "MSG-DEMO-001",
        "sender": "victim",
        "text": (
            "I have been feeling very anxious and worried "
            "because these people keep contacting me. "
            "They keep calling and messaging me again and again."
        )
    },

    {
        "messageId": "MSG-DEMO-002",
        "sender": "victim",
        "text": (
            "They have threatened to harm me if I report what "
            "happened. They keep trying to intimidate me and "
            "pressure me into staying silent."
        )
    },

    {
        "messageId": "MSG-DEMO-003",
        "sender": "victim",
        "text": (
            "I am scared and frightened because I noticed that "
            "they were following me and watching me when I was "
            "returning home."
        )
    },

    {
        "messageId": "MSG-DEMO-004",
        "sender": "victim",
        "text": (
            "They came outside my house and my mother is also "
            "afraid. My family is worried about what might happen."
        )
    },

    {
        "messageId": "MSG-DEMO-005",
        "sender": "victim",
        "text": (
            "I feel completely helpless and overwhelmed. "
            "I feel powerless and I don't know what to do."
        )
    },

    {
        "messageId": "MSG-DEMO-006",
        "sender": "victim",
        "text": (
            "I am alone and I have nobody to help me. "
            "No one knows what is happening to me."
        )
    },

    {
        "messageId": "MSG-DEMO-007",
        "sender": "victim",
        "text": (
            "I cannot leave this situation and I cannot get help. "
            "I have no way to get help and I cannot escape."
        )
    },

    {
        "messageId": "MSG-DEMO-008",
        "sender": "victim",
        "text": (
            "They also know where I work and I am worried about "
            "what may happen to me at my workplace."
        )
    },

    {
        "messageId": "MSG-DEMO-009",
        "sender": "victim",
        "text": (
            "They are outside my house right now. "
            "I am not safe and I am currently in danger. "
            "I am terrified that they may hurt me or my family."
        )
    }
]


# ============================================================
# DISPLAY INPUT
# ============================================================

print("=" * 78)
print("                 SAHAY - AI / ML ASSESSMENT")
print("=" * 78)

print("\nCASE ID")
print("-" * 78)
print(CASE_ID)

print("\nINPUT TYPE")
print("-" * 78)
print("Voice / Text Conversation")

print("\nLANGUAGE")
print("-" * 78)
print("English")

print("\nVICTIM CONVERSATION")
print("-" * 78)

for index, message in enumerate(conversation, start=1):

    print(f"\nMessage {index}:")
    print(message["text"])


# ============================================================
# CURRENT MESSAGE
# ============================================================

current_message = conversation[-1]["text"]

previous_messages = conversation[:-1]


# ============================================================
# RUN SAHAY ML ASSESSMENT
# ============================================================

result = create_assessment(

    case_id=CASE_ID,

    message_id=conversation[-1]["messageId"],

    text=current_message,

    conversation_history=previous_messages,

    # Previous assessment values are provided so that the
    # demonstration can also show risk trend and escalation.
    previous_svi=72,

    previous_risk_level="HIGH",

    input_type="voice",

    language="en"
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 78)
print("                    AI ANALYSIS RESULT")
print("=" * 78)


# ------------------------------------------------------------
# RISK ASSESSMENT
# ------------------------------------------------------------

print("\nRISK ASSESSMENT")
print("-" * 78)

print(f"SVI                : {result['svi']}")
print(f"RISK LEVEL         : {result['riskLevel']}")
print(f"CONFIDENCE         : {result['confidence']}")
print(f"CONFIDENCE LEVEL   : {result['confidenceLevel']}")


# ------------------------------------------------------------
# RISK TREND
# ------------------------------------------------------------

print("\nRISK TREND")
print("-" * 78)

print(f"PREVIOUS SVI       : {result['previousSvi']}")
print(f"CURRENT SVI        : {result['svi']}")
print(f"SVI CHANGE         : {result['sviChange']}")
print(f"RISK TREND         : {result['riskTrend']}")


# ------------------------------------------------------------
# RISK ESCALATION
# ------------------------------------------------------------

print("\nRISK ESCALATION")
print("-" * 78)

print(f"PREVIOUS RISK      : {result['previousRiskLevel']}")
print(f"CURRENT RISK       : {result['riskLevel']}")
print(f"RISK ESCALATION    : {result['riskEscalation']}")


# ------------------------------------------------------------
# EMOTIONAL INDICATORS
# ------------------------------------------------------------

print("\nEMOTIONAL INDICATORS")
print("-" * 78)

if result["emotionalIndicators"]:

    for indicator in result["emotionalIndicators"]:
        print(f"• {indicator}")

else:

    print("None detected")


# ------------------------------------------------------------
# CONTEXTUAL INDICATORS
# ------------------------------------------------------------

print("\nCONTEXTUAL INDICATORS")
print("-" * 78)

if result["contextualIndicators"]:

    for indicator in result["contextualIndicators"]:
        print(f"• {indicator}")

else:

    print("None detected")


# ------------------------------------------------------------
# SAFETY INDICATORS
# ------------------------------------------------------------

print("\nSAFETY INDICATORS")
print("-" * 78)

if result["safetyIndicators"]:

    for indicator in result["safetyIndicators"]:
        print(f"• {indicator}")

else:

    print("None detected")


# ------------------------------------------------------------
# KEY EVIDENCE
# ------------------------------------------------------------

print("\nKEY EVIDENCE")
print("-" * 78)

for evidence in result["keyEvidence"]:

    print(f'• "{evidence}"')


# ------------------------------------------------------------
# EXPLAINABLE REASONING
# ------------------------------------------------------------

print("\nAI REASONING")
print("-" * 78)

print(result["reasoning"])


# ------------------------------------------------------------
# CONVERSATION CONTEXT
# ------------------------------------------------------------

print("\nCONVERSATION CONTEXT")
print("-" * 78)

context = result["conversationContext"]

print(
    f"History considered : "
    f"{context['historyConsidered']}"
)

print(
    f"Previous messages  : "
    f"{context['previousMessageCount']}"
)


# ------------------------------------------------------------
# ADAPTIVE QUESTION
# ------------------------------------------------------------

print("\nADAPTIVE FOLLOW-UP QUESTION")
print("-" * 78)

print(result["adaptiveQuestion"])


# ------------------------------------------------------------
# RECOMMENDED ACTION
# ------------------------------------------------------------

print("\nRECOMMENDED ACTION")
print("-" * 78)

print(result["recommendedAction"])


# ------------------------------------------------------------
# HUMAN REVIEW
# ------------------------------------------------------------

print("\nHUMAN REVIEW")
print("-" * 78)

print(
    f"Required           : "
    f"{result['requiresHumanReview']}"
)


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 78)
print("                  END OF ML ASSESSMENT")
print("=" * 78)