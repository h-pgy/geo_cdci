from fpdf import FPDF
from fpdf.enums import Align
from .model import CertidaoModel
import os

class LayoutCertidao(FPDF):
    def __init__(self, model: CertidaoModel):
        super().__init__()
        self.model = model

    def header(self):
        if os.path.exists(self.model.path_header_logo):
            self.image(self.model.path_header_logo, x=14, y=2, w=25)
        
        self.set_font("helvetica", size=10)
        self.cell(w=35)
        self.multi_cell(w=0, h=5, text=self.model.header, align="C")
        self.ln(15)

    def watermark(self):

        largura_imagem = 140
        altura_estimada_imagem = 140
        posicao_x = (self.w - largura_imagem) / 2
        posicao_y = (self.h - altura_estimada_imagem) / 2
        if os.path.exists(self.model.path_watermark):
            with self.local_context(fill_opacity=0.15):
                self.image(self.model.path_watermark, x=posicao_x, y=posicao_y, w=largura_imagem)

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

    def write_mapa_lote(self):
        
        self.multi_cell(w=0, h=5, text="** Localização do imóvel **", align="C", markdown=True)
        if os.path.exists(self.model.mapa_lote_path):
            self.image(self.model.mapa_lote_path, x=30, w=self.w - 60)