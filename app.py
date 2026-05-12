import streamlit as st
from frontend.components import (
    Header, 
    AddressSearchForm, LogradouroSearchProcessor, AddressSelectionHandler, PropertyMatchHandler
    )
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO
from frontend.services.adress import get_address_matcher
from frontend.services.data_loaders import get_df_enderecos_lotes
import time
from frontend.utils.scroll_to import AnchorManager

from frontend.state import AppState

        

def main():
    '''Renderiza o app'''

    state = AppState()
    state.write_namespace('address')
    anchor_manager = AnchorManager(verbose=True) 

    #header
    render_header = Header()
    render_header()

    anchor_manager.scroll_to_last_existing_anchor()
    
    #--------------------------------------------
    # address fuzzy search functionality

    #inicializa o matcher service
    df_endereco_lotes = get_df_enderecos_lotes()
    matcher_service = get_address_matcher(df_endereco_lotes)

    #search input form
    address_form = AddressSearchForm(state)
    address_data: AddressSearchInputDTO = address_form()
    if not state.address_search_form_filled:
        st.warning("Preencha o formulário de busca para iniciar a pesquisa de logradouro.")
        st.stop()

    anchor_manager.set_anchor('address_search')
    anchor_manager.scroll_to_last_existing_anchor()

    #fuzzy match search for logradouro

    search_processor = LogradouroSearchProcessor(matcher_service)
    logradouro_input = state.address_search_input.logradouro
    numero_input = state.address_search_input.numero
    results_dto: LogradouroSearchResultsDTO | None = search_processor(logradouro_input)
    space_logradouro = st.empty()
    if not state.logradouro_already_selected:
        selection_handler = AddressSelectionHandler(state, space_logradouro)
        selection_handler(results_dto)
    logradouro_selecionado = state.logradouro_selecionado
    with space_logradouro:
        with st.container(border=True):
            if logradouro_selecionado is not None:
                st.success(f"Logradouro selecionado: {logradouro_selecionado}", icon=":material/house:")
            else:
                st.warning("Nenhum logradouro selecionado. Por favor, revise os resultados da busca.", icon=":material/error:")
                st.stop()
    
    anchor_manager.set_anchor('logradouro_search_results')
    anchor_manager.scroll_to_last_existing_anchor()
        
    # property full address match

    space_property_match = st.empty()
    anchor_manager.set_anchor('property_match')
    anchor_manager.scroll_to_last_existing_anchor()

    space_property_match_results = st.empty()
    property_match_handler = PropertyMatchHandler(state, matcher_service, space_property_match)
    id_selected_property = property_match_handler(logradouro_selecionado, numero_input)

    with space_property_match_results:
        with st.container(border=True):
            if state.address_matched:
                st.success(f"Endereço completo selecionado com ID: {id_selected_property}", icon=":material/house:")
            elif state.address_not_listed:
                st.warning("Endereço marcado como 'Não listado'. Por favor, siga as instruções para buscar seu endereço no mapa.", icon=":material/map:")
            else:
                st.error("Não foi possível encontrar um endereço correspondente ou próximo. Por favor, revise os dados de entrada e tente novamente.", icon=":material/error:")
    
    anchor_manager.set_anchor('property_match_results')
    anchor_manager.scroll_to_last_existing_anchor()
    

    

if __name__ =="__main__":

    main()