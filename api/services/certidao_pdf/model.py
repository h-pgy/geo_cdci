from pydantic import BaseModel, Field
from typing import List

class CertidaoModel(BaseModel):
    header: str = Field(..., description="Texto principal do cabeçalho")
    path_header_logo: str = Field(..., description="Caminho local para o arquivo de imagem do logo")
    path_watermark: str = Field(..., description="Caminho local para o arquivo de imagem da marca d'água")
    space_between_sections: int = Field(6, description="Espaçamento entre seções em mm")
    footer: str = Field(..., description="Texto do rodapé em formato markdown")