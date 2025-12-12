# Installation

Diese Seite beschreibt die Installation von `seven2one-questra-authentication` und die erforderlichen Voraussetzungen.

## Voraussetzungen

### Python Version

`seven2one-questra-authentication` benötigt Python 3.10 oder höher.

Überprüfen Sie Ihre Python-Version:

```bash
python --version
```

oder

```bash
python3 --version
```

Die Ausgabe sollte mindestens `Python 3.10.x` anzeigen.

### Abhängigkeiten

Die folgenden Abhängigkeiten werden automatisch installiert:

- `requests-oauthlib` >= 2.0.0

## Installation mit pip

Die einfachste Methode ist die Installation über pip:

```bash
pip install seven2one-questra-authentication
```

### In einer virtuellen Umgebung (empfohlen)

Es wird empfohlen, eine virtuelle Umgebung zu verwenden:

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Virtuelle Umgebung aktivieren
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Paket installieren
pip install questra-authentication
```

## Installation mit Poetry

Wenn Sie Poetry als Paketmanager verwenden:

```bash
poetry add seven2one-questra-authentication
```

### Poetry-Projekt neu erstellen

Falls Sie ein neues Projekt starten:

```bash
# Neues Projekt erstellen
poetry new mein-projekt
cd mein-projekt

# questra-authentication hinzufügen
poetry add seven2one-questra-authentication

# Abhängigkeiten installieren
poetry install
```

## Installation aus Source

### Von Azure DevOps

Wenn Sie die neueste Entwicklungsversion installieren möchten:

```bash
# Repository klonen
git clone https://dev.azure.com/seven2one/Seven2one.Questra/_git/S2O.Questra.Python.Authentication
cd S2O.Questra.Python.Authentication

# Mit poetry installieren
poetry install

# Oder mit pip
pip install -e .
```

### Für Entwicklung

Für Entwicklungsarbeiten mit allen zusätzlichen Tools:

```bash
# Repository klonen
git clone https://dev.azure.com/seven2one/Seven2one.Questra/_git/S2O.Questra.Python.Authentication
cd S2O.Questra.Python.Authentication

# Alle Dependencies installieren (inkl. Test und Docs)
poetry install --with test,docs

# Pre-commit Hooks installieren
poetry run pre-commit install
```

## Verifizierung der Installation

Nach der Installation können Sie überprüfen, ob das Paket korrekt installiert wurde:

```python
import questra_authentication

print(questra_authentication.__version__)
```

Oder direkt die Hauptklasse importieren:

```python
from questra_authentication import QuestraAuthentication

# Dies sollte ohne Fehler funktionieren
print(QuestraAuthentication)
```

## Häufige Probleme

### ModuleNotFoundError

Wenn Sie einen `ModuleNotFoundError` erhalten:

1. Stellen Sie sicher, dass Sie die richtige Python-Umgebung aktiviert haben
2. Überprüfen Sie, ob die Installation erfolgreich war: `pip list | grep questra`
3. Reinstallieren Sie das Paket: `pip install --force-reinstall seven2one-questra-authentication`

### Python-Version zu alt

Wenn Sie eine Fehlermeldung bezüglich der Python-Version erhalten:

```
ERROR: Package 'seven2one-questra-authentication' requires a different Python: 3.9.x not in '>=3.10'
```

Aktualisieren Sie auf Python 3.10 oder höher.

## Nächste Schritte

Nach der erfolgreichen Installation:

- [Quickstart](quickstart.md) - Erste Schritte mit dem Client
- [Authentifizierungsmodi](authentication-modes.md) - Verfügbare Authentifizierungsmethoden
- [API Referenz](../api/index.md) - Vollständige API-Dokumentation
