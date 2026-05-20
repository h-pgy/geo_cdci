from frontend.config import settings
from frontend.state import AppState
from api.services.fuzzy_iptu_address_search.address_match import AddressMatcher
import pandas as pd
import streamlit as st
import time
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

class PropertyMatchHandler:
    def __init__(self, state:AppState, address_matcher:AddressMatcher, search_space:StreamlitWidget, results_space:StreamlitWidget) -> None:
        self.state = state
        self.address_matcher = address_matcher
        self.search_space = search_space
        self.results_space = results_space

    def _check_busca_endereco_filled(self, edited_df:pd.DataFrame, button_buscar_clicado:bool)->bool:

        if button_buscar_clicado:

            if edited_df["Escolha"].sum() == 0:
                st.error("Nenhum endereço selecionado. Por favor, selecione um endereço para prosseguir.", icon=":material/error:")
                return False
            elif edited_df["Escolha"].sum() > 1:
                st.error("Múltiplos endereços selecionados. Por favor, selecione apenas um endereço para prosseguir.", icon=":material/error:")
                return False
            else:
                return True
        else:
            st.warning("Por favor, selecione um endereço e clique no botão para prosseguir.", icon=":material/warning:")
            return False

    def _check_endereco_not_listed(self, button_nao_encontrado_clicado:bool)->bool:

        if button_nao_encontrado_clicado:
            st.info('Será necessário realizar a busca pelo mapa para encontrar seu endereço. Por favor, siga as instruções para buscar seu endereço no mapa.', icon=":material/map:")
            self.state.address_matched = False
            self.state.delete_key("address_matched_id", namespace="address")
            self.state.address_not_listed = True
            return True
        return False
    
    def __get_submit_button_text_and_icon(self)->tuple[str, str]:

        if self.state.address_matched:
            return "Buscar novo endereço", ":material/search:"
        elif self.state.address_not_listed:
            return "Buscar novo endereço", ":material/search:"
        else:
            return "Selecionar endereço", ":material/check_box:"
        
    def clean_up_state(self):

        self.state.delete_key("address_matched", namespace="address")
        self.state.delete_key("address_matched_id", namespace="address")
        self.state.delete_key("address_not_listed", namespace="address")
        
    def data_editor_property_choice(self, df_matches:pd.DataFrame)->int|None:
        
        with self.form_space:
            with st.container(border=True):
                st.write('Foram encontrados os seguintes endereços próximos ao logradouro e número fornecidos. Por favor, selecione o que corresponde ao seu endereço.')
                df_display = df_matches[["nm_logradouro_completo", "cd_numero_porta", "tx_complemento_endereco"]].copy()
                df_display.rename(columns={"nm_logradouro_completo" : "Logradouro", 
                                        "cd_numero_porta" : "Número",
                                        "tx_complemento_endereco" : "Complemento"}, inplace=True)
                df_display['Escolha'] = False

                edited_df = data_editor = st.data_editor(df_display, column_config={
                    "Escolha": st.column_config.CheckboxColumn("Escolha este endereço")
                }, hide_index=True, disabled=["Logradouro", "Número", "Complemento"], num_rows='delete')
            
                cols = st.columns([1 ,2, 1])
                with cols[0]:
                    button_text, button_icon = self.__get_submit_button_text_and_icon()
                    button_buscar_clicado = st.button(button_text, icon=button_icon)
                with cols[2]:
                    with st.popover("Nenhum desses é meu endereço", type='tertiary', icon=':material/wrong_location:'):
                        button_nao_encontrado_clicado = st.button("Estou certo de que nenhum desses é meu endereço", icon=":material/wrong_location:", type='tertiary')

                with st.container():
                        st.write('Resultados da busca por lista de endereços próximos')
                        with st.container():
                            check_not_found = self._check_endereco_not_listed(button_nao_encontrado_clicado)
                            if check_not_found:
                                return None

                            check_submitted_data = self._check_busca_endereco_filled(edited_df, button_buscar_clicado)
                            if not check_submitted_data:
                                return None
                            if check_submitted_data:
                                self.clean_up_state()
                                st.success("Endereço selecionado com sucesso!", icon=":material/house:")

        index_selecionado = edited_df[edited_df["Escolha"]].index[0]

        return index_selecionado

    def many_matches(self, df_matches:pd.DataFrame, qtd_ocorrencias:int)->int:

        st.warning(f"Foram encontrados {qtd_ocorrencias} endereços que correspondem ao logradouro e número fornecidos. Selecione o que corresponde ao seu endereço.", icon=':material/other_houses:')
        
        index_selecionado = self.data_editor_property_choice(df_matches)
        match_selecionado: pd.Series = df_matches.loc[index_selecionado]
        st.success(f"Endereço selecionado: {match_selecionado['nm_logradouro_completo']} {match_selecionado['cd_numero_porta']}", icon=":material/house:")
        
        return match_selecionado["cd_identificador"]
          
    def exact_match(self, df_matches:pd.DataFrame)->int:

        assert len(df_matches)==1, "A função exact_match deve ser chamada apenas quando houver apenas um match exato"
        with self.form_space:
            with st.spinner("Buscando match exato..."):
                time.sleep(1)  # Simula um tempo de processamento para melhorar a experiência do usuário
            match = df_matches.iloc[0]
            st.write(df_matches[["nm_logradouro_completo", "cd_numero_porta", "tx_complemento_endereco"]])
        with self.exact_match_space:
            with st.container(border=True):
                st.write('Resultados da busca por endereço exato')
            with st.container():
                st.success(f"Endereço encontrado com match exato! ({match['nm_logradouro_completo']} {match['cd_numero_porta']})", icon=":material/celebration:")
    
    
        return match["cd_identificador"]
    
    def full_address_match(self, logradouro:str, numero:int)->int|None:

        numero_str = str(numero)
        full_matches = self.address_matcher.get_full_address_info(logradouro, numero_str)
        if full_matches is not None and not full_matches.empty:
            qtd_ocorrencias = len(full_matches)

            if qtd_ocorrencias == 1:
                return self.exact_match(full_matches)
            else:
                return self.many_matches(full_matches, qtd_ocorrencias)
        else:
            with self.exact_match_space:
                with st.container(border=True):
                    st.write('Resultados da busca por endereço exato')
                    with st.container():
                        st.info(f"Nenhum endereço encontrado para o logradouro {logradouro} com o número {numero}. Vamos fazer a busca para os endereços mais próximos", icon=":material/warning:")
                return None
        
    def nearest_neighbor_match(self, logradouro:str, numero:str)->int|None:

        try:
            numero = int(numero)
        except ValueError:
            with self.results_space:
                st.error(f"Número de porta {numero} não é um valor numérico. Não é possível realizar a busca por vizinhos mais próximos.", icon=":material/error:")
            return None
        
        df_vizinhos_proximos = self.address_matcher.get_nearest_neighbor_addresses(logradouro, numero)
        if df_vizinhos_proximos is None or df_vizinhos_proximos.empty:
            with self.results_space:
                st.error(f"Nenhum endereço encontrado para o logradouro fornecido ({logradouro}) com o número ({numero}). Por favor, revise o logradouro e tente novamente.", icon=":material/error:")
            return None
        
        index_selecionado = self.data_editor_property_choice(df_vizinhos_proximos)

        if index_selecionado is None:
            return None

        match_selecionado: pd.Series = df_vizinhos_proximos.loc[index_selecionado]
        with self.results_space:
            st.success(f"Endereço mais próximo selecionado: {match_selecionado['nm_logradouro_completo']}, {match_selecionado['cd_numero_porta']}", icon=":material/house:")
        return match_selecionado["cd_identificador"]
    
    def handle_property_match_pairs(self, logradouro:str, numero:str)->int|None:

        id_match = self.full_address_match(logradouro, numero)
        if id_match is not None:
            return id_match
        
        # se não encontrou match exato, tenta encontrar o mais próximo
        id_match_vizinho_proximo = self.nearest_neighbor_match(logradouro, numero)
        return id_match_vizinho_proximo
    
    def run_search(self, logradouro:str, numero:str)->int|None:
        """Executa o processo completo de busca do endereço e atualização do estado do app."""
        id_match = self.handle_property_match_pairs(logradouro, numero)
        return id_match
    
    def save_results_to_state(self, id_match:int|None)->None:
        """Salva os resultados da busca no estado do app."""
        if id_match is not None:
            self.state.address_matched = True
            self.state.address_matched_id = id_match
        else:
            self.state.address_matched = False
            self.state.delete_key("address_matched_id", namespace="address")

    def results_tag(self)->int|None:

        with self.results_space:
            with st.container(border=True):
                st.write('##### Resultados da busca por endereço completo')
                with st.container():
                    if self.state.address_matched and self.state.address_matched_id is not None:
                        st.success(f"Endereço completo encontrado com ID: {self.state.address_matched_id}", icon=":material/house:")
                        return self.state.address_matched_id
                    elif self.state.address_not_listed:
                        st.warning("Endereço marcado como 'Não listado'. Por favor, selecione um novo endereço ou siga as instruções para buscar seu endereço no mapa.", icon=":material/map:")
                    else:
                        st.error("Não foi possível encontrar um endereço correspondente ou próximo. Por favor, revise os dados de entrada e tente novamente.", icon=":material/error:")

    def __call__(self, logradouro:str, numero:str)->int|None:
        """Dado um logradouro e número, busca o endereço mais próximo na base de dados e atualiza o estado do app."""
        with self.search_space:
            with st.container(border=True):
                st.markdown("#### Buscando correspondência para o endereço completo... :material/house:")
                with st.container(border=True):
                    self.exact_match_space = st.empty()
                    self.form_space = st.empty()
                    id_match = self.run_search(logradouro, numero)
            self.save_results_to_state(id_match)
        
            return self.results_tag()
                


