# backend/app/db/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base  # ← Import from base.py, not session.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="patient")  # "patient" or "doctor"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    patients = relationship("Patient", back_populates="user")

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password[:72])

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)  # e.g., "Male", "Female", "Other"
    contact = Column(String, nullable=True)  # phone/email
    # Relationship to ReportLog
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="patients")
    reports = relationship("ReportLog", back_populates="patient")  # ← Must match ReportLog's back_populates

class ReportLog(Base):
    __tablename__ = "report_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    cleaned_text = Column(Text, nullable=True)
    structured_output = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 🔗 New: Link to patient
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    # Relationship to Patient
    patient = relationship("Patient", back_populates="reports")  # ← Must match Patient's relationship name

class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    symptoms = Column(Text, nullable=False)
    predicted_disease = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FeedbackLog(Base):
    __tablename__ = "feedback_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String, nullable=False)  # "symptom" or "report"
    original_prediction = Column(String, nullable=False)
    corrected_label = Column(String, nullable=False)
    user_comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional: Link to original log
    report_log_id = Column(Integer, ForeignKey("report_logs.id"), nullable=True)
    symptom_log_id = Column(Integer, ForeignKey("symptom_logs.id"), nullable=True)