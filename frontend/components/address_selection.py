import streamlit as st
import time
from typing import Optional
from frontend.dto.logradouro_match import LogradouroSearchResultsDTO
from frontend.state import AppState


class AddressSelectionHandler:

    def __init__(self, results: LogradouroSearchResultsDTO, appstate: AppState):
        self.results = results
        self.appstate = appstate

    def handle_selection(self) -> str:

        if self.results.match_100:
            match_ui = PerfectAddressMatchComponent(self.results, self.appstate)
            logradouro_selecionado = match_ui()
            
        else:
            selection_ui = ManualAddressSelectionComponent(self.results, self.appstate)
            logradouro_selecionado = selection_ui()
        
        return logradouro_selecionado
    
    def render(self)->str:

        if not self.appstate.address_search_form_filled:
             st.warning("Nenhum endereço submetido. Por favor, preencha o formulário de busca de endereço.")
             st.stop()

        if self.appstate.logradouro_already_selected:
            logradouro = self.appstate.logradouro_selecionado
            st.info(f"Logradouro já selecionado: **{logradouro}**")
            return logradouro
        
        logradouro_selecionado = self.handle_selection()
        return logradouro_selecionado
    
    def __call__(self)->str:
        return self.render()


class PerfectAddressMatchComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, appstate:AppState):
        self.results = results
        self.appstate = appstate

    def render(self):

        logradouro = self.results.melhor_match.logradouro        
        with st.columns([0.05, 0.9, 0.05])[1]:
            st.success(f"Logradouro identificado: **{logradouro}**")
            st.caption(f"Match perfeito encontrado para '{self.results.input_usuario_processado}'")
            st.checkbox('Teste')
        return logradouro
    
    def __call__(self)->str:
        return self.render()
    

class ManualAddressSelectionComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, appstate: AppState):
        self.results = results
        self.appstate = appstate

    def render(self):

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
    
    def __call__(self)->str:
        return self.render()