# ml/evaluation/evaluate_models.py
import json
import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, multilabel_confusion_matrix
from sklearn.model_selection import train_test_split
import pickle

# Ensure outputs directory exists
os.makedirs("outputs", exist_ok=True)

def evaluate_report_classifier():
    """Evaluate report-based condition classifier."""
    # Load preprocessed data
    df = pd.read_csv("ml/data/processed/heart_disease_processed.csv")
    
    # Prepare features and labels
    X = df[["glucose", "hemoglobin", "cholesterol", "wbc"]]
    y_true = df["heart_disease"]  # Binary label
    
    # Load trained model
    with open("ml/models/report_classifier.pkl", "rb") as f:
        model, mlb = pickle.load(f)
    
    # Predict
    y_pred = model.predict(X).flatten()
    
    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average='binary', zero_division=0
    )
    
    return {
        "model": "report_classifier",
        "task": "heart_disease_prediction",
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "support": int(np.sum(y_true))  # Number of positive cases
    }

def evaluate_symptom_classifier():
    """Evaluate symptom → disease classifier."""
    # Load symptom data
    df = pd.read_csv("ml/data/raw/symptom_disease.csv")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        df["symptoms"], df["disease"], test_size=0.2, random_state=42
    )
    
    # Load model
    with open("ml/models/symptom_model.pkl", "rb") as f:
        vectorizer, model = pickle.load(f)
    
    # Vectorize and predict
    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average='weighted', zero_division=0
    )
    
    return {
        "model": "symptom_classifier",
        "task": "symptom_to_disease",
        "metrics": {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "test_size": len(y_test)
    }

def generate_evaluation_report():
    """Generate full evaluation report."""
    report = {
        "evaluation_timestamp": pd.Timestamp.now().isoformat(),
        "models": [
            evaluate_report_classifier(),
            evaluate_symptom_classifier()
        ]
    }
    
    # Save to outputs/metrics.json
    with open("outputs/metrics.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("✅ Evaluation report saved to outputs/metrics.json")
    print("\n📊 MODEL METRICS:")
    for model in report["models"]:
        print(f"\n{model['model']} ({model['task']}):")
        for metric, value in model["metrics"].items():
            print(f"  {metric}: {value}")
    
    return report

if __name__ == "__main__":
    generate_evaluation_report()