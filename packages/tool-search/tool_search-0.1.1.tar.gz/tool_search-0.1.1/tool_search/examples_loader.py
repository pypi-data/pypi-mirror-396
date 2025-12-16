"""Load and manage tool examples from YAML files."""

import logging
from pathlib import Path
from typing import Any

import jsonschema
import yaml

logger = logging.getLogger(__name__)


class ExamplesLoader:
    """Load and manage tool examples from YAML files."""

    def __init__(self, examples_dir: Path | None = None):
        """Initialize the loader.

        Args:
            examples_dir: Directory containing example YAML files.
                         Defaults to tool_search/examples/
        """
        if examples_dir is None:
            self.examples_dir = Path(__file__).parent / "examples"
        else:
            self.examples_dir = examples_dir

        # Cache: server_name -> tool_name -> list of examples
        self._cache: dict[str, dict[str, list[dict[str, Any]]]] = {}

    def load_file(self, file_path: Path) -> None:
        """Load examples from a single YAML file.

        Args:
            file_path: Path to YAML file
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as e:
            logger.debug(f"Failed to parse {file_path}: {e}")
            return

        if not isinstance(data, dict):
            logger.debug(f"Invalid format in {file_path}: expected dict")
            return

        server = data.get("server")
        if not server:
            logger.debug(f"Missing 'server' field in {file_path}")
            return

        tools = data.get("tools", {})
        if not isinstance(tools, dict):
            logger.debug(f"Invalid 'tools' field in {file_path}")
            return

        if server not in self._cache:
            self._cache[server] = {}

        for tool_name, examples in tools.items():
            if isinstance(examples, list):
                self._cache[server][tool_name] = examples

    def load_all(self) -> None:
        """Load all YAML files from the examples directory."""
        if not self.examples_dir.exists():
            logger.debug(f"Examples directory not found: {self.examples_dir}")
            return

        for yaml_file in self.examples_dir.glob("*.yaml"):
            self.load_file(yaml_file)

        logger.debug(f"Loaded examples for {len(self._cache)} servers")

    def get_examples(self, server: str, tool: str) -> list[dict[str, Any]] | None:
        """Get examples for a specific tool.

        Args:
            server: Server name
            tool: Tool name

        Returns:
            List of example input dicts, or None if not found
        """
        server_examples = self._cache.get(server)
        if not server_examples:
            return None
        return server_examples.get(tool)

    def validate_examples(
        self,
        tool_name: str,
        examples: list[dict[str, Any]],
        schema: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Validate examples against a JSON schema.

        Args:
            tool_name: Tool name (for logging)
            examples: List of example input dicts
            schema: JSON schema to validate against, or None to skip validation

        Returns:
            List of valid examples (invalid ones filtered out)
        """
        if schema is None:
            return examples

        valid = []
        for i, example in enumerate(examples):
            try:
                jsonschema.validate(example, schema)
                valid.append(example)
            except jsonschema.ValidationError as e:
                logger.debug(f"Example {i} for {tool_name} failed validation: {e.message}")
        return valid
