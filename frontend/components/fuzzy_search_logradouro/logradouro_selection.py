from frontend.components.base import UIComponent
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.dto.logradouro_fuzzy_search import LogradouroSearchResultsDTO, LogradouroMatchDTO, LogradouroChoiceDTO
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.utils.message import error_message, success_message, info_message, render_message
from frontend.utils.maps.map_logradouro import LogradouroMapPlugin
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

    def assert_not_match_100(self, input_dto: LogradouroSearchResultsDTO)->None:
        if input_dto.match_100:
            raise ValueError("O DTO de entrada não deve conter um match com score 100 para ser processado por este componente.")
        
    def get_logradouro_by_escolha(self, results: LogradouroSearchResultsDTO, escolha:str)->LogradouroMatchDTO:
        for match in results.matches:
            if match.logradouro == escolha:
                return match
        raise ValueError("A escolha selecionada não corresponde a nenhum logradouro nos resultados.")
        
    def blocking_messages(self, submit_button:bool, escolha:str|None)->None:

        if not submit_button:
           st.info('Selecione um logradouro e clique em "Confirmar" para prosseguir.', icon=":material/left_click:")
           st.stop()
        
        if submit_button and not escolha:
            st.warning("Nenhuma opção selecionada. Por favor, selecione um logradouro para prosseguir.", icon=":material/warning:")
            st.stop()
    
    def process_choice(self, escolha, results: LogradouroSearchResultsDTO)->BaseComponentResponse[LogradouroChoiceDTO]:

        logradouro_escolhido = self.get_logradouro_by_escolha(results, escolha)
        codlog = self.matcher.get_codlog_by_logradouro(logradouro_escolhido.logradouro)

        sucess_message = info_message(self, 
                                         f"Logradouro '{logradouro_escolhido.logradouro}' selecionado com confiança de {logradouro_escolhido.score}%. Codlog: {codlog}")
        st.info('Logradouro selecionado: ' + escolha, icon=":material/check_circle:")
        return BaseComponentResponse(
            data=LogradouroChoiceDTO(original_match=logradouro_escolhido, codlog=codlog),
            signal=AppFlowSignal.GO,
            message=sucess_message
        )

    
    def form(self, results: LogradouroSearchResultsDTO, container: StreamlitWidget)->BaseComponentResponse[LogradouroChoiceDTO]:

        opcoes = [m.logradouro for m in results.matches]
        captions = [f"Confiança: {m.score}%" for m in results.matches]

        with container:
            with st.form(key="manual_address_selection_form"):
                escolha = st.radio(
                    "Selecione a opção correta:",
                    options=opcoes,
                    captions=captions,
                )
                submit_button = st.form_submit_button(label="Confirmar")
                
                self.blocking_messages(submit_button, escolha)

                return self.process_choice(escolha, results)
        
    def _render(self, container: StreamlitWidget, input_dto: LogradouroSearchResultsDTO) -> BaseComponentResponse[LogradouroChoiceDTO]:
        
        self.assert_not_match_100(input_dto)
        internal_container = container.container(border=True)
        internal_container.markdown("### Resultados da busca por logradouro")
        internal_container.info("Não encontramos um match perfeito para o logradouro digitado. Por favor, selecione a opção correta abaixo para prosseguir.", icon=":material/info:")

        return self.form(input_dto, internal_container)