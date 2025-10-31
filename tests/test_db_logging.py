from backend.app.db.models import ReportLog
from backend.app.db.session import SessionLocal

def test_report_log_creation(db_session):
    log = ReportLog(
        filename="test.pdf",
        raw_text="Glucose: 100",
        cleaned_text="glucose: 100",
        structured_output='{"glucose": {"value": 100, "unit": "mg/dL"}}',
        analysis='[{"type": "glucose", "is_abnormal": false}]'
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    
    assert log.id is not None
    assert log.filename == "test.pdf"
    assert "glucose" in log.structured_output