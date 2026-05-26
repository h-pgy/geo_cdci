from api.integrations.wfs import WFSFetcher
from typing import Any, Optional
import geopandas as gpd
import folium
from api.config import settings

LAYER_LOTES = settings.LAYER_LOTES
WFS_CRS = settings.WFS_CRS

class LoteDataFetcher:

    layer_name = LAYER_LOTES
    base_crs = WFS_CRS

    def __init__(self, wfs_fetcher: Optional[WFSFetcher]=None) -> None:

        self.wfs_fetcher = wfs_fetcher or WFSFetcher(verbose=True)


    def get_data_by_cd_identificador(self, cd_identificador: int, atributes:list[str]) -> list[dict[str, Any]]:

        
        cql_filter = f"cd_identificador={cd_identificador}"
        
        todos_os_lotes = []
        
        for lote in self.wfs_fetcher(nome_camada=self.layer_name, 
                                     cql_filter=cql_filter,
                                     propertyName=",".join(atributes)):
            todos_os_lotes.extend(lote)
            
        return todos_os_lotes
    
    def assert_single_lote(self, lotes: list[dict[str, Any]]) -> dict[str, Any]:
        if len(lotes) == 0:
            raise ValueError("Nenhum lote encontrado para o cd_identificador fornecido.")
        elif len(lotes) > 1:
            raise ValueError("Mais de um lote encontrado para o cd_identificador fornecido.")
        return lotes[0]
    
    def __call__(self, cd_identificador: int, atributes: list[str]) -> dict[str, Any]:
        
        lotes = self.get_data_by_cd_identificador(cd_identificador, atributes=atributes)
        lote = self.assert_single_lote(lotes)

        return lote['properties']


