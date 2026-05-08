from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    STATIC_FOLDER: str = 'static'

    #imagens
    BANNER_IMG: str = "banner.png"

    #STATE_KEYS
    FORM_LOGRADOURO_SUBMITED: str = 'form_logradouro_submited'
    SELECTED_LOGRADOURO_KEY: str = "selected_logradouro_final"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()