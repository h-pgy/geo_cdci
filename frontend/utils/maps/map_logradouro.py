import folium
import streamlit as st
from streamlit_folium import st_folium
from api.services.logradouro.logradouro_line import LogradouroLineFetcher
from api.services.map.geojson_layer import GeoJsonLayerFactory
from api.services.map.tile_layer import add_tile_layer_to_map
import geopandas as gpd
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget


class LogradouroMapPlugin:

    def __init__(self):
        self.logradouro_line_fetcher = LogradouroLineFetcher()
        self.add_geojson_layer = GeoJsonLayerFactory()
        self.add_tile_layer = add_tile_layer_to_map
        self._current_codlog: str = ""

    def get_centroid(self, gdf:gpd.GeoDataFrame) -> list[float]:

        centroide_uniao = gdf.geometry.union_all().centroid
        return [float(centroide_uniao.y), float(centroide_uniao.x)]
    
    @property
    def key_state(self) -> str:
        return f"map_{self._current_codlog}"
    
    @property
    def interactions(self) -> dict:
        if self.key_state in st.session_state and st.session_state[self.key_state] is not None:
            return st.session_state[self.key_state]
        return {}

    def build_map(self, codlog:str)->folium.Map:

        gdf = self.logradouro_line_fetcher(codlog, reprojetar_para_4326=True)
        centroid = self.get_centroid(gdf)
        mapa = folium.Map(location=centroid, zoom_start=15, tiles="openstreetmap")
        #mapa = self.add_tile_layer(mapa)
        mapa = self.add_geojson_layer(mapa, gdf, layer_name="Logradouro")

        return mapa
        
    def render(self, codlog: str, container:StreamlitWidget) -> dict:

        self._current_codlog = codlog
        internal_continar = container.container()
        mapa = self.build_map(codlog)
        with internal_continar:
            interactions =st_folium(
                mapa, 
                use_container_width=True, 
                key=self.key_state,
                returned_objects=[]
            )
        return interactions
    
    def __call__(self, codlog: str, container:StreamlitWidget) -> dict:
        return self.render(codlog, container)