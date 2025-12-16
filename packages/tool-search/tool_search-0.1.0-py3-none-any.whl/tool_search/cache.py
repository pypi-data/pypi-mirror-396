"""Embedding cache for persistent storage."""

import hashlib
import json
import os
from typing import Any

import numpy as np


class EmbeddingCache:
    """Cache for tool embeddings on disk."""

    TOOLS_FILE = "tools.json"
    EMBEDDINGS_FILE = "embeddings.npz"
    HASH_FILE = "tools_hash.txt"

    def __init__(self, cache_dir: str | None = None):
        """Initialize cache.

        Args:
            cache_dir: Directory for cache files. Defaults to ~/.factory/tool-search/
        """
        if cache_dir is None:
            cache_dir = os.path.expanduser("~/.factory/tool-search")
        self.cache_dir = cache_dir

    def _ensure_dir(self) -> None:
        """Ensure cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)

    def _tools_path(self) -> str:
        return os.path.join(self.cache_dir, self.TOOLS_FILE)

    def _embeddings_path(self) -> str:
        return os.path.join(self.cache_dir, self.EMBEDDINGS_FILE)

    def _hash_path(self) -> str:
        return os.path.join(self.cache_dir, self.HASH_FILE)

    @staticmethod
    def _compute_hash(tools: list[dict[str, Any]]) -> str:
        """Compute hash of tool definitions."""
        # Sort keys for consistent hashing
        json_str = json.dumps(tools, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def save(self, tools: list[dict[str, Any]], embeddings: np.ndarray) -> None:
        """Save tools and embeddings to cache.

        Args:
            tools: List of tool definitions
            embeddings: Numpy array of embeddings
        """
        self._ensure_dir()

        # Save tools
        with open(self._tools_path(), "w") as f:
            json.dump(tools, f)

        # Save embeddings
        np.savez_compressed(self._embeddings_path(), embeddings=embeddings)

        # Save hash
        with open(self._hash_path(), "w") as f:
            f.write(self._compute_hash(tools))

    def load(self) -> tuple[list[dict[str, Any]], np.ndarray] | None:
        """Load tools and embeddings from cache.

        Returns:
            Tuple of (tools, embeddings) or None if cache doesn't exist
        """
        tools_path = self._tools_path()
        embeddings_path = self._embeddings_path()

        if not os.path.exists(tools_path) or not os.path.exists(embeddings_path):
            return None

        with open(tools_path) as f:
            tools = json.load(f)

        data = np.load(embeddings_path)
        embeddings = data["embeddings"]

        return tools, embeddings

    def is_valid(self, tools: list[dict[str, Any]]) -> bool:
        """Check if cache is valid for given tools.

        Args:
            tools: Current tool definitions

        Returns:
            True if cache matches current tools
        """
        hash_path = self._hash_path()
        if not os.path.exists(hash_path):
            return False

        with open(hash_path) as f:
            cached_hash = f.read().strip()

        return cached_hash == self._compute_hash(tools)

    def clear(self) -> None:
        """Remove all cache files."""
        for filename in [self.TOOLS_FILE, self.EMBEDDINGS_FILE, self.HASH_FILE]:
            path = os.path.join(self.cache_dir, filename)
            if os.path.exists(path):
                os.remove(path)
