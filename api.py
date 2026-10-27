from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.assessment import create_assessment

app = FastAPI(
    title="SAHAY ML Intelligence API",
    description="AI-powered victim vulnerability and risk assessment service",
    version="1.0.0"
)


class AssessmentRequest(BaseModel):
    caseId: str
    messageId: str
    text: str
    inputType: str = "text"
    language: str = "en"


@app.get("/")
def root():
    return {
        "service": "SAHAY ML Intelligence API",
        "status": "running"
    }
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SAHAY ML Intelligence API",
        "model": "risk_model.pkl"
    }


@app.post("/assess")
def assess_victim(request: AssessmentRequest):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Message text cannot be empty"
        )

    try:
        assessment = create_assessment(
            text=request.text,
            case_id=request.caseId,
            message_id=request.messageId
        )

        return assessment

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Assessment processing failed"
        )