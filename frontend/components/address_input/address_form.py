from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.header import HeaderRenderedDTO
from frontend.utils import message
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

class AddressForm(UIComponent[AddressInputDTO]):

    name = "AddressForm"
    user_error_msg = "Ocorreu um erro ao processar o formulário de endereço. Por favor, revise suas entradas e tente novamente."
    input_type=HeaderRenderedDTO
    output_type=AddressInputDTO

    def _render(self, container: StreamlitWidget, input_dto: HeaderRenderedDTO) -> BaseComponentResponse[AddressInputDTO]:

        with container.form(key="address_form"):
            st.write("### Insira o endereço do imóvel")
            st.write("Preencha os campos abaixo para iniciar o processo de geocodificação e emissão de certidões.")
            logradouro = st.text_input("Logradouro", placeholder="Ex: Avenida Paulista")
            numero = st.number_input("Número", placeholder="Ex: 1000")
    
            submit_button = st.form_submit_button(label="Enviar")

        if submit_button:
            address_data = AddressInputDTO(
                logradouro=logradouro,
                numero=int(numero)
            )
            return BaseComponentResponse(
                signal=AppFlowSignal.GO,
                data=address_data,
                message=message.success_message("Endereço enviado com sucesso! Iniciando processamento...")
            )

        return BaseComponentResponse(signal=AppFlowSignal.NO_GO, message=message.info_message("Aguardando o envio do endereço para iniciar o processamento."))
    