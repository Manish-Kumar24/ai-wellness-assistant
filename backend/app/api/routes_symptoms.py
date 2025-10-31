import pickle
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal  # ✅ Same as report route
from app.db.models import SymptomLog       # ✅ Defined in models.py
from pydantic import BaseModel

router = APIRouter()

# ✅ Load model ONCE at startup
MODEL_PATH = "ml/models/symptom_model.pkl"
vectorizer = None
model = None

try:
    with open(MODEL_PATH, "rb") as f:
        vectorizer, model = pickle.load(f)
    print("✅ Symptom prediction model loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load model from {MODEL_PATH}: {e}")


class SymptomRequest(BaseModel):
    symptoms: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/predict")
def predict_symptom(request: SymptomRequest, db: Session = Depends(get_db)):
    global vectorizer, model

    if vectorizer is None or model is None:
        raise HTTPException(status_code=500, detail="Symptom model not available")

    try:
        symptoms_text = request.symptoms.strip()
        if not symptoms_text:
            raise HTTPException(status_code=400, detail="Symptoms text is empty")

        # Predict
        X = vectorizer.transform([symptoms_text])
        prediction = model.predict(X)[0]

        # Save to same DB as reports
        log = SymptomLog(symptoms=symptoms_text, predicted_disease=prediction)
        db.add(log)
        db.commit()
        db.refresh(log)

        return {"prediction": prediction}

    except Exception as e:
        print(f"❌ Symptom prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")