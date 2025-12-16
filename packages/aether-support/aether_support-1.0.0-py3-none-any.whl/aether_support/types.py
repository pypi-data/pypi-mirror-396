"""
Pydantic models for Aether Support SDK types.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a support ticket."""
    
    id: str
    author_name: str
    author_email: Optional[str] = None
    author_type: str = Field(description="One of: user, agent, ai")
    content: str
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        extra = "allow"


class Ticket(BaseModel):
    """A support ticket."""
    
    ticket_id: str
    app_id: str
    subject: str
    description: str
    category: str = "general"
    status: str = "open"
    priority: int = 0
    customer_email: str
    customer_name: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_agents: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    messages: list[Message] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        extra = "allow"


class User(BaseModel):
    """User identification data."""
    
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    plan: Optional[str] = None
    metadata: dict[str, str] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"


class KnowledgeDocument(BaseModel):
    """A knowledge base document."""
    
    document_id: str
    title: str
    content: str
    category: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    is_public: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        extra = "allow"


class SearchResult(BaseModel):
    """A search result from the knowledge base."""
    
    document_id: str
    title: str
    content: str
    score: float = 0.0
    highlights: list[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class WebhookEvent(BaseModel):
    """A webhook event payload."""
    
    event_id: str
    type: str = Field(description="Event type: ticket.created, ticket.replied, etc.")
    app_id: str
    timestamp: datetime
    data: dict[str, Any]
    
    class Config:
        extra = "allow"


class UsageStats(BaseModel):
    """Usage statistics for an app."""
    
    period_start: datetime
    period_end: datetime
    total_conversations: int = 0
    ai_responses: int = 0
    tickets_created: int = 0
    tickets_resolved: int = 0
    avg_response_time: Optional[float] = None
    avg_resolution_time: Optional[float] = None
    
    class Config:
        extra = "allow"


class TicketListResponse(BaseModel):
    """Response from listing tickets."""
    
    tickets: list[Ticket]
    total: int
    page: int = 1
    per_page: int = 20
    
    class Config:
        extra = "allow"


class KnowledgeListResponse(BaseModel):
    """Response from listing knowledge documents."""
    
    documents: list[KnowledgeDocument]
    total: int
    
    class Config:
        extra = "allow"


class SearchResponse(BaseModel):
    """Response from knowledge search."""
    
    results: list[SearchResult]
    query: str
    total: int
    
    class Config:
        extra = "allow"
