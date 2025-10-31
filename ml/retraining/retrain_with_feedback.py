# ml/retraining/retrain_with_feedback.py
import pandas as pd
import sqlite3
import pickle
import os
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from ml.config import MODEL_SAVE_DIR, REPORT_FEATURES

def load_existing_training_data():
    """Load original UCI heart disease data."""
    df = pd.read_csv("ml/data/processed/heart_disease_processed.csv")
    return df

def load_feedback_data():
    """Load user feedback from SQLite DB and parse structured_output."""
    import sqlite3
    import pandas as pd
    import json

    conn = sqlite3.connect("app.db")
    query = """
    SELECT 
        r.structured_output,
        f.corrected_label
    FROM feedback_logs f
    JOIN report_logs r ON f.report_log_id = r.id
    WHERE f.log_type = 'report'
    """
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            print("ℹ️ No feedback records found in DB.")
            return pd.DataFrame()
        
        print(f"📥 Loaded {len(df)} feedback records.")
        
        # Parse structured_output safely
        def parse_lab_values(json_str):
            try:
                # Handle both string and dict (if already parsed)
                if isinstance(json_str, str):
                    data = json.loads(json_str)
                else:
                    data = json_str
                
                return {
                    "glucose": float(data.get("glucose", {}).get("value", 100)),
                    "hemoglobin": float(data.get("hemoglobin", {}).get("value", 14)),
                    "cholesterol": float(data.get("cholesterol", {}).get("value", 200)),
                    "wbc": float(data.get("wbc", {}).get("value", 7000))  # Default if missing
                }
            except Exception as e:
                print(f"⚠️ Error parsing structured_output: {e} | Input: {json_str}")
                return {
                    "glucose": 100.0,
                    "hemoglobin": 14.0,
                    "cholesterol": 200.0,
                    "wbc": 7000.0
                }
        
        # Apply parsing
        lab_values = df["structured_output"].apply(parse_lab_values)
        lab_df = pd.DataFrame(lab_values.tolist())
        
        # Add heart_disease label
        lab_df["heart_disease"] = df["corrected_label"].apply(
            lambda x: 1 if str(x).lower() in ["heart_disease", "yes", "true", "1"] else 0
        )
        
        print("✅ Feedback data parsed successfully.")
        return lab_df[["glucose", "hemoglobin", "cholesterol", "wbc", "heart_disease"]]
        
    except Exception as e:
        print(f"❌ Critical error in load_feedback_data: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return pd.DataFrame()
    """Load user feedback from SQLite DB and parse structured_output."""
    conn = sqlite3.connect("app.db")
    query = """
    SELECT 
        r.structured_output,
        f.corrected_label
    FROM feedback_logs f
    JOIN report_logs r ON f.report_log_id = r.id
    WHERE f.log_type = 'report'
    """
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
        
        # Parse structured_output JSON
        def parse_lab_values(json_str):
            try:
                import json
                data = json.loads(json_str)
                return {
                    "glucose": data.get("glucose", {}).get("value", 100),
                    "hemoglobin": data.get("hemoglobin", {}).get("value", 14),
                    "cholesterol": data.get("cholesterol", {}).get("value", 200),
                    "wbc": data.get("wbc", {}).get("value", 7000)
                }
            except:
                return {
                    "glucose": 100,
                    "hemoglobin": 14,
                    "cholesterol": 200,
                    "wbc": 7000
                }
        
        # Extract lab values
        lab_values = df["structured_output"].apply(parse_lab_values)
        lab_df = pd.DataFrame(lab_values.tolist())
        
        # Add corrected_label
        lab_df["corrected_label"] = df["corrected_label"]
        
        # Convert to heart_disease binary flag
        lab_df["heart_disease"] = lab_df["corrected_label"].apply(
            lambda x: 1 if x.lower() in ["heart_disease", "yes", "true"] else 0
        )
        
        return lab_df[["glucose", "hemoglobin", "cholesterol", "wbc", "heart_disease"]]
        
    except Exception as e:
        print(f"⚠️ Error loading feedback data: {e}")
        conn.close()
        return pd.DataFrame()
    

def retrain_report_model():
    """Retrain report classifier with original + feedback data."""
    # Load original data
    original_df = load_existing_training_data()
    print(f"📊 Original training  {len(original_df)} samples")
    
    # Load feedback data
    feedback_df = load_feedback_data()
    if feedback_df.empty:
        print("ℹ️ No feedback data available. Skipping retraining.")
        return False
    
    print(f"🔄 Feedback  {len(feedback_df)} samples")
    
    # Combine datasets
    combined_df = pd.concat([original_df, feedback_df], ignore_index=True)
    print(f"✅ Combined dataset: {len(combined_df)} samples")
    
    # Prepare features and labels
    X = combined_df[REPORT_FEATURES]
    y = combined_df["heart_disease"].apply(lambda x: ["heart_disease"] if x == 1 else [])
    
    # Binarize labels
    mlb = MultiLabelBinarizer()
    y_bin = mlb.fit_transform(y)
    
    # Retrain model
    model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100, random_state=42))
    model.fit(X, y_bin)
    
    # Save retrained model
    model_path = os.path.join(MODEL_SAVE_DIR, "report_classifier_retrained.pkl")
    with open(model_path, "wb") as f:
        pickle.dump((model, mlb), f)
    
    # Replace active model
    active_model_path = os.path.join(MODEL_SAVE_DIR, "report_classifier.pkl")
    with open(active_model_path, "wb") as f:
        pickle.dump((model, mlb), f)
    
    print(f"✅ Model retrained and saved to {active_model_path}")
    return True

if __name__ == "__main__":
    print("🔄 Starting retraining pipeline with user feedback...")
    success = retrain_report_model()
    if success:
        print("🎉 Retraining completed successfully!")
    else:
        print("ℹ️ Retraining skipped (no feedback data).")