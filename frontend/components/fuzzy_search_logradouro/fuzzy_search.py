from frontend.components.base import UIComponent
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.dto.logradouro_fuzzy_search import (LogradouroMatchDTO, LogradouroSearchResultsDTO)
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from typing import Optional, List
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.utils.message import error_message, success_message, processing_message, render_message


class LogradouroSearchProcessor(UIComponent[LogradouroSearchResultsDTO]):

    name = "LogradouroFuzzySearch"
    user_error_msg = "Ocorreu um erro ao fazer a busca do logradouro em nossa base de dados. Por favor revise suas entradas e tente novamente."
    input_types={AddressInputDTO}
    output_type=LogradouroSearchResultsDTO

    def __init__(self, matcher: Optional[AddressMatcher] = None):
        self.matcher = matcher or AddressMatcher()

    def _build_results_dto(self, raw_matches:List[dict], input_original:str)->Optional[LogradouroSearchResultsDTO]:
        """
        Encapsula a lógica de conversão e tratamento de erros de integridade.
        """
        try:
            input_processado = raw_matches[0]["input_processado"]
            matches_list = [
                LogradouroMatchDTO(logradouro=m["logradouro"], score=m["score"]) 
                for m in raw_matches
            ]
            
            return LogradouroSearchResultsDTO(
                input_original=input_original,
                input_usuario_processado=input_processado,
                matches=matches_list,
                match_100=any(m.score >= 100.0 for m in matches_list)
            )
        except (ValueError, KeyError, IndexError) as e:
            return None
        
    def fixed_error_msg(self, container: StreamlitWidget, logradouro_input:str)->None:
        
        internal_container = container.container(border=True)
        internal_container.error(f"Nenhum logradouro encontrado para o termo: '{logradouro_input}'. Verifique a grafia ou tente um nome mais genérico.")
        
    def pipeline(self, container: StreamlitWidget, input_dto: AddressInputDTO) -> BaseComponentResponse[LogradouroSearchResultsDTO]:
        
        logradouro_input = input_dto.logradouro

        raw_matches = self.matcher.find_matches_pipeline(logradouro_input)
        
        if not raw_matches:
            self.fixed_error_msg(container, logradouro_input)
            message = error_message(
                self,
                body=f"Não localizamos nenhum logradouro com o termo informado: {logradouro_input}. Verifique a grafia ou tente um nome mais genérico.",
                duration=3
            )
            return BaseComponentResponse(signal=AppFlowSignal.NO_GO, message=message)
        
        results_dto = self._build_results_dto(raw_matches, logradouro_input)

        if results_dto is None:
            message = error_message(
                self,
                body="Ocorreu um erro ao processar os resultados da busca. Por favor, tente novamente.",
                duration=3
            )
            return BaseComponentResponse(signal=AppFlowSignal.NO_GO, message=message)
        
        #sucesso

        message = success_message(
            self,
            body=f"Encontramos {len(results_dto.matches)} correspondências para o logradouro informado.",
            duration=2
        )

        return BaseComponentResponse(signal=AppFlowSignal.GO, data=results_dto, message=message)
    
    def _render(self, container: StreamlitWidget, input_dtos: List[AddressInputDTO]) -> BaseComponentResponse[LogradouroSearchResultsDTO]:
        
        input_dto = input_dtos[0]
        message=  processing_message(
            self,
            "Consultando base de logradouros..."
        )
        
        render_message(message, container)

        response = self.pipeline(container, input_dto)
    
        return response



