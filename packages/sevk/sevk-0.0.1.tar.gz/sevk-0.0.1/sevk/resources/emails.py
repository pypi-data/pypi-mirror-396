"""
Emails Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Emails:
    """Emails API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a transactional email

        Args:
            params: Dictionary containing email parameters:
                - from: Sender email address
                - to: Recipient email address
                - subject: Email subject
                - html: HTML content (optional)
                - text: Plain text content (optional)
                - replyTo: Reply-to address (optional)
                - cc: CC recipients (optional)
                - bcc: BCC recipients (optional)
                - headers: Custom headers (optional)
        """
        return self._client.post("/emails", params)
