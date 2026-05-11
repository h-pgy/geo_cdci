import streamlit as st
import time
from typing import Optional
from frontend.dto.logradouro_match import LogradouroSearchResultsDTO
from frontend.state import AppState


class AddressSelectionHandler:

    def __init__(self, appstate: AppState, space):
        self.appstate = appstate
        self.space = space

    def handle_selection(self, results: LogradouroSearchResultsDTO) -> str:

        if results.match_100:
            match_ui = PerfectAddressMatchComponent(self.appstate)
            logradouro_selecionado = match_ui(results)
            
        else:
            selection_ui = ManualAddressSelectionComponent(self.appstate)
            logradouro_selecionado = selection_ui(results)
        
        return logradouro_selecionado
    
    def render(self, results: LogradouroSearchResultsDTO):

        #escolha do logradouro com base na busca
        if results is not None:
            with self.space:
                with st.container(border=True):
                    logradouro_selecionado = self.handle_selection(results)
                    self.appstate.logradouro_selecionado = logradouro_selecionado
                    self.appstate.logradouro_already_selected = True
                    

        return self.appstate.logradouro_selecionado
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str:

        return self.render(results)



class PerfectAddressMatchComponent:
    def __init__(self, appstate:AppState):
        self.appstate = appstate

    def render(self, results: LogradouroSearchResultsDTO):

        logradouro = results.melhor_match.logradouro        
        st.success(f"Match perfeito encontrado para '{results.input_usuario_processado}' : {logradouro}", icon=":material/celebration: ")
        with st.spinner("Processando seleção..."):
            time.sleep(1)
        
        return logradouro
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str:
        return self.render(results)
    

class ManualAddressSelectionComponent:
    def __init__(self, appstate: AppState):
        self.appstate = appstate

    def form(self, results: LogradouroSearchResultsDTO):

        opcoes = [m.logradouro for m in results.matches]
        captions = [f"Confiança: {m.score}%" for m in results.matches]

        with st.form(key="manual_address_selection_form"):
            escolha = st.radio(
                "Selecione a opção correta:",
                options=opcoes,
                captions=captions,
            )
            submit_button = st.form_submit_button(label="Confirmar")
            if not submit_button:
                st.info("Selecione um logradouro e clique em 'Confirmar' para prosseguir.", icon=":material/left_click:")
                st.stop()
        
        return escolha
    

    def render(self, results: LogradouroSearchResultsDTO):
       
        st.warning(f"Não encontramos um match exato para '{results.input_usuario_processado}'.", icon=":material/check_alert:")
        space_form = st.empty()
        if not self.appstate.logradouro_already_selected:
            with space_form:
                escolha = self.form(results)
                with st.spinner("Processando seleção..."):
                    time.sleep(1)
                    st.space()
                                    
            return escolha
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str|None:
        return self.render(results)