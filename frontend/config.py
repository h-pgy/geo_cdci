from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    STATIC_FOLDER: str = 'static'

    #imagens
    BANNER_IMG: str = "banner.png"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()