"""Tool indexer - Convert tool definitions to embeddings."""

from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


def tool_to_text(tool: dict[str, Any]) -> str:
    """Convert a tool definition to searchable text.

    Combines tool name, description, and parameter information
    into a single text representation for embedding.

    Args:
        tool: Tool definition dict with name, description, inputSchema

    Returns:
        Text representation suitable for embedding
    """
    parts = [
        f"Tool: {tool.get('name', 'unknown')}",
        f"Description: {tool.get('description', 'No description')}",
    ]

    # Extract parameter information
    schema = tool.get("inputSchema") or tool.get("input_schema", {})
    properties = schema.get("properties", {})

    if properties:
        param_texts = []
        for param_name, param_info in properties.items():
            param_desc = param_info.get("description", "")
            param_type = param_info.get("type", "")
            enum_values = param_info.get("enum", [])

            param_text = f"{param_name} ({param_type}): {param_desc}"
            if enum_values:
                param_text += f" [options: {', '.join(enum_values)}]"
            param_texts.append(param_text)

        if param_texts:
            parts.append("Parameters: " + "; ".join(param_texts))

    return "\n".join(parts)


class ToolIndexer:
    """Index tool definitions with embeddings for semantic search."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize indexer with embedding model.

        Args:
            model_name: HuggingFace model name for embeddings
        """
        self._model: SentenceTransformer | None = None
        self._model_name = model_name
        self.tools: list[dict[str, Any]] = []
        self.tool_texts: list[str] = []
        self.embeddings: np.ndarray | None = None
        self._name_to_index: dict[str, int] = {}
        self._deferred_tools: set[str] = set()

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the embedding model."""
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def add_tool(self, tool: dict[str, Any]) -> None:
        """Add a single tool to the index.

        Args:
            tool: Tool definition dict
        """
        self.add_tools([tool])

    def add_tools(self, tools: list[dict[str, Any]]) -> None:
        """Add multiple tools to the index.

        Args:
            tools: List of tool definition dicts
        """
        if not tools:
            return

        # Convert tools to text
        new_texts = [tool_to_text(tool) for tool in tools]

        # Generate embeddings
        new_embeddings = self.model.encode(new_texts, convert_to_numpy=True)

        # Update index
        start_idx = len(self.tools)
        for i, tool in enumerate(tools):
            name = tool.get("name", f"tool_{start_idx + i}")
            self._name_to_index[name] = start_idx + i

            # Track defer_loading status
            if tool.get("defer_loading", False):
                self._deferred_tools.add(name)

        self.tools.extend(tools)
        self.tool_texts.extend(new_texts)

        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Get tool definition by name.

        Args:
            name: Tool name

        Returns:
            Tool definition or None if not found
        """
        idx = self._name_to_index.get(name)
        if idx is not None:
            return self.tools[idx]
        return None

    def is_deferred(self, name: str) -> bool:
        """Check if a tool is marked as deferred.

        Args:
            name: Tool name

        Returns:
            True if tool has defer_loading=True, False otherwise
        """
        return name in self._deferred_tools

    def get_deferred_tool_names(self) -> set[str]:
        """Get names of all deferred tools.

        Returns:
            Set of tool names with defer_loading=True
        """
        return self._deferred_tools.copy()

    def get_immediate_tool_names(self) -> set[str]:
        """Get names of all non-deferred tools.

        Returns:
            Set of tool names without defer_loading or defer_loading=False
        """
        all_names = set(self._name_to_index.keys())
        return all_names - self._deferred_tools

    def clear(self) -> None:
        """Clear all indexed tools."""
        self.tools = []
        self.tool_texts = []
        self.embeddings = None
        self._name_to_index = {}
        self._deferred_tools = set()
