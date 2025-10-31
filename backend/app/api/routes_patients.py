import json
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Patient, User, ReportLog
from app.schemas import PatientCreate, PatientResponse
from app.api.deps import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency: Only patients can access their own data
def get_current_patient(current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

@router.post("/add_patient", response_model=PatientResponse)
def add_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Doctors can add any patient; patients can only add themselves
    if current_user.role == "patient":
        # Prevent patients from creating multiple profiles
        existing = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Patient profile already exists")
    
    db_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        contact=patient.contact,
        user_id=current_user.id  # ← Link to user
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/get_patients")
def get_all_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "doctor":
        # Doctors see all patients
        return db.query(Patient).all()
    else:
        # Patients see only their own profile
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        return [patient] if patient else []

@router.get("/get_patient/{patient_id}/reports")
def get_patient_reports(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify patient exists and belongs to user (or user is doctor)
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if current_user.role != "doctor" and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Fetch reports for this patient
    reports = db.query(ReportLog).filter(ReportLog.patient_id == patient_id).all()
    
    report_list = []
    for report in reports:
        report_list.append({
            "id": report.id,
            "filename": report.filename,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "structured_output": json.loads(report.structured_output) if report.structured_output else None,
            "analysis": json.loads(report.analysis) if report.analysis else None,
        })
    
    return {
        "patient_id": patient_id,
        "patient_name": patient.name,
        "total_reports": len(reports),
        "reports": report_list
    }