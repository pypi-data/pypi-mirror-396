"""Custom exceptions for questra-authentication."""


class QuestraAuthenticationError(Exception):
    """Base exception for all questra-authentication errors."""

    pass


class AuthenticationError(QuestraAuthenticationError):
    """Raised when authentication fails."""

    pass


class NotAuthenticatedError(AuthenticationError):
    """Raised when operation requires authentication but not authenticated."""

    pass


class SessionNotInitializedError(AuthenticationError):
    """Raised when OAuth2 session is not initialized."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid or of wrong type."""

    pass


class OidcDiscoveryError(QuestraAuthenticationError):
    """Raised when OIDC discovery fails."""

    def __init__(
        self,
        message: str,
        urls: list | None = None,
        original_error: Exception | None = None,
    ):
        """
        Initialize OidcDiscoveryError.

        Args:
            message: Error message
            urls: List of URLs that were tried
            original_error: Original exception that caused the error
        """
        super().__init__(message)
        self.urls = urls or []
        self.original_error = original_error

    def __str__(self) -> str:
        """
        String representation of the error.

        Returns:
            str: Error message mit zusätzlichen Details
        """
        msg = super().__str__()
        if self.urls:
            msg += f"\nTried URLs: {', '.join(self.urls)}"
        if self.original_error:
            msg += f"\nOriginal error: {str(self.original_error)}"
        return msg


class TokenExpiredError(AuthenticationError):
    """Raised when a token has expired and cannot be refreshed."""

    pass
