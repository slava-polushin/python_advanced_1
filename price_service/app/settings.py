from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_port: int = 8002
    price_per_km: float = 1

    class Config:
        env_file = ".env"

settings = Settings()