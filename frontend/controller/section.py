from pydantic import BaseModel, Field, ConfigDict, PrivateAttr
from typing import List, Optional, Any, Set
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

from frontend.components.base import UIComponent

class AppSection(BaseModel):
    """
    Representa uma unidade lógica e visual da aplicação.
    Gerencia dependências com validações rigorosas de circularidade e tipos.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    component: UIComponent
    container: StreamlitWidget
    initial_data: Optional[BaseModel] = None
    
    _depends_on_sections: List["AppSection"] = PrivateAttr(default_factory=list)

    @property
    def name(self) -> str:
        return self.component.name

    @property
    def depends_on_names(self) -> Set[str]:
        return {s.name for s in self._depends_on_sections}

    def add_dependency(self, other_section: "AppSection"):
        """
        Adiciona uma dependência executando todas as checagens de segurança.
        """
        self._check_circularity(other_section)
        self._check_duplicate(other_section)
        self._check_type_compatibility(other_section)

        self._depends_on_sections.append(other_section)

    def _check_circularity(self, other: "AppSection"):
        """
        Impede que a seção dependa de si mesma ou que uma dependência mútua ocorra.
        """
        if other.name == self.name:
            raise ValueError(f"Circularidade detectada: A seção '{self.name}' não pode depender de si mesma.")
        
        # Checa se a 'other' já depende desta (self) em qualquer nível do grafo dela
        if self.name in other.depends_on_names:
            raise ValueError(
                f"Circularidade detectada: A seção '{other.name}' já depende de '{self.name}'. "
                "Isso criaria um ciclo infinito no fluxo."
            )

    def _check_duplicate(self, other: "AppSection"):
        """
        Garante que a mesma dependência não seja adicionada duas vezes.
        """
        if other.name in self.depends_on_names:
            raise ValueError(f"A seção '{other.name}' já é uma dependência de '{self.name}'.")

    def _check_type_compatibility(self, other: "AppSection"):
        """
        Valida se o DTO de saída do Alter é compatível com o DTO de entrada do Ego.
        """
        alter_output = other.component.output_type
        ego_input = self.component.input_type

        if not issubclass(alter_output, ego_input):
            raise TypeError(
                f"Contrato Inválido: '{other.name}' produz {alter_output.__name__}, "
                f"mas '{self.name}' requer {ego_input.__name__}."
            )

    def remove_dependency(self, section_name: str):
        self._depends_on_sections = [
            s for s in self._depends_on_sections if s.name != section_name
        ]

    def get_dependencies(self) -> List["AppSection"]:
        return self._depends_on_sections