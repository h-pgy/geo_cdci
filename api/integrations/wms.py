from api.config import settings
from json import JSONDecodeError
import requests
import geopandas as gpd
from api.services.map.bounding_box import BoundingBoxModel, BoundingBoxGenerator


class WMSFetcher:
    """
    Abstração para extração de imagens via WMS do GeoSampa.

    Recebe um bounding box e retorna a imagem em png correspondente àquela área, de acordo com a camada solicitada.
    Retorno em bytes.
    """

    version = settings.WMS_VERSION
    CRS= "EPSG:31983"
    format = "image/png"

    def __init__(self, raster: bool = False, convert_to_4326:bool=False, default_width: int = 256, default_height: int = 256, verbose:bool=True) -> None:

        self.raster = raster
        self.width = default_width
        self.height = default_height
        self.domain_url = self.solve_domain_url()
        self.generate_bbox = self.solve_bbox_generator(convert_to_4326=convert_to_4326)
        self.verbose=verbose

    def solve_bbox_generator(self, convert_to_4326:bool=False) -> BoundingBoxGenerator:
        if convert_to_4326:
            crs_saida = "EPSG:4326"
        else:
            crs_saida = self.CRS
        generate_bbox = BoundingBoxGenerator(crs_entrada=self.CRS, crs_saida=crs_saida)

        return generate_bbox


    def solve_domain_url(self)->str:

        if self.raster:
            return settings.WMS_RASTER_URL  
        return settings.WMS_URL

    @property
    def url_base(self)->str:

        return f"{self.domain_url}?service=WMS&version={self.version}&request=GetMap&format={self.format}&styles=&transparent=true"
    
    def log(self, message:str):
        if self.verbose:
            print(f"[WMSFetcher] {message}")

    def full_url(self, params:dict)->str:
        return f"{self.url_base}&{'&'.join([f'{key}={value}' for key, value in params.items()])}"

    def fetch_image(self, bbox: BoundingBoxModel, layer: str, width:Optional[int]=None, height:Optional[int]=None) -> bytes:

        if width is None:
            width = self.width
        if height is None:
            height = self.height

        params = {
            "layers": layer,
            "crs": self.CRS,
            "bbox": bbox.string_wms,
            "width": width,
            "height": height
        }

        response = requests.get(self.url_base, params=params)
        self.log(f"Request URL: {response.url}")

        if response.status_code != 200:
            raise Exception(f"Erro ao obter imagem do WMS. Status code: {response.status_code}. Response: {response.text}")

        return response.content
    
    def pipeline(self, gdf: gpd.GeoDataFrame, layer:str, padding_x_metros: float = 0.0, padding_y_metros: float = 0.0, width:Optional[int]=None, height:Optional[int]=None) -> bytes:
        bbox = self.generate_bbox(gdf, padding_x_metros=padding_x_metros, padding_y_metros=padding_y_metros)
        return self.fetch_image(bbox=bbox, layer=layer, width=width, height=height)
    
    def __call__(self, gdf: gpd.GeoDataFrame, layer:str, padding_x_metros: float = 0.0, padding_y_metros: float = 0.0, width:Optional[int]=None, height:Optional[int]=None) -> bytes:
        
        return self.pipeline(gdf=gdf, layer=layer, padding_x_metros=padding_x_metros, padding_y_metros=padding_y_metros, width=width, height=height)
    
