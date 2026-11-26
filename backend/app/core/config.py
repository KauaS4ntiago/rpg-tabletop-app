from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from pydantic import model_validator

MIN_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(hide_input_in_errors=True)

    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str
    postgres_host: str = "db"
    postgres_port: int = 5432

    secret_key: SecretStr
    
    #Tokens
    access_token_expire_minutes: int = Field(default=15, gt=0)
    
    refresh_token_expire_days: int = Field(default=7, gt=0)
    session_expire_days: int = Field(default=30, gt=0)
    
    #Cookies 
    refresh_token_cookie_name: str = "refresh_token"
    refresh_token_cookie_httponly: bool = True
    refresh_token_cookie_secure: bool = True
    refresh_token_cookie_samesite: str = "strict"
    refresh_token_cookie_path: str = "/api/v1/auth"
    
    @model_validator(mode="after")
    def validate_session_expiration(self):
        if self.refresh_token_expire_days > self.session_expire_days:
            raise ValueError(
                "Refresh token expiration cannot exceed session expiration"
            )
        return self

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_length(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value()) < MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                f"must be at least {MIN_SECRET_KEY_LENGTH} characters long"
            )
        return value

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()