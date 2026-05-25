import folium
import streamlit as st
from streamlit_folium import st_folium
from api.services.map.geojson_layer import GeoJsonLayerFactory
from api.services.map.tile_layer import add_mapa_base, add_ortofoto
from frontend.utils.maps.cached_map_utils import cached_lote_polygon_fetcher
import geopandas as gpd
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget


class LoteUnicoMapPlugin:

    def __init__(self):
        self.lote_polygon_fetcher = cached_lote_polygon_fetcher
        self.add_geojson_layer = GeoJsonLayerFactory()
        self.add_mapa_base = add_mapa_base
        self.add_ortofoto = add_ortofoto
        self._current_cd_identificador: int = 0

    def get_centroid(self, gdf:gpd.GeoDataFrame) -> list[float]:

        centroide_uniao = gdf.geometry.union_all().centroid
        return [float(centroide_uniao.y), float(centroide_uniao.x)]
    
    @property
    def key_state(self) -> str:
        return f"map_{self._current_cd_identificador}"
    
    @property
    def interactions(self) -> dict:
        if self.key_state in st.session_state and st.session_state[self.key_state] is not None:
            return st.session_state[self.key_state]
        return {}

    def build_map(self, cd_identificador:int)->folium.Map:

        gdf = self.lote_polygon_fetcher(cd_identificador, reprojetar_para_4326=True)
        centroid = self.get_centroid(gdf)
        mapa = folium.Map(location=centroid, zoom_start=15, 
                          tiles=None
                          )
        #o tile layer do geosampa não suporta conversão de CRS
        mapa = self.add_geojson_layer(mapa, gdf, name="Lote", 
                                      pop_up_def={'fields': ['cd_setor_fiscal', 'cd_quadra_fiscal', 'cd_lote', 'cd_tipo_lote', 'nm_logradouro_completo', 'cd_numero_porta'],
                                                    'aliases': ['Código do Setor Fiscal', 'Código da Quadra Fiscal', 'Código do Lote', 'Tipo de lote', 'Nome do Logradouro', 'Número da porta']},
                                      tooltip_def={'fields': ['cd_setor_fiscal', 'cd_quadra_fiscal', 'cd_lote'],
                                                    'aliases': ['Setor', 'Quadra', 'Lote']})
        mapa = self.add_mapa_base(mapa)
        mapa=self.add_ortofoto(mapa)
        folium.LayerControl().add_to(mapa)

        return mapa
        
    def render(self, cd_identificador: int, container:StreamlitWidget) -> dict:

        self._current_cd_identificador = cd_identificador
        internal_continar = container.container()
        mapa = self.build_map(cd_identificador)
        with internal_continar:
            interactions =st_folium(
                mapa, 
                use_container_width=True, 
                key=self.key_state,
                returned_objects=[]
            )
        return interactions
    
    def __call__(self, cd_identificador: int, container:StreamlitWidget) -> dict:
        return self.render(cd_identificador, container)