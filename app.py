import streamlit as st
from frontend.state import AppState
from frontend.controller import AppFlowController, AppSection
from frontend.components.header import Header
from frontend.components.address_input import AddressForm


def main():

    state = AppState()

    controller = AppFlowController(state)

    # espaços para organizar o layout
    header_space = st.empty()
    form_space = st.empty()

    header = AppSection(
        container=header_space,
        component=Header(),
    )

    address_form = AppSection(
        container=form_space,
        component=AddressForm(),
    )

    address_form.add_dependency(header)

    controller.register(header)
    controller.register(address_form)

    controller.trigger_section(header)        
    controller.trigger_section(address_form)

    

if __name__=="__main__":
    main()