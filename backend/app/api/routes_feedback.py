from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import FeedbackLog

router = APIRouter()

class FeedbackRequest(BaseModel):
    log_type: str  # "symptom" or "report"
    original_prediction: str
    corrected_label: str
    user_comment: str | None = None
    report_log_id: int | None = None
    symptom_log_id: int | None = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/feedback")
def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    try:
        # Validate log_type
        if feedback.log_type not in ["symptom", "report"]:
            raise HTTPException(status_code=400, detail="log_type must be 'symptom' or 'report'")
        
        # Validate foreign key consistency
        if feedback.log_type == "report" and not feedback.report_log_id:
            raise HTTPException(status_code=400, detail="report_log_id required for report feedback")
        if feedback.log_type == "symptom" and not feedback.symptom_log_id:
            raise HTTPException(status_code=400, detail="symptom_log_id required for symptom feedback")

        feedback_log = FeedbackLog(
            log_type=feedback.log_type,
            original_prediction=feedback.original_prediction,
            corrected_label=feedback.corrected_label,
            user_comment=feedback.user_comment,
            report_log_id=feedback.report_log_id,
            symptom_log_id=feedback.symptom_log_id
        )
        db.add(feedback_log)
        db.commit()
        db.refresh(feedback_log)
        
        return {"message": "Feedback recorded successfully", "feedback_id": feedback_log.id}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")