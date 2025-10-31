# backend/app/db/create_db.py
from app.db.session import engine
from app.db.base import Base

# 🔴 CRITICAL: Import models so Base knows about them
from app.db.models import Patient, ReportLog, SymptomLog  # ← Import Patient

def init_db():
    Base.metadata.drop_all(bind=engine)  # Optional: for clean dev reset
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with tables.")

if __name__ == "__main__":
    init_db()