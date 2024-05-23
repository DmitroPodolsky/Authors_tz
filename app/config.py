from datetime import timedelta
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

project_dir = Path(__file__).parent


class Settings(BaseSettings):
    """
    Class for storing app settings.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    DB_PATH: Path = project_dir / "db"
    STATIC_PATH: Path = project_dir.parent / "static"

    HOST: str
    HOST_URL: str

    SECRET: str = "lol"
    ALGORITHM: str = "HS256"
    JWT_ACCESS_EXP: int = 10
    JWT_REFRESH_EXP: int = 10


settings = Settings()
settings.JWT_ACCESS_EXP = timedelta(minutes=float(settings.JWT_ACCESS_EXP))
settings.JWT_REFRESH_EXP = timedelta(minutes=float(settings.JWT_REFRESH_EXP))
