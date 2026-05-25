from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.logradouro_fuzzy_search import LogradouroChoiceDTO
from frontend.dto.property_match import PropertyChoiceDTO
from api.services.fuzzy_iptu_address_search import AddressMatcher
import pandas as pd
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from typing import Optional, Tuple

from frontend.utils.message import warning_message



class NearNeighboorsPropertyMatch(UIComponent[PropertyChoiceDTO]):

    name = "NearNeighboorsPropertyMatch"
    user_error_msg = "Ocorreu um problema ao buscar os endereços mais próximos do endereço selecionado. Entre em contato com o suporte"
    input_types={AddressInputDTO, LogradouroChoiceDTO}
    output_type=PropertyChoiceDTO

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()

    def extract_codlog(self, logradouro_choice: LogradouroChoiceDTO) -> str:
        return logradouro_choice.codlog
    
    def extract_numero_porta(self, address_input: AddressInputDTO) -> int:
        return int(address_input.numero)

    def get_address_info(self, logradouro_choice: LogradouroChoiceDTO, numero_porta: int) -> Optional[pd.DataFrame]:
        codlog = logradouro_choice.codlog
        return self.matcher.get_full_address_info_by_codlog(codlog, numero_porta)
    
    def _render(self, container: StreamlitWidget, input_dtos: Tuple[AddressInputDTO, LogradouroChoiceDTO]) -> BaseComponentResponse[PropertyChoiceDTO]:

        message = warning_message(self, "Match não perfeita de endereço. Em desenvolvimento")

        return BaseComponentResponse(signal=AppFlowSignal.NO_GO, data=None, message=message)