#!/bin/bash
# entrypoint.sh

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

echo "🚀 Running database initialization..."
python init_db_postgres.py || echo "⚠️ DB already initialized or error occurred, continuing..."

echo "✅ Starting backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000