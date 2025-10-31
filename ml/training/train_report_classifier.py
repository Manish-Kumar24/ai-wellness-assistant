# ml/training/train_report_classifier.py
import pandas as pd
import pickle
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from ml.config import (
    PROCESSED_DATA_DIR, MODEL_SAVE_DIR, 
    REPORT_FEATURES, REPORT_MODEL_PARAMS
)

def train_report_classifier():
    """Train multi-label classifier on preprocessed report data."""
    # Load data
    df = pd.read_csv(f"{PROCESSED_DATA_DIR}/heart_disease_processed.csv")
    
    # Prepare features
    X = df[REPORT_FEATURES]
    
    # Prepare labels (convert heart_disease to list)
    df["conditions"] = df["heart_disease"].apply(
        lambda x: ["heart_disease"] if x == 1 else []
    )
    mlb = MultiLabelBinarizer()
    y = mlb.fit_transform(df["conditions"])
    
    # Train model
    model = MultiOutputClassifier(
        RandomForestClassifier(**REPORT_MODEL_PARAMS)
    )
    model.fit(X, y)
    
    # Save model + label binarizer
    with open(f"{MODEL_SAVE_DIR}/report_classifier.pkl", "wb") as f:
        pickle.dump((model, mlb), f)
    
    print("✅ Report classifier trained and saved!")
    print("Labels:", mlb.classes_)

if __name__ == "__main__":
    train_report_classifier()