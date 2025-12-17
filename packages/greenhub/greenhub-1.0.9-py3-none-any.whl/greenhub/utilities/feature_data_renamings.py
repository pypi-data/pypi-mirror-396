import pandas as pd

"""
The feature data still contains some minor errors, such as non-uniform column names and missing country 2-digit codes, ... .
This file includes a method for each feature data source, which transforms the fetched data into the correct format.
These adjustments are only temporary, and the data should be corrected later (and the jobs updated accordingly), 
making this file obsolete in the future. (see issue #219)
"""


def historical_yield_data_renaming(data: pd.DataFrame) -> pd.DataFrame:

    # columns renaming
    renamings = {
        'valueType': 'ValueType',
        'year': 'Year',
        'crop': 'Crop',
        'spatialResolution': 'SpatialResolution',
        'country': 'Country',
        'state': 'State',
        'municipality': 'Municipality',
        'value': 'Value'
    }
    data = data.rename(columns=renamings)

    return data


def vi_data_renaming(data: pd.DataFrame) -> pd.DataFrame:

    # columns renaming
    renamings = {
        'Fpar': 'FPAR',
        'NAME': 'Country',
        'GID_0': 'CountryCode',
        'GEOID': 'CountryCode',
    }
    data = data.rename(columns=renamings)

    # the `CountryCode` colum sometimes contains three-digit country codes -> can simply cut to two-digit codes
    data['CountryCode'] = data['CountryCode'].str.slice(0, 2)

    # the US vi data contains an unnecessary column `AFFGEOID`
    data = data.drop(columns=['AFFGEOID'], errors='ignore')

    # remove unnecessary column `COUNTRY`
    data = data.drop(columns=['COUNTRY'], errors='ignore')

    return data


def climate_data_renaming(data: pd.DataFrame) -> pd.DataFrame:

    # columns renaming
    renamings = {
        'Country': 'CountryCode',
        'COUNTRY': 'Country',
        'NAME': 'Country',
        'GID_0': 'CountryCode',
        'GEOID': 'CountryCode',
    }
    data = data.rename(columns=renamings)

    # the climate data contains an unnecessary column `Unnamed: 0`
    data = data.drop(columns=['Unnamed: 0'], errors='ignore')

    return data


def forecast_data_renaming(data: pd.DataFrame) -> pd.DataFrame:

    # columns renaming
    renamings = {
        'country': 'Country',
        'state': 'State',
        'municipality': 'Municipality'
    }
    data = data.rename(columns=renamings)

    # create missing column containing '2 digits country code'
    country_to_country_code = {
        'Brazil': 'BR',
        'Argentina': 'AR',
        'Germany': 'DE',
        'United States': 'US'
    }
    data['CountryCode'] = data['Country'].apply(lambda c: country_to_country_code[c])

    return data


def soil_data_renaming(data: pd.DataFrame) -> pd.DataFrame:

    # columns renaming
    renamings = {
        'GID_0': 'CountryCode',
    }
    data = data.rename(columns=renamings)

    # the `CountryCode` colum sometimes contains three-digit country codes -> can simply cut to two-digit codes
    data['CountryCode'] = data['CountryCode'].str.slice(0, 2)

    # remove unnecessary column `COUNTRY`
    data = data.drop(columns=['COUNTRY'], errors='ignore')

    return data

