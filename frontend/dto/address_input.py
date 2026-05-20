from pydantic import BaseModel, ConfigDict, field_validator, Field
import re

class AddressInputDTO(BaseModel):

    logradouro: str = Field(..., min_length=2, description="Logradouro do endereço")
    numero: int = Field(..., ge=0, description="Número do imóvel (zero ou superior)")

    #remove os whitespaces automaticamente
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('logradouro')
    def validate_logradouro(cls, value: str) -> str:

        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]+$', value):
            raise ValueError("O logradouro contém caracteres inválidos.")
        return value.strip()
