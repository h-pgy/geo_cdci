from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.logradouro_fuzzy_search import LogradouroSearchResultsDTO, LogradouroChoiceDTO
from api.services.fuzzy_iptu_address_search import AddressMatcher
from typing import Optional, List
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.utils.message import info_message
from frontend.utils.maps.map_logradouro import LogradouroMapPlugin
from frontend.utils.button import ButtonGate
import streamlit as st

class PerfectMatchLogradouro(UIComponent[LogradouroChoiceDTO]):

    name = "PerfectMatchLogradouro"
    input_types = {LogradouroSearchResultsDTO}
    output_type = LogradouroChoiceDTO
    user_error_msg= "Ocorreu um erro ao processar o resultado da busca por logradouro. Por favor, revise os dados e tente novamente."

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()
        self.map_plugin = LogradouroMapPlugin()

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
    
    def show_map(self, container: StreamlitWidget, result: LogradouroChoiceDTO) -> None:

        logradouro_name = result.original_match.logradouro
        codlog = result.codlog

        container_map = container.container(border=True)
        container_map.markdown(f"#### Visualização do logradouro '{logradouro_name}' no mapa")
        mapa = self.map_plugin(codlog, container=container_map)

    def not_found_reinit(self, container:StreamlitWidget) -> bool:

        key_short_circuit_button = "logradouro_nao_encontrado_match_perfeito"
        gate_short_circuit = ButtonGate(key_short_circuit_button)
        space_short_circuit = container.empty()
        button_short_circuit = container.button("O logradouro exibido não é o que você esperava?", type="tertiary", on_click=gate_short_circuit.press)
        if gate_short_circuit.is_pressed:
            container_info_short_circuit = space_short_circuit.container(border=True)
            container_info_short_circuit.warning("Lamentamos que o resultado não tenha atendido às suas expectativas.", icon=":material/x_circle:")
            container_info_short_circuit.write('Tente realizar a busca novamente, certificando-se de que o nome do logradouro esteja correto e completo.')
            container_info_short_circuit.write('Caso o sistema não consiga encontrar o logradouro, não será possível a emissão da certidão de formar automatizada. Nesse caso, sugerimos solicitar a certidão manual pelo 156.')
            button_nova_busca = container_info_short_circuit.button("Realizar nova busca", type="primary", key="realizar_nova_busca_match_perfeito")
            button_continuar = container_info_short_circuit.button("Continuar mesmo assim", type="secondary", key="continuar_mesmo_assim_match_perfeito")
            if not (button_nova_busca or button_continuar):
                container_info_short_circuit.info("Favor escolher uma das opções para prosseguir.", icon=":material/info:")
                st.stop()
            if button_nova_busca:
                return True
        gate_short_circuit.reset()
        space_short_circuit.empty()
        return False
    
    def show_result_in_ui(self, col_result:StreamlitWidget, result: LogradouroChoiceDTO) -> None:

        codlog = result.codlog
        logradouro_name = result.original_match.logradouro
        
        with col_result:
            container_result = col_result.container()
            container_result.markdown(f"### Resultados da busca por logradouro")
            container_result.success(f"Match perfeito encontrado para '{logradouro_name}' com código {codlog}!", icon=":material/celebration:")
            
    def _render(self, container: StreamlitWidget, input_dtos: List[LogradouroSearchResultsDTO]) -> BaseComponentResponse[LogradouroChoiceDTO]:
        
        input_dto = input_dtos[0]
        logradouro = self.data_pipeline(input_dto)

        internal_container = container.container(border=True)
        col_result, col_mapa = internal_container.columns([1,2])

        self.show_result_in_ui(col_result, logradouro)
        self.show_map(col_mapa, logradouro)
        button_short_circuit = self.not_found_reinit(col_result)
        if button_short_circuit:
            return BaseComponentResponse(
                data = None,
                signal = AppFlowSignal.RERUN
            )

        
        message = info_message(
            self,
            body=f"O logradouro digitado possui um equivalente perfeito em nossa base de dados. Você será redirecionado para a próxima etapa automaticamente.",
            duration=3
        )

        return BaseComponentResponse(
            data = logradouro,
            signal = AppFlowSignal.GO,
            message=message
        )




    