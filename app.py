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
from frontend.components.certidao.certidao_pdf import CertidaoPDFComponent
from frontend.dto.base import AppFlowSignal
from api.services.fuzzy_iptu_address_search import AddressMatcher


def main(debug: bool = True):

    # Inicialização do estado e controlador

    state = AppState()

    controller = AppFlowController(state)

    # Inicialização dos serviços

    matcher = AddressMatcher()

    # main container
    main_container = st.container(autoscroll=True)

    # ---------- HEADER SECTION -----------------------------
    header_space = main_container.container()

    header = AppSection(
        container=header_space,
        component=Header(),
    )
    controller.register(header)
    controller.trigger_section(header)    


    # ---------- ADDRESS INPUT SECTION -----------------------------


    form_space = main_container.container()
    
    address_form = AppSection(
        container=form_space,
        component=AddressForm(),
    )

    address_form.add_dependency(header)
    controller.register(address_form)
    address_input = controller.trigger_section(address_form)
    if address_input.signal == AppFlowSignal.NO_GO or address_input.signal ==  AppFlowSignal.ERROR:
        #nao dá pra seguir no app se não tiver o input de endereço, então a gente para aqui
        st.stop()

    # --------- LOGRADOURO MATCHING SECTION -----------------------------


    logradouro_match_space = main_container.container()

    #essa selçao é mais complexa, tem mais subseções e tem branching
    logradouro_search = AppSection(
        container=logradouro_match_space,
        component=LogradouroSearchProcessor(matcher=matcher),
    )

    perfect_match_logradouro = AppSection(
        container=logradouro_match_space,
        component=PerfectMatchLogradouro(matcher=matcher),
    )

    logradouro_selection = AppSection(
        container=logradouro_match_space,
        component=LogradouroSelection(matcher=matcher),
    )

    logradouro_search.add_dependency(address_form)
    logradouro_selection.add_dependency(logradouro_search)
    perfect_match_logradouro.add_dependency(logradouro_search)

    controller.register(logradouro_search)
    controller.register(perfect_match_logradouro)
    controller.register(logradouro_selection)

    logradouro_results = controller.trigger_section(logradouro_search)

    #resolve qual o tipo de selecao de logradouro e estrutura as dependencias da aplicacao de acordo
    if logradouro_results.signal == AppFlowSignal.GO and logradouro_results.data.match_100:
        selected_logradouro = controller.trigger_section(perfect_match_logradouro)
        if selected_logradouro.signal == AppFlowSignal.GO:
            controller.bypass_section(logradouro_selection, data=selected_logradouro.data)
        property_match_depencency = perfect_match_logradouro
    elif logradouro_results.signal == AppFlowSignal.GO and not logradouro_results.data.match_100:
        selected_logradouro = controller.trigger_section(logradouro_selection)
        if selected_logradouro.signal == AppFlowSignal.GO:
            controller.bypass_section(perfect_match_logradouro, data=selected_logradouro.data)
        property_match_depencency = logradouro_selection
    else:
        st.error("Ocorreu um erro ao buscar os logradouros correspondentes ao endereço inserido. Por favor, tente novamente ou entre em contato com o suporte.")
        st.stop()

    # --------- PROPERTY MATCHING SECTION -----------------------------

    property_match_space = main_container.container()

        
    perfect_property_match = AppSection(
        container=property_match_space,
        component=PerfectPropertyMatch(matcher=matcher),
    )

    near_neighboors_property_match = AppSection(
        container=property_match_space,
        component=NearNeighboorsPropertyMatch(matcher=matcher),
    )

    
    perfect_property_match.add_dependency(address_form)
    perfect_property_match.add_dependency(property_match_depencency)
    near_neighboors_property_match.add_dependency(address_form)
    near_neighboors_property_match.add_dependency(property_match_depencency)

    
    controller.register(perfect_property_match)
    controller.register(near_neighboors_property_match)

    if selected_logradouro.signal == AppFlowSignal.GO:
        codlog_selecionado = selected_logradouro.data.codlog
        numero_porta_selecionado = int(address_input.data.numero)
        full_match = matcher.is_full_match(codlog_selecionado, numero_porta_selecionado)

        if full_match:
            selected_imovel = controller.trigger_section(perfect_property_match)
            if selected_logradouro.signal == AppFlowSignal.GO:
                controller.bypass_section(near_neighboors_property_match, data=selected_imovel.data)
                certidao_dependency = perfect_property_match
        else:
            selected_imovel = controller.trigger_section(near_neighboors_property_match)
            if selected_logradouro.signal == AppFlowSignal.GO:
                controller.bypass_section(perfect_property_match, data=selected_imovel.data)
                certidao_dependency = near_neighboors_property_match
    else:
        st.stop()

    # --------- CERTIDAO PDF GENERATION SECTION -----------------------------

    if selected_imovel.signal == AppFlowSignal.GO:
        certidao_pdf_space = main_container.container()
        certidao_pdf_component = AppSection(
            container=certidao_pdf_space,
            component=CertidaoPDFComponent()
        )

        certidao_pdf_component.add_dependency(certidao_dependency)
        controller.register(certidao_pdf_component)
        controller.trigger_section(certidao_pdf_component)
    else:
        st.stop()

    # ---------- DEBUG SECTION -----------------------------
    if debug:
        debug_container = st.container(border=True)
        with debug_container:
            st.markdown('## Seção de Debug - Apenas em modo de desenvolvimento')
            st.button('Rerun')
            st.write(st.session_state)   
            st.stop()

if __name__=="__main__":
    main()