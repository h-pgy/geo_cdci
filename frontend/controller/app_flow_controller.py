from frontend.state import AppState
from frontend.dto.base import BaseComponentResponse, AppFlowSignal
from .section import AppSection
from typing import Dict, Optional, Any, List
from pydantic import BaseModel
from collections import OrderedDict
import streamlit as st
from frontend.utils.message import info_message

class AppFlowController:
    """
    O motor de inteligência da aplicação. 
    Valida dependências, gerencia a cascata de invalidação e executa os componentes.
    """
    def __init__(self, state: AppState):
        self.state = state
        self._sections: Dict[str, AppSection] = OrderedDict()

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

    def _invalidate_all_rerun(self):
        """Pega a primeira seção e invalida todas após ela. Depois roda o app novamente"""

        primeira_secao = list(self._sections.values())[0]
        self._invalidate_downstream(primeira_secao)
        st.session_state.clear()
        st.rerun()


    def _resolve_input(self, section: AppSection) -> Optional[List[BaseModel|None]]|None:
        """
        Define qual dado será injetado no componente. 
        """
        if not section.depends_on_names:
            return section.initial_data
        
        # Por padrão, pega o dado do primeiro item na lista de dependências
        resps = [self.state.get_response(dep_name) for dep_name in section.depends_on_names_list]
        data = [resp.data for resp in resps]
        return data
    
    def bypass_section(self, section:AppSection, data:Optional[Any]=None)->None:
        """Força o bypass de uma seção, forçando o resultado GO."""
        nome_secao = section.name
        message = info_message(section.component, f"Seção '{nome_secao}' foi marcada para bypass. Pulando a execução dela e de suas dependências.")            
        bypass_response = BaseComponentResponse(signal=AppFlowSignal.GO, data=data, message=message)
        section.component._validate_output(bypass_response)
        self.state.store_response(section.name, bypass_response)
    
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

        input_dtos = self._resolve_input(section_interna)

        response = section_interna.component(
            container=section_interna.container,
            input_dtos=input_dtos,
            state=self.state
        )

        self.state.store_response(section_interna.name, response)

        if response.signal == AppFlowSignal.RERUN:
            print('*'*45)
            print('Sinal de RERUN recebido. Iniciando processo de rerun...')
            self._invalidate_all_rerun()

        if response.signal != AppFlowSignal.GO:
            self._invalidate_downstream(section_interna)

        


        return response