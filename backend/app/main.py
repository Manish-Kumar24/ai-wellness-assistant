from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import (
    routes_symptoms,
    routes_analysis,
    routes_chat,
    routes_patients,
    routes_dashboard,
    routes_auth,
    routes_feedback,
    routes_doctor,
)
from app.db.base import Base
from app.db.session import engine
from app.db.models import User, Patient, ReportLog, SymptomLog, FeedbackLog
from ml.model_loader import generate_response


app = FastAPI(title="AI Wellness Assistant")

@app.get("/")
async def root():
    return {"message": "TinyLlama Backend is Running 🚀"}


# Create tables on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(routes_auth.router, prefix="/auth", tags=["Auth"])
app.include_router(routes_symptoms.router, prefix="/symptoms", tags=["Symptoms"])
app.include_router(routes_analysis.router, prefix="/cv", tags=["Analysis"])
app.include_router(routes_chat.router, prefix="/chat", tags=["Chat"])
app.include_router(routes_patients.router, prefix="/cv", tags=["Patients"])
app.include_router(routes_dashboard.router, prefix="/cv", tags=["Dashboard"])
app.include_router(routes_feedback.router, prefix="/cv", tags=["Feedback"])
app.include_router(routes_doctor.router, prefix="/doctor", tags=["Doctor"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running 🚀"}

@app.post("/generate")
async def generate_text(data: dict):
    prompt = data.get("prompt", "")
    result = generate_response(prompt)
    return {"response": result}
