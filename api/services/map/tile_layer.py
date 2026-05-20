import folium
from api.config import settings
from functools import partial

URL_WMS = settings.WMS_URL
URL_WMS_RASTER = settings.WMS_RASTER_URL
LAYER_MAPA_BASE = settings.LAYER_MAPA_BASE
LAYER_ORTOFOTO = settings.LAYER_ORTOFOTO
TILE_LAYER_ATTRIBUTION = settings.TILE_LAYER_ATTRIBUTION
WMS_CRS = settings.WMS_CRS
WMS_VERSION = settings.WMS_VERSION


def add_tile_layer_to_map(map:folium.Map, 
                          layer_name:str,
                          wms_url:str=URL_WMS, 
                          tile_layer_attribution:str=TILE_LAYER_ATTRIBUTION,
                          crs:str=WMS_CRS,
                          omit_crs:bool=True,
                          version:str=WMS_VERSION)->folium.Map:

    layer_title = layer_name.replace('_', ' ').capitalize()

    if omit_crs:
        #não me pergunte porque mas o WMS do geosampa só funciona quando não passa o CRS
        folium.WmsTileLayer(
                url=wms_url,
                layers=layer_name,
                format="image/png",
                transparent=False,
                name=layer_title,
                attr=tile_layer_attribution,
                overlay=False,
                control=True,
                version=version
            ).add_to(map)
    else:
        folium.WmsTileLayer(
            url=wms_url,
            layers=layer_name,
            format="image/png",
            transparent=False,
            name=layer_title,
            attr=tile_layer_attribution,
            overlay=False,
            control=True,
            version=version,
            crs=crs
        ).add_to(map) 
    
    return map


add_mapa_base = partial(add_tile_layer_to_map, layer_name=LAYER_MAPA_BASE)
add_ortofoto = partial(add_tile_layer_to_map, layer_name=LAYER_ORTOFOTO, wms_url=URL_WMS_RASTER)