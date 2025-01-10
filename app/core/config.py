from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Memory Management System"
    API_V1_STR: str = "/api/v1"
    
    # JWT设置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # 数据库设置
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # LLM设置
    APPL_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 