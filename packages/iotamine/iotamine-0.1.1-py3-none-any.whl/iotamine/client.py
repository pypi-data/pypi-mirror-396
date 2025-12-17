import requests
from .exceptions import IotamineAPIError

class IotamineClient:
    def __init__(self, api_key: str, base_url: str = "https://iotamine.com/api"):
        self.api_key = api_key
        self.base_url = base_url

    def _headers(self):
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }

    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=self._headers(), **kwargs)

        if not response.ok:
            raise IotamineAPIError(response.status_code, response.text)
        return response.json()
