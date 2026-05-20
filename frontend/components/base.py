from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Any, Type
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from pydantic import BaseModel

from frontend.dto.base import (
    ComponentError, 
    BaseComponentResponse, 
    AppFlowSignal
)

from frontend.utils.message import render_message
from frontend.state import AppState
from frontend.config import settings
import time

ERROR_MSG_DURATION_SECONDS = settings.ERROR_MSG_DURATION_SECONDS

T = TypeVar('T', bound=BaseModel)

class UIComponent(ABC, Generic[T]):
    # Sobrescrever esses atributos nas classes filhas quando for o caso
    input_type: Optional[Type[BaseModel]] = None
    output_type: Optional[Type[BaseModel]] = None
    user_error_msg: str = "Ocorreu uma falha técnica ao carregar este componente."
    name: str = "BaseComponent"
    previous_response: Optional[BaseComponentResponse[Any]] = None

    @abstractmethod
    def _render(
        self, 
        container: StreamlitWidget, 
        input_dto: Optional[BaseModel]
    ) -> BaseComponentResponse[T]:
        pass

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._validate_class_name()

    @classmethod
    def _validate_class_name(cls):
        # 1. Verifica se o nome foi alterado
        if cls.name == "BaseComponent":
            raise ValueError(
                f"A classe '{cls.__name__}' não definiu um nome único. "
                "Por favor, sobrescreva o atributo 'name'."
            )

    def _validate_input(self, input_dto: Optional[BaseModel]) -> None:
        if self.input_type is None:
            if input_dto is not None:
                raise TypeError(
                    f"{self.__class__.__name__} não espera entrada, "
                    f"mas recebeu {type(input_dto).__name__}"
                )
            return

        if not isinstance(input_dto, self.input_type):
            received = type(input_dto).__name__ if input_dto else "None"
            raise TypeError(
                f"{self.__class__.__name__} espera {self.input_type.__name__}, "
                f"mas recebeu {received}"
            )

    def _validate_output(self, response: BaseComponentResponse[T]) -> None:
        if response.signal != AppFlowSignal.GO:
            return

        if self.output_type is None:
            if response.data is not None:
                raise TypeError(
                    f"{self.__class__.__name__} não deveria retornar dados, "
                    f"mas retornou {type(response.data).__name__}"
                )
            return

        if not isinstance(response.data, self.output_type):
            received = type(response.data).__name__ if response.data else "None"
            raise TypeError(
                f"{self.__class__.__name__} prometeu retornar {self.output_type.__name__}, "
                f"mas entregou {received}"
            )

    def _create_internal_error_message(self, e: Exception) -> str:
        class_name = self.__class__.__name__
        error_type = type(e).__name__
        return f"[COMPONENT_FAILURE] Class: {class_name} | Type: {error_type} | Details: {str(e)}"

    def _log_internal_error(self, e: Exception) -> str:
        message = self._create_internal_error_message(e)
        print(message)
        return message

    def _render_user_error(self, message: str, container: StreamlitWidget) -> None:
        container.error(message)

    def _handle_exception(
        self,
        container: StreamlitWidget,  
        e: Exception
    ) -> BaseComponentResponse[T]:
        internal_msg = self._log_internal_error(e)
        self._render_user_error(self.user_error_msg, container)

        return BaseComponentResponse(
            signal=AppFlowSignal.ERROR,
            error=ComponentError(
                internal_message=internal_msg,
                user_message=self.user_error_msg
            ),
            component_name=self.name
        )
    
    def _render_message(self, response: BaseComponentResponse[Any], container: StreamlitWidget) -> None:
        if response.message:
            render_message(response.message, container)

    def _inject_previous_response(self, state: AppState) -> None:

        previous_response = state.get_response(self.name)
        if previous_response:
            print('Injetando resposta anterior no componente', self.name)
            self._validate_output(previous_response)
            self.previous_response = previous_response

    def flash_message(self, container:StreamlitWidget, message:str, type:str="info"):
        """
        Exibe uma mensagem de erro de validação dentro do formulário.
        """
        msg_espace = container.empty()
        if type == "error":
            msg_espace.error(message, icon=":material/error:")
        elif type == "success":
            msg_espace.success(message, icon=":material/check:")
        elif type == "warning":
            msg_espace.warning(message, icon=":material/warning:")
        else:
            msg_espace.info(message)

        #apaga a msg
        time.sleep(ERROR_MSG_DURATION_SECONDS)
        msg_espace.empty()

    @st.fragment
    def _fragment_render(self, target: StreamlitWidget, input_dto: Optional[BaseModel]) -> BaseComponentResponse[T]:

        internal_container = target.container()
        try:
            self._validate_input(input_dto)
            response = self._render(internal_container, input_dto)
            response.component_name = self.name
            self._validate_output(response)
            self._render_message(response, internal_container)

            return response

        except Exception as e:
            return self._handle_exception(internal_container, e)
        
    def _rerun_render(self, target: StreamlitWidget, input_dto: Optional[BaseModel]) -> BaseComponentResponse[T]:

        try:
            self._validate_input(input_dto)
            response = self._render(target, input_dto)
            response.component_name = self.name
            self._validate_output(response)
            self._render_message(response, target)

            return response

        except Exception as e:
            return self._handle_exception(target, e)

    def __call__(
        self, 
        container: StreamlitWidget, 
        state: AppState,
        input_dto: Optional[BaseModel] = None,
        fragment=False
    ) -> BaseComponentResponse[T]:
        
        #ai posso usar a resposta anterior dentro do componente como quiser
        self._inject_previous_response(state)
        with container:
            try:
                if fragment:
                    response = self._fragment_render(container, input_dto)
                else:
                    response = self._rerun_render(container, input_dto)
                return response
            except Exception as e:
                return self._handle_exception(container, e)