"""
Sevk API Resources
"""

from .contacts import Contacts
from .audiences import Audiences
from .templates import Templates
from .broadcasts import Broadcasts
from .domains import Domains
from .topics import Topics
from .segments import Segments
from .subscriptions import Subscriptions
from .emails import Emails

__all__ = [
    "Contacts",
    "Audiences",
    "Templates",
    "Broadcasts",
    "Domains",
    "Topics",
    "Segments",
    "Subscriptions",
    "Emails",
]
