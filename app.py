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
        name="Header",
        container=header_space,
        component=Header(),
    )

    address_form = AppSection(
        name="AddressForm",
        container=form_space,
        component=AddressForm(),
    )

    address_form.add_dependency(header)

    controller.register(header)
    controller.register(address_form)

    controller.trigger_section("Header")        
    controller.trigger_section("AddressForm")

    

if __name__=="__main__":
    main()