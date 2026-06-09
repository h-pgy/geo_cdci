from .models import Paridade
from .orientacao_segmento import SolverOrientacaoSegmento
from api.integrations.wfs import WFSFetcher
from api.config import settings
from .exceptions import SegmentoNotFoundError, NumeracaoNotFoundError
from shapely.geometry import Point, LineString
from typing import cast
import geopandas as gpd



class DimapGeocoder:

    cols_numeracao = {
        Paridade.PAR: {
        "inicial" :   'cd_numero_inicial_par',
        "final" : 'cd_numero_final_par'     
    },
    Paridade.IMPAR: {
        "inicial" : 'cd_numero_inicial_impar',
        "final" : 'cd_numero_final_impar'
    }
    }

    def __init__(self)->None:

        self.layer_logradouros = settings.LAYER_LOGRADOUROS
        self.corrigir_orientacao_segmento = SolverOrientacaoSegmento(self.cols_numeracao)

    @property
    def cols_numeracao_lst(self):
        cols = []
        for paridade in Paridade:
            cols.extend(self.cols_numeracao[paridade].values())
        return cols

    def get_segmentos(self, codlog:int)->gpd.GeoDataFrame:

        segmentos = []

        #por alguma razao nao estava puxando a cada vez, ai precisa instanciar aqui
        wfs = WFSFetcher()
        batch_gen = wfs(self.layer_logradouros, cql_filter=f"codlog={codlog}")
        for batch in batch_gen:
            segmentos.extend(batch)

        gdf_segmentos = gpd.GeoDataFrame.from_features(segmentos)

        if gdf_segmentos.empty:
            #usando erro especifico para poder dar catch depois e retornar 404
            raise SegmentoNotFoundError(f"Nenhum segmento encontrado para codlog={codlog}")

        return gdf_segmentos
    
    def paridade_numeracao(self, numero:int)->Paridade:

        if numero % 2 == 0:
            return Paridade.PAR
        else:
            return Paridade.IMPAR
        
    def clean_segmentos_sem_numeracao(self, gdf_segmentos:gpd.GeoDataFrame)->gpd.GeoDataFrame:

       df_numeracao = gdf_segmentos[self.cols_numeracao_lst]
       sem_numeracao_nenhum_lado = df_numeracao.isnull().all(axis=1)
       return gdf_segmentos[~sem_numeracao_nenhum_lado]
    

    def find_segmento_contem_numero(self, gdf_segmentos:gpd.GeoDataFrame, numero:int, paridade:Paridade)->gpd.GeoDataFrame:

        col_inicial = self.cols_numeracao[paridade]["inicial"]
        col_final = self.cols_numeracao[paridade]["final"]

        #filtrando segmentos que contem o numero buscado
        gdf_segmentos_contem_numero = gdf_segmentos[
            (gdf_segmentos[col_inicial] <= numero) & 
            (gdf_segmentos[col_final] >= numero)
        ]

        if gdf_segmentos_contem_numero.empty:
            raise NumeracaoNotFoundError(f"Nenhum segmento encontrado contendo o numero {numero}")

        if gdf_segmentos_contem_numero.shape[0] > 1:
            print(f"Warning: mais de um segmento encontrado contendo o numero {numero}. Retornando o primeiro.")
            gdf_segmentos_contem_numero = gdf_segmentos_contem_numero.iloc[[0]]

        return gdf_segmentos_contem_numero
    
    def interpolar_numero_da_rua(self, segmento:gpd.GeoDataFrame, numero:int, paridade:Paridade)->Point:

        coluna_inicial = self.cols_numeracao[paridade]["inicial"]
        coluna_final = self.cols_numeracao[paridade]["final"]

        numero_inicial = segmento.iloc[0][coluna_inicial]
        numero_final = segmento.iloc[0][coluna_final]

        geom_segmento = cast(LineString, segmento.geometry.iloc[0])

        if numero_final == numero_inicial:
            #se o numero inicial e final são iguais, não tem como interpolar, então retorno o ponto médio do segmento
            print(f"Warning: numero inicial e final são iguais ({numero_inicial}), não é possível interpolar. Retornando ponto médio do segmento.")
            return geom_segmento.interpolate(0.5, normalized=True)

        #calculando a proporção do número em relação ao segmento
        proporcao = (numero - numero_inicial) / (numero_final - numero_inicial)

        #interpolando a posição no segmento com base na proporção
        ponto_interpolado = geom_segmento.interpolate(proporcao, normalized=True)

        return ponto_interpolado

    def pipeline_geocode(self, codlog:int, numero:int)->Point:


        paridade = self.paridade_numeracao(numero)
        gdf_segmentos = self.get_segmentos(codlog)
        gdf_segmentos = self.clean_segmentos_sem_numeracao(gdf_segmentos)
        segmento_numero = self.find_segmento_contem_numero(gdf_segmentos, numero, paridade)
        segmento_numero = self.corrigir_orientacao_segmento(segmento_numero, gdf_segmentos, paridade)

        ponto = self.interpolar_numero_da_rua(segmento_numero, numero, paridade)

        return ponto

    def __call__(self, codlog:int, numero:int)->Point:
        return self.pipeline_geocode(codlog, numero)