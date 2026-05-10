from .state_handler import AbstractAppState
from typing import Optional
from frontend.dto import LogradouroMatchDTO, LogradouroSearchResultsDTO, AddressSearchInputDTO

class AppState(AbstractAppState):

    @property
    def address_search_input(self) -> Optional[AddressSearchInputDTO]:
        return self.get_value("address_search_input", namespace="address")
    
    @address_search_input.setter
    def address_search_input(self, value: AddressSearchInputDTO) -> None:
        self.set_value("address_search_input", value, namespace="address")

    @property
    def address_search_form_filled(self)->bool:

        search_input = self.address_search_input
        return search_input is not None and search_input.submitted
    
    @property
    def logradouro_search_results(self) -> Optional[LogradouroSearchResultsDTO]:
        return self.get_value("logradouro_search_results", namespace="address")
    
    @logradouro_search_results.setter
    def logradouro_search_results(self, value: LogradouroSearchResultsDTO) -> None:
        self.set_value("logradouro_search_results", value, namespace="address")

    @property
    def logradouro_selecionado(self) -> Optional[str]:
        return self.get_value("selected_logradouro", namespace="address")

    @logradouro_selecionado.setter
    def logradouro_selecionado(self, value: str) -> None:
        self.set_value("selected_logradouro", value, namespace="address")

    @property
    def logradouro_already_selected(self)->bool:
        return self.logradouro_selecionado is not None
