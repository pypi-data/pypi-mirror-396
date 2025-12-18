"""Prompt discovery and management for devskills MCP server."""

import re
from pathlib import Path

import yaml


class PromptManager:
    """Manages prompt discovery and content retrieval.

    Prompts are markdown files with YAML frontmatter that define
    user-triggered entry points to skills.
    """

    def __init__(
        self,
        extra_paths: list[Path] | None = None,
        include_bundled: bool = True,
    ) -> None:
        """Initialize PromptManager with prompt paths.

        Args:
            extra_paths: Additional directories containing prompts/ subdirectories.
            include_bundled: Whether to include bundled default prompts.
        """
        self._prompt_paths: list[Path] = []

        # 1. Extra paths from CLI (highest priority)
        if extra_paths:
            for path in extra_paths:
                expanded = Path(path).expanduser().resolve()
                prompts_dir = expanded / "prompts"
                if prompts_dir.exists():
                    self._prompt_paths.append(prompts_dir)

        # 2. Bundled prompts (lowest priority)
        if include_bundled:
            bundled = Path(__file__).parent / "bundled_prompts"
            if bundled.exists():
                self._prompt_paths.append(bundled)

    def _discover_prompts(self) -> dict[str, Path]:
        """Discover all available prompts.

        Returns:
            Dict mapping prompt name (filename stem) to its file path.
        """
        prompts: dict[str, Path] = {}

        # Process in reverse order so earlier paths (higher priority) override
        for prompts_dir in reversed(self._prompt_paths):
            if not prompts_dir.exists():
                continue
            for item in prompts_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    name = item.stem
                    prompts[name] = item

        return prompts

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from prompt file.

        Args:
            content: Full content of the prompt markdown file.

        Returns:
            Dict with parsed frontmatter (name, description, etc.)
        """
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}

        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _get_body(self, content: str) -> str:
        """Get content after frontmatter.

        Args:
            content: Full content of the prompt markdown file.

        Returns:
            Content after the YAML frontmatter, stripped of leading/trailing whitespace.
        """
        match = re.match(r"^---\n.*?\n---\n?(.*)", content, re.DOTALL)
        return match.group(1).strip() if match else content.strip()

    def list_all(self) -> list[dict]:
        """Return list of all prompts with metadata.

        Returns:
            List of dicts with 'name' and 'description' keys.
        """
        prompts = self._discover_prompts()
        result = []

        for name, path in sorted(prompts.items()):
            try:
                content = path.read_text()
                fm = self._parse_frontmatter(content)
                result.append({
                    "name": fm.get("name", name),
                    "description": fm.get("description", ""),
                })
            except OSError:
                pass

        return result

    def get_body(self, name: str) -> str:
        """Get prompt body content (after frontmatter).

        Args:
            name: Prompt name to retrieve.

        Returns:
            Prompt body content.

        Raises:
            ValueError: If prompt not found.
        """
        prompts = self._discover_prompts()

        if name not in prompts:
            available = ", ".join(sorted(prompts.keys()))
            raise ValueError(f"Prompt '{name}' not found. Available: {available}")

        content = prompts[name].read_text()
        return self._get_body(content)
