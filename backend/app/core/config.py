from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "dev"

    OPENAI_API_KEY: str = "ollama"
    OPENAI_BASE_URL: str = "http://localhost:11434/v1"

    OPENAI_MODEL: str = "llama3.2"
    FAST_MODEL: str = "llama3.2"
    SMART_MODEL: str = "deepseek-r1:8b"
    VISION_MODEL: str = "llama3.2-vision"

    EMAIL_USER: str | None = None
    EMAIL_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
