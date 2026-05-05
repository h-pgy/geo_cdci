import streamlit as st
from frontend.components import Header


def main():
    '''Renderiza o app'''

    render_header = Header()
    render_header()



if __name__ =="__main__":

    main()