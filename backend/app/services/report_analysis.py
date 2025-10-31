# backend/app/services/report_analysis.py

def analyze_report(structured_data: dict):
    """
    Analyze structured medical report data using simple rules.
    Args:
        structured_data: dict with fields like {"Hemoglobin": "10 g/dL", "Glucose": "180 mg/dL"}
    Returns:
        dict with findings and risk flags
    """

    findings = []

    # Rule: Hemoglobin low → Anemia risk
    if "Hemoglobin" in structured_data:
        try:
            value = float(structured_data["Hemoglobin"].split()[0])
            if value < 12:
                findings.append("Low Hemoglobin → Possible Anemia")
            elif value > 17:
                findings.append("High Hemoglobin → Polycythemia risk")
        except Exception:
            findings.append("Unable to parse Hemoglobin value")

    # Rule: Glucose level
    if "Glucose" in structured_data:
        try:
            value = float(structured_data["Glucose"].split()[0])
            if value > 140:
                findings.append("High Glucose → Possible Diabetes")
            elif value < 70:
                findings.append("Low Glucose → Hypoglycemia")
        except Exception:
            findings.append("Unable to parse Glucose value")

    # Rule: Blood Pressure (format: "120/80 mmHg")
    if "Blood Pressure" in structured_data:
        try:
            bp_str = structured_data["Blood Pressure"].split()[0]
            systolic, diastolic = map(int, bp_str.split("/"))
            if systolic > 140 or diastolic > 90:
                findings.append("High BP → Hypertension risk")
            elif systolic < 90 or diastolic < 60:
                findings.append("Low BP → Hypotension risk")
        except Exception:
            findings.append("Unable to parse Blood Pressure value")

    return {"findings": findings}
