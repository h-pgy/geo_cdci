from api.services.certidao_pdf.layout import LayoutCertidao
from api.services.certidao_pdf.model import CertidaoModel
import os

class GeradorCertidao:

    def __init__(self, model: CertidaoModel):
        self.model = model
        self.layout = LayoutCertidao(model)

    def gerar_pdf(self, sections:list[str], output_path: str):
        self.layout.alias_nb_pages()
        self.layout.add_page()
        
        for section in sections:
            self.layout.write_section(section)

    def salvar_pdf(self, output_path: str)->str:
        self.layout.output(output_path)

        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Erro ao salvar PDF: arquivo {output_path} não encontrado.")

        return output_path
    
    def pipeline(self, sections:list[str], output_path: str)->str:
        self.gerar_pdf(sections, output_path)
        return self.salvar_pdf(output_path)
    
    def __call__(self, sections:list[str], output_path: str)->str:
        return self.pipeline(sections, output_path)