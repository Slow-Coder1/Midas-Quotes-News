from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FINNHUB_API_KEY: str | None = None
    CORS_ORIGINS: str = ""  # comma-separated origins

    @property
    def origins(self):
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
