import streamlit as st
import time
from typing import Optional
from frontend.dto.logradouro_match import LogradouroSearchResultsDTO
from frontend.config import settings

SELECTED_LOGRADOURO_KEY = settings.SELECTED_LOGRADOURO_KEY
LOGRADOURO_MACHED = settings.LOGRADOURO_MACHED 

class PerfectAddressMatchComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, state_key: str=SELECTED_LOGRADOURO_KEY, matched_key: bool=LOGRADOURO_MACHED):
        self.results = results
        self.state_key = state_key
        self.matched_key = matched_key

    def render(self):

        if st.session_state.get(self.matched_key, False) and st.session_state.get(self.state_key):
            st.info(f"Logradouro já selecionado: **{st.session_state.get(self.state_key, '')}**")
            return st.session_state.get(self.state_key, '')

        logradouro = self.results.melhor_match.logradouro
        st.session_state[self.state_key] = logradouro
        st.session_state[self.matched_key] = True
        
        with st.columns([0.05, 0.9, 0.05])[1]:
            st.success(f"Logradouro identificado: **{logradouro}**")
            st.caption(f"Match perfeito encontrado para '{self.results.input_usuario_processado}'")
            st.checkbox('Teste')
        return logradouro
    

class ManualAddressSelectionComponent:
    def __init__(self, results: LogradouroSearchResultsDTO, state_key: str=SELECTED_LOGRADOURO_KEY, matched_key: bool=LOGRADOURO_MACHED):
        self.results = results
        self.state_key = state_key
        self.matched_key = matched_key

    def render(self):

        if st.session_state.get(self.matched_key, False) and st.session_state.get(self.state_key):
            st.info(f"Logradouro já selecionado: **{st.session_state.get(self.state_key, '')}**")
            return st.session_state.get(self.state_key, '')

        opcoes = [m.logradouro for m in self.results.matches]
        captions = [f"Confiança: {m.score}%" for m in self.results.matches]

        logradouro_anterior = st.session_state.get(self.state_key)

        index_ = opcoes.index(logradouro_anterior) if logradouro_anterior in opcoes else None

        with st.columns([0.05, 0.9, 0.05])[1]:
            st.warning(f"Não encontramos um match exato para '{self.results.input_usuario_processado}'.")
            
            with st.form(key="manual_address_selection_form"):
                escolha = st.radio(
                    "Selecione a opção correta:",
                    options=opcoes,
                    captions=captions,
                    index=index_
                )
                submit_button = st.form_submit_button(label="Confirmar")
                if not submit_button:
                    st.stop()
                
            if escolha is None:
                st.warning("Nenhuma opção selecionada. Por favor, selecione um logradouro para continuar.")
                st.stop()
          
        st.session_state[self.state_key] = escolha
        st.session_state[self.matched_key] = True

        return escolha