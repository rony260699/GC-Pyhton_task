from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PDF Editor API"
    max_file_size_mb: int = 10
    max_pdf_pages: int = 100
    translation_provider: str = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    libretranslate_url: str = ""
    libretranslate_api_key: str = ""
    request_timeout_seconds: int = 45
    font_path: Path = Path(__file__).parent / "fonts" / "NotoSansBengali-Regular.ttf"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
