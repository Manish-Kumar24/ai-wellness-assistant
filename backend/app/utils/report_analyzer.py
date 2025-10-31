# backend/app/utils/report_analyzer.py
import re
import pickle
import numpy as np
import os

# ==============================
# 🔹 ML MODEL INTEGRATION (Week-4, Day 1)
# ==============================

# Load ML model and label binarizer if available
MODEL_PATH = "ml/models/report_classifier.pkl"
model = None
mlb = None
MODEL_LOADED = False

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            model, mlb = pickle.load(f)
        MODEL_LOADED = True
        print("✅ ML report classifier loaded for analysis.")
    except Exception as e:
        print(f"⚠️ Failed to load ML model: {e}")

# ==============================
# 🔹 CORE ANALYSIS FUNCTION
# ==============================

def analyze_report(structured_data: dict):
    """
    Analyze structured lab results.
    - If ML model is available → use classifier
    - Else → fall back to rule-based logic (your original code)
    Returns list of findings with 'is_abnormal' flag.
    """
    if MODEL_LOADED:
        return _analyze_with_ml(structured_data)
    else:
        return _analyze_with_rules(structured_data)


# ==============================
# 🔹 ML-BASED ANALYSIS
# ==============================

def _analyze_with_ml(structured_data: dict):
    """Use trained ML classifier to predict conditions."""
    # Extract numeric values from structured_data
    def extract_value(key):
        if key not in structured_data:
            return None
        val = structured_data[key]
        if isinstance(val, dict) and "value" in val:
            return float(val["value"])
        elif isinstance(val, (int, float)):
            return float(val)
        else:
            # Handle string like "180 mg/dl"
            try:
                num = re.findall(r"\d+\.?\d*", str(val))
                return float(num[0]) if num else None
            except:
                return None

    # Build feature vector [glucose, hemoglobin, cholesterol, wbc]
    features = {
        "glucose": extract_value("glucose") or 100.0,
        "hemoglobin": extract_value("hemoglobin") or 14.0,
        "cholesterol": extract_value("cholesterol") or 200.0,
        "wbc": extract_value("wbc") or 7000.0,
    }

    # X = np.array([[features["glucose"], features["hemoglobin"], features["cholesterol"], features["wbc"]]])
    import pandas as pd

    X = pd.DataFrame([[
        features["glucose"],
        features["hemoglobin"],
        features["cholesterol"],
        features["wbc"]
    ]], columns=["glucose", "hemoglobin", "cholesterol", "wbc"])

    # Predict
    y_pred = model.predict(X)
    predicted_labels = mlb.inverse_transform(y_pred)[0]

    findings = []
    if len(predicted_labels) == 0:
        findings.append({
            "type": "general",
            "message": "No significant abnormalities detected.",
            "is_abnormal": False
        })
    else:
        # Map labels to user-friendly messages (same style as your rules)
        message_map = {
            "diabetes": lambda v: f"Glucose {v} → Possible diabetes risk",
            "prediabetes": lambda v: f"Glucose {v} → Prediabetic range",
            "anemia": lambda v: f"Hemoglobin {v} → Possible anemia risk",
            "polycythemia": lambda v: f"Hemoglobin {v} → Possible polycythemia",
            "high_cholesterol": lambda v: f"Cholesterol {v} → High cholesterol (risk of heart disease)",
            "leukopenia": lambda v: f"WBC {v} → Possible leukopenia (low immunity)",
            "infection": lambda v: f"WBC {v} → Possible infection / inflammation",
            "heart_disease": lambda v: f"High cholesterol ({v} mg/dL) → Elevated heart disease risk. Consult a cardiologist.",
        }

        # Get original values for messages
        orig_vals = {
            "glucose": extract_value("glucose"),
            "hemoglobin": extract_value("hemoglobin"),
            "cholesterol": extract_value("cholesterol"),
            "wbc": extract_value("wbc"),
        }

        for label in predicted_labels:
            val = None
            unit = "unknown"
            if label in ["diabetes", "prediabetes"]:
                val = orig_vals["glucose"] or features["glucose"]
                unit = "mg/dL"
            elif label in ["anemia", "polycythemia"]:
                val = orig_vals["hemoglobin"] or features["hemoglobin"]
                unit = "g/dL"
            elif label in ["high_cholesterol", "heart_disease"]:  # ← heart_disease uses cholesterol
                val = orig_vals["cholesterol"] or features["cholesterol"]
                unit = "mg/dL"
            elif label in ["leukopenia", "infection"]:
                val = orig_vals["wbc"] or features["wbc"]
                unit = "cells/μL"

            message = message_map.get(label, lambda v: f"Detected condition: {label}")(val)
            findings.append({
                "type": label,
                "value": val,
                "unit": unit,
                "message": message,
                "is_abnormal": True
            })

    return findings


# ==============================
# 🔹 RULE-BASED ANALYSIS (Your Original Code)
# ==============================

def _analyze_with_rules(structured_data: dict):
    """Fallback to your original rule-based logic."""
    findings = []

    # --- Hemoglobin ---
    if "hemoglobin" in structured_data:
        try:
            hb_value = float(re.findall(r"\d+\.?\d*", str(structured_data["hemoglobin"]))[0])
            if hb_value < 12.0:
                findings.append({
                    "type": "hemoglobin",
                    "value": hb_value,
                    "unit": "g/dL",
                    "message": f"Hemoglobin {hb_value} → Possible anemia risk",
                    "is_abnormal": True
                })
            elif hb_value > 16.5:
                findings.append({
                    "type": "hemoglobin",
                    "value": hb_value,
                    "unit": "g/dL",
                    "message": f"Hemoglobin {hb_value} → Possible polycythemia",
                    "is_abnormal": True
                })
        except Exception:
            pass

    # --- Glucose / Blood Sugar ---
    if "glucose" in structured_data or "blood sugar" in structured_data:
        glucose_value = structured_data.get("glucose") or structured_data.get("blood sugar")
        try:
            g_val = float(re.findall(r"\d+\.?\d*", str(glucose_value))[0])
            if g_val > 126:
                findings.append({
                    "type": "glucose",
                    "value": g_val,
                    "unit": "mg/dL",
                    "message": f"Glucose {g_val} → Possible diabetes risk",
                    "is_abnormal": True
                })
            elif g_val < 70:
                findings.append({
                    "type": "glucose",
                    "value": g_val,
                    "unit": "mg/dL",
                    "message": f"Glucose {g_val} → Possible hypoglycemia",
                    "is_abnormal": True
                })
        except Exception:
            pass

    # --- Cholesterol ---
    if "cholesterol" in structured_data:
        try:
            chol_val = float(re.findall(r"\d+\.?\d*", str(structured_data["cholesterol"]))[0])
            if chol_val > 200:
                findings.append({
                    "type": "cholesterol",
                    "value": chol_val,
                    "unit": "mg/dL",
                    "message": f"Cholesterol {chol_val} → High cholesterol (risk of heart disease)",
                    "is_abnormal": True
                })
        except Exception:
            pass

    # --- WBC ---
    if "wbc" in structured_data or "white blood cells" in structured_data:
        wbc_value = structured_data.get("wbc") or structured_data.get("white blood cells")
        try:
            w_val = float(re.findall(r"\d+\.?\d*", str(wbc_value))[0])
            if w_val < 4000:
                findings.append({
                    "type": "wbc",
                    "value": w_val,
                    "unit": "cells/μL",
                    "message": f"WBC {w_val} → Possible leukopenia (low immunity)",
                    "is_abnormal": True
                })
            elif w_val > 11000:
                findings.append({
                    "type": "wbc",
                    "value": w_val,
                    "unit": "cells/μL",
                    "message": f"WBC {w_val} → Possible infection / inflammation",
                    "is_abnormal": True
                })
        except Exception:
            pass

    # --- Default: no abnormalities ---
    if not findings:
        findings.append({
            "type": "general",
            "message": "No critical issues detected with basic rules. Consult a doctor for detailed analysis.",
            "is_abnormal": False
        })

    return findings