# Sovant Python SDK

**Sovant is a governed AI memory layer for AI agents and applications.**
Use it to store, search, and recall memories with profile awareness and enterprise-grade control over how memory is captured and used.

[![PyPI version](https://img.shields.io/pypi/v/sovant.svg)](https://pypi.org/project/sovant/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
pip install sovant
```

## Quick Start

```python
from sovant import Sovant

# Initialize the client
client = Sovant(api_key="sk_live_your_api_key_here", base_url="https://sovant.ai")

# Create a memory
mem = client.memory.create({
    "content": "User prefers dark mode",
    "type": "preference",
    "tags": ["ui", "settings"]
})

# Search memories
results = client.memory.search({
    "query": "user preferences",
    "limit": 10
})

# Update a memory
updated = client.memory.update(mem["id"], {
    "tags": ["ui", "settings", "theme"]
})

# Delete a memory
client.memory.delete(mem["id"])
```

## Recall vs Search

Sovant provides two ways to query memories:

- **`memory_recall()`** – Hybrid recall, profile-aware
  Use for conversational queries: "What do you know about me?", "What happened on Project X?".
  Uses Sovant's hybrid pipeline (profile fast-path + thread-scoped lexical + vector semantic search) and prioritizes profile facts (name/age/location) when available.

- **`memory_search()`** – Semantic search
  Use for topic lookup and discovery. Pure vector similarity search without profile logic.
  Behavior unchanged from previous versions.

```python
# Recall for conversational queries
context = client.memory_recall(
    query="what do you know about me?",
    limit=10
)

# Search for topic discovery
topics = client.memory_search({
    "query": "project updates",
    "limit": 5
})
```

## Chat in 60 Seconds

Stream real-time chat responses with memory context:

```python
from sovant import Sovant
import sys

client = Sovant(api_key="sk_live_your_api_key_here", base_url="https://sovant.ai")

# Create a chat session
session = client.chat.create_session({"title": "Demo"})

# Stream a response
stream = client.chat.send_message(
    session["id"],
    "hello",
    {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "use_memory": True
    },
    stream=True
)

for ev in stream:
    if ev["type"] == "delta":
        sys.stdout.write(ev.get("data", ""))
    elif ev["type"] == "done":
        print("\n[done]")

# Get chat history
messages = client.chat.get_messages(session["id"])
```

## Profile Recall Helpers

Save and recall user profile facts with canonical patterns:

```python
# Extract profile entity from text
fact = client.recall.extract_profile("i'm from kuching")
# -> {"entity": "location", "value": "kuching"} | None

if fact:
    client.recall.save_profile_fact(fact)  # canonicalizes and persists

# Get all profile facts
profile = client.recall.get_profile_facts()
# -> {"name": "...", "age": "...", "location": "...", "preferences": [...]}
```

## Configuration

```python
from sovant import Sovant

client = Sovant(
    api_key="sk_live_your_api_key_here",  # Required
    base_url="https://sovant.ai",         # Optional, API endpoint
    timeout=30.0,                          # Optional, request timeout in seconds (default: 30.0)
    max_retries=3,                         # Optional, max retry attempts (default: 3)
    debug=False,                           # Optional, enable debug logging (default: False)
)
```

The SDK handles dual authentication automatically, preferring the `x-sovant-api-key` header over `Authorization: Bearer`.

## API Reference

### Memory Operations

#### Create Memory

```python
memory = client.memory.create({
    "content": "Customer contacted support about billing",
    "type": "observation",          # 'journal' | 'insight' | 'observation' | 'task' | 'preference'
    "tags": ["support", "billing"],
    "metadata": {"ticket_id": "12345"},
    "thread_id": "thread_abc123",   # Optional thread association
})
```

#### List Memories

```python
memories = client.memory.list({
    "limit": 20,                    # Max items per page (default: 20)
    "offset": 0,                    # Pagination offset
    "tags": ["billing"],            # Filter by tags
    "type": "observation",          # Filter by type
    "is_archived": False,           # Filter archived status
})

print(memories["memories"])         # Array of memories
print(memories["total"])            # Total count
print(memories["has_more"])         # More pages available
```

#### Get Memory by ID

```python
memory = client.memory.get("mem_123abc")
```

#### Update Memory (Partial)

```python
updated = client.memory.update("mem_123abc", {
    "tags": ["support", "billing", "resolved"],
    "metadata": {
        **memory.get("metadata", {}),
        "resolved": True,
    },
    "is_archived": True,
})
```

#### Replace Memory (Full)

```python
replaced = client.memory.put("mem_123abc", {
    "content": "Updated content here",  # Required for PUT
    "type": "observation",
    "tags": ["updated"],
})
```

#### Delete Memory

```python
client.memory.delete("mem_123abc")
```

#### Search Memories

```python
# Semantic search
semantic_results = client.memory.search({
    "query": "customer preferences about notifications",
    "limit": 10,
    "type": "preference",
})

# Filter-based search
filter_results = client.memory.search({
    "tags": ["settings", "notifications"],
    "from_date": "2024-01-01",
    "to_date": "2024-12-31",
    "limit": 20,
})
```

#### Batch Operations

```python
batch = client.memory.batch({
    "operations": [
        {
            "op": "create",
            "data": {
                "content": "First memory",
                "type": "journal",
            },
        },
        {
            "op": "update",
            "id": "mem_123abc",
            "data": {
                "tags": ["updated"],
            },
        },
        {
            "op": "delete",
            "id": "mem_456def",
        },
    ],
})

print(batch["results"])         # Individual operation results
print(batch["summary"])         # Summary statistics
```

### Thread Management

Associate memories with conversation threads:

```python
# Create a thread
thread = client.threads.create({
    "title": "Customer Support Session",
    "metadata": {"user_id": "user_123"}
})

# List threads
threads = client.threads.list({
    "limit": 10,
    "offset": 0
})

# Get thread by ID
thread = client.threads.get("thread_abc123")

# Update thread
updated_thread = client.threads.update("thread_abc123", {
    "title": "Resolved: Billing Issue",
    "metadata": {"status": "resolved"}
})

# Delete thread
client.threads.delete("thread_abc123")

# Link memory to thread
client.threads.link_memory("thread_abc123", "mem_123abc")

# Create memories within a thread
memory1 = client.memory.create({
    "content": "User asked about pricing",
    "type": "observation",
    "thread_id": "thread_abc123",
})

memory2 = client.memory.create({
    "content": "User selected enterprise plan",
    "type": "observation",
    "thread_id": "thread_abc123",
})

# List memories in a thread
thread_memories = client.memory.list({
    "thread_id": "thread_abc123",
})
```

### API Key Management

Manage API keys programmatically:

```python
# List all API keys
keys = client.keys.list()
print(keys)  # Array of key objects

# Create a new API key
new_key = client.keys.create({"name": "CI key"})
print(new_key["key"])  # The actual secret key (only shown once!)

# Update key metadata
client.keys.update(new_key["id"], {"name": "Production key"})

# Revoke a key
client.keys.revoke(new_key["id"])
```

## Memory Types

- **journal** - Chronological entries and logs
- **insight** - Derived patterns and conclusions
- **observation** - Factual, observed information
- **task** - Action items and todos
- **preference** - User preferences and settings

## Error Handling

The SDK provides typed errors for better error handling:

```python
from sovant import Sovant, SovantError, AuthError, RateLimitError, NetworkError, TimeoutError

try:
    memory = client.memory.get("invalid_id")
except AuthError as e:
    print(f"Authentication failed: {e}")
    # Handle authentication error
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Retry after: {e.retry_after}")
    # Handle rate limiting
except NetworkError as e:
    print(f"Network error: {e}")
    # Handle network issues
except TimeoutError as e:
    print(f"Request timed out: {e}")
    # Handle timeout
except SovantError as e:
    print(f"API Error: {e}")
    print(f"Status: {e.status}")
    print(f"Request ID: {e.request_id}")

    if e.status == 404:
        # Handle not found
        pass
    elif e.status == 400:
        # Handle bad request
        pass
```

## Advanced Features

### Retry Configuration

The SDK automatically retries failed requests with exponential backoff:

```python
client = Sovant(
    api_key="sk_live_...",
    max_retries=5,           # Increase retry attempts
    timeout=60.0,            # Increase timeout for slow connections
)
```

### Debug Mode

Enable debug logging to see detailed request/response information:

```python
client = Sovant(
    api_key="sk_live_...",
    debug=True,              # Enable debug output
)
```

### Custom Base URL

Connect to different environments:

```python
client = Sovant(
    api_key="sk_live_...",
    base_url="https://staging.sovant.ai",
)
```

## Best Practices

1. **Use appropriate memory types** - Choose the correct type for your use case
2. **Add meaningful tags** - Tags improve searchability and organization
3. **Use threads** - Group related memories together
4. **Handle errors gracefully** - Implement proper error handling
5. **Batch operations** - Use batch API for multiple operations
6. **Archive don't delete** - Consider archiving instead of deleting

## Examples

### Customer Support Integration

```python
# Track customer interaction
interaction = client.memory.create({
    "content": "Customer reported slow dashboard loading",
    "type": "observation",
    "thread_id": f"ticket_{ticket_id}",
    "tags": ["support", "performance", "dashboard"],
    "metadata": {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "priority": "high",
    },
})

# Record resolution
resolution = client.memory.create({
    "content": "Resolved by clearing cache and upgrading plan",
    "type": "insight",
    "thread_id": f"ticket_{ticket_id}",
    "tags": ["support", "resolved"],
    "metadata": {
        "ticket_id": ticket_id,
        "resolution_time": "2h",
    },
})
```

### User Preference Tracking

```python
# Store preference
preference = client.memory.create({
    "content": "User prefers email notifications over SMS",
    "type": "preference",
    "tags": ["notifications", "email", "settings"],
    "metadata": {
        "user_id": user_id,
        "setting": "notification_channel",
        "value": "email",
    },
})

# Query preferences
preferences = client.memory.search({
    "query": "notification preferences",
    "type": "preference",
    "tags": ["notifications"],
})
```

## Rate Limiting

The API implements rate limiting. The SDK automatically handles rate limit responses with retries. Rate limit headers are included in responses:

- `X-RateLimit-Limit` - Request limit per window
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

## Support

- Documentation: [https://sovant.ai/docs](https://sovant.ai/docs)
- API/Auth docs: [https://sovant.ai/docs/security/auth](https://sovant.ai/docs/security/auth)
- Issues: [GitHub Issues](https://github.com/sovant-ai/python-sdk/issues)
- Support: support@sovant.ai

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for a detailed history of changes.

## License & Use

- This SDK is MIT-licensed for integration convenience.
- The Sovant API and platform are proprietary to Sovant Technologies Sdn. Bhd.
- You may use this SDK to integrate with Sovant's hosted API.
- Hosting/redistributing the Sovant backend or any proprietary components is not permitted.

## License

MIT - See [LICENSE](LICENSE) file for details.