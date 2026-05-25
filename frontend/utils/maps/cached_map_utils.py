import streamlit as st
from api.services.logradouro.logradouro_line import LogradouroLineFetcher
from api.services.lote.lote_polygon import LotePolygonFetcher
import geopandas as gpd

@st.cache_data(show_spinner=True)
def cached_logradouro_line_fetcher(codlog:str, reprojetar_para_4326:bool = True) -> gpd.GeoDataFrame:
    fetcher = LogradouroLineFetcher()
    return fetcher(codlog, reprojetar_para_4326)


@st.cache_data(show_spinner=True)
def cached_lote_polygon_fetcher(cd_identificador:int, reprojetar_para_4326:bool = True) -> gpd.GeoDataFrame:
    fetcher = LotePolygonFetcher()
    return fetcher(cd_identificador, reprojetar_para_4326)