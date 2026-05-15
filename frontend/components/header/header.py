from frontend.dto.header import HeaderRenderedDTO
from frontend.dto.base import BaseComponentResponse
from frontend.components.base import UIComponent
from frontend.dto.base import AppFlowSignal
from frontend.utils.static import render_static_image
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

from frontend.config import settings


APP_NAME = settings.APP_NAME
APP_TITLE = settings.APP_TITLE
BANNER_IMG: str = settings.BANNER_IMG


class Header(UIComponent[HeaderRenderedDTO]):

    name = "Header"
    user_error_msg = "Ocorreu um erro ao renderizar o cabeçalho. Por favor, tente recarregar a página."
    output_type=HeaderRenderedDTO

    def _setup_page_config(self):
        """
        Define as configurações básicas da página no navegador.
        """
        st.set_page_config(
            page_title=APP_NAME,
            page_icon="🏙️",
            layout="wide"
        )

    def _render_banner_img(self):

        img_container = st.container()
        cols = img_container.columns([1, 2, 1])
        img_caption = "Imagem ilustrativa do processo de geocodificação e emissão de certidões"
        with cols[1]:
            render_static_image(BANNER_IMG, caption=img_caption)

    def _render_techical_description(self):

        with st.expander("Informações técnicas", width='stretch'):
                st.write(
                    "O sistema executa consultas automatizadas nas bases geoespaciais da Secretaria da Fazenda (SF) e do GeoSampa. "
                    "A integração utiliza o protocolo WFS para acessar camadas de lotes fiscais e logradouros em tempo real."
                )
                st.write(
                    "Para o processamento de endereços, o motor utiliza busca fonética para tratar variações de grafia. "
                    "Caso o número da porta não conste na base oficial, o sistema realiza a interpolação linear para estimar a coordenada."
                )
                st.write(
                    "O processamento resulta na identificação do perímetro do imóvel e das suas confrontações. "
                    "Os dados extraídos servem de base para a geração automática do documento técnico."
                )



    def _render_description(self):
        """
        Renderiza a descrição funcional do sistema e detalhes técnicos em popover.
        """

        
        desc_container = st.container()
        cols = desc_container.columns([0.2, 0.8, 0.2])
        with cols[1]:
            st.markdown(
                ("Este sistema realiza o processamento de dados imobiliários para a emissão da Certidão de Dados Cadastrais do Imóvel. "
                "A aplicação valida endereços e vincula informações fiscais à base geográfica da Prefeitura."),
                text_alignment='justify'
            )
            self._render_techical_description()

    def _render(self, container: StreamlitWidget, input_dto: None) -> BaseComponentResponse[HeaderRenderedDTO]:

        self._setup_page_config()
        with container:
            st.header(APP_NAME, text_alignment='center')
            self._render_banner_img()
            st.subheader(APP_TITLE, text_alignment='center')
            self._render_description()

        output_dto = HeaderRenderedDTO(rendered=True)
        return BaseComponentResponse(
            signal=AppFlowSignal.GO,
            data=output_dto
        )
            