import math
import geopandas as gpd
import pyproj
from shapely.geometry import box
from pydantic import BaseModel, model_validator
from typing import Self, Tuple

class BoundingBoxModel(BaseModel):
    minx: float
    miny: float
    maxx: float
    maxy: float

    @model_validator(mode="after")
    def validar_coordenadas(self) -> Self:
        if self.minx >= self.maxx:
            raise ValueError("O valor de minx deve ser estritamente menor que maxx.")
        if self.miny >= self.maxy:
            raise ValueError("O valor de miny deve ser estritamente menor que maxy.")
        return self

    @property
    def string_wms(self) -> str:
        return f"{self.minx},{self.miny},{self.maxx},{self.maxy}"
    
    @property
    def as_tuple(self) -> Tuple[float, float, float, float]:
        return (self.minx, self.miny, self.maxx, self.maxy)
    
class BoundingBoxGenerator:
    """
    Classe para gerar BoundingBoxModel a partir de um GeoDataFrame, aplicando padding em metros
    e realizando as conversoes necessarias de sistema de coordenadas.
    """
    
    def __init__(self, crs_entrada: str = "EPSG:4326", crs_saida: str = "EPSG:4326") -> None:

        if not self._validar_epsg(crs_entrada):
            raise ValueError(f"CRS de entrada inválido: {crs_entrada}. Deve estar no formato 'EPSG:XXXX'.")
        if not self._validar_epsg(crs_saida):
            raise ValueError(f"CRS de saída inválido: {crs_saida}. Deve estar no formato 'EPSG:XXXX'.")

        self.crs_entrada = crs_entrada
        self.crs_saida = crs_saida

    def _validar_epsg(self, epsg: str) -> bool:
        
        if not epsg.startswith("EPSG:"):
            return False
        if not epsg.replace('EPSG:', '').isdigit():
            return False
        return True
    
    def _conversao_projetada(self, crs: pyproj.CRS) -> Tuple[float, float]:
        fator = crs.axis_info[0].unit_conversion_factor
        return fator, fator
    
    def _conversao_graus(self, bounds: Tuple[float, float, float, float])-> Tuple[float, float]:

        
        circunferencia_terra = 40075017.0
        metros_por_grau = circunferencia_terra / 360.0

        metros_por_grau_lat = metros_por_grau

        #no caso da longitude, tem que ajustar pela latitude, pois a distancia entre os meridianos diminui à medida que se aproxima dos polos
        _, miny, _, maxy = bounds
        lat_media = (miny + maxy) / 2.0
        metros_por_grau_lon = metros_por_grau * math.cos(math.radians(lat_media))
        
        return metros_por_grau_lon, metros_por_grau_lat

    def _obter_fator_conversao(self, bounds: Tuple[float, float, float, float]) -> Tuple[float, float]:
        
        crs = pyproj.CRS(self.crs_entrada)
        
        if crs.is_projected:
            return self._conversao_projetada(crs)
        
        return self._conversao_graus(bounds)
        

    def _converter_padding_para_unidade_crs(
        self, 
        padding_x_metros: float, 
        padding_y_metros: float, 
        fator_x: float, 
        fator_y: float
    ) -> Tuple[float, float]:
        pad_x_crs = padding_x_metros / fator_x
        pad_y_crs = padding_y_metros / fator_y
        return pad_x_crs, pad_y_crs

    def _aplicar_padding_coordenadas(
        self, 
        bounds: Tuple[float, float, float, float], 
        pad_x: float, 
        pad_y: float
    ) -> Tuple[float, float, float, float]:
        minx, miny, maxx, maxy = bounds
        return minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y

    def _padronizar_crs_entrada(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if gdf.crs is None:
            return gdf.set_crs(self.crs_entrada)
        elif gdf.crs.to_string() != self.crs_entrada:
            return gdf.to_crs(self.crs_entrada)
        return gdf

    def _processar_padding(
        self, 
        bounds: Tuple[float, float, float, float], 
        padding_x_metros: float, 
        padding_y_metros: float
    ) -> Tuple[float, float, float, float]:
        if padding_x_metros <= 0 and padding_y_metros <= 0:
            return bounds

        fator_x, fator_y = self._obter_fator_conversao(bounds)
        pad_x_crs, pad_y_crs = self._converter_padding_para_unidade_crs(
            padding_x_metros, padding_y_metros, fator_x, fator_y
        )
        return self._aplicar_padding_coordenadas(bounds, pad_x_crs, pad_y_crs)

    def _processar_reprojecao_saida(
        self, 
        bounds: Tuple[float, float, float, float]
    ) -> Tuple[float, float, float, float]:
        if self.crs_entrada == self.crs_saida:
            return bounds

        bbox_geom = box(*bounds)
        bbox_series = gpd.GeoSeries([bbox_geom], crs=self.crs_entrada)
        return bbox_series.to_crs(self.crs_saida).total_bounds

    def gerar(
        self, 
        gdf: gpd.GeoDataFrame, 
        padding_x_metros: float = 0.0, 
        padding_y_metros: float = 0.0
    ) -> BoundingBoxModel:
        
        gdf_operacao = self._padronizar_crs_entrada(gdf)
        bounds_iniciais = gdf_operacao.total_bounds
        
        bounds_com_padding = self._processar_padding(
            bounds_iniciais, 
            padding_x_metros, 
            padding_y_metros
        )
        
        bounds_finais = self._processar_reprojecao_saida(bounds_com_padding)

        return BoundingBoxModel(
            minx=bounds_finais[0],
            miny=bounds_finais[1],
            maxx=bounds_finais[2],
            maxy=bounds_finais[3]
        )

    def __call__(
        self, 
        gdf: gpd.GeoDataFrame, 
        padding_x_metros: float = 0.0, 
        padding_y_metros: float = 0.0
    ) -> BoundingBoxModel:
        return self.gerar(gdf, padding_x_metros=padding_x_metros, padding_y_metros=padding_y_metros)