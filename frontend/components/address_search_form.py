import streamlit as st
import re
from frontend import dto
from frontend.dto.address_search_input import AddressSearchInputDTO
from frontend.config import settings
from frontend.state import AppState

class AddressSearchForm:


    def __init__(self, appstate: AppState)->None:
        self.appstate = appstate

    
    def logradouro_input(self):
        """
        Renderiza o campo de texto para o nome da rua.
        """

        value = self.appstate.address_search_input.logradouro if self.appstate.address_search_input else ""

        return st.text_input(
            "Logradouro",
            value=value,
            placeholder="Ex: Avenida Paulista ou Rua Direita",
            help="O logradouro é o nome da rua, avenida, praça ou alameda onde o imóvel está localizado."
        )

    def numero_input(self):
        """
        Renderiza o campo numérico para a porta do imóvel.
        """

        value = self.appstate.address_search_input.numero if self.appstate.address_search_form_filled else 1

        return st.number_input(
            "Número",
            min_value=1,
            step=1,
            value=value,
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

    def validate_logradouro(self, logradouro: str|None) -> bool:
        """
        Valida se o logradouro possui apenas caracteres válidos e conteúdo suficiente.
        """

        if logradouro is None or len(logradouro)==0:
            st.error("O campo logradouro é obrigatório.")
            return False
        
        clean_text = str(logradouro).strip()
        
        if not clean_text:
            st.error("O campo logradouro não pode estar vazio.", icon=":material/error:")
            return False

        if len(clean_text) < 2:
            st.error("O logradouro deve conter ao menos 2 caracteres.", icon=":material/error:")
            return False

        # Verifica se existem caracteres que não deveriam estar em um nome de rua
        # Permite letras (incluindo acentuadas), números, espaços e hifens
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]+$', clean_text):
            st.error("O logradouro contém caracteres inválidos. Utilize apenas letras, números e espaços.", icon=":material/error:")
            return False
            
        return True
    

    def define_submit_text(self)->str:
        """
        Define o texto do botão de submit com base no estado atual do formulário.
        """
        if self.appstate.address_search_input is None or not self.appstate.address_search_input.submitted:
            return "Consultar endereço"
        else:
            return "Atualizar busca"
        
    def define_submit_icon(self)->str:
        """
        Define o ícone do botão de submit com base no estado atual do formulário.
        """
        if self.appstate.address_search_input is None or not self.appstate.address_search_input.submitted:
            return ":material/search:"
        else:
            return ":material/refresh:"

    def form(self):

        st.write("Identificação do Imóvel")
                
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
            submit_button = st.form_submit_button(submit_text, icon=submit_icon)
            return submit_button, logradouro, numero
        
    def state_clean_up(self):
        self.appstate.delete_key("selected_logradouro", namespace="address")
        self.appstate.delete_key("logradouro_already_selected", namespace="address")
        self.appstate.delete_key("logradouro_search_results", namespace="address")

    def render(self) -> AddressSearchInputDTO:
        """
        Orquestra a renderização dos inputs dentro de um formulário e container.
        """
     
        with st.container(border=True):
            
                submit_button, logradouro, numero = self.form()
                if submit_button:
                    
                    #aqui precisa apagar o logradouro selecionado
                    self.state_clean_up()
                    
                    if self.validate_logradouro(logradouro):
                        dto = AddressSearchInputDTO(
                            logradouro=logradouro,
                            numero=numero,
                            submitted=True
                        )
                        self.appstate.address_search_form_filled = True
                        self.appstate.address_search_input = dto
                        return dto        
                else:
                    if not self.appstate.address_search_form_filled:
                        st.info("Preencha o formulário e clique em 'Consultar endereço' para iniciar a busca.", icon=":material/type_specimen:")
                        st.stop()
                    else:
                        #form já preenchido, apenas renderiza os dados atuais
                        dto = AddressSearchInputDTO(
                            logradouro=logradouro,
                            numero=numero,
                            submitted=True
                        )
                        return dto


    def __call__(self)->AddressSearchInputDTO:
        """
        Permite chamar a instância da classe como uma função.
        """
        return self.render()