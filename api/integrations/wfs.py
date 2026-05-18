import requests
from typing import Optional, Generator, List, Union, Any
from json import JSONDecodeError

from api.config import settings

class WFSFetcher:
    """
    Abstração para extração de dados via WFS do GeoSampa.

    Esta classe gerencia a paginação automática e permite a iteração
    por lotes de features de qualquer camada do Geosampa.

    Attributes:
        start_index (int): Índice inicial da busca.
        count (int): Quantidade de registros por lote.
        features_fetched_count (int): Contador acumulado de registros obtidos.
    """
    
    domain = settings.WFS_DOMAIN
    endpoint = settings.WFS_ENDPOINT
    service = settings.WFS_SERVICE
    version = settings.WFS_VERSION
    namespace = settings.WFS_NAMESPACE
    

    def __init__(self, start_index:int=0, verbose:bool=False)->None:
        self.start_index = start_index
        self.features_fetched_count = 0
        self.last_resp_metadata = {}
        self.verbose = verbose

    @property
    def url_base(self):
        return f"https://{self.domain}/{self.endpoint}"

    def gen_get_features_parameters(self, nome_camada:str, output_format:str="application/json", 
                                    count:Optional[int]=None, start_index:Optional[int]=None, **query_parameters) -> dict[str, Union[str, int]]:
        params: dict[str, str|int] = {
            "service": self.service,
            "version": self.version,
            "request": "GetFeature",
            "typeName": f"{self.namespace}:{nome_camada}",
            "outputFormat": output_format
        }
        
        if count is not None:
            params["maxFeatures"] = count
        
        if start_index is not None:
            params["startIndex"] = start_index
            
        params.update(query_parameters)
        return params
    
    def build_query_url_string(self, nome_camada:str, params:dict[str, Union[str, int]]) -> str:
        
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{self.url_base}?{query_string}"


    def get_layer_data(self, nome_camada:str, output_format:str="application/json", count:Optional[int]=None, 
                       start_index:Optional[int]=None, **query_parameters)->dict:
        params = self.gen_get_features_parameters(
            nome_camada=nome_camada, 
            output_format=output_format, 
            count=count, 
            start_index=start_index,
            **query_parameters
        )

        if self.verbose:
            print(f"Fetching data at url {self.build_query_url_string(nome_camada, params)}")
        
        response = requests.get(self.url_base, params=params)
        
        if response.status_code != 200:
            response.raise_for_status()
        try:
            return response.json()
        except JSONDecodeError:
            raise ValueError(f"Response content is not valid JSON: {response.text}")
    
    def fetch_feature_batches(self, nome_camada:str, output_format:str="application/json", count:Optional[int]=None, 
                       start_index:Optional[int]=None, **query_parameters)->Generator[List[dict], None, None]:
        while True:
            data = self.get_layer_data(
                nome_camada=nome_camada,
                start_index=self.start_index,
                output_format=output_format,
                count=count,
                **query_parameters
            )
            
            features = data.pop("features", [])
            self.last_resp_metadata = data
            total_matched = data.get("numberMatched", 0)
            
            if not features:
                break
            
            qtd_features = len(features)
            self.features_fetched_count += qtd_features
            self.start_index += qtd_features
            yield features
            
            if self.features_fetched_count >= total_matched:
                break
                
            

    def __call__(self, nome_camada:str, output_format:str="application/json", count:Optional[int]=None, 
                       start_index:Optional[int]=None, **query_parameters)-> Generator[List[dict[str, Any]], None, None]:
        return self.fetch_feature_batches(nome_camada, output_format=output_format, count=count, start_index=start_index, **query_parameters)