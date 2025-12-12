# Quickstart

Diese Anleitung zeigt Ihnen, wie Sie in wenigen Minuten mit `questra-authentication` loslegen können.

## 5-Minuten-Beispiel

### Service Account Authentifizierung

Das einfachste Szenario ist die Authentifizierung mit einem Service Account:

```python
from questra_authentication import QuestraAuthentication

# 1. Client initialisieren
client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password",
    oidc_discovery_paths=['/application/o/questra']
)

# 2. Access Token abrufen
access_token = client.get_access_token()

# 3. Token für API-Aufrufe verwenden
print(f"Token: {access_token[:20]}...")

# 4. Authentifizierungsstatus prüfen
if client.is_authenticated():
    print("Erfolgreich authentifiziert!")
```

### Interaktive Authentifizierung

Für Anwendungen, die Benutzereingaben erfordern:

```python
from questra_authentication import QuestraAuthentication

# 1. Client im interaktiven Modus initialisieren
client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    interactive=True,
    oidc_discovery_paths=['/application/o/questra']
)

# 2. Der Benutzer wird aufgefordert, im Browser zu autorisieren
# Eine URL wird angezeigt, die der Benutzer besuchen muss

# 3. Nach erfolgreicher Autorisierung kann das Token abgerufen werden
access_token = client.get_access_token()
```

## Integration in API-Clients

### Mit requests

Typische Integration mit der `requests`-Bibliothek:

```python
import requests
from questra_authentication import QuestraAuthentication

# Client initialisieren
auth_client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password"
)

# API-Anfrage mit Token
def make_api_request(endpoint: str):
    token = auth_client.get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.get(
        f"https://api.example.com{endpoint}",
        headers=headers
    )

    return response.json()

# Verwenden
data = make_api_request("/api/v1/users")
print(data)
```

### Mit httpx

Für asynchrone Anwendungen mit `httpx`:

```python
import httpx
from questra_authentication import QuestraAuthentication

# Client initialisieren
auth_client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password"
)

async def make_async_request(endpoint: str):
    token = auth_client.get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.example.com{endpoint}",
            headers=headers
        )
        return response.json()
```

### Mit GraphQL-Client (gql)

Integration mit einem GraphQL-Client:

```python
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from questra_authentication import QuestraAuthentication

# Authentication Client
auth_client = QuestraAuthentication(
    url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password"
)

# GraphQL Transport mit Auth Header
def get_auth_headers():
    return {
        "Authorization": f"Bearer {auth_client.get_access_token()}"
    }

transport = RequestsHTTPTransport(
    url="https://api.example.com/graphql",
    headers=get_auth_headers()
)

# GraphQL Client
graphql_client = Client(transport=transport, fetch_schema_from_transport=True)

# Query ausführen
query = gql("""
    query {
        users {
            id
            name
        }
    }
""")

result = graphql_client.execute(query)
print(result)
```

## Wiederverwendbarer Client

Für langlebige Anwendungen sollten Sie einen wiederverwendbaren Client erstellen:

```python
from questra_authentication import QuestraAuthentication
from typing import Optional

class APIClient:
    """Wiederverwendbarer API-Client mit automatischer Authentifizierung."""

    def __init__(
        self,
        api_base_url: str,
        auth_url: str,
        username: str,
        password: str
    ):
        self.api_base_url = api_base_url
        self._auth_client = QuestraAuthentication(
            url=auth_url,
            username=username,
            password=password
        )

    def _get_headers(self) -> dict:
        """Gibt Headers mit aktuellem Access Token zurück."""
        return {
            "Authorization": f"Bearer {self._auth_client.get_access_token()}",
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str) -> dict:
        """GET-Request mit automatischer Authentifizierung."""
        import requests
        response = requests.get(
            f"{self.api_base_url}{endpoint}",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """POST-Request mit automatischer Authentifizierung."""
        import requests
        response = requests.post(
            f"{self.api_base_url}{endpoint}",
            json=data,
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

# Verwenden
api = APIClient(
    api_base_url="https://api.example.com",
    auth_url="https://authentik.dev.example.com",
    username="ServiceUser",
    password="secret_password"
)

users = api.get("/api/v1/users")
new_user = api.post("/api/v1/users", {"name": "John Doe"})
```

## Umgebungsvariablen

Best Practice: Credentials in Umgebungsvariablen speichern:

```python
import os
from questra_authentication import QuestraAuthentication

client = QuestraAuthentication(
    url=os.getenv("QUESTRA_AUTH_URL"),
    username=os.getenv("QUESTRA_USERNAME"),
    password=os.getenv("QUESTRA_PASSWORD"),
    oidc_discovery_paths=['/application/o/questra']
)
```

Setzen Sie die Variablen in Ihrer Shell:

=== "Windows (PowerShell)"

    ```powershell
    $env:QUESTRA_AUTH_URL = "https://authentik.dev.example.com"
    $env:QUESTRA_USERNAME = "ServiceUser"
    $env:QUESTRA_PASSWORD = "secret_password"
    ```

=== "Linux/Mac"

    ```bash
    export QUESTRA_AUTH_URL="https://authentik.dev.example.com"
    export QUESTRA_USERNAME="ServiceUser"
    export QUESTRA_PASSWORD="secret_password"
    ```

=== ".env Datei"

    ```env
    QUESTRA_AUTH_URL=https://authentik.dev.example.com
    QUESTRA_USERNAME=ServiceUser
    QUESTRA_PASSWORD=secret_password
    ```

    Mit `python-dotenv`:

    ```python
    from dotenv import load_dotenv
    load_dotenv()
    ```

## Fehlerbehandlung

Grundlegende Fehlerbehandlung:

```python
from questra_authentication import (
    QuestraAuthentication,
    AuthenticationError,
    OidcDiscoveryError,
    InvalidCredentialsError
)

try:
    client = QuestraAuthentication(
        url="https://authentik.dev.example.com",
        username="ServiceUser",
        password="wrong_password"
    )
    token = client.get_access_token()

except OidcDiscoveryError as e:
    print(f"Fehler bei OIDC Discovery: {e}")
    print(f"Versuchte URLs: {e.urls}")

except InvalidCredentialsError:
    print("Ungültige Credentials. Bitte überprüfen Sie Username/Password.")

except AuthenticationError as e:
    print(f"Authentifizierung fehlgeschlagen: {e}")

except Exception as e:
    print(f"Unerwarteter Fehler: {e}")
```

## Nächste Schritte

- [Authentifizierungsmodi](authentication-modes.md) - Detaillierte Erklärung der verschiedenen Modi
- [Error Handling Guide](../guides/error-handling.md) - Umfassende Fehlerbehandlung
- [Best Practices](../guides/best-practices.md) - Empfehlungen für den produktiven Einsatz
- [API Referenz](../api/index.md) - Vollständige API-Dokumentation
