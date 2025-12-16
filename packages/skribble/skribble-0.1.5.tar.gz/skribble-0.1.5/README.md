# Skribble SDK

A production-ready Python SDK for the **Skribble API v2**, generated from the official
Skribble Postman collection.

## Features

- Authentication via `/v2/access/login`
- Redis-based JWT access token caching (default TTL: 20 minutes, per Skribble docs)
- High-level clients for:
  - SignatureRequests
  - Documents
  - Seal
  - Send-to
  - User
  - Report (activities)
  - Monitoring (callbacks & system health)

## Installation

```bash
pip install skribble
```

## Usage
```python
import redis
from skribble import SkribbleClient

r = redis.Redis(host="localhost", port=6379, db=0)

client = SkribbleClient(
    username="api_demo_your_name",
    api_key="your_api_key",
    redis_client=r,
)

# Upload a document
doc = client.documents.upload(
    title="Example contract PDF",
    content="<BASE64_PDF>",
)

# Create a signature request using that document
sr = client.signature_requests.create(
    title="Example contract",
    signatures=[{"account_email": "john.doe@skribble.com"}],
    document_id=doc["id"],
)

# List signature requests
srs = client.signature_requests.list(page_size=50)
```
