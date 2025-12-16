"""MCP server exposing tool_search functionality.

This server discovers tools from MCP configurations and provides
semantic search over them via the tool_search tool.

Usage:
    # Run with sample tools (for testing)
    python -m tool_search.server --sample

    # Run with tools from Factory MCP config
    python -m tool_search.server

    # Run with tools from all MCP configs
    python -m tool_search.server --all-configs

    # Run with specific HTTP MCP sources (for production)
    python -m tool_search.server \\
        --source linear=https://mcp.linear.app/mcp \\
        --source context7=https://mcp.context7.com/mcp
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from tool_search.auth.keyring_provider import KeyringTokenProvider
from tool_search.connection import (
    MCPConnectionPool,
    MCPServerConfig,
    load_all_mcp_configs,
    load_factory_mcp_config,
)
from tool_search.errors import (
    ToolSearchErrorCode,
    build_error_response,
    validate_query,
)
from tool_search.examples_loader import ExamplesLoader
from tool_search.searcher import ToolSearcher

logger = logging.getLogger(__name__)

# Sample tools for testing without MCP server discovery
SAMPLE_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_weather",
        "description": "Get current weather conditions for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name or coordinates"}
            },
            "required": ["location"],
        },
    },
    {
        "name": "get_forecast",
        "description": "Get weather forecast for multiple days ahead",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "days": {"type": "integer", "description": "Number of days (1-10)"},
            },
        },
    },
    {
        "name": "get_stock_price",
        "description": "Get current stock price and market data for a ticker symbol",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "Stock ticker (e.g., AAPL)"}
            },
        },
    },
    {
        "name": "convert_currency",
        "description": "Convert amount between currencies using current exchange rates",
        "inputSchema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string"},
                "to_currency": {"type": "string"},
            },
        },
    },
    {
        "name": "search_web",
        "description": "Search the web for information on any topic",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
        },
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file from the filesystem",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute or relative file path"}
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file on the filesystem",
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write to"},
                "content": {"type": "string", "description": "Content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "execute_command",
        "description": "Execute a shell command and return the output",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories in a given path",
        "inputSchema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Directory path to list"}},
            "required": ["path"],
        },
    },
    {
        "name": "create_github_issue",
        "description": "Create a new issue on a GitHub repository",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository in owner/repo format"},
                "title": {"type": "string", "description": "Issue title"},
                "body": {"type": "string", "description": "Issue body (markdown)"},
            },
            "required": ["repo", "title"],
        },
    },
]


class ToolSearchServer:
    """MCP server for semantic tool search with invocation proxy."""

    def __init__(self, name: str = "tool-search", examples_dir: Path | None = None):
        """Initialize the server.

        Args:
            name: Server name for MCP protocol
            examples_dir: Directory for example YAML files
        """
        self.server = Server(name)
        self.searcher = ToolSearcher()
        self._indexed = False
        self._connection_pool: MCPConnectionPool | None = None
        self._discovered_tools: list[dict[str, Any]] = []

        # Examples loader
        self._examples_loader = ExamplesLoader(examples_dir=examples_dir)
        self._examples_loader.load_all()

        # Register handlers
        self._register_handlers()

    def set_connection_pool(self, pool: MCPConnectionPool) -> None:
        """Set the connection pool for proxying tool calls.

        Args:
            pool: Connection pool for upstream servers
        """
        self._connection_pool = pool

    def _register_handlers(self) -> None:
        """Register MCP protocol handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            return await self._list_tools_handler()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            return await self._call_tool_handler(name, arguments)

    async def _list_tools_handler(self) -> list[Tool]:
        """Return available tools: tool_search and tool_invoke."""
        # Note: MCP's Tool type may not have input_examples field.
        # We return dicts that get serialized with extra fields.
        return [
            Tool(
                name="tool_search",
                description=(
                    "Search for available tools that can help with a task. "
                    "Returns tool names and their server. Use tool_invoke to "
                    "execute discovered tools."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Natural language description of what kind of "
                                "tool you need (e.g., 'create issues', "
                                "'get documentation', 'search code')"
                            ),
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of tools to return (default: 5)",
                            "default": 5,
                        },
                        "examples_for_top_k": {
                            "type": "integer",
                            "description": (
                                "Include input_examples for top N results to help "
                                "with tool usage (default: 3, set 0 to disable)"
                            ),
                            "default": 3,
                        },
                    },
                    "required": ["query"],
                },
                # input_examples for tool_search itself
                **{
                    "input_examples": [
                        {"query": "create issues", "top_k": 5},
                        {"query": "search documentation"},
                        {"query": "list projects and teams", "top_k": 10, "examples_for_top_k": 5},
                    ]
                },
            ),
            Tool(
                name="tool_invoke",
                description=(
                    "Invoke a tool discovered via tool_search. "
                    "Specify the server name, tool name, and arguments."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "server": {
                            "type": "string",
                            "description": "MCP server name (from tool_search results)",
                        },
                        "tool": {
                            "type": "string",
                            "description": "Tool name to invoke",
                        },
                        "arguments": {
                            "type": "object",
                            "description": "Arguments to pass to the tool",
                            "default": {},
                        },
                    },
                    "required": ["server", "tool"],
                },
                **{
                    "input_examples": [
                        {
                            "server": "linear",
                            "tool": "create_issue",
                            "arguments": {"title": "Bug fix", "team": "ENG"},
                        },
                        {
                            "server": "github",
                            "tool": "list_repos",
                            "arguments": {"org": "anthropics"},
                        },
                    ]
                },
            ),
        ]

    async def _call_tool_handler(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool invocations."""
        if name == "tool_search":
            tool_use_id = arguments.get("_tool_use_id", f"toolu_{id(arguments)}")
            query = arguments.get("query", "")
            top_k = arguments.get("top_k", 5)
            examples_for_top_k = arguments.get("examples_for_top_k", 3)

            result = await self._handle_tool_search(
                tool_use_id=tool_use_id,
                query=query,
                top_k=top_k,
                examples_for_top_k=examples_for_top_k,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        if name == "tool_invoke":
            return await self._handle_tool_invoke(
                server=arguments.get("server", ""),
                tool=arguments.get("tool", ""),
                tool_arguments=arguments.get("arguments", {}),
            )

        raise ValueError(f"Unknown tool: {name}")

    async def _handle_tool_search(
        self,
        tool_use_id: str,
        query: str,
        top_k: int = 5,
        examples_for_top_k: int = 3,
    ) -> dict[str, Any]:
        """Handle a tool_search invocation.

        Args:
            tool_use_id: The tool_use_id from the MCP request
            query: Natural language search query
            top_k: Number of results to return
            examples_for_top_k: Include examples for top N results

        Returns:
            Response dict in Anthropic's tool_search_tool_result format
        """
        # Check if indexed
        if not self._indexed:
            return build_error_response(
                tool_use_id=tool_use_id,
                error_code=ToolSearchErrorCode.NOT_INDEXED,
                message="No tools indexed. Server may not be fully initialized.",
            )

        # Validate query
        error_code = validate_query(query)
        if error_code:
            return build_error_response(
                tool_use_id=tool_use_id,
                error_code=error_code,
            )

        # Perform search
        results = self.searcher.search(query, top_k=top_k)

        # Enrich top results with examples
        if examples_for_top_k > 0:
            self._enrich_with_examples(results, examples_for_top_k)

        # Build response in Anthropic format
        return self.searcher.build_search_result(
            results=results,
            tool_use_id=tool_use_id,
            include_matches=True,  # Include scores for debugging
        )

    def _enrich_with_examples(
        self,
        results: list[dict[str, Any]],
        examples_for_top_k: int,
    ) -> None:
        """Enrich search results with input_examples.

        Args:
            results: Search results to enrich (modified in place)
            examples_for_top_k: Number of top results to enrich
        """
        for i, result in enumerate(results):
            if i >= examples_for_top_k:
                break

            tool = result["tool"]
            server = tool.get("_mcp_server")
            tool_name = tool.get("name")

            if not server or not tool_name:
                continue

            examples = self._examples_loader.get_examples(server, tool_name)
            if examples:
                # Validate against schema if available
                schema = tool.get("inputSchema")
                validated = self._examples_loader.validate_examples(tool_name, examples, schema)
                if validated:
                    result["tool"]["input_examples"] = validated

    async def _handle_tool_invoke(
        self,
        server: str,
        tool: str,
        tool_arguments: dict[str, Any],
    ) -> list[TextContent]:
        """Handle tool_invoke calls.

        Args:
            server: MCP server name
            tool: Tool name
            tool_arguments: Arguments for the tool

        Returns:
            Tool result as TextContent
        """
        if not self._connection_pool:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": "No connection pool configured", "isError": True}),
                )
            ]

        if server not in self._connection_pool.server_names:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown server: {server}", "isError": True}),
                )
            ]

        try:
            result = await self._connection_pool.invoke_tool(
                server, tool, tool_arguments, timeout=60.0
            )

            # Return the content as JSON
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Invocation failed: {e}", "isError": True}),
                )
            ]

    def index_tools(self, tools: list[dict[str, Any]]) -> None:
        """Index tools for search.

        Args:
            tools: List of tool definitions
        """
        self.searcher.index_tools(tools)
        self._indexed = True
        logger.info(f"Indexed {self.searcher.tool_count} tools")

    async def run_stdio(self) -> None:
        """Run the server using stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.server.create_initialization_options()
            )


def parse_source_arg(source: str) -> MCPServerConfig:
    """Parse a --source argument into MCPServerConfig.

    Format: name=url or just url (name derived from url)

    Args:
        source: Source string like "linear=https://mcp.linear.app/mcp"

    Returns:
        MCPServerConfig for the source
    """
    if "=" in source:
        name, url = source.split("=", 1)
    else:
        # Derive name from URL
        url = source
        # Extract name from URL like https://mcp.linear.app/mcp -> linear
        import re

        match = re.search(r"mcp\.([^./]+)\.", url)
        if match:
            name = match.group(1)
        else:
            name = url.split("/")[-2] if "/" in url else "source"

    return MCPServerConfig(name=name, transport="http", url=url)


async def discover_and_index_tools(
    server: ToolSearchServer,
    use_all_configs: bool = False,
    use_sample: bool = False,
    sources: list[str] | None = None,
    configs: list[MCPServerConfig] | None = None,
) -> None:
    """Discover tools and index them in the server.

    Args:
        server: ToolSearchServer instance
        use_all_configs: Use all MCP configs (Factory + Claude Desktop)
        use_sample: Use sample tools instead of discovery
        sources: List of HTTP MCP server URLs to discover from
        configs: Explicit list of MCPServerConfig objects
    """
    if use_sample:
        logger.info("Using sample tools")
        server.index_tools(SAMPLE_TOOLS)
        return

    # Determine configs to use
    if configs:
        final_configs = configs
    elif sources:
        logger.info(f"Discovering tools from {len(sources)} source(s)...")
        final_configs = [parse_source_arg(s) for s in sources]
    elif use_all_configs:
        logger.info("Discovering tools from all MCP configs...")
        final_configs = load_all_mcp_configs()
    else:
        logger.info("Discovering tools from Factory MCP config...")
        final_configs = load_factory_mcp_config()

    if not final_configs:
        logger.warning("No MCP configs found, using sample tools")
        server.index_tools(SAMPLE_TOOLS)
        return

    # Create token provider and connection pool
    token_provider = KeyringTokenProvider()
    pool = MCPConnectionPool(final_configs, token_provider=token_provider)
    server.set_connection_pool(pool)

    try:
        tools = await pool.discover_tools(timeout=30.0)
        if tools:
            logger.info(f"Discovered {len(tools)} tools from MCP servers")
            server.index_tools(tools)
        else:
            logger.warning("No tools discovered, using sample tools")
            server.index_tools(SAMPLE_TOOLS)
    except Exception as e:
        logger.error(f"Tool discovery failed: {e}, using sample tools")
        server.index_tools(SAMPLE_TOOLS)


def load_config_file(config_path: str) -> list[MCPServerConfig]:
    """Load MCP server configs from a JSON file.

    Args:
        config_path: Path to JSON config file

    Returns:
        List of MCPServerConfig objects
    """
    import os

    with open(config_path) as f:
        data = json.load(f)

    configs = []
    for server in data.get("servers", []):
        transport = server.get("transport", "stdio")
        if transport == "http":
            configs.append(
                MCPServerConfig(name=server["name"], transport="http", url=server["url"])
            )
        else:
            # Merge env with current environment
            env = os.environ.copy()
            if server.get("env"):
                env.update(server["env"])
            configs.append(
                MCPServerConfig(
                    name=server["name"],
                    transport="stdio",
                    command=server["command"],
                    args=server.get("args", []),
                    env=env,
                )
            )
    return configs


async def main() -> None:
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server for semantic tool search")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use sample tools instead of discovering from MCP servers",
    )
    parser.add_argument(
        "--all-configs",
        action="store_true",
        help="Discover from all MCP configs (Factory + Claude Desktop)",
    )
    parser.add_argument(
        "--config", "-c", metavar="FILE", help="Load upstream MCP servers from a JSON config file"
    )
    parser.add_argument(
        "--source",
        action="append",
        metavar="NAME=URL",
        help=(
            "HTTP MCP server to discover tools from. "
            "Format: name=url or just url. Can be used multiple times. "
            "Example: --source linear=https://mcp.linear.app/mcp"
        ),
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Configure logging (to stderr to not interfere with stdio transport)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Create and initialize server
    server = ToolSearchServer()

    # Load configs from file if provided
    configs_from_file = None
    if args.config:
        logger.info(f"Loading upstream servers from config: {args.config}")
        configs_from_file = load_config_file(args.config)
        logger.info(f"Loaded {len(configs_from_file)} server configs")

    # Discover and index tools
    await discover_and_index_tools(
        server,
        use_all_configs=args.all_configs,
        use_sample=args.sample,
        sources=args.source,
        configs=configs_from_file,
    )

    # Run server
    logger.info("Starting tool-search MCP server...")
    await server.run_stdio()


def run_server() -> None:
    """Entry point for running the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
