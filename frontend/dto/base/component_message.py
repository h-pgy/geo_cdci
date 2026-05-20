from pydantic import BaseModel
from typing import Optional
from enum import Enum, auto

class MessageType(Enum):
    """Define o tom semântico da mensagem para a UI."""
    SUCCESS = auto()
    WARNING = auto()
    INFO = auto()
    ERROR = auto() # Útil para mensagens de erro que não interrompem o fluxo (stasis)
    PROCESSING = auto() # Para indicar que uma ação está em andamento, sem ser um erro ou sucesso definitivo

class ComponentMessage(BaseModel):
    """Encapsula feedbacks positivos ou instruções de progresso."""
    title: Optional[str] = None
    body: str
    status: MessageType
    duration: Optional[int] = None  # Duração em segundos para exibir a mensagem, se aplicável
    key: str # Chave única para controle de estado e atualização da mensagem na UI