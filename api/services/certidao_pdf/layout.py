from fpdf import FPDF
from .model import CertidaoModel
import os

class LayoutCertidao(FPDF):
    def __init__(self, model: CertidaoModel):
        super().__init__()
        self.model = model

    def header(self):
        if os.path.exists(self.model.path_logo_cabecalho):
            self.image(self.model.path_logo_cabecalho, x=14, y=10, w=25)
        
        self.set_font("helvetica", size=10)
        self.cell(w=35)
        self.multi_cell(w=0, h=5, text=self.model.cabecalho, align="C")
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font("helvetica", size=9)
        self.multi_cell(w=0, h=5, text=self.model.footer, align="C", markdown=True)
        
        self.set_y(-10)
        self.set_font("helvetica", size=8)
        self.cell(w=0, h=5, text=f"Página {self.page_no()}/{{nb}}", align="R")

    def write_section(self, section:str)->None:
        
        self.multi_cell(w=0, h=6, text=section, markdown=True)
        self.ln(self.model.space_between_sections) #espaço entre seções