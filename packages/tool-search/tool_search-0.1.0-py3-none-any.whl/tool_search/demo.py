#!/usr/bin/env python3
"""Demo script for tool_search module.

Usage:
    # Search with sample tools
    python -m tool_search.demo "weather forecast"

    # Discover from Factory MCP servers (linear, context7)
    python -m tool_search.demo --discover "stock prices"

    # Discover from all configured MCP servers
    python -m tool_search.demo --discover-all "documentation"
"""

import argparse
import asyncio

from tool_search import (
    ToolSearcher,
    discover_tools_from_all_configs,
    discover_tools_from_factory_config,
)

SAMPLE_TOOLS = [
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
]


async def main() -> None:
    """Main entry point for the demo script."""
    parser = argparse.ArgumentParser(description="Tool Search Demo")
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--discover", action="store_true", help="Discover tools from Factory MCP servers"
    )
    parser.add_argument("--discover-all", action="store_true", help="Discover from all MCP configs")
    parser.add_argument("--top-k", type=int, default=3, help="Number of results (default: 3)")
    args = parser.parse_args()

    print("\n🔍 Tool Search Demo")
    print(f"{'=' * 50}\n")

    # Get tools
    if args.discover_all:
        print("📡 Discovering tools from all MCP servers...")
        tools = await discover_tools_from_all_configs()
        if not tools:
            print("⚠️  No tools discovered, using samples")
            tools = SAMPLE_TOOLS
        else:
            print(f"✓ Discovered {len(tools)} tools\n")
    elif args.discover:
        print("📡 Discovering tools from Factory MCP servers...")
        tools = await discover_tools_from_factory_config()
        if not tools:
            print("⚠️  No tools discovered from Factory config, using samples")
            tools = SAMPLE_TOOLS
        else:
            print(f"✓ Discovered {len(tools)} tools\n")
    else:
        tools = SAMPLE_TOOLS
        print(f"📦 Using {len(tools)} sample tools\n")

    # Create searcher
    print("🧠 Creating embeddings...")
    searcher = ToolSearcher()
    searcher.index_tools(tools)
    print(f"✓ Indexed {searcher.tool_count} tools\n")

    # Search
    print(f'🔎 Searching for: "{args.query}"\n')
    results = searcher.search(args.query, top_k=args.top_k)

    print("📋 Results:")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        tool = result["tool"]
        score = result["score"]
        print(f"\n{i}. {tool['name']} (score: {score:.3f})")
        print(f"   {tool.get('description', 'No description')}")
        if "_mcp_server" in tool:
            print(f"   [from: {tool['_mcp_server']}]")

    # Show tool_reference output
    refs = searcher.to_tool_references(results)
    print("\n\n📤 tool_reference output:")
    print("-" * 50)
    for ref in refs:
        print(f"  {ref}")

    print()


if __name__ == "__main__":
    asyncio.run(main())
