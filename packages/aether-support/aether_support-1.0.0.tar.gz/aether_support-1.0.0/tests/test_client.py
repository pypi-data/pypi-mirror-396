"""
Tests for Aether Support Python SDK.
"""

import pytest
from unittest.mock import Mock, patch
import httpx

from aether_support import AetherSupport, AsyncAetherSupport
from aether_support.types import Ticket, TicketListResponse
from aether_support.exceptions import AetherError, AuthenticationError, NotFoundError


# Sample test data - include app_id as required by Ticket model
SAMPLE_TICKET = {
    "ticket_id": "TKT-123",
    "app_id": "test_app",
    "subject": "Test ticket",
    "description": "Test description",
    "status": "open",
    "priority": 1,
    "category": "general",
    "customer_email": "user@example.com",
    "customer_name": "Test User",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "messages": [],
    "tags": [],
}

SAMPLE_TICKET_LIST = {
    "tickets": [SAMPLE_TICKET],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "has_more": False,
}


class TestAetherSupportInit:
    """Test client initialization."""
    
    def test_init_with_app_id_and_api_key(self):
        client = AetherSupport(app_id="test_app", api_key="test_key")
        assert client.app_id == "test_app"
        assert client.api_key == "test_key"
    
    def test_init_with_custom_api_url(self):
        client = AetherSupport(
            app_id="test_app",
            api_key="test_key",
            api_url="https://custom.api.com"
        )
        assert client.api_url == "https://custom.api.com"
    
    def test_init_default_api_url(self):
        client = AetherSupport(app_id="test_app", api_key="test_key")
        assert "aether-support.com" in client.api_url


class TestTicketsAPI:
    """Test ticket operations."""
    
    @pytest.fixture
    def client(self):
        return AetherSupport(app_id="test_app", api_key="test_key")
    
    @pytest.fixture
    def mock_response(self):
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.is_success = True
        return response
    
    def test_list_tickets(self, client, mock_response):
        mock_response.json.return_value = SAMPLE_TICKET_LIST
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.tickets.list()
            
            assert isinstance(result, TicketListResponse)
            assert len(result.tickets) == 1
            assert result.tickets[0].ticket_id == "TKT-123"
    
    def test_get_ticket(self, client, mock_response):
        mock_response.json.return_value = SAMPLE_TICKET
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.tickets.get("TKT-123")
            
            assert isinstance(result, Ticket)
            assert result.ticket_id == "TKT-123"
            assert result.subject == "Test ticket"
    
    def test_create_ticket(self, client, mock_response):
        mock_response.json.return_value = {"ticket": SAMPLE_TICKET}
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.tickets.create(
                subject="Test ticket",
                description="Test description",
                customer_email="user@example.com"
            )
            
            assert isinstance(result, Ticket)
            assert result.subject == "Test ticket"
    
    def test_update_ticket(self, client, mock_response):
        updated_ticket = {**SAMPLE_TICKET, "status": "resolved"}
        mock_response.json.return_value = {"ticket": updated_ticket}
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.tickets.update("TKT-123", status="resolved")
            
            assert result.status == "resolved"
    
    def test_reply_to_ticket(self, client, mock_response):
        mock_response.json.return_value = {"ticket": SAMPLE_TICKET}
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.tickets.reply("TKT-123", content="Test reply")
            
            assert isinstance(result, Ticket)


class TestErrorHandling:
    """Test error handling."""
    
    @pytest.fixture
    def client(self):
        return AetherSupport(app_id="test_app", api_key="test_key")
    
    def test_authentication_error(self, client):
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 401
        error_response.is_success = False
        error_response.json.return_value = {"error": "Invalid API key"}
        
        with patch.object(client._http, 'request', return_value=error_response):
            with pytest.raises(AuthenticationError):
                client.tickets.list()
    
    def test_not_found_error(self, client):
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 404
        error_response.is_success = False
        error_response.json.return_value = {"error": "Ticket not found"}
        
        with patch.object(client._http, 'request', return_value=error_response):
            with pytest.raises(NotFoundError):
                client.tickets.get("TKT-999")
    
    def test_api_error(self, client):
        error_response = Mock(spec=httpx.Response)
        error_response.status_code = 500
        error_response.is_success = False
        error_response.json.return_value = {"error": "Internal server error"}
        
        with patch.object(client._http, 'request', return_value=error_response):
            with pytest.raises(AetherError):
                client.tickets.list()


class TestAsyncClient:
    """Test async client."""
    
    @pytest.fixture
    def async_client(self):
        return AsyncAetherSupport(app_id="test_app", api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_async_list_tickets(self, async_client):
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = SAMPLE_TICKET_LIST
        
        with patch.object(async_client._http, 'request', return_value=mock_response):
            result = await async_client.tickets.list()
            
            assert isinstance(result, TicketListResponse)
            assert len(result.tickets) == 1


class TestKnowledgeAPI:
    """Test knowledge base operations."""
    
    @pytest.fixture
    def client(self):
        return AetherSupport(app_id="test_app", api_key="test_key")
    
    def test_search_knowledge(self, client):
        """Test knowledge search returns list of SearchResult."""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {
            "results": [
                {
                    "document_id": "DOC-1",
                    "title": "Getting Started",
                    "content": "Welcome to our platform...",
                    "score": 0.95,
                }
            ],
        }
        
        with patch.object(client._http, 'request', return_value=mock_response):
            result = client.knowledge.search("getting started")
            
            # Returns a list of SearchResult
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].title == "Getting Started"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
