import streamlit as st
from typing import Optional, List, Dict
from frontend.dto.logradouro_match import (
    LogradouroMatchDTO, 
    LogradouroSearchResultsDTO
)

class LogradouroSearchProcessor:
    def __init__(self, matcher):
        self.matcher = matcher

    def _show_not_found_error(self):
        """
        Exibe feedback visual para buscas sem retorno.
        """
        st.error(
            "Não localizamos nenhum logradouro com o termo informado. "
            "Verifique a grafia ou tente um nome mais genérico."
        )

    def _build_results_dto(self, raw_matches: List[Dict]) -> Optional[LogradouroSearchResultsDTO]:
        """
        Encapsula a lógica de conversão e tratamento de erros de integridade.
        """
        try:
            input_processado = raw_matches[0]["input_processado"]
            matches_list = [
                LogradouroMatchDTO(logradouro=m["logradouro"], score=m["score"]) 
                for m in raw_matches
            ]
            
            return LogradouroSearchResultsDTO(
                input_usuario_processado=input_processado,
                matches=matches_list,
                match_100=any(m.score >= 100.0 for m in matches_list)
            )
        except (ValueError, KeyError, IndexError) as e:
            st.error(f"Erro na estruturação dos dados de resposta: {str(e)}")
            return None

    def __call__(self, logradouro_input: str) -> Optional[LogradouroSearchResultsDTO]:
        """
        Fluxo principal: Consulta, validação de existência e montagem do DTO.
        """
        with st.spinner("Consultando base de logradouros..."):
            raw_matches = self.matcher.find_matches_pipeline(logradouro_input)
        
        if not raw_matches:
            self._show_not_found_error()
            return None

        return self._build_results_dto(raw_matches)