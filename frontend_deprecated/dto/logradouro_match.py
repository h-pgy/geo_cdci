from pydantic import BaseModel, Field, model_validator
from typing import List, Optional

class LogradouroMatchDTO(BaseModel):
    logradouro: str
    score: float

class LogradouroSearchResultsDTO(BaseModel):
    input_original: str
    input_usuario_processado: str
    matches: List[LogradouroMatchDTO]
    match_100: bool = False

    @model_validator(mode='after')
    def process_and_validate_matches(self) -> 'LogradouroSearchResultsDTO':
        """
        Ordena a lista de matches por score e valida a consistência da flag match_100.
        """
        # 1. Ordenação garantida: do maior score para o menor

        if not self.matches:
            raise ValueError("A lista de matches não pode ser vazia.")

        self.matches.sort(key=lambda x: x.score, reverse=True)

        # 2. Verificação de consistência da flag match_100
        scores = [m.score for m in self.matches]
        tem_score_100 = any(score >= 100.0 for score in scores)

        if self.match_100 and not tem_score_100:
            raise ValueError(
                "A flag match_100 não pode ser True se nenhum match possui score 100."
            )
        
        if not self.match_100 and tem_score_100:
            raise ValueError(
                "A flag match_100 deve ser True quando existe um match com score 100."
            )

        return self

    @property
    def melhor_match(self) -> Optional[LogradouroMatchDTO]:
        """
        Como a lista é ordenada na validação, o melhor match é sempre o primeiro.
        """
        return self.matches[0] if self.matches else None