from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.logradouro_fuzzy_search import LogradouroSearchResultsDTO, LogradouroChoiceDTO
from api.services.fuzzy_iptu_address_search import AddressMatcher
from typing import Optional
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.utils.message import info_message
import streamlit as st

class PerfectMatchLogradouro(UIComponent[LogradouroChoiceDTO]):

    name = "PerfectMatchLogradouro"
    input_type = LogradouroSearchResultsDTO
    output_type = LogradouroChoiceDTO
    user_error_msg= "Ocorreu um erro ao processar o resultado da busca por logradouro. Por favor, revise os dados e tente novamente."

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()

    def assert_match_100(self, input_dto: LogradouroSearchResultsDTO)->None:
        if not input_dto.match_100:
            raise ValueError("O DTO de entrada deve conter um match com score 100 para ser processado por este componente.")
        
    def extract_perfect_match(self, input_dto: LogradouroSearchResultsDTO) -> str:

        return input_dto.melhor_match.logradouro

    def data_pipeline(self, input_dto: LogradouroSearchResultsDTO) -> LogradouroChoiceDTO:

        self.assert_match_100(input_dto)
        logradouro = self.extract_perfect_match(input_dto)
        codlog = self.matcher.get_codlog_by_logradouro(logradouro)

        result = LogradouroChoiceDTO(
            original_match = input_dto.melhor_match,
            codlog = codlog
        )

        return result
    
    def show_result_in_ui(self, container:StreamlitWidget, result: LogradouroChoiceDTO) -> None:

        internal_container = container.container(border=True)
        internal_container.markdown(f"### Resultados da busca por logradouro")
        internal_container.success(f"Match perfeito encontrado para '{result.original_match.logradouro}' com código {result.codlog}!", icon=":material/celebration:")
    
    def _render(self, container: StreamlitWidget, input_dto: LogradouroSearchResultsDTO) -> BaseComponentResponse[LogradouroChoiceDTO]:
        
        logradouro = self.data_pipeline(input_dto)
        self.show_result_in_ui(container, logradouro)

        message = info_message(
            body=f"O logradouro digitado possui um equivalente perfeito em nossa base de dados. Você será redirecionado para a próxima etapa automaticamente.",
            duration=5
        )

        return BaseComponentResponse(
            data = logradouro,
            signal = AppFlowSignal.GO,
            message=message
        )




    