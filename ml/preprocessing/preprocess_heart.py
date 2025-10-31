# ml/preprocessing/preprocess_heart.py
import pandas as pd
import numpy as np
from ml.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

def preprocess_heart_data():
    """Convert UCI Heart Disease data to standardized format."""
    # Load raw data
    columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
    ]
    df = pd.read_csv(f"{RAW_DATA_DIR}/processed.cleveland.data", 
                     names=columns, na_values="?")
    
    # Clean data
    df = df.dropna()
    df["target"] = df["target"].apply(lambda x: 1 if x > 0 else 0)
    
    # Map to your biomarkers (fixed values for missing features)
    processed = []
    for _, row in df.iterrows():
        processed.append({
            "glucose": 100,          # Fixed normal
            "hemoglobin": 14,        # Fixed normal
            "cholesterol": row["chol"],
            "wbc": 7000,             # Fixed normal
            "heart_disease": row["target"]
        })
    
    # Save processed data
    pd.DataFrame(processed).to_csv(
        f"{PROCESSED_DATA_DIR}/heart_disease_processed.csv", index=False
    )
    print("✅ Heart disease data preprocessed and saved.")

if __name__ == "__main__":
    preprocess_heart_data()