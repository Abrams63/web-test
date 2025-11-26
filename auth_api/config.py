from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Налаштування JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Налаштування сервера
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Створення екземпляра налаштувань
settings = Settings()