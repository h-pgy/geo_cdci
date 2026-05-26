from pydantic import BaseModel, field_validator, Field
from frontend.dto.property_match import PropertyChoiceDTO
from typing import Optional
import os


class DadosImovelCertidaoDTO(BaseModel):

    numero: str 
    logradouro: str 
    complemento: Optional[str]=None 
    codlog: str 
    cd_setor: str
    cd_quadra: str
    cd_lote: str
    cd_digito_sql: str

    @property
    def setor_quadra_lote(self) -> str:
        return f"{self.cd_setor}.{self.cd_quadra}.{self.cd_lote}-{self.cd_digito_sql}"

class CertidaoDTO(BaseModel):

    certidao_path: str
    input_data: PropertyChoiceDTO
    dados_imovel: DadosImovelCertidaoDTO

    @property
    def cd_identificador_lote(self) -> int:
        return self.input_data.cd_identificador_lote

    @field_validator('certidao_path')
    def validate_certidao_path(cls, value):
        if not os.path.isfile(value):
            raise ValueError(f'O caminho {value} não é um arquivo válido.')
        return value
    

    
