"""MCP connection management for tool invocation proxying."""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from tool_search.auth.http_client import AuthenticatedMCPClient
from tool_search.auth.keyring_provider import KeyringTokenProvider

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""

    name: str
    transport: str = "stdio"  # "stdio" or "http"
    # For stdio transport
    command: str | None = None
    args: list[str] = field(default_factory=list)
    env: dict[str, str] | None = None
    # For HTTP transport
    url: str | None = None


def parse_mcp_config(config_dict: dict[str, Any]) -> list[MCPServerConfig]:
    """Parse MCP server configs from Claude Desktop or Factory format.

    Args:
        config_dict: Dict with 'mcpServers' key

    Returns:
        List of MCPServerConfig objects
    """
    servers = config_dict.get("mcpServers", {})
    configs = []

    for name, server_config in servers.items():
        # Skip disabled servers
        if server_config.get("disabled", False):
            continue

        # Determine transport type
        server_type = server_config.get("type", "stdio")

        if server_type == "http":
            configs.append(
                MCPServerConfig(name=name, transport="http", url=server_config.get("url", ""))
            )
        else:
            # stdio transport (default)
            configs.append(
                MCPServerConfig(
                    name=name,
                    transport="stdio",
                    command=server_config.get("command", ""),
                    args=server_config.get("args", []),
                    env=server_config.get("env"),
                )
            )

    return configs


def load_factory_mcp_config() -> list[MCPServerConfig]:
    """Load MCP configs from Factory config file (~/.factory/mcp.json).

    Returns:
        List of MCPServerConfig objects
    """
    config_path = os.path.expanduser("~/.factory/mcp.json")

    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        return parse_mcp_config(config)

    return []


def load_claude_desktop_config() -> list[MCPServerConfig]:
    """Load MCP configs from Claude Desktop config file.

    Returns:
        List of MCPServerConfig objects
    """
    config_paths = [
        os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),
        os.path.expanduser("~/.config/claude/claude_desktop_config.json"),
    ]

    for path in config_paths:
        if os.path.exists(path):
            with open(path) as f:
                config = json.load(f)
            return parse_mcp_config(config)

    return []


def load_all_mcp_configs() -> list[MCPServerConfig]:
    """Load MCP configs from all known sources.

    Returns:
        Combined list of MCPServerConfig objects
    """
    configs = []
    configs.extend(load_factory_mcp_config())
    configs.extend(load_claude_desktop_config())
    return configs


def _parse_sse_response(text: str) -> dict[str, Any]:
    """Parse Server-Sent Events response to extract JSON data."""
    for line in text.strip().split("\n"):
        if line.startswith("data: "):
            return json.loads(line[6:])
    return json.loads(text)


class MCPConnection:
    """Manages a persistent connection to a single MCP server.

    Supports both stdio and HTTP transports. The connection is established
    lazily on first tool invocation and maintained for subsequent calls.
    """

    def __init__(
        self,
        config: MCPServerConfig,
        token_provider: KeyringTokenProvider | None = None,
    ):
        """Initialize connection (does not connect yet).

        Args:
            config: Server configuration
            token_provider: OAuth token provider for HTTP transport
        """
        self.config = config
        self._token_provider = token_provider or KeyringTokenProvider()
        self._process: asyncio.subprocess.Process | None = None
        self._session_id: str | None = None
        self._initialized = False
        self._request_id = 0

    @property
    def server_name(self) -> str:
        """Name of the MCP server."""
        return self.config.name

    @property
    def is_connected(self) -> bool:
        """Whether the connection is established."""
        if self.config.transport == "stdio":
            return (
                self._process is not None and self._process.returncode is None and self._initialized
            )
        else:
            return self._initialized

    def _next_request_id(self) -> int:
        """Get next JSON-RPC request ID."""
        self._request_id += 1
        return self._request_id

    async def connect(self, timeout: float = 30.0) -> None:
        """Establish connection and initialize MCP session.

        Args:
            timeout: Timeout in seconds for initialization
        """
        if self.is_connected:
            return

        if self.config.transport == "stdio":
            await self._connect_stdio(timeout)
        else:
            await self._connect_http(timeout)

    async def _connect_stdio(self, timeout: float) -> None:
        """Connect to stdio MCP server."""
        env = os.environ.copy()
        if self.config.env:
            env.update(self.config.env)

        self._process = await asyncio.create_subprocess_exec(
            self.config.command,
            *self.config.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "tool-search-proxy", "version": "0.1.0"},
            },
        }
        await self._send_stdio(init_request)
        await self._read_stdio(timeout)

        await self._send_stdio({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._initialized = True

    async def _connect_http(self, timeout: float) -> None:
        """Connect to HTTP MCP server and get session ID."""
        async with AuthenticatedMCPClient(
            token_provider=self._token_provider, timeout=timeout
        ) as client:
            init_response = await client.request(
                "POST",
                self.config.url,
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_request_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "tool-search-proxy", "version": "0.1.0"},
                    },
                },
            )
            init_response.raise_for_status()

            self._session_id = init_response.headers.get("mcp-session-id")

            session_headers = {"Mcp-Session-Id": self._session_id} if self._session_id else {}
            await client.request(
                "POST",
                self.config.url,
                json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                headers=session_headers,
            )

        self._initialized = True

    async def _send_stdio(self, message: dict) -> None:
        """Send JSON-RPC message to stdio process."""
        if not self._process or not self._process.stdin:
            raise ConnectionError("Process not started")
        data = json.dumps(message).encode() + b"\n"
        self._process.stdin.write(data)
        await self._process.stdin.drain()

    async def _read_stdio(self, timeout: float) -> dict:
        """Read JSON-RPC response from stdio process."""
        if not self._process or not self._process.stdout:
            raise ConnectionError("Process not started")
        line = await asyncio.wait_for(self._process.stdout.readline(), timeout=timeout)
        return json.loads(line.decode())

    async def close(self) -> None:
        """Close the connection."""
        if self.config.transport == "stdio" and self._process:
            self._process.stdin.close()
            try:
                self._process.terminate()
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except TimeoutError:
                self._process.kill()
            self._process = None

        self._initialized = False
        self._session_id = None

    async def __aenter__(self) -> "MCPConnection":
        """Enter async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        await self.close()

    async def list_tools(self, timeout: float = 30.0) -> list[dict[str, Any]]:
        """List available tools on this server.

        Args:
            timeout: Timeout in seconds

        Returns:
            List of tool definitions

        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected")

        if self.config.transport == "stdio":
            return await self._list_tools_stdio(timeout)
        else:
            return await self._list_tools_http(timeout)

    async def _list_tools_stdio(self, timeout: float) -> list[dict[str, Any]]:
        """List tools via stdio transport."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/list",
            "params": {},
        }

        await self._send_stdio(request)
        response = await self._read_stdio(timeout)

        if "error" in response:
            raise RuntimeError(response["error"].get("message", "Unknown error"))

        return response.get("result", {}).get("tools", [])

    async def _list_tools_http(self, timeout: float) -> list[dict[str, Any]]:
        """List tools via HTTP transport."""
        async with AuthenticatedMCPClient(
            token_provider=self._token_provider, timeout=timeout
        ) as client:
            session_headers = {"Mcp-Session-Id": self._session_id} if self._session_id else {}

            response = await client.request(
                "POST",
                self.config.url,
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_request_id(),
                    "method": "tools/list",
                    "params": {},
                },
                headers=session_headers,
            )
            response.raise_for_status()

            result = _parse_sse_response(response.text)

            if "error" in result:
                raise RuntimeError(result["error"].get("message", "Unknown error"))

            return result.get("result", {}).get("tools", [])

    async def invoke_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """Invoke a tool on this MCP server.

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments
            timeout: Timeout in seconds

        Returns:
            Tool result with 'content' and 'isError' fields

        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected")

        if self.config.transport == "stdio":
            return await self._invoke_tool_stdio(tool_name, arguments, timeout)
        else:
            return await self._invoke_tool_http(tool_name, arguments, timeout)

    async def _invoke_tool_stdio(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any]:
        """Invoke tool via stdio transport."""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        await self._send_stdio(request)
        response = await self._read_stdio(timeout)

        if "error" in response:
            return {
                "content": [
                    {"type": "text", "text": response["error"].get("message", "Unknown error")}
                ],
                "isError": True,
            }

        return response.get("result", {})

    async def _invoke_tool_http(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any]:
        """Invoke tool via HTTP transport."""
        async with AuthenticatedMCPClient(
            token_provider=self._token_provider, timeout=timeout
        ) as client:
            session_headers = {"Mcp-Session-Id": self._session_id} if self._session_id else {}

            request_body = {
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments,
                },
            }

            response = await client.request(
                "POST",
                self.config.url,
                json=request_body,
                headers=session_headers,
            )
            response.raise_for_status()

            result = _parse_sse_response(response.text)

            if "error" in result:
                return {
                    "content": [
                        {"type": "text", "text": result["error"].get("message", "Unknown error")}
                    ],
                    "isError": True,
                }

            return result.get("result", {})


class MCPConnectionPool:
    """Pool of connections to multiple MCP servers.

    Manages lazy connection creation and reuse for upstream MCP servers.
    """

    def __init__(
        self,
        configs: list[MCPServerConfig],
        token_provider: KeyringTokenProvider | None = None,
    ):
        """Initialize pool with server configurations.

        Args:
            configs: List of MCP server configurations
            token_provider: Shared token provider for HTTP auth
        """
        self._configs = {c.name: c for c in configs}
        self._token_provider = token_provider or KeyringTokenProvider()
        self._connections: dict[str, MCPConnection] = {}

    @property
    def server_names(self) -> set[str]:
        """Names of all configured servers."""
        return set(self._configs.keys())

    async def get_connection(self, server_name: str) -> MCPConnection:
        """Get or create connection to a server.

        Args:
            server_name: Name of the MCP server

        Returns:
            Active MCPConnection

        Raises:
            KeyError: If server not configured
        """
        if server_name not in self._configs:
            raise KeyError(f"Unknown server: {server_name}")

        if server_name not in self._connections:
            config = self._configs[server_name]
            conn = MCPConnection(config, token_provider=self._token_provider)
            await conn.connect()
            self._connections[server_name] = conn

        return self._connections[server_name]

    async def discover_tools(self, timeout: float = 30.0) -> list[dict[str, Any]]:
        """Connect to all servers and list their tools.

        Connections remain open for subsequent invoke_tool() calls.
        Each tool is tagged with _mcp_server field.

        Args:
            timeout: Timeout per server in seconds

        Returns:
            List of tool definitions from all servers
        """
        all_tools: list[dict[str, Any]] = []

        for server_name in self._configs:
            try:
                conn = await self.get_connection(server_name)
                tools = await conn.list_tools(timeout=timeout)

                # Tag tools with server name
                for tool in tools:
                    tool["_mcp_server"] = server_name

                all_tools.extend(tools)
            except Exception as e:
                logger.warning(f"Failed to discover tools from {server_name}: {e}")

        return all_tools

    async def invoke_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """Invoke a tool on a specific server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to invoke
            arguments: Tool arguments
            timeout: Timeout in seconds

        Returns:
            Tool result
        """
        conn = await self.get_connection(server_name)
        return await conn.invoke_tool(tool_name, arguments, timeout=timeout)

    async def close_all(self) -> None:
        """Close all open connections."""
        for conn in self._connections.values():
            await conn.close()
        self._connections.clear()

    async def __aenter__(self) -> "MCPConnectionPool":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        await self.close_all()
