from pydantic import BaseModel, Field
from typing import List

class CertidaoModel(BaseModel):
    cabecalho: str = Field(..., description="Texto principal do cabeçalho")
    path_logo_cabecalho: str = Field(..., description="Caminho local para o arquivo de imagem do logo")
    space_between_sections: int = Field(6, description="Espaçamento entre seções em mm")
    footer: str = Field(..., description="Texto do rodapé em formato markdown")