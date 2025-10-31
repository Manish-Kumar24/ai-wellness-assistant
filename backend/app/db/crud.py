from sqlalchemy.orm import Session
from .models import SymptomLog

def create_log(db: Session, symptoms: str, prediction: str):
    log = SymptomLog(symptoms=symptoms, prediction=prediction)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
