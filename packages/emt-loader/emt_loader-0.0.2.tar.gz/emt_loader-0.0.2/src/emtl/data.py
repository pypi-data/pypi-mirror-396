from pathlib import Path
from typing import Any
import requests
from tqdm import tqdm

from .utils import _get_base_url, _get_cache


CHUNK_SIZE = 8192  # 8 KB


def get_data_files(request: dict[str, Any], cache: bool = True) -> list[Path]:
    """
    Given a 'request' that represents a valid filled-out schema,
    the data is retrieved and the paths to the stored data files are returned.
    """

    # query /data endpoint with requests to trigger data retrievers
    url_retrievers = f"{_get_base_url()}/data"
    response = requests.post(url_retrievers, json=request)
    response.raise_for_status()
    data_file_names = response.json()
    if not isinstance(data_file_names, list) or not all(isinstance(d, str) for d in data_file_names):
        raise ValueError(f"Data request with failed - request object\n'{request}'")

    # given the created data files on the server side -> check if they are already cached -> download if not
    data_cache = _get_cache()
    cache_dir_path = data_cache.cache_dir_path
    data_file_paths = list()
    for d in data_file_names:
        if data_cache.is_file_cached(d):
            data_file_paths.append(cache_dir_path / d)
            print(f"{d}: loaded from cache")
        else:
            data_file_paths.append(_retrieve_data_file(d, cache_dir_path))
    return data_file_paths


def _retrieve_data_file(file_name: str, cache_dir_path: Path) -> Path:
    """Download the given file_name into cache_dir_path."""

    file_name_path = cache_dir_path / file_name
    url_download = f"{_get_base_url()}/data/download/{file_name}"

    with requests.get(url_download, stream=True) as r:
        r.raise_for_status()

        # get total size
        total_size = int(r.headers.get("Content-Length", 0))

        # progress bar
        progress = tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=file_name,
        )

        with file_name_path.open("wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                f.write(chunk)
                progress.update(len(chunk))

        progress.close()

    return file_name_path
