import streamlit as st
from frontend.config import settings
from frontend.utils.static import render_static_image

BANNER_IMG = settings.BANNER_IMG

class Header:


    def setup_page_config(self):
        """
        Define as configurações básicas da página no navegador.
        """
        st.set_page_config(
            page_title="GEOCDCI - Certidão Automática de Dados Cadastrais do Imóvel",
            page_icon="🏙️",
            layout="wide"
        )

    def render_title_section(self):
        """
        Renderiza o cabeçalho principal com o nome completo do sistema.
        """
        st.header("GeoCDCI", text_alignment='center')
        st.subheader("Certidão Automática de Dados Cadastrais do Imóvel", text_alignment='center')

    def render_description(self):
        """
        Renderiza a descrição funcional do sistema e detalhes técnicos em popover.
        """

        
        cols = st.columns([0.5, 2, 0.5])
        with cols[1]:
            st.markdown(
                ("Este sistema realiza o processamento de dados imobiliários para a emissão da Certidão de Dados Cadastrais do Imóvel. "
                "A aplicação valida endereços e vincula informações fiscais à base geográfica da Prefeitura."),
                text_alignment='justify'
            )
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

    def render_banner_img(self):

        cols = st.columns([1, 2, 1])
        with cols[1]:
            render_static_image(BANNER_IMG, caption="Imagem ilustrativa do processo de geocodificação e emissão de certidões")


    def render_pipeline(self)->None:

        self.setup_page_config()
        with st.container(border=False):
            
            self.render_banner_img()
            self.render_title_section()
            self.render_description()

    def __call__(self)->None:
        """
        Método principal para renderizar o cabeçalho completo.
        """
        self.render_pipeline()