"""
Integration Tests für QuestraAuthentication ohne Mocks.

Diese Tests prüfen die tatsächliche Integration zwischen den Komponenten,
um Probleme wie falsche Parameter-Namen zu erkennen.
"""

from unittest.mock import Mock, patch

from questra_authentication import QuestraAuthentication
from questra_authentication.authentication import (
    OAuth2ServiceCredential,
    OidcConfig,
)


class TestQuestraAuthenticationIntegration:
    """Integration Tests die echte Klassen ohne vollständige Mocks verwenden."""

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("requests.get")
    def test_init_creates_oauth2_authentication_with_correct_parameters(
        self,
        mock_requests_get,
        mock_session_class,
        mock_oidc_discovery_response,
        mock_token_response,
    ):
        """
        Test: QuestraAuthentication initialisiert OAuth2Authentication
        mit korrekten Parameter-Namen.

        Dieser Test verwendet die echte OAuth2Authentication-Klasse
        (nicht gemockt) um sicherzustellen, dass Parameter-Namen korrekt sind.
        """
        # Mock OIDC Discovery
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Mock OAuth2Session
        mock_session = Mock()
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        # Dies sollte ohne TypeError funktionieren
        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
        )

        # Prüfe dass OAuth2Authentication korrekt initialisiert wurde
        assert client._oauth_client is not None
        assert client._oauth_client.client_id == "Questra"
        assert isinstance(client._oauth_client.credentials, OAuth2ServiceCredential)
        assert isinstance(client._oauth_client.oidc_config, OidcConfig)

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("requests.get")
    def test_oauth2_authentication_parameter_name_validation(
        self,
        mock_requests_get,
        mock_session_class,
        mock_oidc_discovery_response,
        mock_token_response,
    ):
        """
        Test: OAuth2Authentication akzeptiert nur 'oidc_config', nicht 'oidcConfig'.

        Dies ist ein Regressions-Test für das CamelCase-Problem.
        """
        # Mock OIDC Discovery
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Mock OAuth2Session
        mock_session = Mock()
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        # Test sollte durchlaufen ohne TypeError
        try:
            client = QuestraAuthentication(
                url="https://test.example.com",
                username="testuser",
                password="testpass",
            )
            # Wenn wir hier ankommen, war die Initialisierung erfolgreich
            assert client._oauth_client is not None
        except TypeError as e:
            # Falls ein TypeError auftritt, sollte es NICHT "oidcConfig" erwähnen
            assert "oidcConfig" not in str(e), (
                "OAuth2Authentication wurde mit falschem Parameter-Namen aufgerufen: "
                f"{e}"
            )

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("requests.get")
    def test_full_authentication_flow(
        self,
        mock_requests_get,
        mock_session_class,
        mock_oidc_discovery_response,
        mock_token_response,
    ):
        """
        Test: Vollständiger Authentifizierungs-Flow von QuestraAuthentication
        bis OAuth2Authentication.
        """
        # Mock OIDC Discovery
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Mock OAuth2Session
        mock_session = Mock()
        mock_session.access_token = mock_token_response["access_token"]
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        # Initialisierung und Authentifizierung
        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
        )

        # Prüfe dass Authentifizierung erfolgreich war
        assert client.is_authenticated()
        assert client._oauth_client is not None
        assert client._oauth_client.authenticated

        # Token abrufen
        token = client.get_access_token()
        assert token == mock_token_response["access_token"]

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("requests.get")
    def test_oidc_config_passed_correctly(
        self,
        mock_requests_get,
        mock_session_class,
        mock_oidc_discovery_response,
        mock_token_response,
    ):
        """
        Test: OidcConfig wird korrekt von QuestraAuthentication
        zu OAuth2Authentication übergeben.
        """
        # Mock OIDC Discovery
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Mock OAuth2Session
        mock_session = Mock()
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        # Initialisierung
        client = QuestraAuthentication(
            url="https://test.example.com",
            username="testuser",
            password="testpass",
        )

        # Prüfe dass oidc_config korrekt übergeben wurde
        assert client._oauth_client is not None
        assert client._oauth_client.oidc_config is not None
        assert client._oauth_client.oidc_config == client._oidc_config
        assert (
            client._oauth_client.oidc_config.token_endpoint
            == mock_oidc_discovery_response["token_endpoint"]
        )

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("requests.get")
    def test_credentials_passed_correctly(
        self,
        mock_requests_get,
        mock_session_class,
        mock_oidc_discovery_response,
        mock_token_response,
    ):
        """
        Test: Credentials werden korrekt von QuestraAuthentication
        zu OAuth2Authentication übergeben.
        """
        # Mock OIDC Discovery
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_requests_get.return_value = mock_response

        # Mock OAuth2Session
        mock_session = Mock()
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        # Initialisierung mit spezifischen Credentials
        test_username = "integration_test_user"
        test_password = "integration_test_pass"

        client = QuestraAuthentication(
            url="https://test.example.com",
            username=test_username,
            password=test_password,
        )

        # Prüfe dass Credentials korrekt übergeben wurden
        assert client._oauth_client is not None
        assert isinstance(client._oauth_client.credentials, OAuth2ServiceCredential)
        assert client._oauth_client.credentials.username == test_username
        assert client._oauth_client.credentials.password == test_password
