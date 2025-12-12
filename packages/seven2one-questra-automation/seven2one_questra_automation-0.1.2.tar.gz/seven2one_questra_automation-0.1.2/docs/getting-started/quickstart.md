# Quickstart

## Client initialisieren

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

## GraphQL Operations

Details siehe [API Referenz](../api/index.md).
