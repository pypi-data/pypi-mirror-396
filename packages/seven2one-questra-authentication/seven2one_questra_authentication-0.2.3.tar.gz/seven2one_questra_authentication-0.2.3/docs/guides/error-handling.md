# Error Handling

Umfassende Anleitung zur Fehlerbehandlung mit `seven2one-questra-authentication`.

## Exception-Hierarchie

```
QuestraAuthenticationError (Base)
├── AuthenticationError
│   ├── NotAuthenticatedError
│   ├── SessionNotInitializedError
│   ├── InvalidCredentialsError
│   └── TokenExpiredError
└── OidcDiscoveryError
```

## Grundlegende Fehlerbehandlung

### Initialisierungsfehler

```python
from questra_authentication import (
    QuestraAuthentication,
    OidcDiscoveryError,
    AuthenticationError
)

try:
    client = QuestraAuthentication(
        url="https://authentik.dev.example.com",
        username="ServiceUser",
        password="wrong_password"
    )
except OidcDiscoveryError as e:
    print(f"OIDC Discovery fehlgeschlagen")
    print(f"Versuchte URLs: {e.urls}")
    print(f"Original Error: {e.__cause__}")
except AuthenticationError as e:
    print(f"Authentifizierung fehlgeschlagen: {e}")
```

### Token-Abruf-Fehler

```python
from questra_authentication import NotAuthenticatedError, TokenExpiredError

try:
    token = client.get_access_token()
except NotAuthenticatedError:
    print("Client nicht authentifiziert")
    client.reauthenticate()
    token = client.get_access_token()
except TokenExpiredError:
    print("Token abgelaufen und nicht erneuerbar")
    client.reauthenticate()
    token = client.get_access_token()
```

## Exception-Details

### OidcDiscoveryError

Wird geworfen wenn OIDC Discovery fehlschlägt.

**Attribute:**

- `urls`: Liste der versuchten URLs
- `__cause__`: Original Exception

**Beispiel:**

```python
from questra_authentication import OidcDiscoveryError

try:
    client = QuestraAuthentication(
        url="https://invalid-url.example.com",
        username="user",
        password="pass"
    )
except OidcDiscoveryError as e:
    print(f"Discovery failed for URLs: {e.urls}")
    if e.__cause__:
        print(f"Reason: {e.__cause__}")
```

### AuthenticationError

Allgemeiner Authentifizierungsfehler.

**Verwendung:**

```python
from questra_authentication import AuthenticationError

try:
    client.reauthenticate()
except AuthenticationError as e:
    logging.error(f"Authentication failed: {e}")
    # Benachrichtige Admin, verwende Fallback, etc.
```

### NotAuthenticatedError

Client ist nicht authentifiziert.

**Ursachen:**

- `authenticate()` wurde noch nicht aufgerufen
- Authentifizierung ist fehlgeschlagen

**Lösung:**

```python
from questra_authentication import NotAuthenticatedError

try:
    token = client.get_access_token()
except NotAuthenticatedError:
    # Authentifiziere zuerst
    client.reauthenticate()
    token = client.get_access_token()
```

### TokenExpiredError

Token ist abgelaufen und kann nicht erneuert werden.

**Ursachen:**

- Refresh Token abgelaufen
- Refresh Token ungültig
- Server lehnt Refresh ab

**Lösung:**

```python
from questra_authentication import TokenExpiredError

try:
    token = client.get_access_token()
except TokenExpiredError:
    # Neu authentifizieren erforderlich
    client.reauthenticate()
    token = client.get_access_token()
```

### InvalidCredentialsError

Credentials sind ungültig.

**Ursachen:**

- Falsches Username/Password
- Account gesperrt
- Falscher Credential-Typ

**Lösung:**

```python
from questra_authentication import InvalidCredentialsError

try:
    client = QuestraAuthentication(
        url="...",
        username="wrong_user",
        password="wrong_pass"
    )
except InvalidCredentialsError:
    # Credentials prüfen
    logging.error("Invalid credentials provided")
    # Alternativen Credentials versuchen oder Fehler melden
```

## Retry-Strategien

### Einfacher Retry

```python
import time
from questra_authentication import AuthenticationError

MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    try:
        token = client.get_access_token()
        break
    except AuthenticationError as e:
        if attempt < MAX_RETRIES - 1:
            wait_time = 2 ** attempt  # Exponential Backoff
            logging.warning(f"Auth failed, retry {attempt + 1}/{MAX_RETRIES} in {wait_time}s")
            time.sleep(wait_time)
        else:
            logging.error(f"Auth failed after {MAX_RETRIES} attempts")
            raise
```

### Mit tenacity

```python
from tenacity import retry, stop_after_attempt, wait_exponential
from questra_authentication import AuthenticationError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def get_token_with_retry():
    return client.get_access_token()

try:
    token = get_token_with_retry()
except AuthenticationError as e:
    logging.error(f"Failed after retries: {e}")
```

## Produktionsreife Fehlerbehandlung

### Decorator für API-Calls

```python
from functools import wraps
from questra_authentication import AuthenticationError, NotAuthenticatedError

def with_auth_retry(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_client = kwargs.get('auth_client') or args[0]

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except NotAuthenticatedError:
                    if attempt < max_retries - 1:
                        auth_client.reauthenticate()
                    else:
                        raise
                except AuthenticationError as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)
            return None
        return wrapper
    return decorator

@with_auth_retry(max_retries=3)
def make_api_call(auth_client):
    token = auth_client.get_access_token()
    # ... API call
```

### Context Manager für Fehlerbehandlung

```python
from contextlib import contextmanager
from questra_authentication import AuthenticationError

@contextmanager
def auth_context(client):
    """Context Manager mit automatischem Error Handling."""
    try:
        yield client
    except AuthenticationError as e:
        logging.error(f"Authentication error: {e}")
        # Cleanup, Benachrichtigungen, etc.
        raise
    finally:
        # Optional: Cleanup
        pass

# Verwendung
with auth_context(client) as auth:
    token = auth.get_access_token()
    # ... API calls
```

## Logging Best Practices

### Strukturiertes Logging

```python
import logging
import json

logger = logging.getLogger(__name__)

class AuthErrorHandler:
    @staticmethod
    def handle_error(error: Exception, context: dict):
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': time.time()
        }

        if isinstance(error, OidcDiscoveryError):
            error_info['urls_tried'] = error.urls

        logger.error(json.dumps(error_info))

try:
    client = QuestraAuthentication(...)
except Exception as e:
    AuthErrorHandler.handle_error(e, {
        'url': url,
        'username': username,
        'interactive': False
    })
```

## Fallback-Strategien

### Graceful Degradation

```python
from questra_authentication import AuthenticationError

class APIClient:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self.cached_token = None

    def get_token(self):
        try:
            self.cached_token = self.auth_client.get_access_token()
            return self.cached_token
        except AuthenticationError:
            if self.cached_token:
                logging.warning("Using cached token due to auth error")
                return self.cached_token
            raise

    def make_request(self, endpoint):
        try:
            token = self.get_token()
            return self._request(endpoint, token)
        except AuthenticationError:
            # Fallback zu öffentlichen Daten oder cached Response
            return self._get_fallback_data(endpoint)
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class AuthCircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except AuthenticationError as e:
            self.on_failure()
            raise

    def on_success(self):
        self.failures = 0
        self.state = 'CLOSED'

    def on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = 'OPEN'

# Verwendung
circuit_breaker = AuthCircuitBreaker()

try:
    token = circuit_breaker.call(client.get_access_token)
except Exception as e:
    logging.error(f"Circuit breaker prevented call: {e}")
```

## Monitoring und Alerting

### Fehler-Metriken

```python
from prometheus_client import Counter

auth_errors = Counter(
    'auth_errors_total',
    'Total authentication errors',
    ['error_type']
)

try:
    token = client.get_access_token()
except AuthenticationError as e:
    auth_errors.labels(error_type=type(e).__name__).inc()
    raise
```

## Siehe auch

- [Best Practices](best-practices.md) - Produktions-Empfehlungen
- [API Exceptions](../api/exceptions.md) - Exception-Referenz
- [Token Management](token-management.md) - Token-Handling
