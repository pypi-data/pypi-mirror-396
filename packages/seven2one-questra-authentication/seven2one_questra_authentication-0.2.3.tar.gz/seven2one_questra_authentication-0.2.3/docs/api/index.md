# API Referenz

Vollständige API-Dokumentation für `seven2one-questra-authentication`.

## Module-Übersicht

Das Paket ist in folgende Hauptmodule unterteilt:

### Hauptschnittstelle

- **[QuestraAuthentication](questra-authentication.md)** - Vereinfachte High-Level API für Questra-Integration

### OAuth2 Authentifizierung

- **[OAuth2Authentication](authentication.md)** - Low-Level OAuth2-Client und Credential-Strategien

### Fehlerbehandlung

- **[Exceptions](exceptions.md)** - Exception-Hierarchie

## Schnellreferenz

### Klassen

| Klasse | Modul | Beschreibung |
|--------|-------|--------------|
| `QuestraAuthentication` | `questra_authentication` | Hauptschnittstelle für Authentifizierung |
| `OAuth2Authentication` | `questra_authentication.authentication` | OAuth2-Client-Implementierung |
| `OAuth2ServiceCredential` | `questra_authentication.authentication` | Service Account Credentials |
| `OAuth2InteractiveUserCredential` | `questra_authentication.authentication` | Interactive User Credentials |
| `OidcDiscoveryClient` | `questra_authentication.authentication` | OIDC Discovery Client |
| `OidcConfig` | `questra_authentication.authentication` | OIDC Konfiguration (Dataclass) |

### Exceptions

| Exception | Beschreibung |
|-----------|--------------|
| `QuestraAuthenticationError` | Basis-Exception für alle Fehler |
| `AuthenticationError` | Allgemeiner Authentifizierungsfehler |
| `NotAuthenticatedError` | Client nicht authentifiziert |
| `SessionNotInitializedError` | OAuth2-Session nicht initialisiert |
| `InvalidCredentialsError` | Ungültige Credentials |
| `TokenExpiredError` | Token abgelaufen und nicht erneuerbar |
| `OidcDiscoveryError` | OIDC Discovery fehlgeschlagen |

## Import-Beispiele

### Haupt-API

```python
from questra_authentication import QuestraAuthentication

client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password"
)
```

### Low-Level API

```python
from questra_authentication import (
    OAuth2Authentication,
    OAuth2ServiceCredential,
    OidcDiscoveryClient
)

# Discovery
discovery_client = OidcDiscoveryClient(url="...")
oidc_config = discovery_client.discover()

# Credentials
credentials = OAuth2ServiceCredential(username="...", password="...")

# OAuth2 Client
oauth_client = OAuth2Authentication(
    client_id="Questra",
    credentials=credentials,
    oidc_config=oidc_config
)
```

### Exception Handling

```python
from questra_authentication import (
    QuestraAuthentication,
    AuthenticationError,
    OidcDiscoveryError,
    InvalidCredentialsError
)

try:
    client = QuestraAuthentication(...)
except OidcDiscoveryError as e:
    print(f"Discovery failed: {e.urls}")
except InvalidCredentialsError:
    print("Invalid credentials")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
```

## Typ-Annotationen

Alle öffentlichen APIs verfügen über vollständige Type Hints für bessere IDE-Unterstützung:

```python
from typing import Optional, List
from questra_authentication import QuestraAuthentication, OidcConfig

def create_client(
    url: str,
    username: Optional[str] = None,
    password: Optional[str] = None
) -> QuestraAuthentication:
    return QuestraAuthentication(
        url=url,
        username=username,
        password=password
    )

def get_config(client: QuestraAuthentication) -> OidcConfig:
    return client.get_oidc_config()
```

## Protokolle und Interfaces

### ClientInterface

Alle Credential-Klassen implementieren das `ClientInterface` Protokoll:

```python
from questra_authentication import ClientInterface
from oauthlib.oauth2 import Client

class CustomCredential(ClientInterface):
    """Custom credential implementation."""

    def get_client(
        self,
        client_id: str,
        oidc_config: OidcConfig,
        scope: Optional[str] = None
    ) -> Client:
        # Implementation
        ...
```

## Detaillierte Dokumentation

Für detaillierte Informationen zu jedem Modul, siehe die entsprechenden Seiten:

- **[QuestraAuthentication](questra-authentication.md)** - Hauptschnittstelle
- **[OAuth2 Authentifizierung](authentication.md)** - OAuth2-Details und Credential-Typen
- **[Exceptions](exceptions.md)** - Fehlerbehandlung
