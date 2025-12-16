"""
Domains Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Domains:
    """Domains API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self, verified: Optional[bool] = None) -> Dict[str, Any]:
        """List all domains"""
        params = {}
        if verified is not None:
            params["verified"] = verified

        return self._client.get("/domains", params or None)

    def get(self, domain_id: str) -> Dict[str, Any]:
        """Get a domain by ID"""
        return self._client.get(f"/domains/{domain_id}")
