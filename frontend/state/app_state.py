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

       return self.get_value("address_search_form_filled", namespace="address") or False
    
    @address_search_form_filled.setter
    def address_search_form_filled(self, value: bool) -> None:
        self.set_value("address_search_form_filled", value, namespace="address")
    
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
        return self.get_value("logradouro_already_selected", namespace="address") or False
    
    @logradouro_already_selected.setter
    def logradouro_already_selected(self, value: bool)->None:
        self.set_value("logradouro_already_selected", value, namespace="address")
