from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.logradouro_fuzzy_search import LogradouroChoiceDTO
from frontend.dto.property_match import PropertyChoiceDTO
from api.services.fuzzy_iptu_address_search import AddressMatcher
import pandas as pd
from frontend.components.property_selection.property_selection_subcomponent import DataEditorPropertyChoice
from typing import Optional, Tuple
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.utils.message import error_message, success_message

class PerfectPropertyMatch(UIComponent[PropertyChoiceDTO]):

    name = "PerfectPropertyMatch"
    user_error_msg = "O endereço selecionado existe em nosso banco de dados. No entanto, ocorreu um erro ao processar os dados para emissão da certidão. Entre em contato com o suporte"
    input_types={AddressInputDTO, LogradouroChoiceDTO}
    output_type=PropertyChoiceDTO

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()
        self.data_editor_component = DataEditorPropertyChoice(submit_button_key="perfect_match_submit")

    def extract_codlog(self, logradouro_choice: LogradouroChoiceDTO) -> str:
        return logradouro_choice.codlog
    
    def extract_numero_porta(self, address_input: AddressInputDTO) -> int:
        return int(address_input.numero)

    def get_address_info(self, logradouro_choice: LogradouroChoiceDTO, address_input: AddressInputDTO) -> Optional[pd.DataFrame]:
        
        codlog = self.extract_codlog(logradouro_choice)
        numero_porta = self.extract_numero_porta(address_input)
        return self.matcher.get_full_address_info_by_codlog(codlog, numero_porta)
    
    def unico_imovel(self, container:StreamlitWidget, imoveis: pd.DataFrame, numero:int, logradouro:LogradouroChoiceDTO) -> PropertyChoiceDTO:

        container.markdown(f"O endereço informado - **{logradouro.logradouro} {numero}** - correspondete ao imóvel abaixo.")
        imoveis_exibicao = self.data_editor_component.clean_dataframe(imoveis) 
        container.write(imoveis_exibicao)

        imovel_selecionado = imoveis.iloc[0]
        cd_identificador_lote = imovel_selecionado['cd_identificador']
        numero = imovel_selecionado['cd_numero_porta']

        data = PropertyChoiceDTO(numero=numero, logradouro_escolhido=logradouro, cd_identificador_lote=cd_identificador_lote)

        return data
    
    def varios_imoveis(self, container:StreamlitWidget, imoveis: pd.DataFrame, numero:int, logradouro:LogradouroChoiceDTO) -> Optional[PropertyChoiceDTO]:

        container.markdown(f"O endereço informado - **{logradouro.logradouro} {numero}** - corresponde a mais de um imóvel em nosso banco de dados. Por favor, selecione o imóvel correto para prosseguir com a emissão da certidão.")
        data_editor_response = self.data_editor_component.render(container, imoveis, title="Seleção de Imóvel", header_message="Marque a caixa de seleção ao lado do imóvel correspondente ao endereço informado.")
        
        if data_editor_response is None or data_editor_response.empty:
            container.warning("Nenhum imóvel selecionado. Por favor, selecione um imóvel para prosseguir.")
            return None
        
        index_selecionado = data_editor_response.index[0]
        imovel_selecionado = imoveis.loc[index_selecionado]

        numero = imovel_selecionado['cd_numero_porta']
        cd_identificador_lote = imovel_selecionado['cd_identificador']

        data = PropertyChoiceDTO(numero=numero, logradouro_escolhido=logradouro, cd_identificador_lote=cd_identificador_lote)

        return data
    
    
    def _render(self, container: StreamlitWidget, input_dtos: Tuple[LogradouroChoiceDTO, AddressInputDTO]) -> BaseComponentResponse[PropertyChoiceDTO]:

        logradouro_choice, address_input = input_dtos

        imoveis = self.get_address_info(
            logradouro_choice=logradouro_choice,
            address_input=address_input
        )

        if imoveis is None or imoveis.empty:
            error_msg_txt = "Não foi possível encontrar informações para o endereço selecionado. Por favor, verifique os dados e tente novamente."
            error_msg_obj = error_message(self, error_msg_txt)
            return BaseComponentResponse(signal=AppFlowSignal.ERROR, data=None, message=error_msg_obj)

        internal_container = container.container(border=True)
        internal_container.markdown("### Imóvel.")

        internal_container.info(f"Endereço {logradouro_choice.logradouro} {address_input.numero} encontrado em nosso banco de dados. Verifique as informações abaixo e prossiga para emissão da certidão.")

        if imoveis.shape[0]==1:
            
            data = self.unico_imovel(internal_container, imoveis, address_input.numero, logradouro_choice)

        else:
            data = self.varios_imoveis(internal_container, imoveis, address_input.numero, logradouro_choice)
            
        

        return BaseComponentResponse(signal=AppFlowSignal.GO, data=data)