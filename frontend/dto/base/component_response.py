from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, model_validator

from .app_flow import AppFlowSignal
from .component_error import ComponentError
from .component_message import ComponentMessage

T = TypeVar('T', bound=BaseModel)

class BaseComponentResponse(BaseModel, Generic[T]):

    signal: AppFlowSignal
    data: Optional[T] = None
    message: Optional[ComponentMessage] = None
    error: Optional[ComponentError] = None
    component_name: Optional[str]=None #vai ser preenchido automaticamente na call da base class

    def _validate_error_state(self):
        """Valida restrições para o sinal de erro crítico."""
        if self.signal == AppFlowSignal.ERROR:
            if self.error is None:
                raise ValueError("Sinal ERROR exige um objeto ComponentError.")
            if self.data is not None:
                raise ValueError("Sinal ERROR não deve conter dados (data).")
            if self.message is not None:
                raise ValueError("Sinal ERROR não deve conter ComponentMessage (use o campo error).")

    def _validate_go_state(self):
        """Valida restrições para o sinal de continuidade."""
        if self.signal == AppFlowSignal.GO:
            if self.data is None:
                raise ValueError("Sinal GO exige o preenchimento de dados (data) para o downstream.")
            if self.error is not None:
                raise ValueError("Sinal GO é incompatível com estado de erro crítico.")

    def _validate_no_go_state(self):
        """Valida restrições para o sinal de estase/aguardo."""
        if self.signal == AppFlowSignal.NO_GO:
            if self.error is not None:
                raise ValueError("Sinal NO_GO não aceita erro crítico. Para erros impeditivos, use Signal.ERROR.")
