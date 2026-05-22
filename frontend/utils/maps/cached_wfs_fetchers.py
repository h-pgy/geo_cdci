import streamlit as st
from api.services.logradouro.logradouro_line import LogradouroLineFetcher
import geopandas as gpd

@st.cache_data(show_spinner=False)
def cached_logradouro_line_fetcher(codlog:str, reprojetar_para_4326:bool = True) -> gpd.GeoDataFrame:
    fetcher = LogradouroLineFetcher()
    return fetcher(codlog, reprojetar_para_4326)

