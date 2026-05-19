import streamlit as st

class ButtonGate:

    def __init__(self, button_key:str):
        self.button_key = button_key
        if self.button_key not in st.session_state:
            st.session_state[self.button_key] = False
    
    @property
    def is_pressed(self)->bool:
        return st.session_state.get(self.button_key, False)
    
    def press(self):
        st.session_state[self.button_key] = True

    def reset(self):
        st.session_state[self.button_key] = False
    
