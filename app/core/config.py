from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str
    DATABASE_URL: str = "sqlite:///./translations.db"

    class Config:
        env_file = ".env"

settings = Settings() 