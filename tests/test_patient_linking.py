from backend.app.db.models import Patient, ReportLog

def test_patient_creation(db_session):
    patient = Patient(name="Test User", age=30, gender="Male")
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    
    assert patient.id is not None
    assert patient.name == "Test User"

def test_link_report_to_patient(db_session):
    # Create patient
    patient = Patient(name="Alice", age=25, gender="Female")
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    
    # Create report linked to patient
    report = ReportLog(
        filename="lab.pdf",
        raw_text="Hemoglobin: 11",
        cleaned_text="hemoglobin: 11",
        structured_output='{"hemoglobin": {"value": 11, "unit": "g/dL"}}',
        analysis='[{"type": "hemoglobin", "is_abnormal": true}]',
        patient_id=patient.id
    )
    db_session.add(report)
    db_session.commit()
    db_session.refresh(report)
    
    assert report.patient_id == patient.id
    assert report.patient.name == "Alice"