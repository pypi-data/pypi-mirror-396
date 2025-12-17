import os
from urllib.error import HTTPError
import requests

API_KEY_CHECK_REST_API_URL: str = 'https://us-central1-digitalyieldmonitoringplatform.cloudfunctions.net/checkApiKey'
ID_TOKEN_AUDIENCE: str = "https://us-central1-digitalyieldmonitoringplatform.cloudfunctions.net/"


class Authentication:

    def get_auth_headers(self) -> dict:
        raise NotImplementedError()


class ApiKeyAuthentication(Authentication):

    def __init__(self, api_key: str):
        self.api_key = api_key
        res = requests.get(API_KEY_CHECK_REST_API_URL, params={'apiKey': self.api_key})

        if res.status_code == 401:
            raise ValueError("Invalid API key.")
        if res.status_code != 200:
            raise HTTPError(f'Checking API key failed with status code: {res.status_code}')

    def get_auth_headers(self) -> dict:
        return {'api_key': self.api_key}


class GCloudIDTokenAuthentication(Authentication):

    def __init__(self):
        # Define the metadata URL
        url = f"http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/identity?audience={ID_TOKEN_AUDIENCE}"

        # Set the headers
        headers = {
            "Metadata-Flavor": "Google"
        }

        # Make the GET request
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise HTTPError(f"Failed to fetch identity: {response.status_code}, {response.text}")

        self.id_token = response.text

    def get_auth_headers(self) -> dict:
        return {'Authorization': f'Bearer {self.id_token}'}


def is_running_in_cloud() -> bool:
    return os.getenv('CLOUD_RUN_JOB') is not None


def get_authentication(api_key: str) -> Authentication:
    if is_running_in_cloud():
        print("Using cloud auth")
        return GCloudIDTokenAuthentication()
    else:
        print("Using api key auth")
        return ApiKeyAuthentication(api_key)
