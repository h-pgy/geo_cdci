from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Conectividade WFS
    WFS_DOMAIN: str = "wfs.geosampa.prefeitura.sp.gov.br"
    WFS_ENDPOINT: str = "geoserver/geoportal/wfs"
    WFS_SERVICE: str = "WFS"
    WFS_VERSION: str = "1.0.0"
    WFS_NAMESPACE: str = "geoportal"

    # Camadas
    LAYER_LOTES: str = "lote_cidadao"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()