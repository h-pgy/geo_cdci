from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Conectividade WFS
    WFS_DOMAIN: str = "wfs.geosampa.prefeitura.sp.gov.br"
    WFS_ENDPOINT: str = "geoserver/geoportal/wfs"
    WFS_SERVICE: str = "WFS"
    WFS_VERSION: str = "1.0.0"
    WFS_NAMESPACE: str = "geoportal"

    #WMS
    WMS_URL: str = "https://wms.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/ows"
    WMS_RASTER_URL: str = "http://raster.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/wms"
    TILE_LAYER_ATTRIBUTION: str = "Prefeitura de São Paulo / GeoSampa"
    WMS_VERSION: str = "1.3.0"

    #crs
    WFS_CRS: str = "EPSG:31983"
    WMS_CRS: str = "EPSG:4326"

    #CAMADAS WFS
    LAYER_MAPA_BASE: str = "geoportal:MapaBase_Politico"
    LAYER_ORTOFOTO: str = "geoportal:ORTO_RGB_2020"

    # Camadas WFS
    LAYER_LOTES: str = "lote_cidadao"
    LAYER_LOGRADOUROS: str = "segmento_logradouro"

    #folder_dados
    FOLDER_DADOS: str = "dados"

    # address_search
    MAX_ADDRESS_SEARCH_RESULTS: int = 5
    ADDRESS_SEARCH_FUZZY_SCORE_THRESHOLD: float = 70.0


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()