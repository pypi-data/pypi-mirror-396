# Questra Authentication Dokumentation

Diese Dokumentation wird mit [MkDocs](https://www.mkdocs.org/) und [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) generiert.

## Lokale Entwicklung

### Voraussetzungen

```bash
poetry install --with docs
```

### Dokumentation lokal ansehen

```bash
poetry run mkdocs serve
```

Die Dokumentation ist dann unter [http://127.0.0.1:8000](http://127.0.0.1:8000) verfügbar.

### Dokumentation bauen

```bash
poetry run mkdocs build
```

Die generierte Dokumentation befindet sich im Ordner `site/`.

## Struktur

```
docs/
├── index.md                    # Startseite
├── getting-started/            # Erste Schritte
│   ├── installation.md
│   ├── quickstart.md
│   └── authentication-modes.md
├── api/                        # API-Referenz (autogeneriert aus Docstrings)
│   ├── index.md
│   ├── client.md
│   ├── authentication.md
│   ├── credentials.md
│   ├── oidc-discovery.md
│   └── exceptions.md
├── guides/                     # Anleitungen
    ├── best-practices.md
    ├── error-handling.md
    └── token-management.md
```

## API-Dokumentation

Die API-Dokumentation wird **automatisch aus den Docstrings** im Code generiert mittels [mkdocstrings](https://mkdocstrings.github.io/).

### Docstring-Format

Wir verwenden **Google-Style Docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Kurzbeschreibung der Funktion.

    Ausführlichere Beschreibung falls notwendig.

    Args:
        param1: Beschreibung von param1
        param2: Beschreibung von param2

    Returns:
        Beschreibung des Rückgabewerts

    Raises:
        ValueError: Wann diese Exception geworfen wird

    Example:
        ```python
        result = example_function("test", 42)
        print(result)  # True
        ```
    """
    return True
```

### API-Dokumentation aktualisieren

Die API-Dokumentation wird automatisch beim Build aktualisiert. Sie müssen lediglich:

1. **Docstrings im Code aktualisieren** ([src/questra_authentication/](../src/questra_authentication/))
2. **Dokumentation neu bauen**: `poetry run mkdocs build`

**Keine manuellen Änderungen an API-Dateien notwendig!**

## Dokumentation deployen

### Option 1: GitHub Pages (wenn öffentlich)

```bash
poetry run mkdocs gh-deploy
```

### Option 2: Manuell

```bash
poetry run mkdocs build
# Kopiere site/ auf Webserver
```

### Option 3: Azure Static Web Apps

Siehe CI/CD Pipeline Konfiguration.

## Best Practices

### Docstrings pflegen

- Immer vollständige Docstrings für public APIs schreiben
- Examples in Docstrings einbauen
- Type Hints verwenden (werden automatisch angezeigt)

### Guides schreiben

- Kurze, prägnante Markdown-Dateien in `docs/guides/`
- Code-Beispiele mit Syntax-Highlighting
- Mermaid-Diagramme für Visualisierungen

## Plugins

Folgende MkDocs-Plugins werden verwendet:

- **mkdocstrings**: Automatische API-Dokumentation aus Docstrings
- **mkdocs-material**: Modernes Theme
- **mkdocs-git-revision-date-localized**: Automatische Zeitstempel
- **mkdocs-minify**: HTML/CSS/JS Minification
- **search**: Suchfunktion (integriert in Material)

## Weitere Ressourcen

- [MkDocs Dokumentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
