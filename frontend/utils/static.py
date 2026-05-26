import streamlit as st
from frontend.config import settings

def static_path(image_name:str) -> str:
    '''Retorna o caminho completo para um arquivo estático a partir do nome do arquivo'''
    return f"{settings.STATIC_FOLDER}/{image_name}"

def render_static_image(image_name:str, width:int|None=None, caption:str|None=None):
    '''Renderiza uma imagem estática a partir do nome do arquivo'''
    image_path = static_path(image_name)

    width_processed:int|str = width if width is not None else "content"

    st.image(image_path, width=width_processed, caption=caption)