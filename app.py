import streamlit as st
from frontend.state import AppState
from frontend.controller import AppFlowController, AppSection
from frontend.components.header import Header
from frontend.components.address_input import AddressForm
from frontend.components.fuzzy_search_logradouro.fuzzy_search import LogradouroSearchProcessor
from frontend.components.fuzzy_search_logradouro.perfect_match import PerfectMatchLogradouro
from frontend.components.fuzzy_search_logradouro.logradouro_selection import LogradouroSelection
from frontend.components.property_selection.perfect_match import PerfectPropertyMatch
from frontend.components.property_selection.near_neighboors import NearNeighboorsPropertyMatch
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
    property_match_space = main_container.container()

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

    logradouro_selection = AppSection(
        container=results_match_space,
        component=LogradouroSelection(matcher=matcher),
    )

    perfect_property_match = AppSection(
        container=property_match_space,
        component=PerfectPropertyMatch(matcher=matcher),
    )

    near_neighboors_property_match = AppSection(
        container=property_match_space,
        component=NearNeighboorsPropertyMatch(matcher=matcher),
    )

    address_form.add_dependency(header)
    logradouro_search.add_dependency(address_form)
    logradouro_selection.add_dependency(logradouro_search)
    perfect_match_logradouro.add_dependency(logradouro_search)
    perfect_property_match.add_dependency(address_form)
    near_neighboors_property_match.add_dependency(address_form)

    
    controller.register(header)
    controller.register(address_form)
    controller.register(logradouro_search)
    controller.register(perfect_match_logradouro)
    controller.register(logradouro_selection)
    controller.register(perfect_property_match)
    controller.register(near_neighboors_property_match)

    controller.trigger_section(header)        
    address_input = controller.trigger_section(address_form)
    if address_input.signal == AppFlowSignal.NO_GO or address_input.signal ==  AppFlowSignal.ERROR:
        #nao dá pra seguir no app se não tiver o input de endereço, então a gente para aqui
        st.stop()
    logradouro_results = controller.trigger_section(logradouro_search) 


    #resolve qual o tipo de selecao de logradouro e estrutura as dependencias da aplicacao de acordo
    if logradouro_results.signal == AppFlowSignal.GO and logradouro_results.data.match_100:
        selected_logradouro = controller.trigger_section(perfect_match_logradouro)
        if selected_logradouro.signal == AppFlowSignal.GO:
            controller.bypass_section(logradouro_selection, data=selected_logradouro.data)
        near_neighboors_property_match.add_dependency(perfect_match_logradouro)
        perfect_property_match.add_dependency(perfect_match_logradouro)
    elif logradouro_results.signal == AppFlowSignal.GO and not logradouro_results.data.match_100:
        selected_logradouro = controller.trigger_section(logradouro_selection)
        if selected_logradouro.signal == AppFlowSignal.GO:
            controller.bypass_section(perfect_match_logradouro, data=selected_logradouro.data)
        near_neighboors_property_match.add_dependency(logradouro_selection)
        perfect_property_match.add_dependency(logradouro_selection)
    else:
        st.error("Ocorreu um erro ao buscar os logradouros correspondentes ao endereço inserido. Por favor, tente novamente ou entre em contato com o suporte.")
        st.stop()


    if selected_logradouro.signal == AppFlowSignal.GO:
        codlog_selecionado = selected_logradouro.data.codlog
        numero_porta_selecionado = int(address_input.data.numero)
        full_match = matcher.is_full_match(codlog_selecionado, numero_porta_selecionado)

        if full_match:
            selected_imovel = controller.trigger_section(perfect_property_match)
            if selected_logradouro.signal == AppFlowSignal.GO:
                controller.bypass_section(near_neighboors_property_match, data=selected_imovel.data)
        else:
            selected_imovel = controller.trigger_section(near_neighboors_property_match)
            if selected_logradouro.signal == AppFlowSignal.GO:
                controller.bypass_section(perfect_property_match, data=selected_imovel.data)


    st.button('Olá')
    st.write(st.session_state)   
    st.stop()

if __name__=="__main__":
    main()