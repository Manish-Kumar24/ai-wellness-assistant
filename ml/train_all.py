# ml/train_all.py
from ml.preprocessing.preprocess_heart import preprocess_heart_data
from ml.training.train_report_classifier import train_report_classifier
from ml.training.train_symptom_classifier import train_symptom_classifier
from ml.evaluation.evaluate_models import generate_evaluation_report  # ← Add this

if __name__ == "__main__":
    print("🚀 Starting full training pipeline...")
    
    # Preprocessing
    preprocess_heart_data()
    
    # Training
    train_symptom_classifier()
    train_report_classifier()
    
    # Evaluation
    generate_evaluation_report()  # ← Add this
    
    print("✅ All models trained and evaluated!")