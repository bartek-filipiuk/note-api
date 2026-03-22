from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str = "sqlite:///./notes.db"
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @model_validator(mode="after")
    def validate_cors_no_wildcard(self):
        if "*" in self.ALLOWED_ORIGINS.split(","):
            raise ValueError("ALLOWED_ORIGINS cannot be '*' when allow_credentials is enabled")
        return self


settings = Settings()
