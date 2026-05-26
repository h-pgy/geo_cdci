from api.integrations.wfs import WFSFetcher
from typing import Any, Optional
import geopandas as gpd
import folium
from api.config import settings

LAYER_LOTES = settings.LAYER_LOTES
WFS_CRS = settings.WFS_CRS

class LotePolygonFetcher:

    layer_name = LAYER_LOTES
    base_crs = WFS_CRS

    def __init__(self, wfs_fetcher: Optional[WFSFetcher]=None) -> None:

        self.wfs_fetcher = wfs_fetcher or WFSFetcher(verbose=True)


    def get_polygons_by_cd_identificador(self, cd_identificador: int) -> list[dict[str, Any]]:

        
        cql_filter = f"cd_identificador={cd_identificador}"
        
        todos_os_lotes = []
        
        for lote in self.wfs_fetcher(nome_camada=self.layer_name, cql_filter=cql_filter):
            todos_os_lotes.extend(lote)
            
        return todos_os_lotes
    
    def convert_polygons_to_gdf(self, lotes: list[dict[str, Any]], reprojetar_para_4326: bool = False) -> gpd.GeoDataFrame:
        if not lotes:
            return gpd.GeoDataFrame()
            
        gdf = gpd.GeoDataFrame.from_features(lotes, crs=self.base_crs)
        
        if reprojetar_para_4326:
            gdf = gdf.to_crs(epsg=4326)
            
        return gdf
    
    def __call__(self, cd_identificador: int, reprojetar_para_4326: bool = False) -> gpd.GeoDataFrame:
        lotes = self.get_polygons_by_cd_identificador(cd_identificador)
        return self.convert_polygons_to_gdf(lotes, reprojetar_para_4326)


