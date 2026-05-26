from pydantic import BaseModel, ConfigDict, Field
from frontend.dto.logradouro_fuzzy_search import LogradouroChoiceDTO

class PropertyChoiceDTO(BaseModel):

    numero: int = Field(..., gt=0, description="Número do endereço escolhido")
    logradouro_escolhido: LogradouroChoiceDTO
    cd_identificador_lote: int = Field(..., gt=1000000, description="Identificador do lote do imóvel escolhido")
    #remove os whitespaces automaticamente
    model_config = ConfigDict(str_strip_whitespace=True)

    @property
    def codlog(self) -> str:
        return self.logradouro_escolhido.codlog
    
    @property
    def logradouro(self) -> str:
        return self.logradouro_escolhido.logradouro

