import streamlit as st
import re

class AddressSearchForm:
    def __init__(self):
        """
        Inicializa o estado interno do componente se necessário.
        """
        pass

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
                        if not self.validate_logradouro(logradouro):
                            return {"submitted": False}
                        return {
                            "logradouro": logradouro,
                            "numero": numero,
                            "submitted": True
                        }
            
            return {"submitted": False}

    def __call__(self):
        """
        Permite chamar a instância da classe como uma função.
        """
        return self.render()