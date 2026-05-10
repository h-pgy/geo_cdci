import streamlit as st
from frontend.components import (
    Header, 
    AddressSearchForm, LogradouroSearchProcessor, PerfectAddressMatchComponent, ManualAddressSelectionComponent
    )
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO, LogradouroMatchDTO
from frontend.services.adress import get_address_matcher
from frontend.services.data_loaders import get_df_enderecos_lotes

from frontend.state import AppState

def main():
    '''Renderiza o app'''

    state = AppState()

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
    if state.address_search_form_filled:
        state.address_search_input = address_data
    else:
        st.warning("Preencha o formulário de busca para iniciar a pesquisa de logradouro.")
        st.stop()


    #fuzzy match search for logradouro
    search_processor = LogradouroSearchProcessor(matcher_service)
    logradouro_input = state.address_search_input.logradouro
    results_dto: LogradouroSearchResultsDTO | None = search_processor(logradouro_input)

    #escolha do logradouro com base na busca
    if results_dto is not None:
        state.logradouro_search_results = results_dto
        if results_dto.match_100:
            match_ui = PerfectAddressMatchComponent(results_dto, state)
            logradouro_selecionado = match_ui.render()
            state.logradouro_selecionado = logradouro_selecionado
        else:
            selection_ui = ManualAddressSelectionComponent(results_dto, state)
            logradouro_selecionado = selection_ui.render()
            state.logradouro_selecionado = logradouro_selecionado
               
    st.info(f"Logradouro selecionado: **{state.logradouro_selecionado}**")
    # Próximo passo da lógica (ex: buscar dados no SQL)


if __name__ =="__main__":

    main()