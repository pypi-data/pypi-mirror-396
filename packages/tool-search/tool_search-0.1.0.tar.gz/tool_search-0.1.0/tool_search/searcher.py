"""Semantic tool searcher using embeddings."""

from typing import Any

import numpy as np

from tool_search.indexer import ToolIndexer


class ToolSearcher:
    """Semantic search over indexed tools."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize searcher.

        Args:
            model_name: HuggingFace model for embeddings
        """
        self._indexer = ToolIndexer(model_name)

    def index_tools(self, tools: list[dict[str, Any]]) -> None:
        """Index a list of tools for search.

        Args:
            tools: List of tool definitions
        """
        self._indexer.add_tools(tools)

    def add_tool(self, tool: dict[str, Any]) -> None:
        """Add a single tool to the index.

        Args:
            tool: Tool definition
        """
        self._indexer.add_tool(tool)

    def search(
        self,
        query: str,
        top_k: int = 5,
        deferred_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Search for tools matching a query.

        Args:
            query: Natural language search query
            top_k: Maximum number of results to return
            deferred_only: If True, only return tools with defer_loading=True

        Returns:
            List of dicts with 'tool' and 'score' keys, sorted by relevance
        """
        if self._indexer.embeddings is None or len(self._indexer.tools) == 0:
            return []

        # Embed the query
        query_embedding = self._indexer.model.encode(query, convert_to_numpy=True)

        # Calculate cosine similarity (embeddings are normalized)
        similarities = np.dot(self._indexer.embeddings, query_embedding)

        # Get all indices sorted by similarity
        sorted_indices = np.argsort(similarities)[::-1]

        # Build results, optionally filtering for deferred tools
        results = []
        for idx in sorted_indices:
            if len(results) >= top_k:
                break

            tool = self._indexer.tools[idx]
            tool_name = tool.get("name", "")

            # Filter by defer_loading if requested
            if deferred_only and not self._indexer.is_deferred(tool_name):
                continue

            results.append({"tool": tool, "score": float(similarities[idx])})

        return results

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool definition or None
        """
        return self._indexer.get_tool(name)

    @staticmethod
    def to_tool_references(results: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Convert search results to tool_reference format.

        Args:
            results: Search results from search()

        Returns:
            List of tool_reference blocks with server info for tool_invoke
        """
        refs = []
        for r in results:
            ref = {
                "type": "tool_reference",
                "tool_name": r["tool"]["name"],
            }
            # Include server if available (for tool_invoke)
            if "_mcp_server" in r["tool"]:
                ref["server"] = r["tool"]["_mcp_server"]
            refs.append(ref)
        return refs

    def build_search_result(
        self,
        results: list[dict[str, Any]],
        tool_use_id: str,
        include_matches: bool = False,
    ) -> dict[str, Any]:
        """Build search result in Anthropic's tool_search_tool_result format.

        Args:
            results: Search results from search()
            tool_use_id: The tool_use_id from the request
            include_matches: Include score details for debugging

        Returns:
            Result dict matching Anthropic's tool_search_tool_result spec
        """
        tool_refs = self.to_tool_references(results)

        content: dict[str, Any] = {
            "type": "tool_search_tool_search_result",
            "tool_references": tool_refs,
        }

        if include_matches:
            matches = []
            for r in results:
                match = {
                    "name": r["tool"]["name"],
                    "score": round(r["score"], 4),
                    "description": r["tool"].get("description", ""),
                }
                # Include server for tool_invoke
                if "_mcp_server" in r["tool"]:
                    match["server"] = r["tool"]["_mcp_server"]
                # Include input_examples if present
                if "input_examples" in r["tool"]:
                    match["input_examples"] = r["tool"]["input_examples"]
                matches.append(match)
            content["matches"] = matches

        return {
            "type": "tool_search_tool_result",
            "tool_use_id": tool_use_id,
            "content": content,
        }

    @property
    def tool_count(self) -> int:
        """Number of indexed tools."""
        return len(self._indexer.tools)

    def clear(self) -> None:
        """Clear the index."""
        self._indexer.clear()
