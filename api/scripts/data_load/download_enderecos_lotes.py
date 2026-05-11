import pandas as pd
from api.integrations.wfs import WFSFetcher
from api.utils.io.path import data_path
from api.utils.io.parquet import save_parquet, load_parquet
from tqdm import tqdm
from api.config import settings


FILE_ENDERECOS= 'enderecos_lotes.parquet'
CAMADA_LOTES = settings.LAYER_LOTES
SUBFOLDER='enderecos_lotes'

def download_enderecos_lotes()->pd.DataFrame:

    path_file = data_path(FILE_ENDERECOS, subfolder=SUBFOLDER)
    if path_file.exists():
        print(f"Arquivo '{FILE_ENDERECOS}' já existe. Carregando dados do arquivo...")
        return load_parquet(FILE_ENDERECOS, subfolder=SUBFOLDER, gdf=False)

    print('Baixando dados de endereços dos lotes do WFS...')
    fetcher = WFSFetcher()
    query_params = {
        'propertyName' : 'cd_identificador,cd_logradouro,nm_logradouro_completo,cd_numero_porta,tx_complemento_endereco',
        "CQL_FILTER": "tx_situ_lote='ATIVO'"
    }
    lotes_lista = []

    for batch in tqdm(fetcher(nome_camada=CAMADA_LOTES, **query_params), desc="Baixando lotes"):
        lotes_lista.extend([item['properties'] for item in batch])
    
    df_lotes = pd.DataFrame(lotes_lista)
    save_parquet(df_lotes, FILE_ENDERECOS, subfolder=SUBFOLDER)
    return df_lotes