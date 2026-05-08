import streamlit as st
from frontend.components import Header, AddressSearchForm, AddressResolverComponent
from frontend.dto import AddressSearchInputDTO, LogradouroSearchResultsDTO, LogradouroMatchDTO
from frontend.services.adress import get_address_matcher
from frontend.services.data_loaders import get_df_enderecos_lotes


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
    address_resolver = AddressResolverComponent(matcher_service)
    resolved_address = address_resolver(address_data)
    st.info('Endereço resolvido: ' + (resolved_address if resolved_address else "Nenhum endereço selecionado."))


if __name__ =="__main__":

    main()