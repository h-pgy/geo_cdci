from pathlib import Path
from typing import Union
import geopandas as gpd
from config import settings

DATA_DIR = Path(settings.FOLDER_DADOS)

def ensure_dir(path: Union[str, Path]) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def join_and_ensure(directory: Union[str, Path], filename: str) -> Path:
    directory = ensure_dir(directory)
    return directory / filename

def data_path(fname: str, subfolder: str = "") -> Path:
    full_dir = DATA_DIR / subfolder
    return join_and_ensure(full_dir, fname)
