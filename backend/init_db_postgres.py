# init_db_postgres.py
import os
from dotenv import load_dotenv
from app.db.session import engine
from app.db.base import Base
from app.db.models import User, Patient, ReportLog, SymptomLog, FeedbackLog

load_dotenv()

def init_db():
    print("🚀 Initializing PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully in PostgreSQL!")

if __name__ == "__main__":
    init_db()
