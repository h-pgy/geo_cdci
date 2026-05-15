from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    # Configurações do aplicativo
    APP_NAME: str = "GEOCEL"
    APP_TITLE: str = "GEOCEL - Certidão Automática de Existência de Lançamento de IPTU"
    APP_VERSION: str = "1.0.0"

    #static
    STATIC_FOLDER: str = 'static'

    #imagens
    BANNER_IMG: str = "banner.png"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()