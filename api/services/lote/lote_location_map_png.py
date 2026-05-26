from api.services.lote.lote_polygon import LotePolygonFetcher
from api.integrations.wms  import WMSFetcher
from api.services.map.bounding_box import BoundingBoxGenerator
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tempfile
import os
from io import BytesIO
from api.config import settings

ORTOFOTO_LAYER = settings.LAYER_ORTOFOTO

class LoteLocationMapPNGService:

    padding_x = 20
    padding_y = 20

    def __init__(self, raster: bool = True, convert_to_4326:bool=False, default_width: int = 256, default_height: int = 256) -> None:
        self.lote_polygon_fetcher = LotePolygonFetcher()
        self.convert_to_4326 = convert_to_4326
        self.wms_fetcher = WMSFetcher(raster=raster, convert_to_4326=convert_to_4326, default_width=default_width, default_height=default_height)
        self.diretorio_temporario = tempfile.gettempdir()
        self.generate_bbox = BoundingBoxGenerator(crs_entrada=self.wms_fetcher.CRS, crs_saida=self.wms_fetcher.CRS)

    def pipeline(self, id_lote: int, output_file:str, base_layer:str)->str:

        gdf_lote = self.lote_polygon_fetcher(cd_identificador=id_lote, reprojetar_para_4326=self.convert_to_4326)
        img_bytes = self.wms_fetcher(gdf_lote, layer=base_layer, padding_x_metros=self.padding_x, padding_y_metros=self.padding_y)
        fig, ax = plt.subplots(figsize=(10, 10))

        imagem = mpimg.imread(BytesIO(img_bytes), format="png")
        minx, miny, maxx, maxy = self.generate_bbox(gdf_lote, padding_x_metros=self.padding_x, padding_y_metros=self.padding_y).as_tuple
        ax.imshow(imagem, extent=(minx, maxx, miny, maxy))
        ax.set_title(f"Localização do Lote {id_lote}")
        gdf_lote.plot(ax=ax, facecolor="none", edgecolor="blue", linewidth=3)

        output_path = os.path.join(self.diretorio_temporario, output_file)
        plt.savefig(output_path, format="png", dpi=300)
        plt.close(fig)

        return output_path
    
    def __call__(self, id_lote: int, output_file:str, base_layer:str=ORTOFOTO_LAYER)->str:
        return self.pipeline(id_lote, output_file, base_layer)
        
