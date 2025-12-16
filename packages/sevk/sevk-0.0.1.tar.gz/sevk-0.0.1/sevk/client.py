"""
Sevk API Client
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import httpx

from .resources.contacts import Contacts
from .resources.audiences import Audiences
from .resources.templates import Templates
from .resources.broadcasts import Broadcasts
from .resources.domains import Domains
from .resources.topics import Topics
from .resources.segments import Segments
from .resources.subscriptions import Subscriptions
from .resources.emails import Emails


@dataclass
class SevkOptions:
    """Configuration options for Sevk client"""
    base_url: str = "https://api.sevk.io"
    timeout: int = 30


class HttpClient:
    """HTTP client wrapper for making API requests"""

    def __init__(self, api_key: str, options: SevkOptions):
        self.api_key = api_key
        self.base_url = options.base_url
        self.timeout = options.timeout
        self._client = httpx.Client(timeout=self.timeout)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> Any:
        if not response.is_success:
            raise Exception(f"Request failed with status {response.status_code}: {response.text}")

        if response.status_code == 204:
            return {}

        return response.json()

    def get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self._client.get(url, headers=self._get_headers(), params=params)
        return self._handle_response(response)

    def post(self, path: str, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self._client.post(url, headers=self._get_headers(), json=data)
        return self._handle_response(response)

    def put(self, path: str, data: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        response = self._client.put(url, headers=self._get_headers(), json=data)
        return self._handle_response(response)

    def delete(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        response = self._client.delete(url, headers=self._get_headers())
        return self._handle_response(response)

    def close(self):
        self._client.close()


class Sevk:
    """
    Sevk API Client

    Usage:
        sevk = Sevk("sevk_your_api_key")
        contacts = sevk.contacts.list()
    """

    def __init__(self, api_key: str, options: Optional[SevkOptions] = None):
        if options is None:
            options = SevkOptions()

        self._client = HttpClient(api_key, options)

        # Initialize resources
        self.contacts = Contacts(self._client)
        self.audiences = Audiences(self._client)
        self.templates = Templates(self._client)
        self.broadcasts = Broadcasts(self._client)
        self.domains = Domains(self._client)
        self.topics = Topics(self._client)
        self.segments = Segments(self._client)
        self.subscriptions = Subscriptions(self._client)
        self.emails = Emails(self._client)

    def close(self):
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
