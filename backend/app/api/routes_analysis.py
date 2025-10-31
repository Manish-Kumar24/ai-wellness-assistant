from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Query
from pydantic import BaseModel
from app.utils.text_cleaner import clean_text, extract_structured_fields
from app.utils.report_analyzer import analyze_report
from app.db.session import SessionLocal
from app.db.models import ReportLog, Patient, User
from app.api.deps import get_current_user
from sqlalchemy.orm import Session
import pytesseract
import easyocr
import io
from PIL import Image
import json
import numpy as np
from pdf2image import convert_from_bytes

router = APIRouter()

class ReportData(BaseModel):
    text: str

@router.post("/analyze_report")
async def analyze_report_endpoint(
    report: ReportData,
    current_user: User = Depends(get_current_user)
):
    try:
        cleaned = clean_text(report.text)
        structured = extract_structured_fields(cleaned)
        results = analyze_report(structured)

        db = SessionLocal()
        try:
            log = ReportLog(
                filename="raw_text_input",
                raw_text=report.text,
                cleaned_text=cleaned,
                structured_output=json.dumps(structured),
                analysis=json.dumps(results),
                patient_id=None  # No patient for raw text
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            print(f"✅ Saved raw text log ID: {log.id}")
        finally:
            db.close()

        return {
            "raw_text": report.text,
            "cleaned_text": cleaned,
            "structured_output": structured,
            "analysis": results,
            "log_id": log.id,
        }
    except Exception as e:
        print(f"❌ Error in /analyze_report: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@router.post("/clean_and_analyze")
async def clean_and_analyze(
    file: UploadFile = File(...),
    patient_id: int | None = Query(None, description="Link report to patient"),
    use_easyocr: bool = False,
    current_user: User = Depends(get_current_user)
):
    print("🚀 NEW CODE: File upload endpoint triggered!")
    contents = await file.read()

    try:
        print(f"📄 Uploading file: '{file.filename}'")
        print(f"🩺 Patient ID (before auto-link): {patient_id}")
        print(f"👤 User role: {current_user.role}")

        db = SessionLocal()
        try:
            # 🧩 Auto-link to user's patient if patient_id not provided
            if current_user.role == "patient" and not patient_id:
                patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
                if patient:
                    patient_id = patient.id
                    print(f"🔗 Auto-linked patient ID: {patient_id}")

            # Validate patient_id if provided
            if patient_id:
                patient = db.query(Patient).filter(Patient.id == patient_id).first()
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                
                # Patients can only upload to their own profile
                if current_user.role == "patient" and patient.user_id != current_user.id:
                    raise HTTPException(status_code=403, detail="Invalid patient ID")
        finally:
            db.close()

        # 🧠 Handle PDF or image input
        if file.filename.lower().endswith(".pdf"):
            print("📄 Converting PDF to images...")
            images = convert_from_bytes(contents)
            raw_text = ""
            for img in images:
                if use_easyocr:
                    reader = easyocr.Reader(["en"], gpu=False)
                    result = reader.readtext(np.array(img))
                    text = " ".join([res[1] for res in result])
                else:
                    text = pytesseract.image_to_string(img)
                raw_text += text + "\n"
        else:
            image = Image.open(io.BytesIO(contents))
            if use_easyocr:
                reader = easyocr.Reader(["en"], gpu=False)
                result = reader.readtext(np.array(image))
                raw_text = " ".join([res[1] for res in result])
            else:
                raw_text = pytesseract.image_to_string(image)

        print(f"🔤 Extracted text (first 200 chars): {raw_text[:200]}...")

        cleaned = clean_text(raw_text)
        structured = extract_structured_fields(cleaned)
        results = analyze_report(structured)

        db = SessionLocal()
        try:
            log = ReportLog(
                filename=file.filename or "unnamed_file",
                raw_text=raw_text,
                cleaned_text=cleaned,
                structured_output=json.dumps(structured),
                analysis=json.dumps(results),
                patient_id=patient_id  # ← Link to patient
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            print(f"✅ Saved uploaded file log ID: {log.id} for patient ID: {log.patient_id}")
        finally:
            db.close()

        return {
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "structured_output": structured,
            "analysis": results,
            "log_id": log.id,
            "patient_id": log.patient_id,
        }

    except Exception as e:
        print(f"❌ Error in /clean_and_analyze: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/logs")
async def fetch_logs(
    current_user: User = Depends(get_current_user)
):
    try:
        db = SessionLocal()
        try:
            query = db.query(ReportLog)
            
            # Patients see only their own reports
            if current_user.role == "patient":
                # Get patient profile
                patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
                if patient:
                    query = query.filter(ReportLog.patient_id == patient.id)
                else:
                    query = query.filter(ReportLog.patient_id.is_(None))
            
            logs = query.order_by(ReportLog.id.desc()).all()
            log_list = []
            for log in logs:
                log_dict = {
                    "id": log.id,
                    "filename": log.filename,
                    "patient_id": log.patient_id,
                    "raw_text": log.raw_text,
                    "cleaned_text": log.cleaned_text,
                    "structured_output": json.loads(log.structured_output) if log.structured_output else None,
                    "analysis": json.loads(log.analysis) if log.analysis else None,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                log_list.append(log_dict)
            return {"logs": log_list}
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=f"Log fetch error: {str(e)}")