from frontend.dto.base import ComponentMessage, MessageType
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

def error_message(body:str, title:str|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.ERROR
    )

def warning_message(body:str, title:str|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.WARNING
    )

def success_message(body:str, title:str|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
    status=MessageType.SUCCESS
)

def info_message(body:str, title:str|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.INFO
    )

def render_message(message: ComponentMessage, container: StreamlitWidget):

    if not isinstance(message, ComponentMessage):
        raise TypeError(f"Esperado ComponentMessage, mas recebeu {type(message).__name__}")

    if message.status == MessageType.ERROR:
        container.error(message.body)
    elif message.status == MessageType.WARNING:
        container.warning(message.body)
    elif message.status == MessageType.SUCCESS:
        container.success(message.body)
    elif message.status == MessageType.INFO:
        container.info(message.body)
    else:
        raise NotImplementedError(f"Tipo de mensagem desconhecido: {message.status}")
