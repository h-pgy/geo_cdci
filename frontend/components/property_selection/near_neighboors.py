from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.logradouro_fuzzy_search import LogradouroChoiceDTO
from frontend.dto.property_match import PropertyChoiceDTO
from frontend.utils.button import ButtonGate
from frontend.utils.message import error_message, warning_message, success_message
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.components.property_selection.property_selection_subcomponent import DataEditorPropertyChoice
from frontend.utils.maps.map_lote_unico import LoteUnicoMapPlugin
import pandas as pd
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from typing import Optional, Tuple
import streamlit as st

from frontend.utils.message import warning_message, error_message



class NearNeighboorsPropertyMatch(UIComponent[PropertyChoiceDTO]):

    name = "NearNeighboorsPropertyMatch"
    user_error_msg = "Ocorreu um problema ao buscar os endereços mais próximos do endereço selecionado. Entre em contato com o suporte"
    input_types={AddressInputDTO, LogradouroChoiceDTO}
    output_type=PropertyChoiceDTO

    def __init__(self, matcher: Optional[AddressMatcher] = None)->None:
        self.matcher = matcher or AddressMatcher()
        self.data_editor_component = DataEditorPropertyChoice(submit_button_key="nearest_neighboors_submit")
        self.render_map_lote = LoteUnicoMapPlugin()

    def extract_codlog(self, logradouro_choice: LogradouroChoiceDTO) -> str:
        return logradouro_choice.codlog
    
    def extract_numero_porta(self, address_input: AddressInputDTO) -> int:
        return int(address_input.numero)

    def get_address_info(self, logradouro_choice: LogradouroChoiceDTO, numero_porta: int) -> Optional[pd.DataFrame]:
        codlog = logradouro_choice.codlog
        return self.matcher.get_full_address_info_by_codlog(codlog, numero_porta)
    
    def not_found_reinit(self, container:StreamlitWidget) -> bool:

        key_short_circuit_button = "imovel_nao_encontrado_near_neighboors"
        gate_short_circuit = ButtonGate(key_short_circuit_button)
        space_short_circuit = container.empty()
        button_short_circuit = container.button("O imóvel esperado não está na lista abaixo?", type="tertiary", on_click=gate_short_circuit.press)
        if gate_short_circuit.is_pressed:
            container_info_short_circuit = space_short_circuit.container(border=True)
            container_info_short_circuit.warning("Lamentamos que o resultado não tenha atendido às suas expectativas.", icon=":material/x_circle:")
            container_info_short_circuit.write('Tente realizar a busca novamente, certificando-se de que o número do imóvel esteja correto e completo.')
            container_info_short_circuit.write('Caso o sistema não consiga encontrar o imóvel, não será possível a emissão da certidão de formar automatizada. Nesse caso, sugerimos solicitar a certidão manual pelo 156.')
            button_nova_busca = container_info_short_circuit.button("Realizar nova busca", type="primary", key="realizar_nova_busca_imovel_selection")
            button_continuar = container_info_short_circuit.button("Continuar mesmo assim", type="secondary", key="continuar_mesmo_assim_imovel_selection")
            if not (button_nova_busca or button_continuar):
                container_info_short_circuit.info("Favor escolher uma das opções para prosseguir.", icon=":material/info:")
                st.stop()
            if button_nova_busca:
                return True
        gate_short_circuit.reset()
        space_short_circuit.empty()
        return False
    
    def imovel_selection(self, container:StreamlitWidget, imoveis: pd.DataFrame, numero:int, logradouro:LogradouroChoiceDTO) -> Optional[PropertyChoiceDTO]:

        index_selecionado = self.data_editor_component(imoveis, container, title="Seleção de Imóvel", header_message="Marque a caixa de seleção ao lado do registro correspondente ao imóvel. Ao selecionar, o imóvel será mostrado no mapa ao lado.")
        
        if index_selecionado is None:
            container.warning("Nenhum imóvel selecionado. Por favor, selecione um imóvel para prosseguir.")
            st.stop()
        
        imovel_selecionado = imoveis.loc[index_selecionado]

        numero = imovel_selecionado['cd_numero_porta']
        cd_identificador_lote = imovel_selecionado['cd_identificador']

        data = PropertyChoiceDTO(numero=numero, logradouro_escolhido=logradouro, cd_identificador_lote=cd_identificador_lote)

        return data
    
    def _render(self, container: StreamlitWidget, input_dtos: Tuple[LogradouroChoiceDTO, AddressInputDTO]) -> BaseComponentResponse[PropertyChoiceDTO]:

        logradouro_choice, address_input = input_dtos

        imoveis = self.matcher.get_nearest_neighbor_addresses(logradouro_choice.codlog, int(address_input.numero))

        if imoveis is None or imoveis.empty:
            not_found_error_message = error_message(self,
                                                    "Não foi possível encontrar imóveis próximos ao endereço selecionado.")
            return BaseComponentResponse(signal=AppFlowSignal.ERROR, data=None, message=not_found_error_message)
        
        internal_contaienr = container.container(border=True)
        internal_contaienr.markdown("### Endereços próximos encontrados")
        internal_contaienr.markdown(f"O endereço informado - **{logradouro_choice.logradouro} {address_input.numero}** - não foi encontrado em nossa base de dados. Mas buscamos aqui os imóveis com a numeração mais próxima da numeração informada para o logradouro selecionado. Por favor, selecione o imóvel correto para prosseguir com a emissão da certidão.")
        not_found_rerun = self.not_found_reinit(internal_contaienr)
        if not_found_rerun:
            return BaseComponentResponse(
                signal=AppFlowSignal.RERUN,
                data=None,
                message=warning_message(self, "Reiniciando a busca por imóveis próximos para que você possa inserir uma nova consulta.")
            )
        
        col_selection, col_mapa = internal_contaienr.columns([2,1])

        data = self.imovel_selection(col_selection, imoveis, int(address_input.numero), logradouro_choice)
        if data:
            self.render_map_lote(data.cd_identificador_lote, col_mapa)

        message = success_message(self, "Imóvel identificado com sucesso! Prosseguindo para a próxima etapa.")

        return BaseComponentResponse(signal=AppFlowSignal.GO, data=data, message=message)