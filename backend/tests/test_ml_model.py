import pickle
import os

def test_model_prediction():
    # Load vectorizer + model
    with open("ml_training/symptom_model.pkl", "rb") as f:
        vectorizer, model = pickle.load(f)

    sample = "fever cough"
    X = vectorizer.transform([sample])
    prediction = model.predict(X)[0]

    assert isinstance(prediction, str)  # should return a disease string
    assert prediction in ["Common Cold", "Migraine", "Flu", "Heart Disease"]
