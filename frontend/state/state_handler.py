import streamlit as st
from typing import Any, List, Optional

class AbstractAppState:
    def _ensure_namespace(self, namespace: str|None):
        if namespace is not None and namespace not in st.session_state:
            st.session_state[namespace] = {}

    def set_value(self, key: str, value: Any, namespace: Optional[str] = None):
        self._ensure_namespace(namespace)
        if namespace is None:
            st.session_state[key] = value
        else:
            st.session_state[namespace][key] = value

    def get_value(self, key: str, namespace: Optional[str] = None, default: Any = None) -> Any:

        if namespace is not None and namespace not in st.session_state:
            return default
        if namespace is None:
            return st.session_state.get(key, default)
        return st.session_state[namespace].get(key, default)

    def delete_key(self, key: str, namespace: Optional[str] = None):
        if namespace is None:
            if key in st.session_state:
                del st.session_state[key]
        else:
            if namespace in st.session_state and key in st.session_state[namespace]:
                del st.session_state[namespace][key]

    def list_keys(self, namespace: Optional[str] = None) -> List[str]:
        if namespace is None:
            return [str(key) for key in st.session_state.keys()]
        if namespace in st.session_state:
            return list(st.session_state[namespace].keys())
        return []

    def clear_namespace(self, namespace: str):
        if namespace in st.session_state:
            del st.session_state[namespace]

    def all(self, namespace: str) -> bool:
        """Retorna True se todas as chaves do namespace avaliarem como True."""
        if namespace not in st.session_state or not st.session_state[namespace]:
            return False
        return all(st.session_state[namespace].values())

    def any(self, namespace: str) -> bool:
        """Retorna True se ao menos uma chave do namespace avaliar como True."""
        if namespace not in st.session_state:
            return False
        return any(st.session_state[namespace].values())
    
    def namespace_dici(self, namespace:str)->dict:
        if namespace not in st.session_state:
            return {}
        else:
            dici = {
                name : value for
                name, value in st.session_state[namespace].items()
            }
            return dici
        
    def write_namespace(self, namespace:str):
        
        namespace_dict = self.namespace_dici(namespace)
        if namespace_dict:
            st.write(f"Estado atual do namespace '{namespace}':")
            st.json(namespace_dict)
        else:
            st.write(f"Namespace '{namespace}' está vazio.")
        