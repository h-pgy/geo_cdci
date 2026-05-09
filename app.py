import streamlit as st
from frontend.components import (
    Header, 
    AddressSearchForm, LogradouroSearchProcessor, PerfectAddressMatchComponent, ManualAddressSelectionComponent
    )
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO, LogradouroMatchDTO
from frontend.services.adress import get_address_matcher
from frontend.services.data_loaders import get_df_enderecos_lotes
from frontend.config import settings

LOGRADOURO_SELECIONADO = settings.SELECTED_LOGRADOURO_KEY

def main():
    '''Renderiza o app'''

    #header
    render_header = Header()
    render_header()

    #--------------------------------------------
    # address fuzzy search functionality

    #inicializa o matcher service
    df_endereco_lotes = get_df_enderecos_lotes()
    matcher_service = get_address_matcher(df_endereco_lotes)

    #search input form
    address_form = AddressSearchForm()
    address_data: AddressSearchInputDTO = address_form()

    #fuzzy search results
    logradouro_selecionado = st.session_state.get(LOGRADOURO_SELECIONADO, '')

    if address_form.form_submitted:
        search_processor = LogradouroSearchProcessor(matcher_service)
        results_dto: LogradouroSearchResultsDTO | None = search_processor(address_data.logradouro)
        if results_dto is not None:
            if results_dto.match_100:
                match_ui = PerfectAddressMatchComponent(results_dto)
                logradouro_selecionado = match_ui.render()
            else:
                selection_ui = ManualAddressSelectionComponent(results_dto)
                logradouro_selecionado = selection_ui.render()
               
    st.info(f"Logradouro selecionado: **{logradouro_selecionado}**")
    # Próximo passo da lógica (ex: buscar dados no SQL)


if __name__ =="__main__":

    main()