import streamlit as st
from typing import Any, List, Optional

class AbstractAppState:
    def _ensure_namespace(self, namespace: str):
        if namespace not in st.session_state:
            st.session_state[namespace] = {}

    def set_value(self, key: str, value: Any, namespace: str = "default"):
        self._ensure_namespace(namespace)
        st.session_state[namespace][key] = value

    def get_value(self, key: str, namespace: str = "default", default: Any = None) -> Any:
        if namespace not in st.session_state:
            return default
        return st.session_state[namespace].get(key, default)

    def delete_key(self, key: str, namespace: str = "default"):
        if namespace in st.session_state and key in st.session_state[namespace]:
            del st.session_state[namespace][key]

    def list_keys(self, namespace: str = "default") -> List[str]:
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