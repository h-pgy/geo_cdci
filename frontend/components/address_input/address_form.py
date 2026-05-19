from frontend.components.base import UIComponent
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from frontend.dto.address_input import AddressInputDTO
from frontend.dto.header import HeaderRenderedDTO
from frontend.utils import message
from frontend.utils.button import ButtonGate
import re
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
import time
from frontend.config import settings

ERROR_MSG_DURATION_SECONDS = settings.ERROR_MSG_DURATION_SECONDS

class AddressForm(UIComponent[AddressInputDTO]):

    name = "AddressForm"
    user_error_msg = "Ocorreu um erro ao processar o formulário de endereço. Por favor, revise suas entradas e tente novamente."
    input_type=HeaderRenderedDTO
    output_type=AddressInputDTO

    def logradouro_input(self):
        """
        Renderiza o campo de texto para o nome da rua.
        """
        return st.text_input(
            "Logradouro",
            key="logradouro_input",
            placeholder="Ex: Avenida Paulista ou Rua Direita",
            help="O logradouro é o nome da rua, avenida, praça ou alameda onde o imóvel está localizado."
        )

    def numero_input(self):
        """
        Renderiza o campo numérico para a porta do imóvel.
        """

        return st.number_input(
            "Número",
            key="numero_input",
            min_value=1,
            step=1,
            help="Este é o número oficial da rua. Caso o seu imóvel seja um apartamento ou sala em um prédio, "
                 "digite o número principal do edifício. Você poderá detalhar a unidade mais adiante."
        )
    
    def help_logradouro(self):
        """
        Explicação detalhada sobre a identificação do logradouro.
        """
        with st.popover("Dúvidas sobre o logradouro?"):
            st.write(
                "O logradouro é o nome oficial da via (rua, avenida, praça, etc.) onde o imóvel está registrado. "
                "É necessário preencher este campo para que o sistema localize a face de quadra correspondente no mapa da cidade."
            )
            st.write(
                "O nome digitado passará por uma conferência automática com a base oficial da Prefeitura. "
                "Caso existam variações na escrita, o sistema apresentará as opções mais prováveis para sua escolha."
            )

    def help_numero(self):
        """
        Explicação detalhada sobre a numeração do imóvel.
        """
        with st.popover("Dúvidas sobre o número?"):
            st.write(
                "Utilizamos o número da porta para identificar a posição exata do imóvel dentro do logradouro. "
                "Esta informação é cruzada com o Cadastro Imobiliário Fiscal para vincular os dados do proprietário e as características do lote."
            )
            st.write(
                "Para condomínios ou edifícios, utilize o número principal da entrada. "
                "A localização precisa é fundamental para que o sistema gere o perímetro georreferenciado que constará na sua certidão."
            )

    def validate_logradouro(self, logradouro: str|None, container: StreamlitWidget) -> bool:
        """
        Valida se o logradouro possui apenas caracteres válidos e conteúdo suficiente.
        """

        if logradouro is None or len(logradouro)==0:
            self.flash_message(container, "O campo logradouro é obrigatório.", type="error")
            return False
        
        clean_text = str(logradouro).strip()
        
        if not clean_text:
            self.flash_message(container, "O campo logradouro não pode estar vazio.", type="error")
            return False

        if len(clean_text) < 2:
            self.flash_message(container, "O logradouro deve conter ao menos 2 caracteres.", type="error")
            return False

        # Verifica se existem caracteres que não deveriam estar em um nome de rua
        # Permite letras (incluindo acentuadas), números, espaços e hifens
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]+$', clean_text):
            self.flash_message(container, "O logradouro contém caracteres inválidos. Utilize apenas letras, números e espaços.")
            return False
            
        return True
    

    def define_submit_text(self) -> str:
        """
        Define o texto do botão de submit com base no estado atual do formulário.
        """
        if self.previous_response is not None or self.button_callback.is_pressed:
            return "Atualizar busca"
        else:
            return "Consultar Endereço"
    
    def define_submit_icon(self) -> str:
        """
        Define o ícone do botão de submit com base no estado atual do formulário.
        """

        if self.previous_response is not None or self.button_callback.is_pressed:
            return ":material/refresh:"
        else:
            return ":material/search:"
                        

    def form(self, container: StreamlitWidget) -> tuple[bool, str|None, int|None]:

        self.button_callback = ButtonGate("address_form_submit_pressed")

        container.write("Identificação do Imóvel")
        with container:
            with st.form(key="address_search_form", clear_on_submit=False):
                cols =  st.columns([0.75, 0.25])
                with cols[0]:
                    logradouro = self.logradouro_input()
                with cols[1]:
                    self.help_logradouro()
                cols = st.columns([0.75, 0.25])
                with cols[0]:
                    numero = self.numero_input()
                with cols[1]:
                    self.help_numero()

                submit_text = self.define_submit_text()
                submit_icon = self.define_submit_icon()
                submit_button = st.form_submit_button(submit_text, icon=submit_icon, on_click=self.button_callback.press)
                if not submit_button and not self.button_callback.is_pressed:
                    st.stop()
                return self.button_callback.is_pressed, logradouro, numero

    def _render(self, container: StreamlitWidget, input_dto: HeaderRenderedDTO) -> BaseComponentResponse[AddressInputDTO]:

        if not input_dto.rendered:
            return BaseComponentResponse(signal=AppFlowSignal.NO_GO, message=message.info_message(self, "Aguardando o carregamento do cabeçalho para exibir o formulário de endereço."))

        internal_container = container.container(border=True)
        internal_container.write("### Insira o endereço do imóvel")
        internal_container.write("Preencha os campos abaixo para iniciar o processo de geocodificação e emissão de certidões.")
        
        submit_button, logradouro, numero = self.form(internal_container)

        if submit_button:
            self.validate_logradouro(logradouro, internal_container)
            address_data = AddressInputDTO(
                logradouro=logradouro,
                numero=int(numero)
            )
            return BaseComponentResponse(
                signal=AppFlowSignal.GO,
                data=address_data,
                message=message.success_message(self, "Endereço enviado com sucesso! Iniciando processamento...",  duration=1)
            )

        return BaseComponentResponse(signal=AppFlowSignal.NO_GO, message=message.info_message(self, "Aguardando o envio do endereço para iniciar o processamento."))
    