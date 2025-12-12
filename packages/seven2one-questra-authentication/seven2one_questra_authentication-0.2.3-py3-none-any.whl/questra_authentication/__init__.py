"""
Questra Authentication - OAuth2 Authentifizierung für Questra API
"""

from .authentication import (
    ClientInterface,
    OAuth2Authentication,
    OAuth2InteractiveUserCredential,
    OAuth2ServiceCredential,
    OidcConfig,
    OidcDiscoveryClient,
)
from .exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    NotAuthenticatedError,
    OidcDiscoveryError,
    QuestraAuthenticationError,
    SessionNotInitializedError,
    TokenExpiredError,
)
from .questra_authentication import QuestraAuthentication

__all__ = [
    "QuestraAuthentication",
    "OAuth2Authentication",
    "OAuth2ServiceCredential",
    "OAuth2InteractiveUserCredential",
    "OidcConfig",
    "OidcDiscoveryClient",
    "ClientInterface",
    "QuestraAuthenticationError",
    "AuthenticationError",
    "NotAuthenticatedError",
    "SessionNotInitializedError",
    "InvalidCredentialsError",
    "OidcDiscoveryError",
    "TokenExpiredError",
]
