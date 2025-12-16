"""Tool Search - Semantic search for MCP server tools.

This module provides:
1. MCP server connection management and tool discovery
2. Embedding-based semantic search
3. MCP server exposing tool_search and tool_invoke

Usage:
    from tool_search import MCPConnectionPool, MCPServerConfig

    # Create pool and discover tools
    configs = [MCPServerConfig(name="linear", transport="http", url="...")]
    pool = MCPConnectionPool(configs)
    tools = await pool.discover_tools()

    # Invoke tools
    result = await pool.invoke_tool("linear", "create_issue", {"title": "Test"})

Server:
    from tool_search import ToolSearchServer, run_server
    run_server()
"""

__version__ = "0.1.0"

from tool_search.connection import (
    MCPConnection,
    MCPConnectionPool,
    MCPServerConfig,
    load_all_mcp_configs,
    load_claude_desktop_config,
    load_factory_mcp_config,
    parse_mcp_config,
)
from tool_search.examples_loader import ExamplesLoader
from tool_search.server import ToolSearchServer, run_server

__all__ = [
    # Connection & config
    "MCPConnection",
    "MCPConnectionPool",
    "MCPServerConfig",
    "parse_mcp_config",
    "load_factory_mcp_config",
    "load_claude_desktop_config",
    "load_all_mcp_configs",
    # Examples
    "ExamplesLoader",
    # Server
    "ToolSearchServer",
    "run_server",
]
