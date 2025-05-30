"""Settings module"""
import os

from dynaconf import Dynaconf
from pydantic_settings import BaseSettings

HERE = os.path.dirname(os.path.abspath(__file__))

class SecuritySettings(BaseSettings):
    """Security settings"""
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 days

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "Microblog"
    debug: bool = False
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "microblog"
    security: SecuritySettings = SecuritySettings()

    class Config:
        env_file = ".env"

settings = Settings()

settings = Dynaconf(
    envvar_prefix="microblog",
    preload=[os.path.join(HERE, "default.toml")],
    settings_files=["settings.toml", ".secrets.toml"],
    environments=["development", "production", "testing"],
    env_switcher="microblog_env",
    load_dotenv=False,
)