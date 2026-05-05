import streamlit as st
from frontend.components import Header, AddressSearchForm


def main():
    '''Renderiza o app'''

    render_header = Header()
    render_header()
    address_form = AddressSearchForm()
    address_data = address_form()
    st.write(address_data)



if __name__ =="__main__":

    main()