from frontend.dto.base import ComponentMessage, MessageType
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
import time

def error_message(body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.ERROR,
        duration=duration
    )

def warning_message(body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.WARNING,
        duration=duration
    )

def success_message(body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.SUCCESS,
        duration=duration
)

def info_message(body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    return ComponentMessage(
        title=title,
        body=body,
        status=MessageType.INFO,
        duration=duration
    )

def render_message(message: ComponentMessage, container: StreamlitWidget) -> None:

    if not isinstance(message, ComponentMessage):
        raise TypeError(f"Esperado ComponentMessage, mas recebeu {type(message).__name__}")

    space = container.empty()
    if message.status == MessageType.ERROR:
        space.error(message.body)
    elif message.status == MessageType.WARNING:
        space.warning(message.body)
    elif message.status == MessageType.SUCCESS:
        space.success(message.body)
    elif message.status == MessageType.INFO:
        space.info(message.body)
    else:
        raise NotImplementedError(f"Tipo de mensagem desconhecido: {message.status}")
    
    duration = message.duration
    if duration:
        time.sleep(duration)
        space.empty()  # Limpa a mensagem após o tempo definido
