from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.genai_service import generate_health_response
from app.db.session import SessionLocal
from app.db.models import Patient

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    patient_id: int | None = None  # Optional patient context

@router.post("/chat")
def chat(message: ChatMessage):
    try:
        # Get patient context if provided
        patient_context = ""
        if message.patient_id:
            db = SessionLocal()
            try:
                patient = db.query(Patient).filter(Patient.id == message.patient_id).first()
                if patient:
                    patient_context = f"Patient: {patient.name}, Age: {patient.age}, Gender: {patient.gender}"
            finally:
                db.close()

        # Generate GenAI response
        response = generate_health_response(message.message, patient_context)
        return {"response": response}
    
    except Exception as e:
        print(f"❌ GenAI error: {e}")
        return {
            "response": "I'm experiencing technical difficulties. For health concerns, please consult a doctor directly."
        }