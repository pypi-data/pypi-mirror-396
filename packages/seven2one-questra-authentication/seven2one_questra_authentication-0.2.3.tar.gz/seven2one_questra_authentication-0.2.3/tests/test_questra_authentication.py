"""
Unit Tests für QuestraAuthentication
"""

from unittest.mock import MagicMock, patch

import pytest

from questra_authentication import QuestraAuthentication
from questra_authentication.authentication import (
    OidcConfig,
)


class TestQuestraAuthentication:
    """Tests für QuestraAuthentication Klasse"""

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_init_with_service_credentials(
        self,
        mock_oauth_class,
        mock_discovery_class,
        mock_oidc_config,
        mock_oauth2_session,
    ):
        """Test: Initialisierung mit Service Account Credentials"""
        # Setup mocks
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
            oidc_discovery_paths=["/application/o/questra"],
        )

        assert client.url == "https://test.example.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert not client.interactive
        assert client.client_id == "Questra"
        mock_oauth.authenticate.assert_called_once()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_init_with_interactive_mode(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: Initialisierung mit interaktivem Modus"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            interactive=True,
            oidc_discovery_paths=["/application/o/questra"],
        )

        assert client.interactive
        assert client.username is None
        assert client.password is None
        mock_oauth.authenticate.assert_called_once()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_init_with_custom_client_id(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: Initialisierung mit benutzerdefinierter Client ID"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            client_id="CustomClient",
            username="testuser",
            password="testpass",
        )

        assert client.client_id == "CustomClient"

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_init_with_scope(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: Initialisierung mit OAuth Scope"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
            scope="openid profile email",
        )

        assert client.scope == "openid profile email"

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    def test_init_without_credentials_raises_error(
        self, mock_discovery_class, mock_oidc_config
    ):
        """Test: Initialisierung ohne Credentials schlägt fehl"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        with pytest.raises(ValueError, match="Username und Password sind erforderlich"):
            QuestraAuthentication(url="https://test.example.com")

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_get_access_token(
        self,
        mock_oauth_class,
        mock_discovery_class,
        mock_oidc_config,
        mock_token_response,
    ):
        """Test: get_access_token gibt Token zurück"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth.get_access_token.return_value = mock_token_response["access_token"]
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        token = client.get_access_token()

        assert token == mock_token_response["access_token"]
        mock_oauth.get_access_token.assert_called_once()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_get_access_token_without_oauth_client(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: get_access_token ohne OAuth Client schlägt fehl"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        client._oauth_client = None

        with pytest.raises(Exception, match="OAuth Client nicht initialisiert"):
            client.get_access_token()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_get_oidc_config(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: get_oidc_config gibt OidcConfig zurück"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        config = client.get_oidc_config()

        assert isinstance(config, OidcConfig)
        assert config == mock_oidc_config

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_get_oidc_config_without_config(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: get_oidc_config ohne Config schlägt fehl"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        client._oidc_config = None

        with pytest.raises(Exception, match="OIDC Config nicht initialisiert"):
            client.get_oidc_config()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_is_authenticated(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: is_authenticated gibt korrekten Status zurück"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        assert client.is_authenticated()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_is_authenticated_false(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: is_authenticated gibt False zurück wenn nicht authentifiziert"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = False
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        assert not client.is_authenticated()

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_reauthenticate(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: reauthenticate ruft authenticate erneut auf"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com", username="testuser", password="testpass"
        )

        # authenticate wurde bereits in __init__ aufgerufen
        initial_call_count = mock_oauth.authenticate.call_count

        client.reauthenticate()

        # authenticate sollte erneut aufgerufen worden sein
        assert mock_oauth.authenticate.call_count == initial_call_count + 1

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_build_discovery_urls_single_url_with_paths(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: _build_discovery_urls mit einzelner URL und Pfaden"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
            oidc_discovery_paths=["/path1", "/path2"],
        )

        urls = client._build_discovery_urls()

        assert isinstance(urls, list)
        assert "https://test.example.com/path1" in urls
        assert "https://test.example.com/path2" in urls

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_build_discovery_urls_multiple_urls_with_paths(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: _build_discovery_urls mit mehreren URLs und Pfaden"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url=["https://test1.example.com", "https://test2.example.com"],
            username="testuser",
            password="testpass",
            oidc_discovery_paths=["/path1", "/path2"],
        )

        urls = client._build_discovery_urls()

        assert isinstance(urls, list)
        assert len(urls) == 4  # 2 URLs * 2 Pfade
        assert "https://test1.example.com/path1" in urls
        assert "https://test1.example.com/path2" in urls
        assert "https://test2.example.com/path1" in urls
        assert "https://test2.example.com/path2" in urls

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_build_discovery_urls_single_url_without_paths(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: _build_discovery_urls mit einzelner URL ohne Pfade verwendet Default"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        # Wenn oidc_discovery_paths=None (nicht angegeben), wird Default verwendet
        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
            # oidc_discovery_paths nicht angegeben
            # -> Default: ['/application/o/questra']
        )

        urls = client._build_discovery_urls()

        # Mit Default-Pfad
        assert isinstance(urls, list)
        assert "https://test.example.com/application/o/questra" in urls

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_build_discovery_urls_multiple_urls_without_paths(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: _build_discovery_urls mit mehreren URLs ohne Pfade verwendet Default"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        urls_list = ["https://test1.example.com", "https://test2.example.com"]
        client = QuestraAuthentication(
            url=urls_list,
            username="testuser",
            password="testpass",
            # oidc_discovery_paths nicht angegeben
            # -> Default: ['/application/o/questra']
        )

        urls = client._build_discovery_urls()

        # Mit Default-Pfad für jede URL
        assert isinstance(urls, list)
        assert "https://test1.example.com/application/o/questra" in urls
        assert "https://test2.example.com/application/o/questra" in urls

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_build_discovery_urls_strips_trailing_slashes(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: _build_discovery_urls entfernt trailing slashes"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com/",
            username="testuser",
            password="testpass",
            oidc_discovery_paths=["/path1"],
        )

        urls = client._build_discovery_urls()

        assert "https://test.example.com/path1" in urls
        assert "https://test.example.com//path1" not in urls

    @patch("questra_authentication.questra_authentication.OidcDiscoveryClient")
    @patch("questra_authentication.questra_authentication.OAuth2Authentication")
    def test_default_oidc_discovery_paths(
        self, mock_oauth_class, mock_discovery_class, mock_oidc_config
    ):
        """Test: Standard OIDC Discovery Pfade werden verwendet"""
        mock_discovery = MagicMock()
        mock_discovery.discover.return_value = mock_oidc_config
        mock_discovery_class.return_value = mock_discovery

        mock_oauth = MagicMock()
        mock_oauth.authenticated = True
        mock_oauth_class.return_value = mock_oauth

        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
            # oidc_discovery_paths nicht angegeben
        )

        assert client.oidc_discovery_paths == ["/application/o/questra"]
