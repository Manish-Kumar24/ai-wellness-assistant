# ml/training/train_symptom_classifier.py
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from ml.config import RAW_DATA_DIR, MODEL_SAVE_DIR, SYMPTOM_MODEL_PARAMS

def train_symptom_classifier():
    """Train symptom → disease classifier."""
    # Load symptom-disease CSV
    df = pd.read_csv(f"{RAW_DATA_DIR}/symptom_disease.csv")
    
    # Vectorize symptoms
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df["symptoms"])
    y = df["disease"]
    
    # Train model
    model = RandomForestClassifier(**SYMPTOM_MODEL_PARAMS)
    model.fit(X, y)
    
    # Save model + vectorizer
    with open(f"{MODEL_SAVE_DIR}/symptom_model.pkl", "wb") as f:
        pickle.dump((vectorizer, model), f)
    
    print("✅ Symptom classifier trained and saved!")

if __name__ == "__main__":
    train_symptom_classifier()