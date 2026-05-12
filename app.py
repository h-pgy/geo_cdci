import streamlit as st
from frontend.components import (
    Header, 
    TabControler,
    AddressSearchForm, LogradouroSearchProcessor, AddressSelectionHandler, PropertyMatchHandler
    )
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO
from frontend.services.adress import get_address_matcher
from frontend.services.data_loaders import get_df_enderecos_lotes
import time

from frontend.state import AppState

        

def main():
    '''Renderiza o app'''

    state = AppState()
    state.write_namespace('address')
    state.initialized = True

    #header
    render_header = Header()
    render_header()

    tab_controler = TabControler(state)
    tab_objs = tab_controler()
        
    #--------------------------------------------
    # address fuzzy search functionality

    #inicializa o matcher service
    df_endereco_lotes = get_df_enderecos_lotes()
    matcher_service = get_address_matcher(df_endereco_lotes)

    #search input form

    active_tab = tab_controler.active_tab_obj
    st.write(f"Tab ativa: {active_tab.name}")
    state.write_namespace("address")

    tab_address_search = tab_objs["Busca de endereço"]
    with tab_address_search.tab_widget:
        tab_controler.tab_warning(tab_address_search)
    
        if tab_controler.is_tab_active_by_state(tab_address_search):
            address_form = AddressSearchForm(state)
            address_data: AddressSearchInputDTO = address_form()
            if state.address_search_form_filled:
                st.success("Formulário preenchido. Você pode prosseguir para a próxima etapa.", icon=":material/check_circle:")
                tab_controler.define_active_tab()
                

    #fuzzy match search for logradouro
    tab_logradouro_search = tab_objs["Localização do logradouro"]
    with tab_logradouro_search.tab_widget:
        tab_controler.tab_warning(tab_logradouro_search)

        if tab_controler.is_tab_active_by_state(tab_logradouro_search):
            #separa os espaços
            space_logradour_perfect_match = st.empty()
            space_logradouro_fuzzy_match = st.empty()
            space_results_logradouro = st.empty()

            #faz a busca fuzzy    
            search_processor = LogradouroSearchProcessor(matcher_service)
            logradouro_input = state.address_search_input.logradouro
            numero_input = state.address_search_input.numero
            results_dto: LogradouroSearchResultsDTO | None = search_processor(logradouro_input)
            if not results_dto:
                with space_results_logradouro:
                    st.error("Ocorreu um erro durante a busca. Por favor, revise os dados de entrada e tente novamente.", icon=":material/error:")
            #faz a escolha do logradouro
            selection_handler = AddressSelectionHandler(state, space_logradour_perfect_match, space_logradouro_fuzzy_match, space_results_logradouro)
            selection_handler(results_dto)
        
        
    # property full address match
    tab_property_match = tab_objs["Identificação do Imóvel"]
    with tab_property_match.tab_widget:
        tab_controler.tab_warning(tab_property_match)

        if tab_controler.is_tab_active_by_state(tab_property_match):

            #espaços
            space_property_match = st.empty()
            space_property_match_results = st.empty()   

            numero_input = state.address_search_input.numero
            logradouro_selecionado = state.logradouro_selecionado

            if logradouro_selecionado is not None:
                property_match_handler = PropertyMatchHandler(state, matcher_service, space_property_match, space_property_match_results)
                id_selected_property = property_match_handler(logradouro_selecionado, numero_input)

        
        

if __name__ =="__main__":

    main()