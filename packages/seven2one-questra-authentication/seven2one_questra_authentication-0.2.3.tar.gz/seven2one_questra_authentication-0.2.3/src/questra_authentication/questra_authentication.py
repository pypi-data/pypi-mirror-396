"""
QuestraAuthentication - Vereinfachte Schnittstelle für Questra API Authentifizierung
"""

from .authentication import (
    OAuth2Authentication,
    OAuth2InteractiveUserCredential,
    OAuth2ServiceCredential,
    OidcConfig,
    OidcDiscoveryClient,
)


class QuestraAuthentication:
    """
    Haupt-Client für Questra API Zugriff mit automatischer OAuth2 Authentifizierung.

    Unterstützt zwei Authentifizierungsmodi:
    1. Service Account (username/password)
    2. Interaktiver Benutzer (Device Code Flow)

    Das Access Token wird automatisch erneuert, wenn es abläuft.
    """

    def __init__(
        self,
        url: str | list[str],
        client_id: str = "Questra",
        username: str | None = None,
        password: str | None = None,
        interactive: bool = False,
        scope: str | None = None,
        oidc_discovery_paths: list[str] | None = None,
    ):
        """
        Initialisiert den QuestraAuthentication.

        Args:
            url: Basis-URL des Identity Providers oder Liste von URLs
            client_id: OAuth2 Client ID (Standard: "Questra")
            username: Benutzername für Service Account Authentifizierung
            password: Passwort für Service Account Authentifizierung
            interactive: True für interaktiven Device Code Flow,
                False für Service Account
            scope: Optionale OAuth2 Scopes
            oidc_discovery_paths: Optionale Liste von Discovery-Pfaden
                (z.B. ['/application/o/techstack', '/application/o/questra'])

        Examples:
            Service Account:
            ```python
            client = QuestraAuthentication(
                url="https://authentik.dev.example.com",
                username="ServiceUser",
                password="secret_password",
                oidc_discovery_paths=[
                    '/application/o/techstack',
                    '/application/o/questra'
                ]
            )
            ```

            Interaktiv:
            ```python
            client = QuestraAuthentication(
                url="https://authentik.dev.example.com",
                interactive=True,
                oidc_discovery_paths=[
                    '/application/o/techstack',
                    '/application/o/questra'
                ]
            )
            ```
        """
        self.url = url
        self.client_id = client_id
        self.username = username
        self.password = password
        self.interactive = interactive
        self.scope = scope or "offline_access"
        self.oidc_discovery_paths = oidc_discovery_paths or ["/application/o/questra"]

        self._oauth_client: OAuth2Authentication | None = None
        self._oidc_config: OidcConfig | None = None

        # Initialisiere OIDC Discovery und OAuth Client
        self._initialize()

    def _initialize(self):
        """Initialisiert OIDC Discovery und OAuth2 Client."""
        # OIDC Discovery
        discovery_urls = self._build_discovery_urls()
        oidc_discovery_client = OidcDiscoveryClient(discovery_urls)
        self._oidc_config = oidc_discovery_client.discover()

        # OAuth2 Credentials erstellen
        if self.interactive:
            credentials = OAuth2InteractiveUserCredential()
        else:
            if not self.username or not self.password:
                raise ValueError(
                    "Username und Password sind erforderlich für "
                    "Service Account Authentifizierung. "
                    "Verwenden Sie interactive=True für interaktiven Login."
                )
            credentials = OAuth2ServiceCredential(
                username=self.username, password=self.password
            )

        # OAuth2 Client erstellen
        self._oauth_client = OAuth2Authentication(
            client_id=self.client_id,
            credentials=credentials,
            oidc_config=self._oidc_config,
            scope=self.scope,
        )

        # Authentifizierung durchführen
        self._oauth_client.authenticate()

    def _build_discovery_urls(self) -> str | list[str]:
        """
        Erstellt Discovery URLs basierend auf Basis-URL und Discovery-Pfaden.

        Returns:
            str | list[str]: String oder Liste von Discovery URLs
        """
        if isinstance(self.url, list):
            # Mehrere URLs wurden übergeben
            if self.oidc_discovery_paths:
                # Kombiniere alle URLs mit allen Discovery-Pfaden
                urls = []
                for base_url in self.url:
                    for path in self.oidc_discovery_paths:
                        urls.append(f"{base_url.rstrip('/')}{path}")
                return urls
            else:
                return self.url
        else:
            # Einzelne URL
            if self.oidc_discovery_paths:
                return [
                    f"{self.url.rstrip('/')}{path}"
                    for path in self.oidc_discovery_paths
                ]
            else:
                return self.url

    def get_access_token(self) -> str:
        """
        Gibt ein gültiges Access Token zurück.

        Das Token wird automatisch erneuert, wenn es abgelaufen ist.
        Diese Methode sollte vor jeder API-Anfrage aufgerufen werden.

        Returns:
            str: Gültiges Access Token

        Raises:
            Exception: Wenn die Authentifizierung fehlgeschlagen ist
        """
        if not self._oauth_client:
            raise Exception("OAuth Client nicht initialisiert")

        return self._oauth_client.get_access_token()

    def get_oidc_config(self) -> OidcConfig:
        """
        Gibt die OIDC-Konfiguration zurück.

        Returns:
            OidcConfig: Objekt mit allen Endpunkten
        """
        if not self._oidc_config:
            raise Exception("OIDC Config nicht initialisiert")

        return self._oidc_config

    def is_authenticated(self) -> bool:
        """
        Prüft, ob der Client authentifiziert ist.

        Returns:
            True wenn authentifiziert, sonst False
        """
        return self._oauth_client is not None and self._oauth_client.authenticated

    def reauthenticate(self):
        """
        Erzwingt eine erneute Authentifizierung.

        Dies kann nützlich sein, wenn die Credentials geändert wurden
        oder bei Authentifizierungsproblemen.
        """
        if self._oauth_client:
            self._oauth_client.authenticate()
        else:
            self._initialize()
