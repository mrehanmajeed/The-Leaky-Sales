from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    HUBSPOT_ACCESS_TOKEN: str
    GMAIL_SENDER_EMAIL: str
    GMAIL_APP_PASSWORD: str
    SHEETS_SPREADSHEET_ID: str
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "service_account.json"
    SALES_REP_EMAIL: str
    DATABASE_URL: str = "sqlite:///./shoprocket.db"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
