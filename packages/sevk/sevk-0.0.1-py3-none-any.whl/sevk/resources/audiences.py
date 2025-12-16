"""
Audiences Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Audiences:
    """Audiences API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all audiences"""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        return self._client.get("/audiences", params or None)

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        users_can_see: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new audience"""
        data = {"name": name}
        if description is not None:
            data["description"] = description
        if users_can_see is not None:
            data["usersCanSee"] = users_can_see

        return self._client.post("/audiences", data)

    def get(self, audience_id: str) -> Dict[str, Any]:
        """Get an audience by ID"""
        return self._client.get(f"/audiences/{audience_id}")

    def update(
        self,
        audience_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        users_can_see: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an audience"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if users_can_see is not None:
            data["usersCanSee"] = users_can_see

        return self._client.put(f"/audiences/{audience_id}", data)

    def delete(self, audience_id: str) -> None:
        """Delete an audience"""
        self._client.delete(f"/audiences/{audience_id}")

    def add_contacts(self, audience_id: str, contact_ids: List[str]) -> Dict[str, Any]:
        """Add contacts to an audience"""
        return self._client.post(
            f"/audiences/{audience_id}/contacts",
            {"contactIds": contact_ids}
        )
