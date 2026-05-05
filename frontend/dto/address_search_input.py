from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
import re

class AddressSearchInputDTO(BaseModel):
    # Permite que o objeto seja instanciado sem dados inicialmente
    logradouro: Optional[str] = None
    numero: Optional[int] = None
    submitted: bool = False

    # Configuração para permitir nomes de atributos flexíveis se necessário
    model_config = ConfigDict(str_strip_whitespace=True)

    @model_validator(mode='after')
    def check_submission_integrity(self) -> 'AddressSearchInputDTO':
        """
        Valida as regras de negócio apenas se o formulário foi enviado.
        """
        if not self.submitted:
            return self

        # Validação do Logradouro
        if not self.logradouro or len(self.logradouro.strip()) < 2:
            raise ValueError("O logradouro deve conter ao menos 2 caracteres.")
        
        if not re.match(r'^[a-zA-Z0-9À-ÿ\s\-]+$', self.logradouro):
            raise ValueError("O logradouro contém caracteres inválidos.")

        # Validação do Número
        if self.numero is None or self.numero < 0:
            raise ValueError("O número do imóvel deve ser informado (zero ou superior).")

        return self