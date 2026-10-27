from src.assessment import create_assessment


def test_assessment_returns_success():
    result = create_assessment(
        case_id="TEST-001",
        message_id="MSG-001",
        text="I am worried but I am currently safe."
    )

    assert result["status"] == "SUCCESS"
    assert result["caseId"] == "TEST-001"
    assert result["messageId"] == "MSG-001"


def test_empty_message():
    result = create_assessment(
        case_id="TEST-002",
        message_id="MSG-002",
        text=""
    )

    assert result["status"] == "ERROR"


def test_critical_message():
    result = create_assessment(
        case_id="TEST-003",
        message_id="MSG-003",
        text="They are outside my house right now and I am in immediate danger."
    )

    assert result["status"] == "SUCCESS"
    assert result["riskLevel"] in [
        "HIGH",
        "CRITICAL"
    ]