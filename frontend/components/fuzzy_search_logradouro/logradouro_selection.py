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
from typing import Optional, List

class LogradouroSelection(UIComponent[LogradouroChoiceDTO]):

    name = "LogradouroSelection"
    input_types = {LogradouroSearchResultsDTO}
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
            
    def not_found_reinit(self, container:StreamlitWidget) -> bool:

        key_short_circuit_button = "logradouro_nao_encontrado_logradouro_selection"
        gate_short_circuit = ButtonGate(key_short_circuit_button)
        space_short_circuit = container.empty()
        button_short_circuit = container.button("Você não encontrou o logradouro esperado?", type="tertiary", on_click=gate_short_circuit.press)
        if gate_short_circuit.is_pressed:
            container_info_short_circuit = space_short_circuit.container(border=True)
            container_info_short_circuit.warning("Lamentamos que o resultado não tenha atendido às suas expectativas.", icon=":material/x_circle:")
            container_info_short_circuit.write('Tente realizar a busca novamente, certificando-se de que o nome do logradouro esteja correto e completo.')
            container_info_short_circuit.write('Caso o sistema não consiga encontrar o logradouro, não será possível a emissão da certidão de formar automatizada. Nesse caso, sugerimos solicitar a certidão manual pelo 156.')
            button_nova_busca = container_info_short_circuit.button("Realizar nova busca", type="primary", key="realizar_nova_busca_logradouro_selection")
            button_continuar = container_info_short_circuit.button("Continuar mesmo assim", type="secondary", key="continuar_mesmo_assim_logradouro_selection")
            if not (button_nova_busca or button_continuar):
                container_info_short_circuit.info("Favor escolher uma das opções para prosseguir.", icon=":material/info:")
                st.stop()
            if button_nova_busca:
                return True
        gate_short_circuit.reset()
        space_short_circuit.empty()
        return False
            
    def show_map(self, container: StreamlitWidget, codlog: str, logradouro_name:str) -> None:

        container_map = container.container(border=True)
        container_map.markdown(f"#### Visualização do logradouro '{logradouro_name}' no mapa")
        mapa = self.map_plugin(codlog, container=container_map)
        
    def _render(self, container: StreamlitWidget, input_dtos: List[LogradouroSearchResultsDTO]) -> BaseComponentResponse[LogradouroChoiceDTO]:
        
        input_dto = input_dtos[0]
        self.assert_not_match_100(input_dto)
        internal_container = container.container(border=True)
        internal_container.markdown("### Resultados da busca por logradouro")
        internal_container.info("Não encontramos um match perfeito para o logradouro digitado. Por favor, selecione a opção correta abaixo para prosseguir.", icon=":material/info:")
        not_found_rerun = self.not_found_reinit(internal_container)
        if not_found_rerun:
            return BaseComponentResponse(
                data=None,
                signal=AppFlowSignal.RERUN,
                message=info_message(self, "Reiniciando a busca por logradouro para que você possa inserir uma nova consulta.")
            )
        results_container = internal_container.container()
        col_form, col_map = results_container.columns([1,2])
        escolha = self.form(input_dto, col_form)
        

        results = self.process_choice(escolha, input_dto, col_form)
        codlog = results.data.codlog
        self.show_map(col_map, codlog, escolha)
        return results