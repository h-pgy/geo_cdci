import streamlit as st
from frontend.state import AppState
from frontend.controller import AppFlowController, AppSection
from frontend.components.header import Header
from frontend.components.address_input import AddressForm
from frontend.components.fuzzy_search_logradouro.fuzzy_search import LogradouroSearchProcessor
from frontend.components.fuzzy_search_logradouro.perfect_match import PerfectMatchLogradouro

from frontend.dto.base import AppFlowSignal
from api.services.fuzzy_iptu_address_search import AddressMatcher


def main():

    # Inicialização do estado e controlador

    state = AppState()

    controller = AppFlowController(state)

    # Inicialização dos serviços

    matcher = AddressMatcher()

    # main container
    main_container = st.container(autoscroll=True)

    # espaços para organizar o layout
    #nao pode fazer tudo space porque se nao o autscroll fica zuado
    #soh usar space se quiser substituir o que tem dentro
    header_space = main_container.container()
    form_space = main_container.container()
    results_match_space = main_container.container()

    header = AppSection(
        container=header_space,
        component=Header(),
    )

    address_form = AppSection(
        container=form_space,
        component=AddressForm(),
    )

    logradouro_search = AppSection(
        container=results_match_space,
        component=LogradouroSearchProcessor(matcher=matcher),
    )

    perfect_match_logradouro = AppSection(
        container=results_match_space,
        component=PerfectMatchLogradouro(matcher=matcher),
    )

    address_form.add_dependency(header)
    logradouro_search.add_dependency(address_form)
    perfect_match_logradouro.add_dependency(logradouro_search)

    controller.register(header)
    controller.register(address_form)
    controller.register(logradouro_search)
    controller.register(perfect_match_logradouro)

    controller.trigger_section(header)        
    controller.trigger_section(address_form)
    logradouro_results = controller.trigger_section(logradouro_search) 
    if logradouro_results.signal == AppFlowSignal.GO and logradouro_results.data.match_100:
        controller.trigger_section(perfect_match_logradouro)

    st.write(state)   

if __name__=="__main__":
    main()