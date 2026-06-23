from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    gemini_api_key: str = ""
    gemini_live_model: str = "gemini-3.1-flash-live-preview"
    cors_origins: str = "http://localhost:8080,https://hai1975.com,https://www.hai1975.com"


settings = Settings()
