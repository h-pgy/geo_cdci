from frontend.state import AppState
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from .section import AppSection
from typing import Dict, Optional, Any
from pydantic import BaseModel
import streamlit as st

class AppFlowController:
    """
    O motor de inteligência da aplicação. 
    Valida dependências, gerencia a cascata de invalidação e executa os componentes.
    """
    def __init__(self, state: AppState):
        self.state = state
        self._sections: Dict[str, AppSection] = {}

    def register(self, section: AppSection) -> "AppFlowController":
        """Registra uma seção no catálogo do controlador."""
        self._sections[section.name] = section
        return self

    def _check_dependencies(self, section: AppSection) -> bool:
        """
        Verifica se todas as dependências declaradas possuem sinal GO no Estado.
        Lógica reside aqui, não no AppState.
        """
        for dep_name in section.depends_on_names:
            response = self.state.get_response(dep_name)
            if not response or response.signal != AppFlowSignal.GO:
                return False
        return True

    def _invalidate_downstream(self, altered_section: AppSection):
        """
        Percorre as seções registradas e remove do estado as respostas 
        de quem depende da seção alterada.
        """
        altered_section_name = altered_section.name
        for name, section in self._sections.items():
            if altered_section_name in section.depends_on_names:
                self.state.delete_response(name)
                # Recursividade para limpar a cascata à frente
                self._invalidate_downstream(section)

    def _resolve_input(self, section: AppSection) -> Optional[BaseModel]:
        """
        Define qual dado será injetado no componente. 
        Se houver dependência, extrai o dado da resposta da primeira dependência.
        """
        if not section.depends_on_names:
            return section.initial_data
        
        # Por padrão, pega o dado do primeiro item na lista de dependências
        first_dep = section.depends_on_names_list[0]
        parent_resp = self.state.get_response(first_dep)
        return parent_resp.data if parent_resp else None
    

    def trigger_section(self, section: AppSection) -> Optional[BaseComponentResponse[Any]]:
        """
        Tenta renderizar e processar uma seção específica.
        """

        print('Iniciando renderização da seção:', section.name)
        section_interna = self._sections.get(section.name)
        if not section_interna:
            raise ValueError(f"Section '{section.name}' não foi registrada.")

        if not self._check_dependencies(section_interna):
            return None

        input_dto = self._resolve_input(section_interna)

        response = section_interna.component(
            container=section_interna.container,
            input_dto=input_dto,
            state=self.state
        )

        self.state.store_response(section_interna.name, response)

        if response.signal != AppFlowSignal.GO:
            self._invalidate_downstream(section_interna)
            st.stop()


        return response