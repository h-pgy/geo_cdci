import streamlit as st
import time
from typing import Optional
from frontend.dto.logradouro_match import LogradouroSearchResultsDTO
from frontend.state import AppState


class AddressSelectionHandler:

    def __init__(self, appstate: AppState, space_logradouro_perfect_match, space_logradouro_fuzzy_match, space_results_logradouro):
        self.appstate = appstate
        self.space_logradouro_perfect_match = space_logradouro_perfect_match
        self.space_logradouro_fuzzy_match = space_logradouro_fuzzy_match
        self.space_results_logradouro = space_results_logradouro

    def render_results(self, logradouro_selecionado:str):
        with self.space_results_logradouro:
            with st.container(border=True):
                if logradouro_selecionado is not None:
                    st.success(f"Logradouro selecionado: {logradouro_selecionado}", icon=":material/house:")
                else:
                    st.warning("Nenhum logradouro selecionado. Por favor, revise os resultados da busca.", icon=":material/error:")

    def handle_selection(self, results: LogradouroSearchResultsDTO) -> str:

        with self.space_logradouro_perfect_match:
            logradouro_selecionado = match_ui = PerfectAddressMatchComponent(self.appstate)
            logradouro_selecionado = match_ui(results)
            if logradouro_selecionado is not None:
                return logradouro_selecionado
            
        with self.space_logradouro_fuzzy_match  :
            selection_ui = ManualAddressSelectionComponent(self.appstate)
            logradouro_selecionado = selection_ui(results)
            if logradouro_selecionado is not None:
                return logradouro_selecionado
            
        return None

    def render(self, results: LogradouroSearchResultsDTO):

        #escolha do logradouro com base na busca
        if results is not None:
            logradouro_selecionado = self.handle_selection(results)
            if logradouro_selecionado is not None:
                self.appstate.logradouro_selecionado = logradouro_selecionado
                self.appstate.logradouro_already_selected = True
                self.render_results(logradouro_selecionado)
                    

        return self.appstate.logradouro_selecionado
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str:

        return self.render(results)



class PerfectAddressMatchComponent:
    def __init__(self, appstate:AppState):
        self.appstate = appstate

    def render(self, results: LogradouroSearchResultsDTO)->str|None:

        with st.container(border=True):
            with st.spinner("Buscando logradouro na base..."):
                        time.sleep(1)
            if results.match_100:
                logradouro = results.melhor_match.logradouro
                
                st.success(f"Match perfeito encontrado para '{results.input_usuario_processado}' : {logradouro}", icon=":material/celebration: ")
                return logradouro
            else:    
                st.warning(f"Não encontramos um match exato para '{results.input_usuario_processado}'.", icon=":material/check_alert:")
                return None
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str|None:
        return self.render(results)
    

class ManualAddressSelectionComponent:
    def __init__(self, appstate: AppState):
        self.appstate = appstate


    def clean_up_state(self):

        self.appstate.delete_key("logradouro_selecionado")
        self.appstate.delete_key("logradouro_already_selected")

    def form(self, results: LogradouroSearchResultsDTO)->str|None:

        opcoes = [m.logradouro for m in results.matches]
        captions = [f"Confiança: {m.score}%" for m in results.matches]

        with st.form(key="manual_address_selection_form"):
            escolha = st.radio(
                "Selecione a opção correta:",
                options=opcoes,
                captions=captions,
            )
            submit_button = st.form_submit_button(label="Confirmar")
            with st.container():
                if not submit_button:
                    st.info("Selecione um logradouro e clique em 'Confirmar' para prosseguir.", icon=":material/left_click:")
                    #st.stop()
                    return self.appstate.logradouro_selecionado
                if submit_button and escolha is None:
                    st.warning("Nenhuma opção selecionada. Por favor, selecione um logradouro para prosseguir.", icon=":material/warning:")
                    return None
                if submit_button and escolha is not None:
                    self.clean_up_state()
                    return escolha
    

    def render(self, results: LogradouroSearchResultsDTO):
        
        with st.container(border=True):
            with st.container():
                escolha = self.form(results)
                with st.spinner("Processando seleção..."):
                    time.sleep(1)
                    st.space()
                                        
                return escolha
    
    def __call__(self, results: LogradouroSearchResultsDTO)->str|None:
        return self.render(results)