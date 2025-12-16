"""
Webhook handling utilities for Aether Support SDK.
"""

import hashlib
import hmac
import json
from datetime import datetime
from typing import Any, Optional

from .types import WebhookEvent
from .exceptions import ValidationError


class WebhookHandler:
    """
    Handler for validating and parsing Aether Support webhook payloads.
    
    Example:
        >>> handler = WebhookHandler(webhook_secret="your-secret")
        >>> event = handler.verify_and_parse(payload, signature)
        >>> if event.type == "ticket.created":
        ...     print(f"New ticket: {event.data['ticket_id']}")
    """
    
    def __init__(self, webhook_secret: str):
        """
        Initialize the webhook handler.
        
        Args:
            webhook_secret: The webhook signing secret from your Aether dashboard.
        """
        self.webhook_secret = webhook_secret
    
    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: Optional[str] = None,
    ) -> bool:
        """
        Verify the webhook signature.
        
        Args:
            payload: The raw request body as bytes.
            signature: The X-Aether-Signature header value.
            timestamp: The X-Aether-Timestamp header value (optional).
        
        Returns:
            True if the signature is valid, False otherwise.
        """
        if not signature:
            return False
        
        # Build the signed payload
        if timestamp:
            signed_payload = f"{timestamp}.".encode() + payload
        else:
            signed_payload = payload
        
        # Calculate expected signature
        expected = hmac.new(
            self.webhook_secret.encode(),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        
        # Handle signature format: sha256=xxx or just xxx
        if signature.startswith("sha256="):
            signature = signature[7:]
        
        return hmac.compare_digest(expected, signature)
    
    def parse_payload(self, payload: bytes | str) -> WebhookEvent:
        """
        Parse a webhook payload into a WebhookEvent object.
        
        Args:
            payload: The raw request body as bytes or string.
        
        Returns:
            A WebhookEvent object.
        
        Raises:
            ValidationError: If the payload is invalid JSON or missing required fields.
        """
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON payload: {e}")
        
        # Validate required fields
        required_fields = ["event_id", "type", "app_id", "timestamp", "data"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")
        
        # Parse timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                data["timestamp"] = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                data["timestamp"] = datetime.now()
        
        return WebhookEvent(**data)
    
    def verify_and_parse(
        self,
        payload: bytes | str,
        signature: str,
        timestamp: Optional[str] = None,
    ) -> WebhookEvent:
        """
        Verify the webhook signature and parse the payload.
        
        Args:
            payload: The raw request body.
            signature: The X-Aether-Signature header value.
            timestamp: The X-Aether-Timestamp header value (optional).
        
        Returns:
            A WebhookEvent object.
        
        Raises:
            ValidationError: If the signature is invalid or payload is malformed.
        """
        payload_bytes = payload if isinstance(payload, bytes) else payload.encode()
        
        if not self.verify_signature(payload_bytes, signature, timestamp):
            raise ValidationError("Invalid webhook signature")
        
        return self.parse_payload(payload)


# Event type constants for easier handling
class EventTypes:
    """Constants for webhook event types."""
    
    # Ticket events
    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    TICKET_REPLIED = "ticket.replied"
    TICKET_RESOLVED = "ticket.resolved"
    TICKET_CLOSED = "ticket.closed"
    TICKET_REOPENED = "ticket.reopened"
    TICKET_ASSIGNED = "ticket.assigned"
    
    # User events
    USER_SIGNUP = "user.signup"
    USER_IDENTIFIED = "user.identified"
    
    # AI events
    AI_RESPONSE_SENT = "ai.response_sent"
    AI_ESCALATED = "ai.escalated"
    
    # Satisfaction events
    SATISFACTION_RATED = "satisfaction.rated"


def handle_webhook(
    webhook_secret: str,
    payload: bytes | str,
    signature: str,
    timestamp: Optional[str] = None,
) -> WebhookEvent:
    """
    Convenience function to verify and parse a webhook in one call.
    
    Args:
        webhook_secret: The webhook signing secret.
        payload: The raw request body.
        signature: The X-Aether-Signature header value.
        timestamp: The X-Aether-Timestamp header value (optional).
    
    Returns:
        A WebhookEvent object.
    
    Example:
        >>> from aether_support.webhooks import handle_webhook
        >>> event = handle_webhook(
        ...     webhook_secret="your-secret",
        ...     payload=request.body,
        ...     signature=request.headers["X-Aether-Signature"],
        ... )
    """
    handler = WebhookHandler(webhook_secret)
    return handler.verify_and_parse(payload, signature, timestamp)
