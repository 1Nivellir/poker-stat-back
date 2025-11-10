from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core import MultiHostUrl
from pydantic import HttpUrl, PostgresDsn, computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    # API Settings
    API_V1_STR: str = "/v1"
    PROJECT_NAME: str = "Poker Tournament API"
    
    # Security Settings
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 дней
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database Settings
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    # Optional Settings
    SENTRY_DSN: HttpUrl | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

settings = Settings() 