import streamlit as st
import time
from typing import Optional
from frontend.dto.logradouro_match import LogradouroSearchResultsDTO
from frontend.state import AppState

class PerfectAddressMatchComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, appstate:AppState):
        self.results = results
        self.appstate = appstate

    def render(self):

        address_state = self.appstate.address_search_input
        if address_state is None or not address_state.submitted:
             st.warning("Nenhum endereço submetido. Por favor, preencha o formulário de busca de endereço.")
             st.stop()

        if self.appstate.logradouro_already_selected:
            logradouro = self.appstate.logradouro_selecionado
            st.info(f"Logradouro já selecionado: **{logradouro}**")
            return logradouro

        logradouro = self.results.melhor_match.logradouro        
        with st.columns([0.05, 0.9, 0.05])[1]:
            st.success(f"Logradouro identificado: **{logradouro}**")
            st.caption(f"Match perfeito encontrado para '{self.results.input_usuario_processado}'")
            st.checkbox('Teste')
        return logradouro
    

class ManualAddressSelectionComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, appstate: AppState):
        self.results = results
        self.appstate = appstate

    def render(self):

        if self.appstate.logradouro_already_selected:
            logradouro = self.appstate.logradouro_selecionado
            st.info(f"Logradouro já selecionado: **{logradouro}**")
            return logradouro

        opcoes = [m.logradouro for m in self.results.matches]
        captions = [f"Confiança: {m.score}%" for m in self.results.matches]


        with st.columns([0.05, 0.9, 0.05])[1]:
            st.warning(f"Não encontramos um match exato para '{self.results.input_usuario_processado}'.")
            
            with st.form(key="manual_address_selection_form"):
                escolha = st.radio(
                    "Selecione a opção correta:",
                    options=opcoes,
                    captions=captions,
                )
                submit_button = st.form_submit_button(label="Confirmar")
                if not submit_button:
                    st.stop()
                
            if escolha is None:
                st.warning("Nenhuma opção selecionada. Por favor, selecione um logradouro para continuar.")
                st.stop()

        return escolha