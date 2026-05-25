from streamlit.delta_generator import DeltaGenerator as StreamlitContainer
from frontend.utils.button import ButtonGate
import pandas as pd
import streamlit as st

class DataEditorPropertyChoice:
     
    display_columns = {
         "Logradouro" : "nm_logradouro_completo", 
         "Numero" : "cd_numero_porta", 
         "Complemento" : "tx_complemento_endereco"
         }
    
    def __init__(self, submit_button_key:str)->None:

        self.submit_button_callback = ButtonGate(submit_button_key)

    def clean_dataframe(self, df:pd.DataFrame) -> pd.DataFrame:
        
        colunas = self.display_columns.values()
        df_cleaned = df[colunas].copy()
        df_cleaned.rename(columns={v:k for k,v in self.display_columns.items()}, inplace=True)
        
        return df_cleaned
    
    def get_submit_button_text(self)->str:
         
         if self.submit_button_callback.is_pressed:
            return "Atualizar Imóvel Selecionado"
         else:             
            return "Selecionar Imóvel"
         
    def get_submit_button_icon(self)->str:

        if self.submit_button_callback.is_pressed:
            return ":material/refresh:"
        else:
            return ":material/check_box:"
        
    def render_submit_button(self, container:StreamlitContainer) -> bool:

        button_text = self.get_submit_button_text()
        button_icon = self.get_submit_button_icon()
        submit_button_clicked = container.button(button_text, icon=button_icon, on_click=self.submit_button_callback.press)
        return submit_button_clicked
    
    def render_editable_df(self, df:pd.DataFrame, container:StreamlitContainer) -> pd.DataFrame:
         
        editable_df =container.data_editor(df, column_config={
                    "Escolha": st.column_config.CheckboxColumn("Escolha este endereço")
                }, 
                #esconde o indice do df
                hide_index=True, 
                #desabilita a edição das colunas de exibição
                disabled=list(self.display_columns.values()),
                #permite apenas o delete de linhas, não a adição 
                num_rows='delete'
                )
        
        return editable_df
    
    def validate_selection(self, df:pd.DataFrame, result_container:StreamlitContainer) -> bool:

        if df["Escolha"].sum() == 0:
            result_container.warning("Por favor, selecione um endereço para prosseguir.")
            return False
        elif df["Escolha"].sum() > 1:
            result_container.warning("Por favor, selecione apenas um endereço para prosseguir.")
            return False
        
        return True
    
    def render(self, df:pd.DataFrame, container:StreamlitContainer, title:str, header_message:str) -> int:

        df_cleaned = self.clean_dataframe(df)
        df_cleaned['Escolha'] = False
        widget_container = container.container(border=True)
        widget_container.markdown(f"#### {title}")
        widget_container.write(header_message)

        editable_df = self.render_editable_df(df_cleaned, widget_container)

        submit_button_clicked = self.render_submit_button(widget_container)
        if not submit_button_clicked and not self.submit_button_callback.is_pressed:
            #bloqueia aqui porque precisa selecionar algo
            container.info("Por favor, selecione um endereço e clique no botão para confirmar sua escolha.")
            st.stop()

        result_container = container.container()
        if not self.validate_selection(editable_df, result_container):
            #também para caso tenha selecionado mais de um, ou nenhum
            st.stop()

        index_selecionado = editable_df[editable_df["Escolha"]].index[0]

        return index_selecionado

    def __call__(self, df:pd.DataFrame, container:StreamlitContainer, title:str, header_message:str) -> int:
        return self.render(df, container, title, header_message)