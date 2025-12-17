from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="proftpd_support_", env_file=(".env", "/etc/proftpd-support.conf")
    )

    database_path: Path

    user_expire_hours: int = 1


settings = Settings()
