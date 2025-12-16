"""
Aether Support Python SDK

Official Python SDK for Aether Support - AI-powered customer support platform.
"""

from .client import AetherSupport, AsyncAetherSupport
from .types import Ticket, Message, User, KnowledgeDocument, WebhookEvent
from .exceptions import (
    AetherError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__version__ = "1.0.0"
__all__ = [
    # Clients
    "AetherSupport",
    "AsyncAetherSupport",
    # Types
    "Ticket",
    "Message",
    "User",
    "KnowledgeDocument",
    "WebhookEvent",
    # Exceptions
    "AetherError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
]
