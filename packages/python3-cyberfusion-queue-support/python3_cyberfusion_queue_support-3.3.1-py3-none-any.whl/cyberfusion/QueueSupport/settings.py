from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="queue_support_",
        env_file=(".env", "/etc/queue-support.conf"),
        extra="ignore",
    )

    database_path: str = "sqlite:///./queue-support.db"

    queue_purge_days: int = 30


settings = Settings()
