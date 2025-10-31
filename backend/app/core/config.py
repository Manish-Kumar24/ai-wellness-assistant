from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "ai_wellness_secret_key_2025_change_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()