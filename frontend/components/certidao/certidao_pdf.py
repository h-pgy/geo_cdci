from api.services.certidao_pdf import GeradorCertidao, CertidaoModel
from api.services.lote.lote_data import LoteDataFetcher
from api.services.datetime.data_por_extenso import ConversorDataExtenso
from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.property_match import PropertyChoiceDTO
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.utils.button import ButtonGate
from frontend.dto.certidao import CertidaoDTO, DadosImovelCertidaoDTO
from frontend.utils.static import static_path
from frontend.utils.message import error_message, info_message, success_message
import streamlit as st
import os
import tempfile


class CertidaoPDFComponent(UIComponent[CertidaoDTO]):

    name= "CertidaoPDF"
    user_error_msg = "Ocorreu um erro ao gerar a certidão. Por favor, tente novamente ou entre em contato com o suporte."
    input_types={PropertyChoiceDTO}
    output_type=CertidaoDTO

    atributos_imovel_certidao = {
        "numero": "cd_numero_porta",
        "logradouro": "nm_logradouro_completo",
        "complemento": "tx_complemento_endereco",
        "codlog": "cd_logradouro",
        "cd_setor": "cd_setor_fiscal",
        "cd_quadra": "cd_quadra_fiscal",
        "cd_lote": "cd_lote"
    }

    def __init__(self)->None:

        self.atributos_imovel_wfs = list(self.atributos_imovel_certidao.values())
        self.fetch_lote_data = LoteDataFetcher()
        self.conveter_data_por_extenso = ConversorDataExtenso()
        self.tempdir = tempfile.gettempdir()

    def parse_lote_data_to_certidao_model(self, lote_data: dict[str, any]) -> DadosImovelCertidaoDTO:

        certidao_data = {}
        print('*' * 30)
        print("Lote data:", lote_data)  # Debug: Verificar os dados do lote
        for certidao_attr, lote_attr in self.atributos_imovel_certidao.items():
            certidao_data[certidao_attr] = lote_data.get(lote_attr, "")
        print("Certidão data mapeada:", certidao_data)  # Debug: Verificar os dados mapeados para a certidão
        return DadosImovelCertidaoDTO(**certidao_data)
                                  
    def dados_imovel(self, property_choice: PropertyChoiceDTO)->DadosImovelCertidaoDTO:

        cd_identificador = property_choice.cd_identificador_lote
        lote_data = self.fetch_lote_data(cd_identificador, atributes=self.atributos_imovel_wfs)
        return self.parse_lote_data_to_certidao_model(lote_data)
    
    def subsecao_dados_imovel(self, container: StreamlitWidget, dados_imovel: DadosImovelCertidaoDTO):

        container.markdown("#### Dados do Imóvel")
        container.markdown(f"- **Número**: {dados_imovel.numero}")
        container.markdown(f"- **Logradouro**: {dados_imovel.logradouro}")
        container.markdown(f"- **Complemento**: {dados_imovel.complemento}")
        container.markdown(f"- **Código do Logradouro**: {dados_imovel.codlog}")
        container.markdown(f"- **Setor/Quadra/Lote**: {dados_imovel.setor_quadra_lote}")

    def despacho(self, dados_imovel: DadosImovelCertidaoDTO) -> str:

        despacho = """

        ####Despacho

        ** Solicitação Deferida **

        Com base nas informações consultadas de forma automatizada junto à base de dados oficial do município de São Paulo, declara-se que o imóvel:

        * Possui lançamento do Imposto Predial e Territorial Urbano (IPTU) pelo contribuinte número {setor_quadra_lote}
        
        """

        return despacho.format(setor_quadra_lote=dados_imovel.setor_quadra_lote)
    
    def identificacao_do_imovel(self, dados_imovel: DadosImovelCertidaoDTO) -> str:

        identificacao = """

        ####Identificação do Imóvel

        O imóvel objeto desta certidão está localizado no endereço {logradouro}, número {numero}, complemento {complemento}, código do logradouro {codlog}.

        """
        return identificacao.format(
            logradouro=dados_imovel.logradouro,
            numero=dados_imovel.numero,
            complemento=dados_imovel.complemento,
            codlog=dados_imovel.codlog
        )

    def secoes_certidao(self, dados_imovel: DadosImovelCertidaoDTO) -> list[str]:

        dia_de_hoje = self.conveter_data_por_extenso()
        inicio = f"São Paulo, {dia_de_hoje}"
        identificacao_imovel = self.identificacao_do_imovel(dados_imovel)
        despacho = self.despacho(dados_imovel)

        return [inicio, identificacao_imovel, despacho]

    def gerar_certidao_model(self, dados_imovel: DadosImovelCertidaoDTO) -> CertidaoModel:

        cabecalho = "Certidão de Existência de Lançamento - IPTU"
        logo_cabecalho = static_path("logo_horizontal.png")
        logo_watermark = static_path("logo_vertical.png")
        rodape = "Esta certidão foi emitida de forma automatizada."

        return CertidaoModel(
            header=cabecalho,
            path_header_logo=logo_cabecalho,
            path_watermark=logo_watermark,
            footer=rodape,
            space_between_sections=6
            )


    def gerar_pdf_certidao(self, dados_imovel: DadosImovelCertidaoDTO) -> str:

        certidao_model = self.gerar_certidao_model(dados_imovel)
        gerar_certidao = GeradorCertidao(certidao_model)
        secoes = self.secoes_certidao(dados_imovel)

        fname = f"certidao_{dados_imovel.setor_quadra_lote}.pdf"
        output_path = os.path.join(self.tempdir, fname)
        if os.path.exists(output_path):
            os.remove(output_path)
        return gerar_certidao(secoes, output_path)
    
    def button_gerar_certidao_txt(self, gate_certidao: ButtonGate)->str:
        
        if gate_certidao.is_pressed:
            return "Atualizar Certidão"
        else:
            return "Gerar Certidão"
    
    def button_gerar_certidao_icon(self, gate_certidao: ButtonGate)->str:
        
        if gate_certidao.is_pressed:
            return ":material/directory_sync:"
        else:
            return ":material/check_circle:"


    def subsecao_gerar_certidao(self, container: StreamlitWidget, dados_imovel: DadosImovelCertidaoDTO, button_gate: ButtonGate):

    
        botao_text = self.button_gerar_certidao_txt(button_gate)
        botao_gerar= container.button(botao_text, on_click=button_gate.press)

        if button_gate.is_pressed:
            with container.spinner("Gerando certidão..."):
                caminho_certidao = self.gerar_pdf_certidao(dados_imovel)
                success_message(container, "Certidão gerada com sucesso!")
                return caminho_certidao
        else:
            container.info("Clique no botão para gerar a certidão.")
            st.stop()
            

    def subsecao_download_certidao(self, container: StreamlitWidget, path_certidao:str, button_gate: ButtonGate):

        botao_text = "Baixar Certidão"
        botao_icon = ":material/download:"

        botao_download = container.download_button(botao_text, 
                                                   icon=botao_icon,
                                                   data=open(path_certidao, "rb"), 
                                                   file_name=os.path.basename(path_certidao), 
                                                   mime="application/pdf",
                                                   on_click=button_gate.press
                                                   )

    def _render(self, container:StreamlitWidget, input_dtos:List[PropertyChoiceDTO])->BaseComponentResponse[CertidaoDTO]:

        property_choice = input_dtos[0]
        internal_container = container.container(border=True)
        internal_container.markdown("### Gerar Certidão.")
        internal_container.info(f"Verifique as informações do imóvel abaixo e clique no botão para gerar a certidão.")

        dados_imovel = self.dados_imovel(property_choice)
        self.subsecao_dados_imovel(internal_container, dados_imovel)

        gate_triger_certidao = ButtonGate("trigger_gerar_certidao")
        path_certidao = self.subsecao_gerar_certidao(internal_container, dados_imovel, gate_triger_certidao)

        button_download_gate = ButtonGate("trigger_download_certidao")
        if os.path.exists(path_certidao):
            self.subsecao_download_certidao(internal_container, path_certidao, button_download_gate)
        else:
            error_message(internal_container, "Erro ao gerar a certidão. Por favor, tente novamente.")
            st.stop()

        if button_download_gate.is_pressed:
            data= CertidaoDTO(
                certidao_path=path_certidao,
                dados_imovel=dados_imovel,
                input_data=property_choice
            )
            #desaperta botao de atualizar
            gate_triger_certidao.reset()

            message = success_message(self, "Certidão baixada com sucesso!")
            return BaseComponentResponse(data=data, signal=AppFlowSignal.GO, message=message)
        else:
            st.stop()
        



            


        

        