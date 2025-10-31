# backend/app/api/routes_dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text  # ← Added 'text' for PostgreSQL compatibility
from app.db.session import SessionLocal
from app.db.models import Patient, ReportLog
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/dashboard_stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        # 1. Total patients
        total_patients = db.query(Patient).count()

        # 2. Total reports
        total_reports = db.query(ReportLog).count()

        # 3. Reports with abnormalities
        reports_with_abnormal = 0
        abnormal_findings = []

        # Fetch all reports and parse analysis
        all_reports = db.query(ReportLog).all()
        for report in all_reports:
            if report.analysis:
                try:
                    analysis = json.loads(report.analysis)
                    if isinstance(analysis, list):
                        for finding in analysis:
                            if finding.get("is_abnormal", False):
                                reports_with_abnormal += 1
                                abnormal_findings.append(finding["type"])
                                break  # Count report once even if multiple abnormalities
                except (json.JSONDecodeError, TypeError, AttributeError):
                    continue

        # 4. Top abnormal findings (by count)
        from collections import Counter
        abnormal_counter = Counter(abnormal_findings)
        top_abnormalities = [
            {"finding": finding, "count": count}
            for finding, count in abnormal_counter.most_common(5)
        ]

        # 5. Average reports per patient
        avg_reports_per_patient = round(total_reports / total_patients, 2) if total_patients > 0 else 0

        # 6. Recent activity (last 7 days) - PostgreSQL compatible
        last_7_days = db.query(ReportLog).filter(
            ReportLog.created_at >= text("NOW() - INTERVAL '7 days'")
        ).count()

        return {
            "summary": {
                "total_patients": total_patients,
                "total_reports": total_reports,
                "reports_with_abnormalities": reports_with_abnormal,
                "abnormality_rate_percent": round((reports_with_abnormal / total_reports * 100), 2) if total_reports > 0 else 0,
                "average_reports_per_patient": avg_reports_per_patient
            },
            "top_abnormal_findings": top_abnormalities,
            "recent_activity": {
                "last_7_days_reports": last_7_days
            }
        }

    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard stats")