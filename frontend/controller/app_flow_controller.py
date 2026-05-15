from frontend.state import AppState
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from .section import AppSection
from typing import Dict, Optional, Any
from pydantic import BaseModel

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

    def _invalidate_downstream(self, altered_section_name: str):
        """
        Percorre as seções registradas e remove do estado as respostas 
        de quem depende da seção alterada.
        """
        for name, section in self._sections.items():
            if altered_section_name in section.depends_on_names:
                self.state.delete_response(name)
                # Recursividade para limpar a cascata à frente
                self._invalidate_downstream(name)

    def _resolve_input(self, section: AppSection) -> Optional[BaseModel]:
        """
        Define qual dado será injetado no componente. 
        Se houver dependência, extrai o dado da resposta da primeira dependência.
        """
        if not section.depends_on_names:
            return section.initial_data
        
        # Por padrão, pega o dado do primeiro item na lista de dependências
        first_dep = list(section.depends_on_names)[0]
        parent_resp = self.state.get_response(first_dep)
        return parent_resp.data if parent_resp else None

    def trigger_section(self, name: str) -> Optional[BaseComponentResponse[Any]]:
        """
        Tenta renderizar e processar uma seção específica.
        """
        section = self._sections.get(name)
        if not section:
            raise ValueError(f"Section '{name}' não foi registrada.")

        # 1. Validação de Dependências
        if not self._check_dependencies(section):
            return None

        # 2. Resolução de Input
        input_dto = self._resolve_input(section)

        # 3. Execução do Componente (via interface UIComponent)
        response = section.component(
            container=section.container,
            input_dto=input_dto
        )

        # 4. Se o sinal não for GO, invalida tudo o que depende desta seção
        if response.signal != AppFlowSignal.GO:
            self._invalidate_downstream(name)

        # 5. Persistência da Resposta Completa
        self.state.store_response(name, response)

        return response