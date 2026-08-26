from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    claude_api_key: str
    gemini_api_key: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    upload_dir: str = "/app/uploads"
    google_application_credentials: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()