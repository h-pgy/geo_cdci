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

    def find_matches(self, user_input: str, limit: int = MAX_ADDRESS_SEARCH_RESULTS, threshold: float = ADDRESS_SEARCH_FUZZY_SCORE_THRESHOLD) -> List[Dict]:
        """Usa o processador interno para limpar o input antes do match."""
        query_processed = self.preprocess_input.run(user_input)
        
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