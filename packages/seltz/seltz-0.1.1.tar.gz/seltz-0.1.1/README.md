# Seltz Python SDK

The official Python SDK for the Seltz AI-powered search API.

## Installation

```bash
pip install seltz
```

## Quick Start

```python
from seltz import Seltz

# Initialize with API key
client = Seltz.create(api_key="your-api-key")

# Perform a search
response = client.search("your search query")

# Access results
for document in response.documents:
    print(f"URL: {document.url}")
    print(f"Content: {document.content}")
```

## API Key

Set your API key using one of these methods:

1. **Environment variable** (recommended):
   ```bash
   export SELTZ_API_KEY="your-api-key"
   ```

2. **Direct parameter**:
   ```python
   client = Seltz.create(api_key="your-api-key")
   ```

## API Reference

### `Seltz.create(api_key=None, endpoint="api.seltz.ai", insecure=False)`

Creates a new Seltz client instance.

**Parameters:**
- `api_key` (str, optional): API key for authentication. Defaults to `SELTZ_API_KEY` environment variable.
- `endpoint` (str): API endpoint. Defaults to "api.seltz.ai".
- `insecure` (bool): Use insecure connection. Defaults to False.

**Returns:** `Seltz` instance

### `client.search(text, max_documents=10)`

Performs a search query.

**Parameters:**
- `text` (str): The search query text.
- `max_documents` (int): Maximum number of documents to return. Defaults to 10.

**Returns:** `SearchResponse` with a `documents` field containing search results.

## Error Handling

```python
from seltz import (
    Seltz,
    SeltzConfigurationError,
    SeltzAuthenticationError,
    SeltzConnectionError,
    SeltzAPIError,
    SeltzTimeoutError,
    SeltzRateLimitError,
)

try:
    client = Seltz.create(api_key="your-api-key")
    response = client.search("query")
except SeltzConfigurationError as e:
    print(f"Configuration error: {e}")
except SeltzAuthenticationError as e:
    print(f"Authentication error: {e}")
except SeltzConnectionError as e:
    print(f"Connection error: {e}")
except SeltzTimeoutError as e:
    print(f"Timeout error: {e}")
except SeltzRateLimitError as e:
    print(f"Rate limit error: {e}")
except SeltzAPIError as e:
    print(f"API error: {e}")
```

## Requirements

- Python 3.8+
- grpcio >= 1.76.0
- protobuf >= 6.33.1