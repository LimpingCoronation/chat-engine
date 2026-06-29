from os import getenv
from pathlib import Path
import logging

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env = load_dotenv()

# Logger settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

BASE_DIR = Path(__file__).parent.parent
DEV_MODE = getenv("DEV_MODE", "true").strip().lower() in {"1", "true", "yes"}

class Settings(BaseSettings):
    DB_NAME: str = "test"
    DB_USER: str = "test"
    DB_PASSWORD: str = "test"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    SALT: str = "salt"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    CHANNEL_NAME: str = "chat"

    class ConfigDict:
        env: Path = BASE_DIR / ".env"


settings = Settings()

DB_URL: str = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
