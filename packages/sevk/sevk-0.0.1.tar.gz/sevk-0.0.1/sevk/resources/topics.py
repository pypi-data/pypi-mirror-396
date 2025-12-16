"""
Topics Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Topics:
    """Topics API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self, audience_id: str) -> Dict[str, Any]:
        """List all topics for an audience"""
        return self._client.get(f"/audiences/{audience_id}/topics")

    def create(
        self,
        audience_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new topic"""
        data = {"name": name}
        if description is not None:
            data["description"] = description

        return self._client.post(f"/audiences/{audience_id}/topics", data)

    def get(self, audience_id: str, topic_id: str) -> Dict[str, Any]:
        """Get a topic by ID"""
        return self._client.get(f"/audiences/{audience_id}/topics/{topic_id}")

    def update(
        self,
        audience_id: str,
        topic_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a topic"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description

        return self._client.put(f"/audiences/{audience_id}/topics/{topic_id}", data)

    def delete(self, audience_id: str, topic_id: str) -> None:
        """Delete a topic"""
        self._client.delete(f"/audiences/{audience_id}/topics/{topic_id}")
