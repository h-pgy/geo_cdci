import streamlit as st
from frontend.components import (
    Header, 
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
    #header
    render_header = Header()
    render_header()

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
        
    # property full address match

    if not state.address_matched:
        property_match_handler = PropertyMatchHandler(state, matcher_service)
        id_selected_property = property_match_handler(logradouro_selecionado, numero_input)

    st.success(f"Endereço completo selecionado com ID: {id_selected_property}", icon=":material/house_with_garden:")

    

    

if __name__ =="__main__":

    main()