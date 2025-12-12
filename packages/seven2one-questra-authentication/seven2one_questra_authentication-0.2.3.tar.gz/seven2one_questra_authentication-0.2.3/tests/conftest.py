"""
Pytest fixtures und Konfiguration für questra-authentication Tests
"""

import json
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest

from questra_authentication.authentication import OidcConfig


@pytest.fixture
def mock_oidc_config() -> OidcConfig:
    """Erstellt eine Mock OIDC Configuration"""
    return OidcConfig(
        issuer="https://test.example.com",
        authorization_endpoint="https://test.example.com/authorize",
        token_endpoint="https://test.example.com/token",
        userinfo_endpoint="https://test.example.com/userinfo",
        end_session_endpoint="https://test.example.com/logout",
        device_authorization_endpoint="https://test.example.com/device",
    )


@pytest.fixture
def mock_oidc_discovery_response() -> dict[str, str]:
    """Mock response für OIDC Discovery"""
    return {
        "issuer": "https://test.example.com",
        "authorization_endpoint": "https://test.example.com/authorize",
        "token_endpoint": "https://test.example.com/token",
        "userinfo_endpoint": "https://test.example.com/userinfo",
        "end_session_endpoint": "https://test.example.com/logout",
        "device_authorization_endpoint": "https://test.example.com/device",
    }


@pytest.fixture
def mock_token_response() -> dict[str, Any]:
    """Mock OAuth2 Token Response"""
    expires_at = (datetime.now() + timedelta(hours=1)).timestamp()
    return {
        "access_token": "test_access_token_12345",
        "token_type": "Bearer",
        "expires_in": 3600,
        "expires_at": expires_at,
        "refresh_token": "test_refresh_token_67890",
    }


@pytest.fixture
def mock_expired_token_response() -> dict[str, Any]:
    """Mock abgelaufener OAuth2 Token Response"""
    expires_at = (datetime.now() - timedelta(hours=1)).timestamp()
    return {
        "access_token": "expired_access_token",
        "token_type": "Bearer",
        "expires_in": 0,
        "expires_at": expires_at,
        "refresh_token": "test_refresh_token",
    }


@pytest.fixture
def mock_device_code_response() -> dict[str, Any]:
    """Mock Device Code Response für interaktive Authentifizierung"""
    return {
        "device_code": "test_device_code_123",
        "user_code": "ABCD-EFGH",
        "verification_uri": "https://test.example.com/device",
        "verification_uri_complete": "https://test.example.com/device?user_code=ABCD-EFGH",
        "expires_in": 600,
        "interval": 5,
    }


@pytest.fixture
def service_credentials() -> dict[str, str]:
    """Service Account Credentials für Tests"""
    return {"username": "test_service_user", "password": "test_service_password"}


@pytest.fixture
def mock_oauth2_session(mock_token_response: dict[str, Any]) -> MagicMock:
    """Mock OAuth2Session"""
    session = MagicMock()
    session.authorized = True
    session.access_token = mock_token_response["access_token"]
    session.token = mock_token_response
    session.fetch_token.return_value = mock_token_response
    session.refresh_token.return_value = mock_token_response
    return session


@pytest.fixture
def mock_requests_get(
    monkeypatch: pytest.MonkeyPatch, mock_oidc_discovery_response: dict[str, str]
) -> Mock:
    """Mock für requests.get für OIDC Discovery"""
    mock_response = Mock()
    mock_response.json.return_value = mock_oidc_discovery_response
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    mock_get = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.get", mock_get)
    return mock_get


@pytest.fixture
def mock_requests_post(
    monkeypatch: pytest.MonkeyPatch, mock_device_code_response: dict[str, Any]
) -> Mock:
    """Mock für requests.post für Device Code Flow"""
    mock_response = Mock()
    mock_response.text = json.dumps(mock_device_code_response)
    mock_response.json.return_value = mock_device_code_response
    mock_response.status_code = 200

    mock_post = Mock(return_value=mock_response)
    monkeypatch.setattr("requests.request", mock_post)
    return mock_post
