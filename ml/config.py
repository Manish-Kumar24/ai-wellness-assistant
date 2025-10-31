# ml/config.py
import os

# Paths
RAW_DATA_DIR = "ml/data/raw"
PROCESSED_DATA_DIR = "ml/data/processed"
MODEL_SAVE_DIR = "ml/models"

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(MODEL_SAVE_DIR, exist_ok=True)

# Model parameters
SYMPTOM_MODEL_PARAMS = {
    "n_estimators": 100,
    "random_state": 42
}

REPORT_MODEL_PARAMS = {
    "n_estimators": 100,
    "random_state": 42
}

# Feature columns
REPORT_FEATURES = ["glucose", "hemoglobin", "cholesterol", "wbc"]
SYMPTOM_FEATURES = ["symptoms"]