import geopandas as gpd
import pandas as pd
from pathlib import Path
from api.utils.io.path import data_path

def save_parquet(data: gpd.GeoDataFrame|pd.DataFrame, filename: str, subfolder: str = "") -> Path:
    # Garante a extensão .parquet
    if not filename.endswith(".parquet"):
        filename += ".parquet"
    path = data_path(filename, subfolder)
    data.to_parquet(path)
    
    return path

def load_parquet(filename: str, subfolder: str = "", gdf:bool=True) -> gpd.GeoDataFrame|pd.DataFrame:
    if not filename.endswith(".parquet"):
        raise ValueError(f"O arquivo '{filename}' deve ter a extensão .parquet")
        
    path = data_path(filename, subfolder)
    
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado no caminho: {path}")
    if gdf:
        return gpd.read_parquet(path)
    else:
        return pd.read_parquet(path)