"""
Unit Tests für OAuth2 Authentication
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest
from oauthlib.oauth2 import OAuth2Error

from questra_authentication.authentication import (
    OAuth2Authentication,
    OAuth2Credential,
    OAuth2InteractiveUserCredential,
    OAuth2ServiceCredential,
)


class TestOAuth2Credentials:
    """Tests für OAuth2 Credential Klassen"""

    def test_create_service_credential(self):
        """Test: OAuth2ServiceCredential kann erstellt werden"""
        cred = OAuth2ServiceCredential(username="testuser", password="testpass")
        assert cred.username == "testuser"
        assert cred.password == "testpass"
        assert isinstance(cred, OAuth2Credential)

    def test_create_interactive_credential(self):
        """Test: OAuth2InteractiveUserCredential kann erstellt werden"""
        cred = OAuth2InteractiveUserCredential()
        assert isinstance(cred, OAuth2Credential)


class TestOAuth2Authentication:
    """Tests für OAuth2Authentication Klasse"""

    def test_init_with_service_credentials(self, mock_oidc_config):
        """Test: Initialisierung mit Service Credentials"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        assert auth.client_id == "test_client"
        assert auth.credentials == credentials
        assert auth.oidc_config == mock_oidc_config
        assert not auth.authenticated

    def test_init_with_interactive_credentials(self, mock_oidc_config):
        """Test: Initialisierung mit Interactive Credentials"""
        credentials = OAuth2InteractiveUserCredential()
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        assert auth.credentials == credentials
        assert not auth.authenticated

    def test_init_with_invalid_credentials(self, mock_oidc_config):
        """Test: Initialisierung mit ungültigen Credentials"""
        # Create a mock that doesn't implement OAuth2Credential interface
        invalid_credentials = Mock(spec=[])  # No methods

        # OAuth2Authentication akzeptiert jetzt alles im __init__,
        # aber authenticate() wird fehlschlagen
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=invalid_credentials,
            oidc_config=mock_oidc_config,
        )

        # authenticate() sollte fehlschlagen weil create_session fehlt
        with pytest.raises(AttributeError):
            auth.authenticate()

    def test_init_with_scope(self, mock_oidc_config):
        """Test: Initialisierung mit Scope"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
            scope="openid profile email",
        )

        assert auth.scope == "openid profile email"

    @patch("questra_authentication.authentication.OAuth2Session")
    def test_authenticate_service(
        self, mock_session_class, mock_oidc_config, mock_token_response
    ):
        """Test: Authentifizierung mit Service Credentials"""
        # Setup mock session
        mock_session = MagicMock()
        mock_session.authorized = True
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        auth.authenticate()

        assert auth.authenticated
        assert auth.session == mock_session
        mock_session.fetch_token.assert_called_once()

    @patch("questra_authentication.authentication.OAuth2Session")
    def test_authenticate_service_failure(
        self, mock_session_class, mock_oidc_config, mock_token_response
    ):
        """Test: Fehlgeschlagene Service Authentifizierung"""
        mock_session = MagicMock()
        # Simuliere Authentication-Fehler durch Exception
        mock_session.fetch_token.side_effect = OAuth2Error("invalid_grant")
        mock_session_class.return_value = mock_session

        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        with pytest.raises(OAuth2Error):
            auth.authenticate()

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("questra_authentication.authentication.requests.post")
    @patch("builtins.print")
    def test_authenticate_interactive(
        self,
        mock_print,
        mock_post,
        mock_session_class,
        mock_oidc_config,
        mock_token_response,
        mock_device_code_response,
    ):
        """Test: Interaktive Authentifizierung mit Device Code Flow"""
        # Setup device code response
        mock_device_response = Mock()
        mock_device_response.json.return_value = mock_device_code_response
        mock_post.return_value = mock_device_response

        # Setup session mock
        mock_session = MagicMock()
        mock_session.scope = None
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        credentials = OAuth2InteractiveUserCredential()
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        auth.authenticate()

        assert auth.authenticated
        mock_print.assert_called()
        mock_post.assert_called_once()

    def test_get_access_token_not_authenticated(self, mock_oidc_config):
        """Test: get_access_token ohne Authentifizierung schlägt fehl"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        with pytest.raises(Exception, match="Not authenticated"):
            auth.get_access_token()

    @patch("questra_authentication.authentication.OAuth2Session")
    def test_get_access_token_success(
        self, mock_session_class, mock_oidc_config, mock_token_response
    ):
        """Test: get_access_token gibt gültiges Token zurück"""
        mock_session = MagicMock()
        mock_session.authorized = True
        mock_session.access_token = mock_token_response["access_token"]
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )
        auth.authenticate()

        token = auth.get_access_token()

        assert token == mock_token_response["access_token"]

    def test_is_token_expired_not_expired(self, mock_oidc_config):
        """Test: Token ist nicht abgelaufen"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        # Token läuft in 2 Stunden ab
        auth.token_expires_at = datetime.now() + timedelta(hours=2)

        assert not auth._is_token_expired()

    def test_is_token_expired_expired(self, mock_oidc_config):
        """Test: Token ist abgelaufen"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        # Token ist vor 1 Stunde abgelaufen
        auth.token_expires_at = datetime.now() - timedelta(hours=1)

        assert auth._is_token_expired()

    def test_is_token_expired_within_minimum_lifetime(self, mock_oidc_config):
        """Test: Token innerhalb minimaler Lebensdauer gilt als abgelaufen"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        # Token läuft in 30 Sekunden ab (weniger als minimum)
        auth.token_expires_at = datetime.now() + timedelta(seconds=30)
        auth.minimum_token_lifetime_seconds = 60

        assert auth._is_token_expired()

    @patch("questra_authentication.authentication.OAuth2Session")
    def test_refresh_authentication_service(
        self, mock_session_class, mock_oidc_config, mock_token_response
    ):
        """Test: Token Refresh für Service Credentials"""
        mock_session = MagicMock()
        mock_session.authorized = True
        mock_session.access_token = "old_token"

        # Neue Token Response mit neuem Token
        new_token_response = mock_token_response.copy()
        new_token_response["access_token"] = "new_access_token"
        new_token_response["expires_at"] = (
            datetime.now() + timedelta(hours=2)
        ).timestamp()

        mock_session.fetch_token.return_value = new_token_response
        mock_session_class.return_value = mock_session

        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )
        auth.authenticate()

        # Simuliere abgelaufenes Token
        auth.token_expires_at = datetime.now() - timedelta(hours=1)

        # Hole neues Token
        auth.get_access_token()

        # fetch_token zweimal aufgerufen (authenticate, refresh)
        assert mock_session.fetch_token.call_count == 2

    @patch("questra_authentication.authentication.OAuth2Session")
    @patch("questra_authentication.authentication.requests.post")
    def test_refresh_authentication_interactive(
        self,
        mock_post,
        mock_session_class,
        mock_oidc_config,
        mock_token_response,
        mock_device_code_response,
    ):
        """Test: Token Refresh für Interactive Credentials"""
        # Setup device code mock
        mock_device_response = Mock()
        mock_device_response.json.return_value = mock_device_code_response
        mock_post.return_value = mock_device_response

        mock_session = MagicMock()
        mock_session.scope = None
        mock_session.access_token = "old_token"

        # Token Responses
        mock_session.fetch_token.return_value = mock_token_response
        new_token_response = mock_token_response.copy()
        new_token_response["access_token"] = "refreshed_token"
        new_token_response["expires_at"] = (
            datetime.now() + timedelta(hours=2)
        ).timestamp()
        mock_session.refresh_token.return_value = new_token_response

        mock_session_class.return_value = mock_session

        credentials = OAuth2InteractiveUserCredential()
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        with patch("builtins.print"):
            auth.authenticate()

        # Simuliere abgelaufenes Token
        auth.token_expires_at = datetime.now() - timedelta(hours=1)

        # Hole neues Token (sollte refresh_token aufrufen)
        auth.get_access_token()

        mock_session.refresh_token.assert_called_once()

    def test_process_token_response(self, mock_oidc_config, mock_token_response):
        """Test: Token Response wird korrekt verarbeitet"""
        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        auth._process_token_response(mock_token_response)

        assert isinstance(auth.token_expires_at, datetime)

    @patch("questra_authentication.authentication.OAuth2Session")
    def test_authenticate_sets_authenticated_flag(
        self, mock_session_class, mock_oidc_config, mock_token_response
    ):
        """Test: authenticate() setzt authenticated Flag"""
        mock_session = MagicMock()
        mock_session.authorized = True
        mock_session.fetch_token.return_value = mock_token_response
        mock_session_class.return_value = mock_session

        credentials = OAuth2ServiceCredential("testuser", "testpass")
        auth = OAuth2Authentication(
            client_id="test_client",
            credentials=credentials,
            oidc_config=mock_oidc_config,
        )

        assert not auth.authenticated
        auth.authenticate()
        assert auth.authenticated
