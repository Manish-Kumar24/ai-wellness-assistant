import joblib
from pathlib import Path

MODEL_PATH = Path("backend/app/models/symptom_model.pkl")
model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None

def predict_disease(symptom_text: str):
    if not model:
        return {"error": "Model not loaded"}
    prediction = model.predict([symptom_text])
    return {"prediction": prediction[0]}