"""
Subscriptions Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Subscriptions:
    """Subscriptions API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def subscribe(
        self,
        email: str,
        audience_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        topic_ids: Optional[List[str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Subscribe a contact

        Args:
            email: Contact email address
            audience_id: Optional audience ID to subscribe to
            topic_id: Optional single topic ID to subscribe to
            topic_ids: Optional list of topic IDs to subscribe to
            data: Optional additional contact data
        """
        payload: Dict[str, Any] = {"email": email}
        if audience_id is not None:
            payload["audienceId"] = audience_id
        if topic_id is not None:
            payload["topicId"] = topic_id
        if topic_ids is not None:
            payload["topicIds"] = topic_ids
        if data is not None:
            payload["data"] = data

        return self._client.post("/subscriptions/subscribe", payload)

    def unsubscribe(
        self,
        email: Optional[str] = None,
        contact_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Unsubscribe a contact

        Args:
            email: Contact email address (either email or contact_id required)
            contact_id: Contact ID (either email or contact_id required)
        """
        payload: Dict[str, Any] = {}
        if email is not None:
            payload["email"] = email
        if contact_id is not None:
            payload["contactId"] = contact_id

        return self._client.post("/subscriptions/unsubscribe", payload)
