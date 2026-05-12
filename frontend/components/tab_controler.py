from frontend.state import AppState
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget
from frontend.dto.tab import Tab
from collections import OrderedDict

class TabControler:

    state_tab_key = "__active_tab"
    slider_tab_key = "__slider_tab"

    tabs = OrderedDict({
        "Busca de endereço" : {
            "warning_message": "Preencha o formulário de busca para iniciar a pesquisa de logradouro.",
            "state_key": "initialized"
        }, 
        "Localização do logradouro" : {
            "warning_message": "Preencha o formulário de busca para iniciar a pesquisa de logradouro.",
            "state_key": "address_search_form_filled"
        },
        "Identificação do Imóvel" : 
        {
            "warning_message": "Selecione um logradouro para prosseguir com a identificação do imóvel.",
            "state_key": "logradouro_already_selected"
        },
        "Geração da certidão" : {
            "warning_message": "Selecione um endereço completo para prosseguir com a geração da certidão.",
            "state_key": "address_matched"
        }
    })

    def __init__(self, state:AppState)->None:

        self.state = state
        self.tab_names = list(self.tabs.keys())
        self.reversed_tab_names = list(reversed(self.tab_names))
        self.tab_objs = self.create_tab_objects()
        self.init_tab = self.define_active_tab()
        

    def create_tab_objects(self)->dict[str, Tab]:
        tab_objects = {}
        for name, info in self.tabs.items():

            tab_objects[name] = Tab(
                name=name,
                warning_message=info["warning_message"],
                state_key=info["state_key"]
            )
        return tab_objects
    
    def get_tab_object(self, tab_name:str)->Tab:

        if tab_name not in self.tab_objs:
            raise ValueError(f"Tab '{tab_name}' não encontrada. Opções: {self.tab_names}")
        return self.tab_objs[tab_name]
    
    def is_tab_active_by_state(self, tab_obj:Tab)->bool:
        state_value = getattr(self.state, tab_obj.state_key)
        return bool(state_value)

    @property
    def frontend_active_tab(self)->str:

        curr_tab_name = st.session_state.get(self.state_tab_key, self.tab_names[0])
        if curr_tab_name not in self.tab_names:
            raise ValueError(f"Tab '{curr_tab_name}' não é uma opção válida. Opções: {self.tab_names}")
        return curr_tab_name
    
    def is_tab_active_by_frontend(self, tab_obj:Tab)->bool:
        return tab_obj.name == self.frontend_active_tab

    def define_active_tab(self) -> str:

        for i, tab_name in enumerate(self.reversed_tab_names):
            tab_obj = self.get_tab_object(tab_name)
            if self.is_tab_active_by_state(tab_obj):
                return tab_name
        return self.tab_names[0]  # default para a primeira tab se nenhuma condição for satisfeita

    @property
    def active_tab(self) -> str:
        return self.define_active_tab()
    
    @property
    def active_tab_obj(self)->Tab:
        active_tab_name = self.active_tab
        return self.get_tab_object(active_tab_name)

    def tab_slider(self)->str:

        current_tab =  st.select_slider(
            "Progresso",
            options=self.tab_names,
            value=self.active_tab,
            key=self.slider_tab_key,
        )

        return current_tab
    
    def render_tabs(self) ->list[StreamlitWidget]:

        tabs = st.tabs(self.tab_names,
                       key=self.state_tab_key,
                       default=self.init_tab,
                       on_change="rerun"
                       )
        
        for i, tab_name in enumerate(self.tab_names):
            tab_widget = tabs[i]
            tab_obj = self.get_tab_object(tab_name)
            tab_obj.tab_widget = tab_widget
            

    def tab_warning(self, tab_obj:Tab)->None:

        if not self.is_tab_active_by_state(tab_obj) and self.is_tab_active_by_frontend(tab_obj):
           st.warning(tab_obj.warning_message)
        return None
        
    def render(self)->dict[str, Tab]:

        tabs = self.render_tabs()

        return self.tab_objs

    def __call__(self)->dict[str, Tab]:
        return self.render()
        