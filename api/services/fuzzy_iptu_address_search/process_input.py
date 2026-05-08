import unicodedata
import re

class AddressStringProcessor:

    tipos_logradouros = {
            'R',
            'AV',
            'AL',
            'TV',
            'LG',
            'PC',
            'VL',
            'VP',
            'PS',
            'LD',
            'PQ',
            'VE',
            'VD',
            'PQM',
            'BC',
            'TVP',
            'VER',
            'RP',
            'ES',
            'PSP',
            'VEP',
            'RV',
            'VIA',
            'VCP',
            'PT',
            'TPJ',
            'AC',
            'ESP',
            'SV',
            'VLP',
            'CM',
            'CMP',
            'RPJ',
            'CP',
            'PCR',
            'VES',
            'CV'
        }
    
    mapa_extenso_para_abreviacao = {
            # Principais
            "RUA": "R",
            "AVENIDA": "AV",
            "ALAMEDA": "AL",
            "TRAVESSA": "TV",
            "LARGO": "LG",
            "PRACA": "PC",
            "PRAÇA": "PC",
            
            # Vilas e Parques
            "VILA": "VL",
            "VIA": "VIA",
            "VALE": "VL",
            "VIADUTO": "VD",
            "PARQUE": "PQ",
            "PASSEIO": "PS",
            
            # Outros comuns em SP
            "BECO": "BC",
            "ESTRADA": "ES",
            "LADEIRA": "LD",
            "RODODVIA": "RV",
            "CAMINHO": "CM",
            "PATIO": "PT",
            "PÁTIO": "PT",
            "ESCADA": "ES",
            "CONJUNTO": "CP",
            "CHACARA": "CH"
        }

    def to_upper(self, text: str) -> str:
        return text.upper()

    def remove_accents(self, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        return "".join(c for c in text if unicodedata.category(c) != 'Mn')

    def clean_special_chars(self, text: str) -> str:
        # Mantém apenas letras, números e espaços
        return re.sub(r'[^A-Z0-9\s]', ' ', text)
    
    def normalizar_tipo_logradouro(self, texto: str) -> str:
        """
        Substitui o tipo de logradouro por sua abreviação oficial 
        caso a primeira palavra seja um termo por extenso.
        """
        partes = texto.split(' ')
        if not partes:
            return texto
        
        primeira_palavra = partes[0]
    
        # Se a primeira palavra (ex: RUA) estiver no mapa, substitui pela abreviação (ex: R)
        if primeira_palavra in self.mapa_extenso_para_abreviacao:
            partes[0] = self.mapa_extenso_para_abreviacao[primeira_palavra]
            return " ".join(partes)
        
        return texto
    
    def remove_address_type(self, text: str) -> str:
        '''Remove o tipo de logradouro do início do texto, se presente.'''

        inicio = text.split(' ')[0]
        if inicio in self.tipos_logradouros:
            return text.removeprefix(inicio).lstrip()
        return text

    def strip_spaces(self, text: str) -> str:
        return " ".join(text.split())
    
    def pipeline(self, text:str, remove_type:bool=True) -> str:
        
        text = self.to_upper(text)
        text = self.remove_accents(text)
        text = self.clean_special_chars(text)
        text = self.normalizar_tipo_logradouro(text)
        if remove_type:
            text = self.remove_address_type(text)
        text = self.strip_spaces(text)

        return text
    
    def __call__(self, text: str, remove_logradouro_type:bool=False) -> str:
        """Executa todo o pipeline de tratamento."""
        if not text:
            return ""
        result = self.pipeline(text, remove_type=remove_logradouro_type)
        return result
