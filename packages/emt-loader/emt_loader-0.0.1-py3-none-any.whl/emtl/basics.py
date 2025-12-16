from typing import Any
import requests
from .utils import _get_base_url, _get_cache


def authenticate(secret: str) -> bool:
    # todo
    pass


def get_available_dataset_ids() -> list[str]:
    """
    Fetch all available dataset ids.
    :return: List of all available dataset ids.
    """
    # request
    url = f"{_get_base_url()}/dataset_ids"
    response = requests.get(url)
    response.raise_for_status()
    # parse
    data = response.json()
    if not isinstance(data, list) or not all(isinstance(d, str) for d in data):
        return []
    return data


def get_request_schema(dataset_id: str) -> dict[str, Any]:
    """
    Fetch the request schema for the given dataset id.
    :return: Request schema as a dict.
    """
    # request
    url = f"{_get_base_url()}/schema/{dataset_id}"
    response = requests.get(url)
    response.raise_for_status()
    # parse
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError(f"Schema for '{dataset_id}' not found.")
    return data


def clear_cache() -> None:
    _get_cache().clear()

