from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # Application
    app_name: str = "Task API"
    app_env: str = "dev"

    # Database - shared
    db_host: str
    db_port: int
    db_name: str

    # Database - app user
    db_app_user: str
    db_app_password: str

    # Database - migration user
    db_migration_user: str
    db_migration_password: str

    # Dev bootstrap
    db_bootstrap: bool = False

    @computed_field
    @property
    def database_url(self) -> str:
        password = quote_plus(self.db_app_password)
        return (
            f"postgresql+psycopg://{self.db_app_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field
    @property
    def database_migration_url(self) -> str:
        password = quote_plus(self.db_migration_password)
        return (
            f"postgresql+psycopg://{self.db_migration_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    
settings = Settings()