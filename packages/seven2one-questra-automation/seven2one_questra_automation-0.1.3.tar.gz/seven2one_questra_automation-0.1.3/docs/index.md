# Questra Automation

Python Client für die Questra Automation GraphQL API.

## Installation

```bash
pip install seven2one-questra-automation
```

## Quickstart

```python
from questra_automation import QuestraAutomationClient
from questra_authentication import QuestraAuthentication

auth = QuestraAuthentication(
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

client = QuestraAutomationClient(
    base_url="https://your-questra-instance.com",
    auth_client=auth
)
```

## Links

- [Installation](getting-started/installation.md)
- [Quickstart](getting-started/quickstart.md)
- [API Referenz](api/index.md)
