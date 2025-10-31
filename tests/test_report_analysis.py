from backend.app.utils.report_analyzer import analyze_report

def test_normal_values():
    data = {
        "hemoglobin": "14 g/dL",
        "glucose": "90 mg/dL",
        "cholesterol": "180 mg/dL"
    }
    result = analyze_report(data)
    assert len(result) == 1
    assert result[0]["is_abnormal"] is False

def test_abnormal_glucose():
    data = {"glucose": "180 mg/dL"}
    result = analyze_report(data)
    assert any(f["type"] == "glucose" and f["is_abnormal"] for f in result)

def test_abnormal_hemoglobin():
    data = {"hemoglobin": "10 g/dL"}
    result = analyze_report(data)
    assert any(f["type"] == "hemoglobin" and f["is_abnormal"] for f in result)