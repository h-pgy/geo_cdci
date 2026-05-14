import streamlit as st
from pydantic import BaseModel, Field
from frontend.dto.base import BaseComponentResponse
from typing import Dict, Any, Optional

class AppState:
    """
    Singleton que encapsula o st.session_state.
    Garante persistência das respostas tipadas entre reruns.
    """
    _instance_key = "app_state_instance"
    responses: Dict[str, BaseComponentResponse[Any]]

    def __new__(cls):
        if cls._instance_key not in st.session_state:
            instance = super(AppState, cls).__new__(cls)
            # Dicionário mapeando Nome do Componente -> BaseComponentResponse
            instance.responses = {}
            st.session_state[cls._instance_key] = instance
        
        return st.session_state[cls._instance_key]

    def store_response(self, name: str, response: BaseComponentResponse[Any]):
        """
        Armazena a resposta com enforcement de tipo.
        """
        if not isinstance(response, BaseComponentResponse):
            raise TypeError(
                f"AppState só aceita BaseComponentResponse. Recebido: {type(response)}"
            )
        self.responses[name] = response

    def get_response(self, name: str) -> Optional[BaseComponentResponse[Any]]:
        return self.responses.get(name)

    def delete_response(self, name: str):
        if name in self.responses:
            del self.responses[name]

    def clear_all(self):
        self.responses.clear()