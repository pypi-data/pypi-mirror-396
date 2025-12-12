# Best Practices

Empfehlungen für den produktiven Einsatz von `seven2one-questra-authentication`.

## Credential-Management

### Niemals Credentials im Code

❌ **Falsch:**

```python
client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",  # Hardcoded!
    password="SuperSecret123"  # Hardcoded!
)
```

✅ **Richtig:**

```python
import os

client = QuestraAuthentication(
    url=os.getenv("QUESTRA_AUTH_URL"),
    username=os.getenv("QUESTRA_USERNAME"),
    password=os.getenv("QUESTRA_PASSWORD")
)
```

### Secret Management nutzen

Für produktive Systeme: Azure Key Vault, HashiCorp Vault, AWS Secrets Manager

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://my-vault.vault.azure.net/",
    credential=credential
)

auth = QuestraAuthentication(
    url=os.getenv("QUESTRA_AUTH_URL"),
    username=client.get_secret("service-username").value,
    password=client.get_secret("service-password").value
)
```

## Client-Instanziierung

### Wiederverwendung von Instanzen

✅ **Richtig:** Client einmal erstellen und wiederverwenden

```python
# Beim Application-Start
auth_client = QuestraAuthentication(...)

# In allen Requests wiederverwenden
def make_api_call():
    token = auth_client.get_access_token()
    # ... API-Aufruf
```

❌ **Falsch:** Client bei jedem Request neu erstellen

```python
def make_api_call():
    auth_client = QuestraAuthentication(...)  # Ineffizient!
    token = auth_client.get_access_token()
```

### Singleton-Pattern für globalen Zugriff

```python
class AuthClient:
    _instance = None

    @classmethod
    def get_instance(cls) -> QuestraAuthentication:
        if cls._instance is None:
            cls._instance = QuestraAuthentication(
                url=os.getenv("QUESTRA_AUTH_URL"),
                username=os.getenv("QUESTRA_USERNAME"),
                password=os.getenv("QUESTRA_PASSWORD")
            )
        return cls._instance

# Verwendung
auth = AuthClient.get_instance()
token = auth.get_access_token()
```

## Error Handling

### Spezifische Exceptions fangen

✅ **Richtig:**

```python
from questra_authentication import (
    QuestraAuthentication,
    OidcDiscoveryError,
    AuthenticationError,
    NotAuthenticatedError
)

try:
    client = QuestraAuthentication(...)
except OidcDiscoveryError as e:
    logger.error(f"OIDC Discovery failed: {e.urls}")
    # Fallback-Logik
except AuthenticationError as e:
    logger.error(f"Authentication failed: {e}")
    # Error Handling
```

❌ **Falsch:**

```python
try:
    client = QuestraAuthentication(...)
except Exception as e:  # Zu generisch!
    print(f"Error: {e}")
```

## Logging

### Strukturiertes Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# questra_authentication verwendet eigenen Logger
logging.getLogger('questra_authentication').setLevel(logging.DEBUG)
```

### Custom Logger

```python
import logging

logger = logging.getLogger(__name__)

try:
    client = QuestraAuthentication(...)
    logger.info("Authentication client initialized successfully")
except AuthenticationError as e:
    logger.error(f"Failed to initialize auth client: {e}", exc_info=True)
```

## Performance

### Token Caching

Tokens werden automatisch gecacht und nur bei Bedarf erneuert:

```python
# Efficient - Token wird nur einmal geholt und gecacht
for i in range(100):
    token = client.get_access_token()  # Nur erste Iteration holt neuen Token
```

### Minimale Token-Lifetime anpassen

```python
from questra_authentication import OAuth2Authentication

# Für High-Frequency-Requests: Token früher erneuern
oauth_client = OAuth2Authentication(
    client_id="Questra",
    credentials=credentials,
    oidc_config=oidc_config,
    minimum_token_lifetime_seconds=300  # 5 Minuten vor Ablauf erneuern
)
```

## Multi-Threading

### Separate Instanzen pro Thread

```python
import threading
from questra_authentication import QuestraAuthentication

def worker(thread_id: int):
    # Eigene Instanz pro Thread
    client = QuestraAuthentication(
        url=os.getenv("QUESTRA_AUTH_URL"),
        username=os.getenv("QUESTRA_USERNAME"),
        password=os.getenv("QUESTRA_PASSWORD")
    )

    for _ in range(10):
        token = client.get_access_token()
        # ... API-Aufrufe

threads = [
    threading.Thread(target=worker, args=(i,))
    for i in range(5)
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

## Testing

### Mocking für Unit-Tests

```python
from unittest.mock import Mock, patch
from questra_authentication import QuestraAuthentication

def test_api_call():
    # Mock den Auth-Client
    mock_auth = Mock(spec=QuestraAuthentication)
    mock_auth.get_access_token.return_value = "fake_token"

    # Testen Sie Ihre API-Logik mit dem Mock
    token = mock_auth.get_access_token()
    assert token == "fake_token"
```

### Integration-Tests mit echtem Auth

```python
import pytest
from questra_authentication import QuestraAuthentication

@pytest.fixture(scope="session")
def auth_client():
    """Shared auth client für alle Tests."""
    return QuestraAuthentication(
        url=pytest.config.getoption("--auth-url"),
        username=pytest.config.getoption("--username"),
        password=pytest.config.getoption("--password")
    )

def test_authentication(auth_client):
    token = auth_client.get_access_token()
    assert token is not None
    assert len(token) > 0
```

## Deployment

### Health-Checks

```python
from questra_authentication import QuestraAuthentication

def health_check() -> bool:
    """Prüft ob Authentifizierung funktioniert."""
    try:
        client = QuestraAuthentication(...)
        return client.is_authenticated()
    except Exception:
        return False
```

### Graceful Degradation

```python
from questra_authentication import AuthenticationError

def make_api_call_with_fallback():
    try:
        token = auth_client.get_access_token()
        return call_api_with_token(token)
    except AuthenticationError:
        # Fallback zu cached Daten oder Default-Response
        return get_cached_data()
```

## Monitoring

### Metriken sammeln

```python
import time
from prometheus_client import Counter, Histogram

auth_requests = Counter('auth_requests_total', 'Total auth requests')
auth_duration = Histogram('auth_duration_seconds', 'Auth request duration')

@auth_duration.time()
def get_token():
    auth_requests.inc()
    return auth_client.get_access_token()
```

## Security

### Least Privilege

✅ Verwenden Sie Service Accounts mit minimalen Berechtigungen

✅ Separate Accounts für verschiedene Services

✅ Regelmäßige Rotation von Credentials

### Audit Logging

```python
import logging

audit_logger = logging.getLogger('audit')

def get_authenticated_token(user_context: dict):
    token = auth_client.get_access_token()
    audit_logger.info(
        "Token retrieved",
        extra={
            'user': user_context.get('user_id'),
            'ip': user_context.get('ip_address'),
            'timestamp': time.time()
        }
    )
    return token
```

## Siehe auch

- [Error Handling](error-handling.md) - Fehlerbehandlung
- [Token Management](token-management.md) - Token-Details
- [API Referenz](../api/index.md) - Vollständige API-Dokumentation
