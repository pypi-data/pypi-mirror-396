from typing import Optional
from .utilities.auth import get_authentication, Authentication
from .utilities.feature_data_cache import FeatureDataCache


authentication: Optional[Authentication] = None
fdc: Optional[FeatureDataCache] = None


def initialize(api_key: str):
    """
    Initialize the greenhub SDK.
    It is important to initialize the greenhub SDK before using any further functionalities of the SDK.
    The given api_key is passed on and checked by the authentication module.

    Note: The method is cloud aware and ignores the api_key in case the method is used in scripts
    running in the gcloud.

    :param api_key: user API key derived from greenhub.ai
    """

    global authentication
    global fdc

    authentication = get_authentication(api_key)
    fdc = FeatureDataCache()


def is_initialized() -> bool:
    return (not fdc is None) and (not authentication is None)


def get_auth() -> Optional[Authentication]:
    global authentication
    return authentication


def get_fdc() -> Optional[FeatureDataCache]:
    global fdc
    return fdc
