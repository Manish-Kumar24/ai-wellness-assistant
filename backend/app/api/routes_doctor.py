from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, Patient, ReportLog
from app.schemas import PatientCreate, PatientResponse
from app.api.deps import get_current_user  # Ensure this exists

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_doctor(current_user: User = Depends(get_current_user)):
    """Ensure user is a doctor"""
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Doctors only"
        )
    return current_user

@router.get("/patients", response_model=list[PatientResponse])
def get_all_patients_for_doctor(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Doctors can view ALL patients
    """
    patients = db.query(Patient).all()
    return patients

@router.post("/patients", response_model=PatientResponse)
def create_patient_for_doctor(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Doctors can create patients (without linking to user)
    """
    db_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        contact=patient.contact
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/patients/{patient_id}/reports")
def get_patient_reports_for_doctor(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Doctors can view ALL reports for any patient
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Get all reports for this patient
    reports = db.query(ReportLog).filter(ReportLog.patient_id == patient_id).all()
    
    report_list = []
    for report in reports:
        report_list.append({
            "id": report.id,
            "filename": report.filename,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "structured_output": report.structured_output,
            "analysis": report.analysis,
        })
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "total_reports": len(reports),
        "reports": report_list
    }

@router.get("/dashboard_stats")
def get_doctor_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Doctor-specific dashboard stats (all patients + reports)
    """
    total_patients = db.query(Patient).count()
    total_reports = db.query(ReportLog).count()
    
    # Reports with abnormalities
    reports_with_abnormal = 0
    abnormal_findings = []
    
    all_reports = db.query(ReportLog).all()
    for report in all_reports:
        if report.analysis:
            try:
                import json
                analysis = json.loads(report.analysis)
                if isinstance(analysis, list):
                    for finding in analysis:
                        if isinstance(finding, dict) and finding.get("is_abnormal", False):
                            reports_with_abnormal += 1
                            abnormal_findings.append(finding.get("type", "unknown"))
                            break
            except (json.JSONDecodeError, TypeError):
                continue
    
    from collections import Counter
    abnormal_counter = Counter(abnormal_findings)
    top_abnormalities = [
        {"finding": finding, "count": count}
        for finding, count in abnormal_counter.most_common(5)
    ]
    
    # Recent activity (last 7 days)
    from sqlalchemy import text
    last_7_days = db.query(ReportLog).filter(
        ReportLog.created_at >= text("NOW() - INTERVAL '7 days'")
    ).count()
    
    return {
        "summary": {
            "total_patients": total_patients,
            "total_reports": total_reports,
            "reports_with_abnormalities": reports_with_abnormal,
            "abnormality_rate_percent": round((reports_with_abnormal / total_reports * 100), 2) if total_reports > 0 else 0,
        },
        "top_abnormal_findings": top_abnormalities,
        "recent_activity": {
            "last_7_days_reports": last_7_days
        }
    }