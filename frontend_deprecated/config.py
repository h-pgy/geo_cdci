from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    #static
    STATIC_FOLDER: str = 'static'

    #imagens
    BANNER_IMG: str = "banner.png"

    #basic msg duration
    MSG_DURATION: int = 2


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()