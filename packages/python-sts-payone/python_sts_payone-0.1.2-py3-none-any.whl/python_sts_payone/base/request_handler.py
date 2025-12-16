import requests
from requests import Response
from ..secure_hash.secure_hash_generator import get_secure_hash


def inject_secure_hash_to_params(auth_token: str, params: dict) -> dict:
    secure_hash: str = get_secure_hash(auth_token, params)
    params['SecureHash'] = secure_hash
    return params


class SmartRouteRequestHandler:
    """This class contains methods to send requests to Smart Route"""
    def __init__(self, sr_url: str, auth_token: str, params: dict):
        self.sr_url: str = sr_url
        self.auth_token: str = auth_token
        self.params: dict = params
    

    def send_request(self) -> Response:
        params: dict = inject_secure_hash_to_params(self.auth_token, self.params)
        return requests.post(self.sr_url, params)