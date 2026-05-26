from datetime import date
from typing import Optional

class ConversorDataExtenso:

    _meses = [
            "", "janeiro", "fevereiro", "março", "abril", "maio", "junho", 
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]

    _unidades = [
            "zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", 
            "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"
        ]
    
    _dezenas = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]

    
    def converter_dia(self, numero:int)->str:

        if numero>31 or numero<1:
            raise ValueError("Número do dia deve ser entre 1 e 31.")
        
        if numero == 1:
            return "primeiro"
        else:
            if numero < 20:
                return self._unidades[numero]
            else:
                dezena = numero // 10
                unidade = numero % 10
                if unidade == 0:
                    return self._dezenas[dezena]
                return f"{self._dezenas[dezena]} e {self._unidades[unidade]}"
            
    def converter_mes(self, numero:int)->str:

        if numero>12 or numero<1:
            raise ValueError("Número do mês deve ser entre 1 e 12.")
        
        return self._meses[numero]


    def obter_data_por_extenso(self, data_referencia:date) -> str:
        dia = data_referencia.day
        mes = data_referencia.month
        ano = data_referencia.year
        
        dia_extenso = self.converter_dia(dia)
        mes_extenso = self.converter_mes(mes)

        return f"{dia_extenso} de {mes_extenso} de {ano}"
    
    def __call__(self, data_referencia:Optional[date]=None) -> str:
        if data_referencia is None:
            data_referencia = date.today()
        return self.obter_data_por_extenso(data_referencia)