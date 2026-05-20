import streamlit as st
import pandas as pd
from api.services.fuzzy_iptu_address_search import AddressMatcher
from .data_loaders import get_df_enderecos_lotes

@st.cache_resource
def get_address_matcher(address_df:pd.DataFrame|None=None)->AddressMatcher:
    '''Inicializa o AddressMatcher e o cacheia para uso futuro'''
    if address_df is None:
        address_df = get_df_enderecos_lotes()
    matcher = AddressMatcher(address_df)
    return matcher

