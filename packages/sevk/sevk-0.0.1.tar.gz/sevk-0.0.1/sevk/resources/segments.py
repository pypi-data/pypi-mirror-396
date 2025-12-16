"""
Segments Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Segments:
    """Segments API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self, audience_id: str) -> Dict[str, Any]:
        """List all segments for an audience"""
        return self._client.get(f"/audiences/{audience_id}/segments")

    def create(
        self,
        audience_id: str,
        name: str,
        rules: List[Dict[str, Any]],
        operator: str = "AND",
        limit_to_topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new segment

        Args:
            audience_id: The audience ID
            name: Segment name
            rules: List of rule objects with field, operator, value
            operator: Logical operator for combining rules ("AND" or "OR")
            limit_to_topics: Optional list of topic IDs to limit the segment to
        """
        data: Dict[str, Any] = {"name": name, "rules": rules, "operator": operator}
        if limit_to_topics is not None:
            data["limitToTopics"] = limit_to_topics

        return self._client.post(f"/audiences/{audience_id}/segments", data)

    def get(self, audience_id: str, segment_id: str) -> Dict[str, Any]:
        """Get a segment by ID"""
        return self._client.get(f"/audiences/{audience_id}/segments/{segment_id}")

    def update(
        self,
        audience_id: str,
        segment_id: str,
        name: Optional[str] = None,
        rules: Optional[List[Dict[str, Any]]] = None,
        operator: Optional[str] = None,
        limit_to_topics: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update a segment"""
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if rules is not None:
            data["rules"] = rules
        if operator is not None:
            data["operator"] = operator
        if limit_to_topics is not None:
            data["limitToTopics"] = limit_to_topics

        return self._client.put(f"/audiences/{audience_id}/segments/{segment_id}", data)

    def delete(self, audience_id: str, segment_id: str) -> Dict[str, Any]:
        """Delete a segment"""
        return self._client.delete(f"/audiences/{audience_id}/segments/{segment_id}")
