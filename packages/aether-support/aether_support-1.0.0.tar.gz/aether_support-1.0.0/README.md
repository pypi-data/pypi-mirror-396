# Aether Support Python SDK

Official Python SDK for [Aether Support](https://aether-support.com) - the AI-powered customer support platform.

## Installation

```bash
pip install aether-support
```

## Quick Start

```python
from aether_support import AetherSupport

# Initialize the client
client = AetherSupport(
    app_id="your-app-id",
    api_key="your-api-key"
)

# Create a ticket
ticket = client.tickets.create(
    subject="Help with integration",
    description="I need help setting up the SDK",
    customer_email="user@example.com",
    category="technical"
)

print(f"Created ticket: {ticket.ticket_id}")

# Get all tickets
tickets = client.tickets.list()
for t in tickets:
    print(f"[{t.status}] {t.subject}")

# Reply to a ticket
client.tickets.reply(
    ticket_id=ticket.ticket_id,
    content="Here's more information about my issue..."
)
```

## Async Support

```python
import asyncio
from aether_support import AsyncAetherSupport

async def main():
    client = AsyncAetherSupport(
        app_id="your-app-id",
        api_key="your-api-key"
    )
    
    # All methods are async
    tickets = await client.tickets.list()
    for t in tickets:
        print(f"[{t.status}] {t.subject}")
    
    await client.close()

asyncio.run(main())
```

## Features

### Ticket Management

```python
# List tickets with filters
tickets = client.tickets.list(
    status="open",
    category="billing",
    limit=50
)

# Get a specific ticket
ticket = client.tickets.get("ticket-id")

# Update ticket status
client.tickets.update("ticket-id", status="resolved")

# Add internal note (agents only)
client.tickets.add_note("ticket-id", "Internal notes here")
```

### Knowledge Base

```python
# Search the knowledge base
results = client.knowledge.search("how to reset password")
for doc in results:
    print(f"{doc.title}: {doc.content[:100]}...")

# Get all documents
docs = client.knowledge.list()
```

### Users & Identification

```python
# Identify a user (for tracking)
client.identify(
    user_id="user-123",
    email="user@example.com",
    name="John Doe",
    plan="pro",
    metadata={
        "company": "Acme Inc",
        "signup_date": "2024-01-15"
    }
)

# Track custom events
client.track("button_clicked", {
    "button_name": "contact_support",
    "page": "/pricing"
})
```

### Webhooks

```python
from aether_support.webhooks import WebhookHandler

# Verify and parse webhook payloads
handler = WebhookHandler(webhook_secret="your-webhook-secret")

@app.post("/webhooks/aether")
async def handle_webhook(request):
    payload = await request.body()
    signature = request.headers.get("X-Aether-Signature")
    
    event = handler.verify_and_parse(payload, signature)
    
    if event.type == "ticket.created":
        print(f"New ticket: {event.data['ticket_id']}")
    elif event.type == "ticket.replied":
        print(f"Reply on: {event.data['ticket_id']}")
    
    return {"status": "ok"}
```

## Configuration

```python
from aether_support import AetherSupport

client = AetherSupport(
    app_id="your-app-id",
    api_key="your-api-key",
    
    # Optional configuration
    api_url="https://api.aether-support.com",  # Custom API URL
    timeout=30.0,  # Request timeout in seconds
    max_retries=3,  # Retry failed requests
)
```

## Error Handling

```python
from aether_support import AetherSupport
from aether_support.exceptions import (
    AetherError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError
)

client = AetherSupport(app_id="...", api_key="...")

try:
    ticket = client.tickets.get("invalid-id")
except NotFoundError:
    print("Ticket not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except AetherError as e:
    print(f"API error: {e}")
```

## Type Hints

The SDK is fully typed for excellent IDE support:

```python
from aether_support import AetherSupport
from aether_support.types import Ticket, Message, User

client = AetherSupport(app_id="...", api_key="...")

# Full type information available
ticket: Ticket = client.tickets.get("ticket-id")
messages: list[Message] = ticket.messages
```

## Framework Integrations

### FastAPI

```python
from fastapi import FastAPI, Depends
from aether_support import AetherSupport

app = FastAPI()

def get_aether() -> AetherSupport:
    return AetherSupport(app_id="...", api_key="...")

@app.get("/tickets")
async def list_tickets(aether: AetherSupport = Depends(get_aether)):
    return aether.tickets.list()
```

### Django

```python
# settings.py
AETHER_SUPPORT = {
    "APP_ID": "your-app-id",
    "API_KEY": "your-api-key",
}

# views.py
from django.conf import settings
from aether_support import AetherSupport

client = AetherSupport(**settings.AETHER_SUPPORT)
```

### Flask

```python
from flask import Flask, g
from aether_support import AetherSupport

app = Flask(__name__)

def get_aether():
    if 'aether' not in g:
        g.aether = AetherSupport(app_id="...", api_key="...")
    return g.aether

@app.route("/tickets")
def list_tickets():
    return get_aether().tickets.list()
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- 📧 Email: support@aether-support.com
- 📖 Docs: https://docs.aether-support.com/sdk/python
- 💬 Discord: https://discord.gg/aether-support
