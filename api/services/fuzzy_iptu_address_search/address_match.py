from rapidfuzz import process, utils as fuzzy_utils
from typing import List, Dict
import pandas as pd
from .process_input import AddressStringProcessor
from api.scripts.data_load.download_enderecos_lotes import download_enderecos_lotes
from api.config import settings

MAX_ADDRESS_SEARCH_RESULTS=settings.MAX_ADDRESS_SEARCH_RESULTS
ADDRESS_SEARCH_FUZZY_SCORE_THRESHOLD=settings.ADDRESS_SEARCH_FUZZY_SCORE_THRESHOLD

class AddressMatcher:
    def __init__(self, address_df: pd.DataFrame|None=None):

        self.df = address_df if address_df is not None else download_enderecos_lotes()
        self.preprocess_input = AddressStringProcessor()
        # Pré-processamos a lista de busca uma única vez no init
        # (Assumindo que nm_logradouro_completo já está limpo na base)
        self.unique_logradouros = self.df["nm_logradouro_completo"].unique().tolist()

    def find_matches(self, user_input: str, remove_logradouro_type:bool=False, limit: int = MAX_ADDRESS_SEARCH_RESULTS, 
                     threshold: float = ADDRESS_SEARCH_FUZZY_SCORE_THRESHOLD) -> List[Dict]:
        """Usa o processador interno para limpar o input antes do match."""
        query_processed = self.preprocess_input(user_input, remove_logradouro_type=remove_logradouro_type)
        
        # O process.extract do RapidFuzz
        results = process.extract(
            query_processed, 
            self.unique_logradouros, 
            limit=limit,
            score_cutoff=threshold,
        )
        
        return [
            {
                "logradouro": name, 
                "score": round(score, 2),
                "input_processado": query_processed
            } 
            for name, score, _ in results
        ]
    
    def is_match_100(self, matches:List[Dict])->bool:
        """Verifica se há um match com score 100."""
        return any(match["score"] >= 100.0 for match in matches)
    
    def find_matches_pipeline(self, user_input:str)->list[dict]:
        """Executa o pipeline completo de pré-processamento e busca."""
        
        first_pass = self.find_matches(user_input, remove_logradouro_type=False)
        if self.is_match_100(first_pass):
            return first_pass
        # Se não houver match 100, tenta novamente removendo o tipo de logradouro
        # isso precisa ser feito porque se remover o tipo de logradouro nao tem como dar match 100%
        second_pass = self.find_matches(user_input, remove_logradouro_type=True)
        return second_pass
    
    def get_full_logradouro_info(self, logradouro: str) -> pd.DataFrame:
        """Dado um logradouro, retorna todas as linhas da base que correspondem a ele."""
        df = self.df[self.df["nm_logradouro_completo"] == logradouro]
        if df.empty:
            raise ValueError(f'Logradouro {logradouro} não encontrado na base de dados.')
        return df
    
    def get_full_address_info(self, logradouro:str, numero_porta:str)->pd.DataFrame|None:

        """Dado um logradouro e número de porta, retorna as linhas da base que correspondem a ambos."""
        df = self.df[
            (self.df["nm_logradouro_completo"] == logradouro) & 
            (self.df["cd_numero_porta"] == numero_porta)
        ]

        if df.empty:
            return None
        return df