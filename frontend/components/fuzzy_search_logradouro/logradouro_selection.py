from frontend.components.base import UIComponent
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.dto.logradouro_fuzzy_search import LogradouroSearchResultsDTO, LogradouroMatchDTO, LogradouroChoiceDTO
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.utils.message import error_message, success_message, info_message, render_message
from frontend.utils.maps.map_logradouro import LogradouroMapPlugin
from frontend.utils.button import ButtonGate
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from typing import Optional

class LogradouroSelection(UIComponent[LogradouroChoiceDTO]):

    name = "LogradouroSelection"
    input_type = LogradouroSearchResultsDTO
    output_type = LogradouroChoiceDTO
    user_error_msg= "Ocorreu um erro ao processar a seleção de logradouro. Por favor, revise os dados e tente novamente."

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()
        self.map_plugin = LogradouroMapPlugin()

    def assert_not_match_100(self, input_dto: LogradouroSearchResultsDTO)->None:
        if input_dto.match_100:
            raise ValueError("O DTO de entrada não deve conter um match com score 100 para ser processado por este componente.")
        
    def get_logradouro_by_escolha(self, results: LogradouroSearchResultsDTO, escolha:str)->LogradouroMatchDTO:
        for match in results.matches:
            if match.logradouro == escolha:
                return match
        raise ValueError("A escolha selecionada não corresponde a nenhum logradouro nos resultados.")
        
    def blocking_messages(self, escolha:str|None)->None:

        if not self.button_gate.is_pressed:
           st.info('Selecione um logradouro e clique em "Confirmar" para prosseguir.', icon=":material/left_click:")
           st.stop()
        
        if self.button_gate.is_pressed and not escolha:
            st.warning("Nenhuma opção selecionada. Por favor, selecione um logradouro para prosseguir.", icon=":material/warning:")
            st.stop()
    
    def process_choice(self, escolha, results: LogradouroSearchResultsDTO, container: StreamlitWidget)->BaseComponentResponse[LogradouroChoiceDTO]:

        logradouro_escolhido = self.get_logradouro_by_escolha(results, escolha)
        codlog = self.matcher.get_codlog_by_logradouro(logradouro_escolhido.logradouro)

        sucess_message = info_message(self, 
                                         f"Logradouro '{logradouro_escolhido.logradouro}' selecionado com confiança de {logradouro_escolhido.score}%. Codlog: {codlog}")
        container.info('Logradouro selecionado: ' + escolha, icon=":material/check_circle:")
        return BaseComponentResponse(
            data=LogradouroChoiceDTO(original_match=logradouro_escolhido, codlog=codlog),
            signal=AppFlowSignal.GO,
            message=sucess_message
        )
    
    def define_button_label(self)->str:

        if self.button_gate.is_pressed:
            return "Atualizar escolha"
        return "Confirmar"

    
    def form(self, results: LogradouroSearchResultsDTO, container: StreamlitWidget)->str:

        opcoes = [m.logradouro for m in results.matches]
        captions = [f"Confiança: {m.score}%" for m in results.matches]

        self.button_gate = ButtonGate("confirm_logradouro_selection_gate")

        with container:
            with st.form(key="manual_address_selection_form"):
                escolha = st.radio(
                    "Selecione a opção correta:",
                    options=opcoes,
                    captions=captions,
                )
                button_label = self.define_button_label()
                submit_button = st.form_submit_button(label=button_label,  on_click=self.button_gate.press)
                
                self.blocking_messages(escolha)

                return escolha
            
    def show_map(self, container: StreamlitWidget, codlog: str, logradouro_name:str) -> None:

        container_map = container.container(border=True)
        container_map.markdown(f"#### Visualização do logradouro '{logradouro_name}' no mapa")
        mapa = self.map_plugin(codlog, container=container_map)
        
    def _render(self, container: StreamlitWidget, input_dto: LogradouroSearchResultsDTO) -> BaseComponentResponse[LogradouroChoiceDTO]:
        
        self.assert_not_match_100(input_dto)
        internal_container = container.container(border=True)
        internal_container.markdown("### Resultados da busca por logradouro")
        internal_container.info("Não encontramos um match perfeito para o logradouro digitado. Por favor, selecione a opção correta abaixo para prosseguir.", icon=":material/info:")

        escolha = self.form(input_dto, internal_container)
        results = self.process_choice(escolha, input_dto, internal_container)
        codlog = results.data.codlog
        self.show_map(internal_container, codlog, escolha)
        return results