import streamlit as st
import time
from typing import Optional
from frontend.dto.address_search_input import AddressSearchInputDTO
from frontend.dto.logradouro_match import (
    LogradouroMatchDTO, 
    LogradouroSearchResultsDTO
)
from api.services.fuzzy_iptu_address_search import AddressMatcher
from frontend.config import settings

SELECTED_LOGRADOURO_KEY = settings.SELECTED_LOGRADOURO_KEY

class AddressResolverComponent:
    def __init__(self, matcher: AddressMatcher):
        """
        Componente responsável por resolver a ambiguidade de logradouros
        utilizando busca fonética e interface de seleção.
        """
        self.matcher = matcher
        self.state_key = SELECTED_LOGRADOURO_KEY

    def run_search(self, input_dto: AddressSearchInputDTO) -> Optional[LogradouroSearchResultsDTO]:
        """
        Executa o match fonético no service e encapsula o resultado no DTO.
        """
        raw_matches = self.matcher.find_matches(input_dto.logradouro)
        
        if not raw_matches:
            return None

        # O primeiro match contém o input processado pelo motor de busca
        input_processado = raw_matches[0]["input_processado"]

        matches_list = [
            LogradouroMatchDTO(
                logradouro=item["logradouro"], 
                score=item["score"]
            ) 
            for item in raw_matches
        ]

        has_match_100 = any(m.score >= 100.0 for m in matches_list)

        return LogradouroSearchResultsDTO(
            input_usuario_processado=input_processado,
            matches=matches_list,
            match_100=has_match_100
        )

    def handle_perfect_match(self, results: LogradouroSearchResultsDTO) -> str:
        """
        Caminho automático para quando a confiança é total.
        """
        logradouro_selecionado = results.melhor_match.logradouro
        st.session_state[self.state_key] = logradouro_selecionado
        return logradouro_selecionado

    def handle_manual_selection(self, results: LogradouroSearchResultsDTO) -> Optional[str]:
        """
        Apresenta interface de rádio para escolha manual do cidadão.
        """
        opcoes = [m.logradouro for m in results.matches]
        captions = [f"Nível de confiança: {m.score}%" for m in results.matches]

        st.warning(f"Não encontramos um match exato para o termo '{results.input_usuario_processado}'.")
        
        with st.form(key="logradouro_selection_form"):
            escolha = st.radio(
                "Selecione o logradouro correto entre as opções encontradas:",
                options=opcoes,
                captions=captions,
                index=0,
                help="Os nomes abaixo correspondem ao cadastro oficial da Prefeitura de São Paulo."
            )
            
            if st.form_submit_button("Confirmar seleção de logradouro"):
                st.session_state[self.state_key] = escolha
                return escolha
                
        
        return None

    def resolve_ui_flow(self, results: LogradouroSearchResultsDTO) -> Optional[str]:
        """
        Roteador de interface que gerencia o estado da seleção.
        """

        # Lógica de decisão inicial
        if results.match_100:
            logradouro_final = self.handle_perfect_match(results)

        else:
            logradouro_final = self.handle_manual_selection(results)
            
        return logradouro_final
    
    @property
    def logradouro_selected(self)->bool:

        return st.session_state.get(self.state_key) is not None
    
    def clean_selected_logradouro(self):
        if self.state_key in st.session_state:
            del st.session_state[self.state_key]

    def __call__(self, input_dto: AddressSearchInputDTO) -> Optional[str]:
        """
        Ponto de entrada do componente.
        """

        print(st.session_state.get(self.state_key))

        if not input_dto.submitted:
            # Reseta o estado caso o formulário de busca principal seja reiniciado
            self.clean_selected_logradouro()
            return None

        if self.logradouro_selected:
            logradouro_selecionado =  st.session_state.get(self.state_key)

        else:
        

            with st.spinner("Buscando logradouros correspondentes..."):
                results_dto = self.run_search(input_dto)

            if not results_dto:
                st.error("Nenhum logradouro encontrado. Verifique se o nome está correto.")
                return None

            logradouro_selecionado = self.resolve_ui_flow(results_dto)

        if logradouro_selecionado:
            st.info('Logradouro selecionado: ' + logradouro_selecionado)

        return logradouro_selecionado