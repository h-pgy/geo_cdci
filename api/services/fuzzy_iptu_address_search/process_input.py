import unicodedata
import re

class AddressStringProcessor:

    def __init__(self):
            # Pipeline de métodos a serem executados na ordem
            self.pipeline = [
                self.to_upper,
                self.remove_accents,
                self.clean_special_chars,
                self.strip_spaces
            ]

    def to_upper(self, text: str) -> str:
        return text.upper()

    def remove_accents(self, text: str) -> str:
        text = unicodedata.normalize('NFD', text)
        return "".join(c for c in text if unicodedata.category(c) != 'Mn')

    def clean_special_chars(self, text: str) -> str:
        # Mantém apenas letras, números e espaços
        return re.sub(r'[^A-Z0-9\s]', ' ', text)

    def strip_spaces(self, text: str) -> str:
        return " ".join(text.split())

    def run(self, text: str) -> str:
        """Executa todo o pipeline de tratamento."""
        if not text:
            return ""
        result = text
        for method in self.pipeline:
            result = method(result)
        return result
    
    def __call__(self, text: str) -> str:
        return self.run(text)
