# backend/app/models/report_log.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class ReportLog(Base):
    __tablename__ = "report_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)   # file name if uploaded, else None
    raw_text = Column(Text, nullable=False)         # OCR or direct input
    cleaned_text = Column(Text, nullable=False)     # cleaned text
    structured_output = Column(Text, nullable=False)  # stored as JSON string
    analysis = Column(Text, nullable=False)         # stored as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
