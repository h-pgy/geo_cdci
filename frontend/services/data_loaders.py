import streamlit as st
import pandas as pd
from api.scripts.data_load import download_enderecos_lotes

@st.cache_data
def get_df_enderecos_lotes()->pd.DataFrame:
    '''Carrega o dataframe de endereços e lotes'''
    return download_enderecos_lotes()

