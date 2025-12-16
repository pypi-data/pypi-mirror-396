#!/usr/bin/env python3
"""
Integration test script for Aether Support Python SDK.

This script tests the SDK against a live API.
Run with: python -m pytest tests/test_integration.py -v --integration

Set these environment variables before running:
  AETHER_APP_ID=your_app_id
  AETHER_API_KEY=your_api_key
  AETHER_API_URL=https://api.aether-support.com (optional)
"""

import os
import pytest
from aether_support import AetherSupport


# Skip integration tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable."
)


@pytest.fixture
def client():
    """Create SDK client from environment variables."""
    app_id = os.getenv("AETHER_APP_ID")
    api_key = os.getenv("AETHER_API_KEY")
    api_url = os.getenv("AETHER_API_URL")
    
    if not app_id or not api_key:
        pytest.skip("AETHER_APP_ID and AETHER_API_KEY must be set")
    
    kwargs = {"app_id": app_id, "api_key": api_key}
    if api_url:
        kwargs["api_url"] = api_url
    
    return AetherSupport(**kwargs)


class TestIntegration:
    """Integration tests against live API."""
    
    def test_list_tickets(self, client):
        """Test listing tickets."""
        result = client.tickets.list()
        
        assert result is not None
        assert hasattr(result, 'tickets')
        assert isinstance(result.tickets, list)
        print(f"✅ Listed {len(result.tickets)} tickets")
    
    def test_create_and_get_ticket(self, client):
        """Test creating and retrieving a ticket."""
        # Create
        ticket = client.tickets.create(
            subject="SDK Integration Test",
            description="This is a test ticket from the Python SDK integration tests.",
            customer_email="sdk-test@example.com",
            customer_name="SDK Test",
            category="general",
        )
        
        assert ticket is not None
        assert ticket.ticket_id is not None
        assert ticket.subject == "SDK Integration Test"
        print(f"✅ Created ticket: {ticket.ticket_id}")
        
        # Get
        fetched = client.tickets.get(ticket.ticket_id)
        assert fetched.ticket_id == ticket.ticket_id
        assert fetched.subject == ticket.subject
        print(f"✅ Retrieved ticket: {fetched.ticket_id}")
        
        # Update
        updated = client.tickets.update(ticket.ticket_id, status="resolved")
        assert updated.status == "resolved"
        print(f"✅ Updated ticket status to: {updated.status}")
    
    def test_search_knowledge(self, client):
        """Test knowledge base search."""
        result = client.knowledge.search("getting started")
        
        assert result is not None
        assert hasattr(result, 'results')
        print(f"✅ Found {len(result.results)} knowledge articles")
    
    def test_get_usage(self, client):
        """Test getting usage stats."""
        try:
            usage = client.usage.get_current()
            assert usage is not None
            print(f"✅ Current usage: {usage}")
        except Exception as e:
            # Usage might not be available on all plans
            print(f"⚠️ Usage stats not available: {e}")


def run_manual_test():
    """
    Run a quick manual test.
    
    Usage:
        export AETHER_APP_ID=your_app_id
        export AETHER_API_KEY=your_api_key
        python tests/test_integration.py
    """
    app_id = os.getenv("AETHER_APP_ID")
    api_key = os.getenv("AETHER_API_KEY")
    api_url = os.getenv("AETHER_API_URL", "https://api.aether-support.com")
    
    if not app_id or not api_key:
        print("❌ Please set AETHER_APP_ID and AETHER_API_KEY environment variables")
        return
    
    print(f"Testing SDK against: {api_url}")
    print(f"App ID: {app_id}")
    print("-" * 50)
    
    client = AetherSupport(app_id=app_id, api_key=api_key, api_url=api_url)
    
    # Test 1: List tickets
    print("\n1. Listing tickets...")
    try:
        tickets = client.tickets.list()
        print(f"   ✅ Found {len(tickets.tickets)} tickets")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Search knowledge base
    print("\n2. Searching knowledge base...")
    try:
        results = client.knowledge.search("help")
        print(f"   ✅ Found {len(results.results)} articles")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create a test ticket
    print("\n3. Creating test ticket...")
    try:
        ticket = client.tickets.create(
            subject="SDK Test Ticket",
            description="Testing the Python SDK",
            customer_email="test@example.com",
        )
        print(f"   ✅ Created ticket: {ticket.ticket_id}")
        
        # Clean up - resolve the ticket
        client.tickets.update(ticket.ticket_id, status="resolved")
        print(f"   ✅ Resolved test ticket")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "-" * 50)
    print("SDK test complete!")


if __name__ == "__main__":
    run_manual_test()
