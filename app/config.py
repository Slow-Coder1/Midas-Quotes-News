from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # env names accepted: CORS_ORIGINS (preferred) or cors_origin (alias)
    CORS_ORIGINS: str = Field(
        default="",
        validation_alias="cors_origin",  
    )
    FINNHUB_API_KEY: str | None = None

    @property
    def origins(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore", 
    )

settings = Settings()
