# ml/retraining/test_feedback.py
import sqlite3
import json

def create_dummy_feedback():
    """Create dummy feedback entries for testing retraining pipeline."""
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    
    # Create a valid report log entry with structured_output as JSON string
    structured_output = json.dumps({
        "cholesterol": {"value": 200, "unit": "mg/dl"},
        "glucose": {"value": 100, "unit": "mg/dl"},
        "hemoglobin": {"value": 14, "unit": "g/dl"},
        "wbc": {"value": 7000, "unit": "cells/μL"}
    })
    
    analysis = json.dumps([{
        "type": "heart_disease",
        "value": 200,
        "unit": "mg/dL",
        "message": "High cholesterol (200.0 mg/dL) → Elevated heart disease risk.",
        "is_abnormal": True
    }])
    
    cursor.execute("""
        INSERT INTO report_logs (filename, raw_text, cleaned_text, structured_output, analysis)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "test_report.pdf",
        "Cholesterol: 200 mg/dl, Glucose: 100 mg/dl",
        "cholesterol: 200 mg/dl glucose: 100 mg/dl",
        structured_output,  # Valid JSON string
        analysis            # Valid JSON string
    ))
    report_id = cursor.lastrowid
    
    # Add feedback: correct "heart_disease" → "no_condition"
    cursor.execute("""
        INSERT INTO feedback_logs (log_type, original_prediction, corrected_label, report_log_id)
        VALUES (?, ?, ?, ?)
    """, (
        "report", 
        "heart_disease", 
        "no_condition", 
        report_id
    ))
    
    conn.commit()
    conn.close()
    print(f"✅ Dummy feedback created for report ID: {report_id}")
    print("   - Original prediction: heart_disease")
    print("   - Corrected label: no_condition")

if __name__ == "__main__":
    create_dummy_feedback()