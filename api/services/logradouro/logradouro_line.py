from api.integrations.wfs import WFSFetcher
from typing import Any, Optional
import geopandas as gpd
import folium
from api.config import settings

LAYER_LOGRADOUROS = settings.LAYER_LOGRADOUROS
WFS_CRS = settings.WFS_CRS

class LogradouroLineFetcher:

    layer_name = LAYER_LOGRADOUROS
    base_crs = WFS_CRS

    def __init__(self, wfs_fetcher: Optional[WFSFetcher]=None) -> None:

        self.wfs_fetcher = wfs_fetcher or WFSFetcher(verbose=True)


    def get_line_segments_by_codlog(self, codlog: str) -> list[dict[str, Any]]:

        
        cql_filter = f"codlog='{codlog}'"
        
        todos_os_segmentos = []
        
        for lote in self.wfs_fetcher(nome_camada=self.layer_name, cql_filter=cql_filter):
            todos_os_segmentos.extend(lote)
            
        return todos_os_segmentos
    
    def convert_segments_to_gdf(self, segmentos: list[dict[str, Any]], reprojetar_para_4326: bool = False) -> gpd.GeoDataFrame:
        if not segmentos:
            return gpd.GeoDataFrame()
            
        gdf = gpd.GeoDataFrame.from_features(segmentos, crs=self.base_crs)
        
        if reprojetar_para_4326:
            gdf = gdf.to_crs(epsg=4326)
            
        return gdf
    
    def __call__(self, codlog: str, reprojetar_para_4326: bool = False) -> gpd.GeoDataFrame:
        segmentos = self.get_line_segments_by_codlog(codlog)
        return self.convert_segments_to_gdf(segmentos, reprojetar_para_4326)


