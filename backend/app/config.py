from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/electricity_bill"
    jwt_secret_key: str = "change-this-secret"
    jwt_expire_minutes: int = 60
    admin_email: str = "admin@demo.com"
    admin_password: str = "admin12345"

    # Email settings
    email_mode: str = "smtp"  # console | smtp
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    sender_email: str = ""
    sender_name: str = "Điện nhà mình"

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", case_sensitive=False, extra="ignore")


settings = Settings()
