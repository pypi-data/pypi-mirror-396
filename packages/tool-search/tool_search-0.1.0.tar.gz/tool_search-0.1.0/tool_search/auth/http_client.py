"""HTTP client with OAuth token injection."""

import httpx

from .keyring_provider import KeyringTokenProvider


class AuthenticatedMCPClient:
    """HTTP client with automatic OAuth token injection.

    Wraps httpx.AsyncClient to automatically add OAuth tokens
    from the system keyring to HTTP requests.
    """

    def __init__(self, token_provider: KeyringTokenProvider | None = None, timeout: float = 30.0):
        """Initialize client.

        Args:
            token_provider: Provider for OAuth tokens (creates default if None)
            timeout: Request timeout in seconds
        """
        self.token_provider = token_provider or KeyringTokenProvider()
        self._client = httpx.AsyncClient(timeout=timeout)

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make authenticated HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments passed to httpx

        Returns:
            HTTP response
        """
        headers = dict(kwargs.pop("headers", {}) or {})

        # MCP servers may use SSE - ensure we accept both JSON and event-stream
        if "Accept" not in headers:
            headers["Accept"] = "application/json, text/event-stream"

        # Inject OAuth token if available
        token = self.token_provider.get_token(url)
        if token:
            headers["Authorization"] = token.authorization_header

        return await self._client.request(method, url, headers=headers, **kwargs)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> "AuthenticatedMCPClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        await self.close()
