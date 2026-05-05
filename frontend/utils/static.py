import streamlit as st
from frontend.config import settings

def render_static_image(image_name:str, width:int|None=None, caption:str|None=None):
    '''Renderiza uma imagem estática a partir do nome do arquivo'''
    image_path = f"{settings.STATIC_FOLDER}/{image_name}"

    width_processed:int|str = width if width is not None else "content"

    st.image(image_path, width=width_processed, caption=caption)