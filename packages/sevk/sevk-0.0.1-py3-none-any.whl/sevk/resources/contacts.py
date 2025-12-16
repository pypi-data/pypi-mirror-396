"""
Contacts Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from ..client import HttpClient


@dataclass
class Contact:
    id: str
    email: str
    subscribed: bool
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    project_id: Optional[str] = None


@dataclass
class ListContactsResponse:
    items: List[Contact]
    total: int
    page: int
    total_pages: int


class Contacts:
    """Contacts API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
        exclude_audience: Optional[str] = None,
        subscribed: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """List all contacts"""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search
        if exclude_audience is not None:
            params["excludeAudience"] = exclude_audience
        if subscribed is not None:
            params["subscribed"] = subscribed

        return self._client.get("/contacts", params or None)

    def create(
        self,
        email: str,
        subscribed: Optional[bool] = None,
        custom_fields: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a new contact"""
        data = {"email": email, **kwargs}
        if subscribed is not None:
            data["subscribed"] = subscribed
        if custom_fields is not None:
            data["customFields"] = custom_fields

        return self._client.post("/contacts", data)

    def get(self, contact_id: str) -> Dict[str, Any]:
        """Get a contact by ID"""
        return self._client.get(f"/contacts/{contact_id}")

    def update(
        self,
        contact_id: str,
        email: Optional[str] = None,
        subscribed: Optional[bool] = None,
        custom_fields: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update a contact"""
        data = {**kwargs}
        if email is not None:
            data["email"] = email
        if subscribed is not None:
            data["subscribed"] = subscribed
        if custom_fields is not None:
            data["customFields"] = custom_fields

        return self._client.put(f"/contacts/{contact_id}", data)

    def delete(self, contact_id: str) -> None:
        """Delete a contact"""
        self._client.delete(f"/contacts/{contact_id}")
