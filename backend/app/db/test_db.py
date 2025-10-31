# test_db.py
from app.db.session import engine
from app.db.models import ReportLog
from sqlalchemy import inspect

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('report_logs')]
print("Columns in report_logs:", columns)