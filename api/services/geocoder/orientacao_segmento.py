from .models import Paridade
import geopandas as gpd
from shapely.geometry import LineString
import math
from typing import Dict, cast


class SolverOrientacaoSegmento:

    def __init__(self, cols_numeracao: Dict[Paridade, dict[str, str]])->None:
        self.cols_numeracao = cols_numeracao

    def is_primeiro_segmento(self, gdf_segmentos:gpd.GeoDataFrame, segmento:gpd.GeoDataFrame, paridade:Paridade)->bool:

        coluna_inicial = self.cols_numeracao[paridade]["inicial"]

        numero_inicial_segmento = segmento.iloc[0][coluna_inicial]

        #menor numero inicial
        menor_numero_inicial = gdf_segmentos[coluna_inicial].min()

        return numero_inicial_segmento == menor_numero_inicial
    
    def is_ultimo_segmento(self, gdf_segmentos:gpd.GeoDataFrame, segmento:gpd.GeoDataFrame, paridade:Paridade)->bool:

        coluna_final = self.cols_numeracao[paridade]["final"]

        numero_final_segmento = segmento.iloc[0][coluna_final]

        #maior numero final
        maior_numero_final = gdf_segmentos[coluna_final].max()

        return numero_final_segmento == maior_numero_final
    
    def segmentos_anteriores(self, gdf_segmentos:gpd.GeoDataFrame, segmento:gpd.GeoDataFrame, paridade:Paridade)->gpd.GeoDataFrame:

        if self.is_primeiro_segmento(gdf_segmentos, segmento, paridade):
            raise ValueError("Segmento é o primeiro da via, não existe segmento anterior")
        coluna_inicial = self.cols_numeracao[paridade]["inicial"]
        coluna_final = self.cols_numeracao[paridade]["final"]
        numero_inicial_segmento = segmento.iloc[0][coluna_inicial]

        #nao deveria ser menor ou igual (só menor) mas estou colocando por precaução
        segmentos_anteriores = gdf_segmentos[gdf_segmentos[coluna_final] <= numero_inicial_segmento] 
        segmentos_anteriores.sort_values(by=coluna_final, ascending=False, inplace=True)
        return segmentos_anteriores
    
    def segmentos_posteriores(self, gdf_segmentos:gpd.GeoDataFrame, segmento:gpd.GeoDataFrame, paridade:Paridade)->gpd.GeoDataFrame:
        
        if self.is_ultimo_segmento(gdf_segmentos, segmento, paridade):
            raise ValueError("Segmento é o último da via, não existe segmento posterior")
        coluna_inicial = self.cols_numeracao[paridade]["inicial"]
        coluna_final = self.cols_numeracao[paridade]["final"]
        numero_final_segmento = segmento.iloc[0][coluna_final]

        #nao deveria ser maior ou igual (só maior) mas estou colocando por precaução
        segmentos_posteriores = gdf_segmentos[gdf_segmentos[coluna_inicial] >= numero_final_segmento] 
        segmentos_posteriores.sort_values(by=coluna_inicial, ascending=True, inplace=True)
        return segmentos_posteriores

    def segmento_adjacente(self, gdf_segmentos:gpd.GeoDataFrame, segmento:gpd.GeoDataFrame, paridade:Paridade)->gpd.GeoDataFrame:

        if self.is_primeiro_segmento(gdf_segmentos, segmento, paridade):
            segmentos_adjacentes = self.segmentos_posteriores(gdf_segmentos, segmento, paridade)

        else:
            segmentos_adjacentes = self.segmentos_anteriores(gdf_segmentos, segmento, paridade)

        return segmentos_adjacentes.iloc[[0]]
    

    def orientacao_segmento_is_correta(self, segmento:gpd.GeoDataFrame, gdf_segmentos:gpd.GeoDataFrame, paridade:Paridade)->bool:

        segmento_adjacente = self.segmento_adjacente(gdf_segmentos, segmento, paridade)
        geom_segmento = cast(LineString, segmento.geometry.iloc[0])
        geom_segmento_adjacente = cast(LineString, segmento_adjacente.geometry.iloc[0])
        
        if self.is_primeiro_segmento(gdf_segmentos, segmento, paridade):
            #se é o primeiro segmento, pego a última coordenada dele e verifico se está próxima da primeira do segmento adjacente
            ponto_referencia_ego = geom_segmento.coords[-1]
            ponto_proximo_alter = geom_segmento_adjacente.coords[0]
            ponto_distante_alter= geom_segmento_adjacente.coords[-1]
        else:
            #se não é o primeiro segmento, aí pego a primeira coordenada do segmento e verifico se está próxima da última do segmento adjacente
            ponto_referencia_ego = geom_segmento.coords[0]
            ponto_proximo_alter = geom_segmento_adjacente.coords[-1]
            ponto_distante_alter= geom_segmento_adjacente.coords[0]

        
        distancia_proximo = math.dist(ponto_referencia_ego, ponto_proximo_alter)
        distancia_distante = math.dist(ponto_referencia_ego, ponto_distante_alter)
        
        if distancia_distante < distancia_proximo:
            return False
            
        return True
    
    def corrigir_orientacao_segmento(self, segmento:gpd.GeoDataFrame, gdf_segmentos:gpd.GeoDataFrame, paridade:Paridade)->gpd.GeoDataFrame:
        

        if self.orientacao_segmento_is_correta(segmento, gdf_segmentos, paridade):
            return segmento
        geom_segmento = cast(LineString, segmento.geometry.iloc[0])
        coordenadas_invertidas = list(geom_segmento.coords)[::-1]
        nova_geometria = LineString(coordenadas_invertidas)
        geometrias = segmento.geometry.tolist()
        geometrias[0] = nova_geometria
        segmento = segmento.set_geometry(geometrias)
        return segmento
    
    def __call__(self, segmento:gpd.GeoDataFrame, gdf_segmentos:gpd.GeoDataFrame, paridade:Paridade)->gpd.GeoDataFrame:
        return self.corrigir_orientacao_segmento(segmento, gdf_segmentos, paridade)