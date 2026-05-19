from frontend.components.base import UIComponent
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.dto.logradouro_fuzzy_search import LogradouroSearchResultsDTO, LogradouroChoiceDTO
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.utils.message import error_message, success_message, info_message
from frontend.utils.maps.map_logradouro import LogradouroMapPlugin
from typing import Optional
import time

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
        
    


