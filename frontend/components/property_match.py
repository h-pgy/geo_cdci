from frontend.config import settings
from frontend.state import AppState
from api.services.fuzzy_iptu_address_search.address_match import AddressMatcher
import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator as StreamlitWidget

class PropertyMatchHandler:
    def __init__(self, state:AppState, address_matcher:AddressMatcher) -> None:
        self.state = state
        self.address_matcher = address_matcher

            
    def _check_busca_endereco_filled(self, edited_df:pd.DataFrame, button_buscar_clicado:bool)->bool:

        if button_buscar_clicado:

            if edited_df["Escolha"].sum() == 0:
                st.warning("Nenhum endereço selecionado. Por favor, selecione um endereço para prosseguir.", icon=":material/error:")
                return False
            elif edited_df["Escolha"].sum() > 1:
                st.warning("Múltiplos endereços selecionados. Por favor, selecione apenas um endereço para prosseguir.", icon=":material/error:")
                return False
            else:
                return True
        else:
            st.warning("Por favor, selecione um endereço e clique no botão para prosseguir.", icon=":material/warning:")
            return False


    def data_editor_property_choice(self, df_matches:pd.DataFrame)->int:

        df_display = df_matches[["nm_logradouro_completo", "cd_numero_porta"]].copy()
        df_display.rename(columns={"nm_logradouro_completo" : "Logradouro", 
                                   "cd_numero_porta" : "Número"}, inplace=True)
        df_display['Escolha'] = False
        edited_df = data_editor = st.data_editor(df_display, column_config={
            "Escolha": st.column_config.CheckboxColumn("Escolha este endereço")
        }, hide_index=True, disabled=["Logradouro", "Número"], num_rows='delete')
       
        button_buscar_clicado = st.button("Selecionar endereço", icon=":material/check_box:")

        check_submitted_data = self._check_busca_endereco_filled(edited_df, button_buscar_clicado)
        if not check_submitted_data:
            st.stop()

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
        match = df_matches.iloc[0]
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
            st.warning("Nenhum endereço encontrado. Vamos fazer a busca para os endereços mais próximos", icon=":material/warning:")
            return None
    
    def nearest_neighbor_match(self, logradouro:str, numero:str)->int|None:

        try:
            numero = int(numero)
        except ValueError:
            st.error("Número de porta não é um valor numérico. Não é possível realizar a busca por vizinhos mais próximos.", icon=":material/error:")
            return None
        
        df_vizinhos_proximos = self.address_matcher.get_nearest_neighbor_addresses(logradouro, numero)
        if df_vizinhos_proximos is None or df_vizinhos_proximos.empty:
            st.error("Nenhum endereço encontrado para o logradouro fornecido. Por favor, revise o logradouro e tente novamente.", icon=":material/error:")
            return None
        
        index_selecionado = self.data_editor_property_choice(df_vizinhos_proximos)

        match_selecionado: pd.Series = df_vizinhos_proximos.loc[index_selecionado]
        st.success(f"Endereço selecionado: {match_selecionado['nm_logradouro_completo']} {match_selecionado['cd_numero_porta']}", icon=":material/house:")
        return match_selecionado["cd_identificador"]
    
    def handle_property_match_pairs(self, logradouro:str, numero:str)->int|None:

        id_match = self.full_address_match(logradouro, numero)
        if id_match is not None:
            return id_match
        
        # se não encontrou match exato, tenta encontrar o mais próximo
        id_match_vizinho_proximo = self.nearest_neighbor_match(logradouro, numero)
        return id_match_vizinho_proximo


    def __call__(self, logradouro:str, numero:str)->int|None:
        """Dado um logradouro e número, busca o endereço mais próximo na base de dados e atualiza o estado do app."""
        id_match = self.handle_property_match_pairs(logradouro, numero)
        if id_match is not None:
            self.state.address_matched = True
            self.state.address_matched_id = id_match
            return id_match
        else:
            self.state.address_matched = False
            self.state.delete_key("address_matched_id", namespace="address")
            return None


