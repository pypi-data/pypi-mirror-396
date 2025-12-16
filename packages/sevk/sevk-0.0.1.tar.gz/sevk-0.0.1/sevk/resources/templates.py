"""
Templates Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Templates:
    """Templates API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all templates"""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        return self._client.get("/templates", params or None)

    def create(self, title: str, content: str) -> Dict[str, Any]:
        """Create a new template"""
        return self._client.post("/templates", {"title": title, "content": content})

    def get(self, template_id: str) -> Dict[str, Any]:
        """Get a template by ID"""
        return self._client.get(f"/templates/{template_id}")

    def update(
        self,
        template_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a template"""
        data = {}
        if title is not None:
            data["title"] = title
        if content is not None:
            data["content"] = content

        return self._client.put(f"/templates/{template_id}", data)

    def delete(self, template_id: str) -> None:
        """Delete a template"""
        self._client.delete(f"/templates/{template_id}")

    def duplicate(self, template_id: str) -> Dict[str, Any]:
        """Duplicate a template"""
        return self._client.post(f"/templates/{template_id}/duplicate", {})
