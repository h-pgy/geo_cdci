import folium
import geopandas as gpd
from typing import Any, Callable, Optional

class GeoJsonLayerFactory:
    """
    Fábrica para processamento e injeção de camadas GeoJson no Folium.
    
    Gerencia a validação de estruturas geoespaciais, reprojeção automática,
    geração dinâmica de estilos e orquestração via pipeline.
    """

    def validar_argumentos(self, mapa_folium: folium.Map, gdf: gpd.GeoDataFrame) -> None:
        if not isinstance(mapa_folium, folium.Map):
            raise ValueError("O argumento 'mapa_folium' precisa ser uma instância válida de folium.Map.")
            
        if not isinstance(gdf, gpd.GeoDataFrame):
            raise ValueError("O argumento 'gdf' precisa ser uma instância válida de geopandas.GeoDataFrame.")
            
        if gdf.empty:
            raise ValueError("O GeoDataFrame fornecido está vazio.")
            
        if "geometry" not in gdf.columns or gdf.geometry.isna().all():
            raise ValueError("O GeoDataFrame não possui nenhuma geometria válida para renderização.")

    def preparar_crs(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            return gdf.to_crs(epsg=4326)
        return gdf

    def gerar_style_function(self, **style_kwargs: Any) -> Callable[[dict[str, Any]], dict[str, Any]]:
        estilos_padrao = {
            "color": "#3388ff",
            "weight": 3,
            "opacity": 1.0,
            "fillColor": "#3388ff",
            "fillOpacity": 0.2
        }
        estilos_padrao.update(style_kwargs)
        return lambda x: estilos_padrao

    def executar_pipeline(
        self, 
        mapa_folium: folium.Map, 
        gdf: gpd.GeoDataFrame, 
        name: str, 
        control: bool, 
        style_function: Optional[Callable[[dict[str, Any]], dict[str, Any]]], 
        **style_kwargs: Any
    ) -> folium.Map:
        self.validar_argumentos(mapa_folium, gdf)
        
        gdf_configurado = self.preparar_crs(gdf)
        funcao_estilo = style_function or self.gerar_style_function(**style_kwargs)

        folium.GeoJson(
            gdf_configurado,
            name=name,
            style_function=funcao_estilo,
            control=control
        ).add_to(mapa_folium)

        return mapa_folium

    def __call__(
        self, 
        mapa_folium: folium.Map, 
        gdf: gpd.GeoDataFrame, 
        name: str = "Camada Vetorial",
        control: bool = True,
        style_function: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
        **style_kwargs: Any
    ) -> folium.Map:
        return self.executar_pipeline(
            mapa_folium=mapa_folium,
            gdf=gdf,
            name=name,
            control=control,
            style_function=style_function,
            **style_kwargs
        )