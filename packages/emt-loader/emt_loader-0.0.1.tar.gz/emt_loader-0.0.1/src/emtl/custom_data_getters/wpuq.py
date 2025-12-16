import pandas as pd

from ..basics import get_request_schema
from ..data import get_data_files


SPATIAL_RESOLUTIONS = ['10s', '1min', '15min', '60min']
YEARS = list(range(2018, 2021))
DATASET_ID = 'wpuq_dataset'


def get_wpuq_description():
    """Get the general information of the WPuQ dataset."""

    schema = get_request_schema(DATASET_ID)
    return schema['description']


def get_wpuq_household_load_data(year: int, spatial_resolution: bool = False,
                                 only_pv: bool = False, only_no_pv: bool = False):
    """
    Get all WPuQ household load data for the given year and spatial resolution.
    Loads household load data for all available WITH_PV and NO_PV single family households.
    """

    # param checking
    if only_pv and only_no_pv:
        raise ValueError('get_wpuq_household_load_data error: only_pv and only_no_pv cannot be True simultaneously.')
    if spatial_resolution not in SPATIAL_RESOLUTIONS:
        raise ValueError(
            f'get_wpuq_household_load_data error: spatial_resolution must be one of {SPATIAL_RESOLUTIONS}.')
    if year not in YEARS:
        raise ValueError(
            f'get_wpuq_household_load_data error: year must between {YEARS[0]} and {YEARS[-1]} (inclusive).')
    # build request schema
    request_schema = get_request_schema(DATASET_ID)
    request_schema['year'] = year
    request_schema['file_name'] = f'data_{spatial_resolution}'
    request_schema['top_level_nodes'] = ['WITH_PV'] if only_pv else ['WITH_NO_PV'] if only_no_pv else ['WITH_PV',
                                                                                                       'WITH_NO_PV']
    request_schema['mid_level_nodes'] = []  # all nodes
    request_schema['low_level_nodes'] = 'HOUSEHOLD'
    # fetch and concat data
    data_file_paths = get_data_files(request_schema)
    data_dfs = [pd.read_csv(f) for f in data_file_paths]
    return pd.concat(data_dfs, axis=0, ignore_index=True)


def get_wpuq_heatpump_load_data(year: int, spatial_resolution: bool = False,
                                only_pv: bool = False, only_no_pv: bool = False):
    """
    Get all WPuQ heatpump load data for the given year and spatial resolution.
    Loads heatpump load data for all available WITH_PV and NO_PV single family households.
    """

    # param checking
    if only_pv and only_no_pv:
        raise ValueError('get_wpuq_heatpump_load_data error: only_pv and only_no_pv cannot be True simultaneously.')
    if spatial_resolution not in SPATIAL_RESOLUTIONS:
        raise ValueError(f'get_wpuq_heatpump_load_data error: spatial_resolution must be one of {SPATIAL_RESOLUTIONS}.')
    if year not in YEARS:
        raise ValueError(
            f'get_wpuq_heatpump_load_data error: year must between {YEARS[0]} and {YEARS[-1]} (inclusive).')
    # build request schema
    request_schema = get_request_schema(DATASET_ID)
    request_schema['year'] = year
    request_schema['file_name'] = f'data_{spatial_resolution}'
    request_schema['top_level_nodes'] = ['WITH_PV'] if only_pv else ['WITH_NO_PV'] if only_no_pv else ['WITH_PV',
                                                                                                       'WITH_NO_PV']
    request_schema['mid_level_nodes'] = []  # all nodes
    request_schema['low_level_nodes'] = 'HEATPUMP'
    # fetch and concat data
    data_file_paths = get_data_files(request_schema)
    data_dfs = [pd.read_csv(f) for f in data_file_paths]
    return pd.concat(data_dfs, axis=0, ignore_index=True)
