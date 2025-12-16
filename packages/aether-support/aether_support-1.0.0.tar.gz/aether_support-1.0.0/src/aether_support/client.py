"""
Main client classes for Aether Support SDK.
"""

from __future__ import annotations

from typing import Any, Optional
import httpx

from .types import (
    Ticket,
    KnowledgeDocument,
    SearchResult,
    User,
    UsageStats,
    TicketListResponse,
    KnowledgeListResponse,
    SearchResponse,
)
from .exceptions import raise_for_status, NetworkError, TimeoutError as AetherTimeoutError


DEFAULT_API_URL = "https://api.aether-support.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3


class TicketsAPI:
    """API client for ticket operations."""
    
    def __init__(self, client: "AetherSupport"):
        self._client = client
    
    def list(
        self,
        *,
        status: Optional[str] = None,
        category: Optional[str] = None,
        assigned_to: Optional[str] = None,
        customer_email: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> TicketListResponse:
        """List tickets with optional filters."""
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        if assigned_to:
            params["assigned_to"] = assigned_to
        if customer_email:
            params["customer_email"] = customer_email
        
        data = self._client._request("GET", "/api/support/tickets", params=params)
        return TicketListResponse(**data)
    
    def get(self, ticket_id: str) -> Ticket:
        """Get a specific ticket by ID."""
        data = self._client._request("GET", f"/api/support/tickets/{ticket_id}")
        return Ticket(**data)
    
    def create(
        self,
        *,
        subject: str,
        description: str,
        customer_email: str,
        category: str = "general",
        priority: int = 0,
        customer_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        custom_fields: Optional[dict[str, Any]] = None,
    ) -> Ticket:
        """Create a new support ticket."""
        payload: dict[str, Any] = {
            "subject": subject,
            "description": description,
            "customer_email": customer_email,
            "category": category,
            "priority": priority,
        }
        if customer_name:
            payload["customer_name"] = customer_name
        if tags:
            payload["tags"] = tags
        if custom_fields:
            payload["custom_fields"] = custom_fields
        
        data = self._client._request("POST", "/api/support/tickets", json=payload)
        return Ticket(**data.get("ticket", data))
    
    def update(
        self,
        ticket_id: str,
        *,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Ticket:
        """Update a ticket."""
        payload: dict[str, Any] = {}
        if status is not None:
            payload["status"] = status
        if priority is not None:
            payload["priority"] = priority
        if category is not None:
            payload["category"] = category
        if assigned_to is not None:
            payload["assigned_to"] = assigned_to
        if tags is not None:
            payload["tags"] = tags
        
        data = self._client._request("PATCH", f"/api/support/tickets/{ticket_id}", json=payload)
        return Ticket(**data.get("ticket", data))
    
    def reply(
        self,
        ticket_id: str,
        *,
        content: str,
        author_name: Optional[str] = None,
        author_type: str = "agent",
    ) -> Ticket:
        """Reply to a ticket."""
        payload: dict[str, Any] = {
            "content": content,
            "author_type": author_type,
        }
        if author_name:
            payload["author_name"] = author_name
        
        data = self._client._request(
            "POST", f"/api/support/tickets/{ticket_id}/messages", json=payload
        )
        return Ticket(**data.get("ticket", data))
    
    def add_note(
        self,
        ticket_id: str,
        *,
        content: str,
        author_name: Optional[str] = None,
    ) -> Ticket:
        """Add an internal note to a ticket."""
        payload: dict[str, Any] = {
            "content": content,
            "is_internal": True,
        }
        if author_name:
            payload["author_name"] = author_name
        
        data = self._client._request(
            "POST", f"/api/support/tickets/{ticket_id}/notes", json=payload
        )
        return Ticket(**data.get("ticket", data))
    
    def resolve(self, ticket_id: str) -> Ticket:
        """Resolve a ticket."""
        return self.update(ticket_id, status="resolved")
    
    def close(self, ticket_id: str) -> Ticket:
        """Close a ticket."""
        return self.update(ticket_id, status="closed")
    
    def reopen(self, ticket_id: str) -> Ticket:
        """Reopen a ticket."""
        return self.update(ticket_id, status="open")


class KnowledgeAPI:
    """API client for knowledge base operations."""
    
    def __init__(self, client: "AetherSupport"):
        self._client = client
    
    def list(
        self,
        *,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> KnowledgeListResponse:
        """List knowledge base documents."""
        params: dict[str, Any] = {}
        if category:
            params["category"] = category
        if is_public is not None:
            params["is_public"] = is_public
        
        data = self._client._request("GET", "/api/knowledge", params=params)
        return KnowledgeListResponse(**data)
    
    def get(self, document_id: str) -> KnowledgeDocument:
        """Get a specific document by ID."""
        data = self._client._request("GET", f"/api/knowledge/{document_id}")
        return KnowledgeDocument(**data)
    
    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        """Search the knowledge base."""
        params = {"query": query, "limit": limit}
        data = self._client._request("GET", "/api/knowledge/search", params=params)
        
        if isinstance(data, dict) and "results" in data:
            return [SearchResult(**r) for r in data["results"]]
        return [SearchResult(**r) for r in data] if isinstance(data, list) else []
    
    def create(
        self,
        *,
        title: str,
        content: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        is_public: bool = True,
    ) -> KnowledgeDocument:
        """Create a knowledge base document."""
        payload: dict[str, Any] = {
            "title": title,
            "content": content,
            "is_public": is_public,
        }
        if category:
            payload["category"] = category
        if tags:
            payload["tags"] = tags
        
        data = self._client._request("POST", "/api/knowledge", json=payload)
        return KnowledgeDocument(**data.get("document", data))
    
    def update(
        self,
        document_id: str,
        *,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        is_public: Optional[bool] = None,
    ) -> KnowledgeDocument:
        """Update a knowledge base document."""
        payload: dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if category is not None:
            payload["category"] = category
        if tags is not None:
            payload["tags"] = tags
        if is_public is not None:
            payload["is_public"] = is_public
        
        data = self._client._request("PATCH", f"/api/knowledge/{document_id}", json=payload)
        return KnowledgeDocument(**data.get("document", data))
    
    def delete(self, document_id: str) -> None:
        """Delete a knowledge base document."""
        self._client._request("DELETE", f"/api/knowledge/{document_id}")


class UsageAPI:
    """API client for usage statistics."""
    
    def __init__(self, client: "AetherSupport"):
        self._client = client
    
    def get_stats(self) -> UsageStats:
        """Get current usage statistics."""
        data = self._client._request("GET", "/api/usage/stats")
        return UsageStats(**data)


class AetherSupport:
    """
    Synchronous client for Aether Support API.
    
    Example:
        >>> client = AetherSupport(app_id="your-app-id", api_key="your-api-key")
        >>> tickets = client.tickets.list()
        >>> for ticket in tickets.tickets:
        ...     print(f"[{ticket.status}] {ticket.subject}")
    """
    
    def __init__(
        self,
        app_id: str,
        api_key: str,
        *,
        api_url: str = DEFAULT_API_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.app_id = app_id
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._http = httpx.Client(
            base_url=self.api_url,
            timeout=timeout,
            headers=self._default_headers(),
        )
        
        # Initialize API namespaces
        self.tickets = TicketsAPI(self)
        self.knowledge = KnowledgeAPI(self)
        self.usage = UsageAPI(self)
        
        # User tracking
        self._identified_user: Optional[User] = None
    
    def _default_headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-App-Id": self.app_id,
            "Content-Type": "application/json",
            "User-Agent": "aether-support-python/1.0.0",
        }
    
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API."""
        try:
            response = self._http.request(
                method=method,
                url=path,
                params=params,
                json=json,
            )
        except httpx.TimeoutException as e:
            raise AetherTimeoutError(
                f"Request to {path} timed out after {self.timeout}s",
                timeout=self.timeout,
            ) from e
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while requesting {path}: {e}",
                original_error=e,
            ) from e
        
        # Handle response
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"detail": response.text}
            raise_for_status(response.status_code, error_data)
        
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    def identify(
        self,
        user_id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        plan: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Identify a user for tracking purposes.
        
        This associates subsequent API calls with the identified user
        and enables user-specific features.
        """
        self._identified_user = User(
            user_id=user_id,
            email=email,
            name=name,
            plan=plan,
            metadata=metadata or {},
        )
        
        # Send identify event to API
        self._request(
            "POST",
            "/api/identify",
            json={
                "user_id": user_id,
                "email": email,
                "name": name,
                "plan": plan,
                "metadata": metadata or {},
            },
        )
    
    def track(
        self,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Track a custom event.
        
        Events can be used to trigger proactive support actions.
        """
        payload = {
            "event": event_name,
            "properties": properties or {},
        }
        
        if self._identified_user:
            payload["user_id"] = self._identified_user.user_id
        
        self._request("POST", "/api/events", json=payload)
    
    def logout(self) -> None:
        """Clear the identified user."""
        self._identified_user = None
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()
    
    def __enter__(self) -> "AetherSupport":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncTicketsAPI:
    """Async API client for ticket operations."""
    
    def __init__(self, client: "AsyncAetherSupport"):
        self._client = client
    
    async def list(
        self,
        *,
        status: Optional[str] = None,
        category: Optional[str] = None,
        assigned_to: Optional[str] = None,
        customer_email: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> TicketListResponse:
        """List tickets with optional filters."""
        params: dict[str, Any] = {"page": page, "per_page": per_page}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        if assigned_to:
            params["assigned_to"] = assigned_to
        if customer_email:
            params["customer_email"] = customer_email
        
        data = await self._client._request("GET", "/api/support/tickets", params=params)
        return TicketListResponse(**data)
    
    async def get(self, ticket_id: str) -> Ticket:
        """Get a specific ticket by ID."""
        data = await self._client._request("GET", f"/api/support/tickets/{ticket_id}")
        return Ticket(**data)
    
    async def create(
        self,
        *,
        subject: str,
        description: str,
        customer_email: str,
        category: str = "general",
        priority: int = 0,
        customer_name: Optional[str] = None,
        tags: Optional[list[str]] = None,
        custom_fields: Optional[dict[str, Any]] = None,
    ) -> Ticket:
        """Create a new support ticket."""
        payload: dict[str, Any] = {
            "subject": subject,
            "description": description,
            "customer_email": customer_email,
            "category": category,
            "priority": priority,
        }
        if customer_name:
            payload["customer_name"] = customer_name
        if tags:
            payload["tags"] = tags
        if custom_fields:
            payload["custom_fields"] = custom_fields
        
        data = await self._client._request("POST", "/api/support/tickets", json=payload)
        return Ticket(**data.get("ticket", data))
    
    async def update(
        self,
        ticket_id: str,
        *,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        category: Optional[str] = None,
        assigned_to: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> Ticket:
        """Update a ticket."""
        payload: dict[str, Any] = {}
        if status is not None:
            payload["status"] = status
        if priority is not None:
            payload["priority"] = priority
        if category is not None:
            payload["category"] = category
        if assigned_to is not None:
            payload["assigned_to"] = assigned_to
        if tags is not None:
            payload["tags"] = tags
        
        data = await self._client._request(
            "PATCH", f"/api/support/tickets/{ticket_id}", json=payload
        )
        return Ticket(**data.get("ticket", data))
    
    async def reply(
        self,
        ticket_id: str,
        *,
        content: str,
        author_name: Optional[str] = None,
        author_type: str = "agent",
    ) -> Ticket:
        """Reply to a ticket."""
        payload: dict[str, Any] = {
            "content": content,
            "author_type": author_type,
        }
        if author_name:
            payload["author_name"] = author_name
        
        data = await self._client._request(
            "POST", f"/api/support/tickets/{ticket_id}/messages", json=payload
        )
        return Ticket(**data.get("ticket", data))
    
    async def resolve(self, ticket_id: str) -> Ticket:
        """Resolve a ticket."""
        return await self.update(ticket_id, status="resolved")
    
    async def close(self, ticket_id: str) -> Ticket:
        """Close a ticket."""
        return await self.update(ticket_id, status="closed")


class AsyncKnowledgeAPI:
    """Async API client for knowledge base operations."""
    
    def __init__(self, client: "AsyncAetherSupport"):
        self._client = client
    
    async def list(
        self,
        *,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> KnowledgeListResponse:
        """List knowledge base documents."""
        params: dict[str, Any] = {}
        if category:
            params["category"] = category
        if is_public is not None:
            params["is_public"] = is_public
        
        data = await self._client._request("GET", "/api/knowledge", params=params)
        return KnowledgeListResponse(**data)
    
    async def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        """Search the knowledge base."""
        params = {"query": query, "limit": limit}
        data = await self._client._request("GET", "/api/knowledge/search", params=params)
        
        if isinstance(data, dict) and "results" in data:
            return [SearchResult(**r) for r in data["results"]]
        return [SearchResult(**r) for r in data] if isinstance(data, list) else []


class AsyncAetherSupport:
    """
    Asynchronous client for Aether Support API.
    
    Example:
        >>> async with AsyncAetherSupport(app_id="...", api_key="...") as client:
        ...     tickets = await client.tickets.list()
        ...     for ticket in tickets.tickets:
        ...         print(f"[{ticket.status}] {ticket.subject}")
    """
    
    def __init__(
        self,
        app_id: str,
        api_key: str,
        *,
        api_url: str = DEFAULT_API_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        self.app_id = app_id
        self.api_key = api_key
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._http = httpx.AsyncClient(
            base_url=self.api_url,
            timeout=timeout,
            headers=self._default_headers(),
        )
        
        # Initialize API namespaces
        self.tickets = AsyncTicketsAPI(self)
        self.knowledge = AsyncKnowledgeAPI(self)
        
        # User tracking
        self._identified_user: Optional[User] = None
    
    def _default_headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-App-Id": self.app_id,
            "Content-Type": "application/json",
            "User-Agent": "aether-support-python/1.0.0",
        }
    
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API."""
        try:
            response = await self._http.request(
                method=method,
                url=path,
                params=params,
                json=json,
            )
        except httpx.TimeoutException as e:
            raise AetherTimeoutError(
                f"Request to {path} timed out after {self.timeout}s",
                timeout=self.timeout,
            ) from e
        except httpx.RequestError as e:
            raise NetworkError(
                f"Network error while requesting {path}: {e}",
                original_error=e,
            ) from e
        
        # Handle response
        if response.status_code >= 400:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"detail": response.text}
            raise_for_status(response.status_code, error_data)
        
        if response.status_code == 204:
            return {}
        
        return response.json()
    
    async def identify(
        self,
        user_id: str,
        *,
        email: Optional[str] = None,
        name: Optional[str] = None,
        plan: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Identify a user for tracking purposes."""
        self._identified_user = User(
            user_id=user_id,
            email=email,
            name=name,
            plan=plan,
            metadata=metadata or {},
        )
        
        await self._request(
            "POST",
            "/api/identify",
            json={
                "user_id": user_id,
                "email": email,
                "name": name,
                "plan": plan,
                "metadata": metadata or {},
            },
        )
    
    async def track(
        self,
        event_name: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """Track a custom event."""
        payload = {
            "event": event_name,
            "properties": properties or {},
        }
        
        if self._identified_user:
            payload["user_id"] = self._identified_user.user_id
        
        await self._request("POST", "/api/events", json=payload)
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.aclose()
    
    async def __aenter__(self) -> "AsyncAetherSupport":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
