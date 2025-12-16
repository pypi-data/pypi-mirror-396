"""Read OAuth tokens from Factory's keyring storage."""

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from urllib.parse import urlparse

import keyring

logger = logging.getLogger(__name__)


@dataclass
class OAuthToken:
    """OAuth token data."""

    access_token: str
    token_type: str = "Bearer"
    expires_at: float | None = None
    refresh_token: str | None = None
    client_id: str | None = None

    @property
    def authorization_header(self) -> str:
        """Generate Authorization header value."""
        return f"{self.token_type} {self.access_token}"


class KeyringTokenProvider:
    """Read OAuth tokens from Factory's keyring storage."""

    # Possible keyring service names (try in order)
    SERVICE_PATTERNS = [
        "tool-search-oauth",  # tool-search's own OAuth tokens (highest priority)
        "Codex MCP Credentials",  # Factory's actual service name
        "factory-mcp-oauth",
        "factory-mcp",
        "com.factory.cli.mcp",
        "factory",
    ]

    # Environment variable names for API keys (server_name -> env_var)
    ENV_VAR_MAPPING = {
        "linear": "LINEAR_API_KEY",
        "context7": "CONTEXT7_API_KEY",
        "notion": "NOTION_API_KEY",
        "sentry": "SENTRY_API_KEY",
        "stripe": "STRIPE_API_KEY",
    }

    # OAuth token endpoints for refresh (server_name -> token_url)
    TOKEN_ENDPOINTS = {
        "linear": "https://api.linear.app/oauth/token",
    }

    def __init__(self):
        self._cache: dict[str, OAuthToken] = {}

    def _get_token_from_env(self, server_url: str) -> OAuthToken | None:
        """Check for API key in environment variable.

        Args:
            server_url: MCP server URL

        Returns:
            OAuthToken if env var found, None otherwise
        """
        host = self._extract_host(server_url)

        # Extract server name from host (e.g., "mcp.linear.app" -> "linear")
        host_parts = host.split(".")
        if len(host_parts) > 1 and host_parts[0] == "mcp":
            server_name = host_parts[1]
        else:
            server_name = host_parts[0]

        # Check for specific env var
        env_var = self.ENV_VAR_MAPPING.get(server_name)
        if env_var:
            api_key = os.environ.get(env_var)
            if api_key:
                logger.debug(f"Using {env_var} for {server_name} authentication")
                return OAuthToken(access_token=api_key, token_type="Bearer")

        # Check for generic pattern: {SERVER_NAME}_API_KEY
        generic_env_var = f"{server_name.upper()}_API_KEY"
        api_key = os.environ.get(generic_env_var)
        if api_key:
            logger.debug(f"Using {generic_env_var} for {server_name} authentication")
            return OAuthToken(access_token=api_key, token_type="Bearer")

        return None

    def get_token(self, server_url: str) -> OAuthToken | None:
        """Get OAuth token for an MCP server URL.

        Checks in order:
        1. Environment variable (e.g., LINEAR_API_KEY)
        2. In-memory cache (if not expired)
        3. System keyring (with refresh if expired)

        Args:
            server_url: Full URL of the MCP server

        Returns:
            OAuthToken if available, None otherwise
        """
        # Check environment variable first (highest priority)
        env_token = self._get_token_from_env(server_url)
        if env_token:
            return env_token

        # Check cache
        if server_url in self._cache:
            cached = self._cache[server_url]
            if not self._is_expired(cached):
                return cached

        # Read from keyring
        token = self._read_from_keyring(server_url)
        if token:
            # Check if token is expired and can be refreshed
            if self._is_expired(token) and token.refresh_token and token.client_id:
                server_name = self._extract_server_name(server_url)
                token_endpoint = self.TOKEN_ENDPOINTS.get(server_name)

                if token_endpoint:
                    logger.debug(f"Token expired, attempting refresh for {server_name}")
                    refreshed = self._refresh_token(token, token_endpoint)

                    if refreshed:
                        # Save refreshed token to keyring
                        self._save_token_to_keyring(server_name, refreshed)
                        self._cache[server_url] = refreshed
                        return refreshed
                    else:
                        logger.warning(f"Token refresh failed for {server_name}")

            self._cache[server_url] = token

        return token

    def _is_expired(self, token: OAuthToken) -> bool:
        """Check if token is expired.

        Args:
            token: Token to check

        Returns:
            True if expired, False otherwise
        """
        if token.expires_at is None:
            return False
        import time

        return time.time() > token.expires_at

    def _parse_token(self, value: str | None) -> OAuthToken | None:
        """Parse token from keyring value (JSON or raw string).

        Args:
            value: Raw value from keyring (JSON string or plain token)

        Returns:
            OAuthToken if valid, None otherwise
        """
        if not value:
            return None

        # Try JSON first
        try:
            data = json.loads(value)

            # Extract client_id from wrapper (tool-search format)
            client_id = data.get("client_id")

            # Handle nested format: {token_response: {access_token: ...}}
            if "token_response" in data:
                data = data["token_response"]

            access_token = data.get("access_token") or data.get("token")
            if not access_token:
                return None

            # Calculate absolute expires_at from relative expires_in
            expires_at = data.get("expires_at")
            if expires_at is None and "expires_in" in data:
                import time

                expires_at = time.time() + data["expires_in"]

            return OAuthToken(
                access_token=access_token,
                token_type=data.get("token_type", "Bearer"),
                expires_at=expires_at,
                refresh_token=data.get("refresh_token"),
                client_id=client_id,
            )
        except json.JSONDecodeError:
            # Raw token string
            return OAuthToken(access_token=value)

    @staticmethod
    def _extract_host(url: str) -> str:
        """Extract host from URL.

        Args:
            url: Full URL (e.g., https://mcp.linear.app/mcp)

        Returns:
            Host portion (e.g., mcp.linear.app)
        """
        return urlparse(url).netloc

    def _extract_server_name(self, server_url: str) -> str:
        """Extract server name from URL (e.g., 'mcp.linear.app' -> 'linear').

        Args:
            server_url: Full URL of the MCP server

        Returns:
            Server name (e.g., 'linear')
        """
        host = self._extract_host(server_url)
        host_parts = host.split(".")
        if len(host_parts) > 1 and host_parts[0] == "mcp":
            return host_parts[1]
        return host_parts[0]

    def _read_from_keyring(self, server_url: str) -> OAuthToken | None:
        """Try multiple keyring patterns to find token.

        Args:
            server_url: MCP server URL

        Returns:
            OAuthToken if found, None otherwise
        """
        # Generate possible keys to try
        url_hash = hashlib.sha256(server_url.encode()).hexdigest()[:12]
        host = self._extract_host(server_url)

        # Extract server name from host (e.g., "mcp.linear.app" -> "linear")
        host_parts = host.split(".")
        server_name = (
            host_parts[1] if len(host_parts) > 1 and host_parts[0] == "mcp" else host_parts[0]
        )

        keys_to_try = [
            server_url,  # Full URL
            host,  # Just the host
            url_hash,  # URL hash
            server_name,  # Simple server name (e.g., "linear")
            f"{server_name}|",  # Factory pattern prefix (will match with startswith)
        ]

        for service in self.SERVICE_PATTERNS:
            for key in keys_to_try:
                try:
                    value = keyring.get_password(service, key)
                    if value:
                        token = self._parse_token(value)
                        if token:
                            return token
                except Exception:
                    continue

        # Try pattern matching for Factory's "{name}|{hash}" format
        # This requires listing keychain entries (platform-specific)
        token = self._try_factory_pattern(server_name)
        if token:
            return token

        return None

    def _try_factory_pattern(self, server_name: str) -> OAuthToken | None:
        """Try Factory's keyring pattern: {server_name}|{hash}.

        Factory stores tokens with account names like "linear|638130d5ab3558f4".
        We need to try to find entries that start with the server name.

        Args:
            server_name: Server name to search for (e.g., "linear")

        Returns:
            OAuthToken if found, None otherwise
        """
        import re
        import subprocess

        try:
            # Use macOS security command to find matching entries
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "Codex MCP Credentials", "-w"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                return self._parse_token(result.stdout.strip())
        except Exception:
            pass

        # Try to find by account pattern
        try:
            result = subprocess.run(
                ["security", "dump-keychain"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Look for account matching "{server_name}|"
                pattern = rf'"acct"<blob>="{server_name}\|([^"]+)"'
                match = re.search(pattern, result.stdout)
                if match:
                    account = f"{server_name}|{match.group(1)}"
                    # Now get the password for this account
                    pw_result = subprocess.run(
                        [
                            "security",
                            "find-generic-password",
                            "-s",
                            "Codex MCP Credentials",
                            "-a",
                            account,
                            "-w",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if pw_result.returncode == 0 and pw_result.stdout.strip():
                        return self._parse_token(pw_result.stdout.strip())
        except Exception:
            pass

        return None

    def _refresh_token(self, token: OAuthToken, token_endpoint: str) -> OAuthToken | None:
        """Refresh an OAuth token using its refresh_token.

        Args:
            token: Token with refresh_token and client_id
            token_endpoint: OAuth token endpoint URL

        Returns:
            New OAuthToken if refresh succeeds, None otherwise
        """
        if not token.refresh_token or not token.client_id:
            logger.debug("Cannot refresh: missing refresh_token or client_id")
            return None

        import time

        import httpx

        try:
            response = httpx.post(
                token_endpoint,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": token.refresh_token,
                    "client_id": token.client_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.warning(f"Token refresh failed: {response.status_code}")
                return None

            data = response.json()
            expires_at = None
            if "expires_in" in data:
                expires_at = time.time() + data["expires_in"]

            return OAuthToken(
                access_token=data["access_token"],
                token_type=data.get("token_type", "Bearer"),
                expires_at=expires_at,
                refresh_token=data.get("refresh_token", token.refresh_token),
                client_id=token.client_id,
            )

        except Exception as e:
            logger.warning(f"Token refresh error: {e}")
            return None

    def _save_token_to_keyring(self, server_name: str, token: OAuthToken) -> bool:
        """Save token to keyring in tool-search format.

        Args:
            server_name: Server identifier (e.g., "linear")
            token: Token to save

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            data = {
                "client_id": token.client_id,
                "token_response": {
                    "access_token": token.access_token,
                    "token_type": token.token_type,
                    "refresh_token": token.refresh_token,
                    "expires_at": token.expires_at,
                },
            }
            keyring.set_password("tool-search-oauth", server_name, json.dumps(data))
            logger.debug(f"Saved refreshed token for {server_name}")
            return True
        except Exception as e:
            logger.warning(f"Failed to save token to keyring: {e}")
            return False
