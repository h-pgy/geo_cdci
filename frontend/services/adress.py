import streamlit as st
from api.services.fuzzy_iptu_address_search import AddressMatcher
from .data_loaders import df_enderecos_lotes

@st.cache_resource
def get_address_matcher()->AddressMatcher:
    '''Inicializa o AddressMatcher e o cacheia para uso futuro'''
    df = df_enderecos_lotes()
    matcher = AddressMatcher(df)
    return matcher

