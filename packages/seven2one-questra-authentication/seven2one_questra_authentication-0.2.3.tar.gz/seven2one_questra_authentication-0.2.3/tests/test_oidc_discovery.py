"""
Unit Tests für OIDC Discovery Client
"""

from unittest.mock import Mock, patch

import pytest

from questra_authentication.authentication import OidcConfig, OidcDiscoveryClient
from questra_authentication.exceptions import OidcDiscoveryError


class TestOidcConfig:
    """Tests für OidcConfig Klasse"""

    def test_create_oidc_config(self):
        """Test: OidcConfig kann erstellt werden"""
        config = OidcConfig(
            issuer="https://test.example.com",
            authorization_endpoint="https://test.example.com/authorize",
            token_endpoint="https://test.example.com/token",
            userinfo_endpoint="https://test.example.com/userinfo",
            end_session_endpoint="https://test.example.com/logout",
            device_authorization_endpoint="https://test.example.com/device",
        )

        assert config.issuer == "https://test.example.com"
        assert config.authorization_endpoint == "https://test.example.com/authorize"
        assert config.token_endpoint == "https://test.example.com/token"
        assert config.userinfo_endpoint == "https://test.example.com/userinfo"
        assert config.end_session_endpoint == "https://test.example.com/logout"
        assert config.device_authorization_endpoint == "https://test.example.com/device"

    def test_to_dict(self, mock_oidc_config):
        """Test: OidcConfig.to_dict() gibt Dictionary zurück"""
        config_dict = mock_oidc_config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["issuer"] == "https://test.example.com"
        assert config_dict["token_endpoint"] == "https://test.example.com/token"

    def test_to_json(self, mock_oidc_config):
        """Test: OidcConfig.to_json() gibt JSON String zurück"""
        config_json = mock_oidc_config.to_json()

        assert isinstance(config_json, str)
        assert "https://test.example.com" in config_json


class TestOidcDiscoveryClient:
    """Tests für OidcDiscoveryClient"""

    def test_init_with_string_url(self):
        """Test: Initialisierung mit einzelner URL"""
        client = OidcDiscoveryClient("https://test.example.com")
        assert client.base_url == "https://test.example.com"

    def test_init_with_list_of_urls(self):
        """Test: Initialisierung mit Liste von URLs"""
        urls = ["https://test1.example.com", "https://test2.example.com"]
        client = OidcDiscoveryClient(urls)
        assert client.base_url == urls

    @patch("requests.get")
    def test_discover_with_direct_url(self, mock_get, mock_oidc_discovery_response):
        """Test: Discovery mit direkter URL funktioniert"""
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OidcDiscoveryClient("https://test.example.com")
        config = client.discover()

        assert isinstance(config, OidcConfig)
        assert config.issuer == "https://test.example.com"
        mock_get.assert_called_once_with("https://test.example.com")

    @patch("requests.get")
    def test_discover_with_wellknown_fallback(
        self, mock_get, mock_oidc_discovery_response
    ):
        """Test: Discovery mit .well-known Fallback"""
        # Erste Anfrage schlägt fehl
        mock_get.side_effect = [
            Exception("Not found"),
            Mock(
                json=lambda: mock_oidc_discovery_response, raise_for_status=lambda: None
            ),
        ]

        client = OidcDiscoveryClient("https://test.example.com")
        config = client.discover()

        assert isinstance(config, OidcConfig)
        assert mock_get.call_count == 2

    @patch("requests.get")
    def test_discover_with_list_tries_all_urls(
        self, mock_get, mock_oidc_discovery_response
    ):
        """Test: Discovery mit Liste probiert alle URLs"""
        # Erste URL schlägt fehl, zweite funktioniert
        mock_get.side_effect = [
            Exception("Not found"),
            Exception("Not found"),
            Mock(
                json=lambda: mock_oidc_discovery_response, raise_for_status=lambda: None
            ),
        ]

        urls = ["https://test1.example.com", "https://test2.example.com"]
        client = OidcDiscoveryClient(urls)
        config = client.discover()

        assert isinstance(config, OidcConfig)
        assert mock_get.call_count >= 2

    @patch("requests.get")
    def test_discover_fails_when_no_valid_url(self, mock_get):
        """Test: Discovery schlägt fehl wenn keine URL funktioniert"""
        mock_get.side_effect = Exception("Not found")

        client = OidcDiscoveryClient("https://test.example.com")

        with pytest.raises(Exception, match="OIDC discovery failed"):
            client.discover()

    @patch("requests.get")
    def test_discover_fails_with_list_when_all_urls_fail(self, mock_get):
        """Test: Discovery mit Liste schlägt fehl wenn alle URLs fehlschlagen"""
        mock_get.side_effect = Exception("Not found")

        urls = ["https://test1.example.com", "https://test2.example.com"]
        client = OidcDiscoveryClient(urls)

        with pytest.raises(OidcDiscoveryError, match="No valid configuration found"):
            client.discover()

    @patch("requests.get")
    def test_fetch_raises_http_error(self, mock_get):
        """Test: _fetch gibt HTTP Fehler weiter"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_get.return_value = mock_response

        client = OidcDiscoveryClient("https://test.example.com")

        with pytest.raises(Exception):
            client._fetch("https://test.example.com")

    @patch("requests.get")
    def test_discover_extracts_all_endpoints(
        self, mock_get, mock_oidc_discovery_response
    ):
        """Test: Discovery extrahiert alle Endpoints korrekt"""
        mock_response = Mock()
        mock_response.json.return_value = mock_oidc_discovery_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OidcDiscoveryClient("https://test.example.com")
        config = client.discover()

        assert config.issuer == mock_oidc_discovery_response["issuer"]
        assert (
            config.authorization_endpoint
            == mock_oidc_discovery_response["authorization_endpoint"]
        )
        assert config.token_endpoint == mock_oidc_discovery_response["token_endpoint"]
        assert (
            config.userinfo_endpoint
            == mock_oidc_discovery_response["userinfo_endpoint"]
        )
        assert (
            config.end_session_endpoint
            == mock_oidc_discovery_response["end_session_endpoint"]
        )
        assert (
            config.device_authorization_endpoint
            == mock_oidc_discovery_response["device_authorization_endpoint"]
        )

    @patch("requests.get")
    def test_discover_fails_with_missing_required_fields(self, mock_get):
        """Test: Discovery schlägt fehl wenn erforderliche Felder fehlen"""
        # Response mit fehlendem token_endpoint
        incomplete_response = {
            "issuer": "https://test.example.com",
            "authorization_endpoint": "https://test.example.com/authorize",
            # token_endpoint fehlt!
            "userinfo_endpoint": "https://test.example.com/userinfo",
            "end_session_endpoint": "https://test.example.com/logout",
            "device_authorization_endpoint": "https://test.example.com/device",
        }

        mock_response = Mock()
        mock_response.json.return_value = incomplete_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = OidcDiscoveryClient("https://test.example.com")

        with pytest.raises(OidcDiscoveryError, match="missing required fields"):
            client.discover()
