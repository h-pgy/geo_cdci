import streamlit as st
from frontend.components import (
    Header, 
    AddressSearchForm, LogradouroSearchProcessor, AddressSelectionHandler
    )
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO, LogradouroMatchDTO
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
    results_dto: LogradouroSearchResultsDTO | None = search_processor(logradouro_input)
    space_logradouro = st.empty()
    if not state.logradouro_already_selected:
        selection_handler = AddressSelectionHandler(state, space_logradouro)
        selection_handler(results_dto)
    logradouro_selecionado = state.logradouro_selecionado
    with space_logradouro:
        with st.container(border=True):
            if logradouro_selecionado is not None:
                state.logradouro_already_selected = True
                st.success(f"Logradouro selecionado: {logradouro_selecionado}", icon=":material/house:")
            else:
                st.warning("Nenhum logradouro selecionado. Por favor, revise os resultados da busca.", icon=":material/error:")
    
    # Próximo passo da lógica (ex: buscar dados no SQL)

    

if __name__ =="__main__":

    main()