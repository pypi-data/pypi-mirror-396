"""
Broadcasts Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Broadcasts:
    """Broadcasts API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all broadcasts"""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        return self._client.get("/broadcasts", params or None)

    def get(self, broadcast_id: str) -> Dict[str, Any]:
        """Get a broadcast by ID"""
        return self._client.get(f"/broadcasts/{broadcast_id}")
