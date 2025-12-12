# Questra Authentication Tests

Umfassende Unit Tests für den questra-client, erstellt mit pytest.

## Struktur

```txt
tests/
├── __init__.py                  # Package Marker
├── conftest.py                  # Pytest Fixtures und Konfiguration
├── test_authentication.py       # Tests für OAuth2 Authentication
├── test_oidc_discovery.py      # Tests für OIDC Discovery Client
└── test_questra_client.py      # Tests für QuestraClient
```

## Voraussetzungen

Installiere die Test-Dependencies mit Poetry:

```bash
poetry install --with test
```

Optional: Installiere zusätzliche Test-Tools (Coverage, Mock):

```bash
poetry add --group test pytest-cov pytest-mock
```

## Tests ausführen

### Alle Tests ausführen

```bash
poetry run pytest
```

### Mit Coverage Report (wenn pytest-cov installiert ist)

```bash
poetry add --group dev pytest-cov
poetry run pytest --cov=src/questra_client --cov-report=html
```

### Spezifische Test-Dateien

```bash
poetry run pytest tests/test_questra_client.py
poetry run pytest tests/test_authentication.py
poetry run pytest tests/test_oidc_discovery.py
```

### Mit verbose Output

```bash
poetry run pytest -v
```

### Nur spezifische Tests

```bash
poetry run pytest tests/test_questra_client.py::TestQuestraClient::test_init_with_service_credentials
```

## Test Coverage

Die Tests decken folgende Bereiche ab:

### QuestraClient (`test_questra_client.py`)

- ✅ Initialisierung mit Service Account Credentials
- ✅ Initialisierung mit interaktivem Modus
- ✅ Custom Client ID und Scope
- ✅ Fehlerbehandlung bei fehlenden Credentials
- ✅ Access Token abrufen
- ✅ OIDC Config abrufen
- ✅ Authentifizierungsstatus prüfen
- ✅ Re-Authentifizierung
- ✅ Discovery URL Generierung (single/multiple URLs, mit/ohne Pfade)

### OAuth2 Authentication (`test_authentication.py`)

- ✅ Service Account Authentifizierung
- ✅ Interaktive Authentifizierung (Device Code Flow)
- ✅ Token Verwaltung und Refresh
- ✅ Token Ablauf-Prüfung
- ✅ Credential Validierung
- ✅ Fehlerbehandlung bei fehlgeschlagener Authentifizierung
- ✅ OAuth2 Session Management

### OIDC Discovery (`test_oidc_discovery.py`)

- ✅ OIDC Configuration erstellen
- ✅ Discovery mit einzelner URL
- ✅ Discovery mit mehreren URLs
- ✅ .well-known Fallback
- ✅ Fehlerbehandlung bei fehlgeschlagener Discovery
- ✅ Endpoint Extraktion

## Fixtures

Die `conftest.py` enthält wiederverwendbare Fixtures:

- `mock_oidc_config` - Mock OIDC Configuration
- `mock_oidc_discovery_response` - Mock Discovery Response
- `mock_token_response` - Mock OAuth2 Token Response
- `mock_expired_token_response` - Mock abgelaufener Token
- `mock_device_code_response` - Mock Device Code Response
- `service_credentials` - Test Credentials
- `mock_oauth2_session` - Mock OAuth2 Session
- `mock_requests_get` - Mock für HTTP GET Requests
- `mock_requests_post` - Mock für HTTP POST Requests

## Best Practices

1. **Isolation**: Jeder Test ist unabhängig und verwendet Mocks
2. **Naming**: Tests folgen dem Pattern `test_<was_wird_getestet>`
3. **Assertions**: Klare und spezifische Assertions
4. **Coverage**: Ziel ist >90% Code Coverage
5. **Dokumentation**: Jeder Test hat einen aussagekräftigen Docstring

## Marker

Tests können mit Markern kategorisiert werden:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Nur bestimmte Marker ausführen:

```bash
pytest -m unit
pytest -m "not slow"
```

## Troubleshooting

### Import Fehler

Stelle sicher, dass das Paket installiert ist:

```bash
poetry install
```

### Coverage nicht verfügbar

Installiere pytest-cov in der test Gruppe:

```bash
poetry add --group test pytest-cov
```

### Tests schlagen fehl

Prüfe und aktualisiere die Dependencies:

```bash
poetry install --with test
poetry update
```
