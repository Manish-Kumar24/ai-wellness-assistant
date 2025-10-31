from pydantic import BaseModel
from typing import Optional

class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: Optional[str] = None

class PatientResponse(PatientCreate):
    id: int

    class Config:
        from_attributes = True  # For SQLAlchemy ORM mode (Pydantic v2)

from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None