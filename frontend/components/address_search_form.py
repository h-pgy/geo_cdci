import streamlit as st
import re
from frontend.dto.address_search_input import AddressSearchInputDTO
from frontend.config import settings

SELECTED_LOGRADOURO_KEY = settings.SELECTED_LOGRADOURO_KEY
FORM_LOGRADOURO_SUBMITED_KEY = settings.FORM_LOGRADOURO_SUBMITED

class AddressSearchForm:


    @property
    def form_submitted(self) -> bool:
        """Verifica se o formulário de busca de endereço foi submetido.
        """
        return st.session_state.get(FORM_LOGRADOURO_SUBMITED_KEY, False)

    @property
    def logradouro_selecionado(self) -> str|None:
        """Verifica se um logradouro já foi selecionado na sessão.
        """
        return st.session_state.get(SELECTED_LOGRADOURO_KEY, '') 
    
    @property
    def logradouro_already_selected(self) -> bool:
        """Verifica se um logradouro já foi selecionado na sessão.
        """
        return bool(self.logradouro_selecionado)
    
    def empty_selected_logradouro(self):
        """Limpa o logradouro selecionado na sessão.
        """
        if SELECTED_LOGRADOURO_KEY in st.session_state:
            del st.session_state[SELECTED_LOGRADOURO_KEY]

    def logradouro_input(self):
        """
        Renderiza o campo de texto para o nome da rua.
        """
        return st.text_input(
            "Logradouro",
            placeholder="Ex: Avenida Paulista ou Rua Direita",
            help="O logradouro é o nome da rua, avenida, praça ou alameda onde o imóvel está localizado."
        )

    def numero_input(self):
        """
        Renderiza o campo numérico para a porta do imóvel.
        """
        return st.number_input(
            "Número",
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

    def validate_logradouro(self, logradouro: str|None) -> bool:
        """
        Valida se o logradouro possui apenas caracteres válidos e conteúdo suficiente.
        """

        if logradouro is None or len(logradouro)==0:
            st.error("O campo logradouro é obrigatório.")
            return False
        
        clean_text = str(logradouro).strip()
        
        if not clean_text:
            st.error("O campo logradouro não pode estar vazio.")
            return False

        if len(clean_text) < 2:
            st.error("O logradouro deve conter ao menos 2 caracteres.")
            return False

        # Verifica se existem caracteres que não deveriam estar em um nome de rua
        # Permite letras (incluindo acentuadas), números, espaços e hifens
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]+$', clean_text):
            st.error("O logradouro contém caracteres inválidos. Utilize apenas letras, números e espaços.")
            return False
            
        return True
    
    def desubmit_form(self):
        """Marca o formulário como não submetido para permitir novas consultas.
        """
        st.session_state[FORM_LOGRADOURO_SUBMITED_KEY] = False

    def clean_up_earlier_submission(self):
        if self.form_submitted:
            st.warning("O formulário já foi submetido. Atualizando os dados com a nova consulta.")
            self.desubmit_form()

        if self.logradouro_already_selected:
            st.warning(f'Apagando logradouro anteriormente selecionado: {self.logradouro_selecionado}.')
            self.empty_selected_logradouro()

    def render(self):
        """
        Orquestra a renderização dos inputs dentro de um formulário e container.
        """
        cols = st.columns([0.05, 0.9, 0.05])
        with cols[1]:
            with st.container(border=True):
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
                    
                    submit_button = st.form_submit_button("Consultar endereço")
                    
                    if submit_button:
                        
                        self.clean_up_earlier_submission()

                        if not self.validate_logradouro(logradouro):
                            return AddressSearchInputDTO(
                                logradouro="",
                                numero=0,
                                submitted=False
                            )
                        return AddressSearchInputDTO(
                            logradouro=logradouro,
                            numero=numero,
                            submitted=True
                        )
            
            return AddressSearchInputDTO(
                logradouro="",
                numero=0,
                submitted=False
            )

    def __call__(self)->AddressSearchInputDTO:
        """
        Permite chamar a instância da classe como uma função.
        """
        return self.render()