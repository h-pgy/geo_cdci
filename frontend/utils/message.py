from frontend.dto.base import ComponentMessage, MessageType
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
import streamlit as st
import time
from frontend.config import settings


def _spinner_aux(message:str):

    with st.spinner(message):
        time.sleep(settings.SPINNER_MSG_DURATION_SECONDS)

class MessageFactory:

    type_mapping = {
        "error": MessageType.ERROR,
        "warning": MessageType.WARNING,
        "success": MessageType.SUCCESS,
        "info": MessageType.INFO,
        "processing" : MessageType.PROCESSING
    }

    type_widget_mapping = {
        MessageType.ERROR: st.error,
        MessageType.WARNING: st.warning,
        MessageType.SUCCESS: st.success,
        MessageType.INFO: st.info,
        MessageType.PROCESSING: _spinner_aux
    }


    def __init__(self)->None:
        #tem um controle de estado próprio
       
        self.component_msg_mapper: dict[str, int] = {} #mapeamento para controlar mensagens por componente, se necessário
        self.initialize_message_state()

    def initialize_message_state(self):

        if 'messages' not in st.session_state:
            st.session_state['messages']: dict[str, ComponentMessage] = {}
        if "runned_messages" not in st.session_state:
            st.session_state['runned_messages']: set[str] = set()

        self.messages = st.session_state['messages']
        self.runned_messages = st.session_state['runned_messages']

    def create_message(self, key:str, body:str, title:str|None=None, status:MessageType=MessageType.INFO, duration:int|None=None) -> ComponentMessage:
        message = ComponentMessage(
            title=title,
            body=body,
            status=status,
            duration=duration,
            key=key
        )
        self.messages[key] = message
        return message
    
    def get_message(self, key:str) -> ComponentMessage|None:
        return self.messages.get(key, None)
    
    def create_message_if_not_exists(self, key:str, body:str, title:str|None=None, status:MessageType=MessageType.INFO, duration:int|None=None) -> ComponentMessage:
        
        message = self.get_message(key)
        if message:
            return message
        else:
            return self.create_message(key, body, title, status, duration)
        
    def create_message_from_type(self, key:str, body:str, title:str|None=None, type_str:str="info", duration:int|None=None) -> ComponentMessage:
        
        if type_str not in self.type_mapping:
            raise ValueError(f"Tipo de mensagem desconhecido: {type_str}. Tipos válidos são: {list(self.type_mapping.keys())}")

        status = self.type_mapping.get(type_str.lower(), MessageType.INFO)
        return self.create_message(key, body, title, status, duration)
    
    def build_message_key(self, component:"UIComponent") -> str:
        
        nome = component.name
        if nome not in self.component_msg_mapper:
            self.component_msg_mapper[nome] = 1
        else:
            self.component_msg_mapper[nome] +=1

        qtd = self.component_msg_mapper[nome]
        
        return f"{nome}_msg_{qtd}"
    
    def clear_message(self, key:str) -> None:
        if key in self.messages:
            del self.messages[key]
        self.runned_messages.discard(key)

    def clear_all_messages(self) -> None:
        self.messages.clear()
        self.runned_messages.clear()

    def get_message_type_widget(self, status:MessageType)->StreamlitWidget:

        widget_func = self.type_widget_mapping.get(status, None)
        if widget_func is None:
            raise NotImplementedError(f"Tipo de mensagem desconhecido: {status}")
        return widget_func
    

    def render_message(self, message: ComponentMessage, container: StreamlitWidget, force_render: bool=False) -> None:

        if not isinstance(message, ComponentMessage):
            raise TypeError(f"Esperado ComponentMessage, mas recebeu {type(message).__name__}")

        if message.key in self.runned_messages and not force_render:
            #mensagem já foi renderizada, então não renderiza novamente
            print(f"Mensagem com chave '{message.key}' já renderizada. Use force_render=True para forçar a renderização.")
            return

        self.runned_messages.add(message.key)

        message_space = container.empty()
        widget_func = self.get_message_type_widget(message.status)

        if message.title:
            txt = f"**{message.title}**\n\n{message.body}"
        else:
            txt = message.body

        with message_space:
            widget_func(txt)       

        duration = message.duration
        if duration:
            time.sleep(duration)
            message_space.empty()  # Limpa a mensagem após o tempo definido

    def __call__(self, parent_component:"UIComponent", body:str, title:str|None=None, type_str:str="info", duration:int|None=None) -> ComponentMessage:

        key = self.build_message_key(parent_component)
        return self.create_message_from_type(key, body, title, type_str, duration)

    
#extraindo as funcoes para ter compatibilidade

def error_message(parent_component:"UIComponent", body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    
    factory = MessageFactory()
    return factory(parent_component, body, title, "error", duration)

def warning_message(parent_component:"UIComponent", body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    factory = MessageFactory()
    return factory(parent_component, body, title, "warning", duration)

def success_message(parent_component:"UIComponent", body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    factory = MessageFactory()
    return factory(parent_component, body, title, "success", duration)    

def info_message(parent_component:"UIComponent", body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    factory = MessageFactory()
    return factory(parent_component, body, title, "info", duration)

def processing_message(parent_component:"UIComponent", body:str, title:str|None=None, duration:int|None=None) -> ComponentMessage:
    factory = MessageFactory()
    return factory(parent_component, body, title, "processing", duration)
    

def render_message(message: ComponentMessage, container: StreamlitWidget) -> None:

    factory = MessageFactory()
    factory.render_message(message, container)
