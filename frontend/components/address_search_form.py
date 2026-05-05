import streamlit as st

class AddressSearchForm:
    def __init__(self):
        """
        Inicializa o estado interno do componente se necessário.
        """
        pass

    def render_logradouro_input(self):
        """
        Renderiza o campo de texto para o nome da rua.
        """
        return st.text_input(
            "Logradouro",
            placeholder="Ex: Avenida Paulista ou Direita",
            help="O logradouro é o nome da rua, avenida, praça ou alameda onde o imóvel está localizado."
        )

    def render_numero_input(self):
        """
        Renderiza o campo numérico para a porta do imóvel.
        """
        return st.number_input(
            "Número",
            min_value=0,
            step=1,
            help="Este é o número oficial da rua. Caso o seu imóvel seja um apartamento ou sala em um prédio, "
                 "digite o número principal do edifício. Você poderá detalhar a unidade mais adiante."
        )

    def render(self):
        """
        Orquestra a renderização dos inputs dentro de um formulário e container.
        """
        with st.container(border=True):
            st.write("Identificação do Imóvel")
            
            with st.form(key="address_search_form", clear_on_submit=False):
                logradouro = self.render_logradouro_input()
                numero = self.render_numero_input()
                
                submit_button = st.form_submit_button("Consultar endereço")
                
                if submit_button:
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