from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    DATABASE_URL: str 
    JWT_SECRET: str  
    JWT_ALGORITHM: str  
    REDIS_URL: str = "redis://localhost:6379/0"
    class Config:
        env_file = ".env"  # relative to where this script is located

# Instantiate once
Config = Settings()

