import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import requests
from oauthlib.oauth2 import BackendApplicationClient, DeviceClient, OAuth2Error
from requests_oauthlib import OAuth2Session

from .exceptions import (
    AuthenticationError,
    NotAuthenticatedError,
    OidcDiscoveryError,
    SessionNotInitializedError,
)

logger = logging.getLogger(__name__)


class ClientInterface(ABC):
    """Abstract interface for OAuth2 clients."""

    @abstractmethod
    def get_access_token(self) -> str:
        """
        Get access token.

        Returns:
            str: Access token
        """
        pass


@dataclass(frozen=True)
class OidcConfig:
    """OIDC Configuration containing OAuth2 endpoints."""

    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    end_session_endpoint: str
    device_authorization_endpoint: str

    def to_dict(self) -> dict[str, str]:
        """
        Convert to dictionary.

        Returns:
            dict[str, str]: Dictionary representation
        """
        return asdict(self)

    def to_json(self) -> str:
        """
        Convert to JSON string.

        Returns:
            str: JSON representation
        """
        return json.dumps(self.to_dict())


class OidcDiscoveryClient:
    def __init__(self, base_url: str | list[str]):
        self.base_url = base_url

    def discover(self) -> OidcConfig:
        config = None
        tried_urls = []

        if isinstance(self.base_url, str):
            urls_to_try = [self.base_url]
        elif isinstance(self.base_url, list):
            urls_to_try = self.base_url
        else:
            raise OidcDiscoveryError("base_url must be string or list of strings")

        for url in urls_to_try:
            tried_urls.append(url)
            try:
                config = self._fetch(url)
                break
            except Exception:
                well_known_url = f"{url}/.well-known/openid-configuration"
                tried_urls.append(well_known_url)
                try:
                    config = self._fetch(well_known_url)
                    break
                except Exception:
                    continue

        if config is None:
            raise OidcDiscoveryError(
                "OIDC discovery failed. No valid configuration found.", urls=tried_urls
            )

        # Validate required fields
        required_fields = [
            "issuer",
            "authorization_endpoint",
            "token_endpoint",
            "userinfo_endpoint",
            "end_session_endpoint",
            "device_authorization_endpoint",
        ]
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            missing = ", ".join(missing_fields)
            raise OidcDiscoveryError(
                f"OIDC configuration missing required fields: {missing}",
                urls=tried_urls,
            )

        return OidcConfig(
            issuer=config["issuer"],
            authorization_endpoint=config["authorization_endpoint"],
            token_endpoint=config["token_endpoint"],
            userinfo_endpoint=config["userinfo_endpoint"],
            end_session_endpoint=config["end_session_endpoint"],
            device_authorization_endpoint=config["device_authorization_endpoint"],
        )

    def _fetch(self, url: str) -> dict[str, Any]:
        """Fetch OIDC configuration from URL."""
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


class OAuth2Credential(ABC):
    """Abstract base class for OAuth2 credentials."""

    @abstractmethod
    def create_session(
        self, client_id: str, oidc_config: "OidcConfig", scope: str | None = None
    ) -> OAuth2Session:
        """
        Create OAuth2 session for this credential type.

        Returns:
            OAuth2Session: OAuth2 session instance
        """
        pass

    @abstractmethod
    def authenticate(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Perform authentication and return token response.

        Returns:
            dict[str, Any]: Token response
        """
        pass

    @abstractmethod
    def refresh(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Refresh authentication token.

        Returns:
            dict[str, Any]: Token response
        """
        pass


@dataclass
class OAuth2ServiceCredential(OAuth2Credential):
    """Service account credentials (username/password)."""

    username: str
    password: str

    def create_session(
        self, client_id: str, oidc_config: "OidcConfig", scope: str | None = None
    ) -> OAuth2Session:
        """
        Create OAuth2 session with backend application client.

        Returns:
            OAuth2Session: OAuth2 session instance
        """
        client = BackendApplicationClient(client_id=client_id)
        return OAuth2Session(client=client)

    def authenticate(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Authenticate using username/password.

        Returns:
            dict[str, Any]: Token response
        """
        return session.fetch_token(
            token_url=oidc_config.token_endpoint,
            client_id=client_id,
            username=self.username,
            password=self.password,
        )

    def refresh(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Refresh token using username/password.

        Returns:
            dict[str, Any]: Token response
        """
        return session.fetch_token(
            token_url=oidc_config.token_endpoint,
            client_id=client_id,
            username=self.username,
            password=self.password,
        )


@dataclass
class OAuth2InteractiveUserCredential(OAuth2Credential):
    """Interactive user credentials (device code flow)."""

    def create_session(
        self, client_id: str, oidc_config: "OidcConfig", scope: str | None = None
    ) -> OAuth2Session:
        """
        Create OAuth2 session with device client.

        Returns:
            OAuth2Session: OAuth2 session instance
        """
        device_client = DeviceClient(client_id=client_id)
        return OAuth2Session(
            client=device_client,
            auto_refresh_url=oidc_config.token_endpoint,
            scope=scope,
        )

    def authenticate(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Authenticate using device code flow.

        Returns:
            dict[str, Any]: Token response
        """
        device_code_response = self._get_device_code(
            client_id, oidc_config, session.scope
        )

        logger.info(
            "Please go to %s and authorize access.",
            device_code_response["verification_uri"],
        )
        uri = device_code_response["verification_uri"]
        print(f"Please go to {uri} and authorize access.")

        while True:
            try:
                token_response = session.fetch_token(
                    token_url=oidc_config.token_endpoint,
                    device_code=device_code_response["device_code"],
                    include_client_id=True,
                )
                return token_response
            except OAuth2Error as e:
                if e.error == "authorization_pending":
                    time.sleep(device_code_response["interval"])
                else:
                    logger.error("Authorization failed: %s", e.error)
                    raise AuthenticationError(f"Authorization failed: {e.error}") from e

    def refresh(
        self, session: OAuth2Session, client_id: str, oidc_config: "OidcConfig"
    ) -> dict[str, Any]:
        """
        Refresh token.

        Returns:
            dict[str, Any]: Token response
        """
        return session.refresh_token(
            token_url=oidc_config.token_endpoint, client_id=client_id
        )

    def _get_device_code(
        self, client_id: str, oidc_config: "OidcConfig", scope: str | None = None
    ) -> dict[str, Any]:
        """
        Get device code from authorization endpoint.

        Returns:
            dict[str, Any]: Device code response
        """
        scope_arg = f"&scope={scope}" if scope else ""
        response = requests.post(
            oidc_config.device_authorization_endpoint,
            data=f"client_id={client_id}{scope_arg}",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        json_response = response.json()

        return {
            "device_code": json_response["device_code"],
            "interval": json_response["interval"],
            "verification_uri": json_response["verification_uri_complete"],
            "expires_in": json_response["expires_in"],
        }


class OAuth2Authentication(ClientInterface):
    """OAuth2 authentication client using Strategy pattern for credentials."""

    def __init__(
        self,
        client_id: str,
        credentials: OAuth2Credential,
        oidc_config: OidcConfig,
        scope: str | None = None,
        minimum_token_lifetime_seconds: int = 60,
    ):
        """
        Initialize OAuth2 authentication client.

        Args:
            client_id: OAuth2 client ID
            credentials: Credential strategy (Service or Interactive)
            oidc_config: OIDC configuration with endpoints
            scope: Optional OAuth2 scopes
            minimum_token_lifetime_seconds: Minimum lifetime before token refresh
        """
        self.client_id = client_id
        self.credentials = credentials
        self.oidc_config = oidc_config
        self.scope = scope
        self.minimum_token_lifetime_seconds = minimum_token_lifetime_seconds

        self.session: OAuth2Session | None = None
        self.authenticated = False
        self.token_expires_at: datetime | None = None

    def authenticate(self) -> None:
        """Perform initial authentication."""
        logger.info("Starting authentication")
        self.session = self.credentials.create_session(
            self.client_id, self.oidc_config, self.scope
        )
        token_response = self.credentials.authenticate(
            self.session, self.client_id, self.oidc_config
        )
        self._process_token_response(token_response)
        self.authenticated = True
        logger.info("Authentication successful")

    def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.

        Returns:
            str: Valid access token
        """
        if not self.authenticated:
            raise NotAuthenticatedError("Not authenticated. Call authenticate() first")
        if not self.session:
            raise SessionNotInitializedError("Session not initialized")

        self._refresh_if_needed()
        return self.session.access_token

    def _refresh_if_needed(self) -> None:
        """Refresh token if expired or close to expiry."""
        if not self._is_token_expired():
            return

        logger.info("Token expired, refreshing")
        if not self.session:
            raise SessionNotInitializedError("Session not initialized")

        token_response = self.credentials.refresh(
            self.session, self.client_id, self.oidc_config
        )
        self._process_token_response(token_response)
        logger.info("Token refreshed successfully")

    def _process_token_response(self, response: dict[str, Any]) -> None:
        """Process token response and update expiry time."""
        self.token_expires_at = datetime.fromtimestamp(response["expires_at"])

    def _is_token_expired(self) -> bool:
        """
        Check if token is expired or close to expiry.

        Returns:
            bool: True wenn Token abgelaufen oder bald abgelaufen, sonst False
        """
        if not self.token_expires_at:
            return True
        return (
            self.token_expires_at
            - timedelta(seconds=self.minimum_token_lifetime_seconds)
        ) < datetime.now()
