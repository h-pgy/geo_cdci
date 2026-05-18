import folium
from api.config import settings

URL_WMS = settings.WMS_URL
LAYER_MAPA_BASE = settings.LAYER_MAPA_BASE
TILE_LAYER_ATTRIBUTION = settings.TILE_LAYER_ATTRIBUTION


def add_tile_layer_to_map(map:folium.Map, 
                          wms_url:str=URL_WMS, 
                          layer_name:str=LAYER_MAPA_BASE,
                          tile_layer_attribution:str=TILE_LAYER_ATTRIBUTION)->folium.Map:

    layer_title = layer_name.replace('_', ' ').capitalize()

    folium.WmsTileLayer(
            url=wms_url,
            layers=layer_name,
            format="image/png",
            transparent=False,
            name=layer_title,
            attr=tile_layer_attribution,
            crs="EPSG:3857",
            overlay=False,
            control=True
        ).add_to(map)
    
    return map