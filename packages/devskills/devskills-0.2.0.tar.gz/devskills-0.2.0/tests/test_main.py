"""Tests for MCP server prompt registration."""

import pytest
from pathlib import Path

from devskills.main import create_server


@pytest.fixture
def temp_prompts_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure with test prompts."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    (prompts_dir / "test-prompt.md").write_text(
        """---
name: test-prompt
description: A test prompt for integration testing
---

Use the test-skill skill exactly as written.
"""
    )

    return tmp_path


class TestPromptRegistration:
    """Tests for MCP prompt registration."""

    def test_server_registers_bundled_prompts(self):
        """Server registers bundled prompts when include_bundled=True."""
        server = create_server(include_bundled=True)

        # FastMCP stores prompts in _prompt_manager
        prompt_names = list(server._prompt_manager._prompts.keys())

        assert "mcp-builder" in prompt_names
        assert "skill-creator" in prompt_names

    def test_server_excludes_bundled_prompts_when_disabled(self, temp_prompts_dir: Path):
        """Server excludes bundled prompts when include_bundled=False."""
        server = create_server(
            extra_paths=[temp_prompts_dir],
            include_bundled=False,
        )

        prompt_names = list(server._prompt_manager._prompts.keys())

        assert "mcp-builder" not in prompt_names
        assert "skill-creator" not in prompt_names
        assert "test-prompt" in prompt_names

    def test_server_registers_prompts_from_extra_paths(self, temp_prompts_dir: Path):
        """Server registers prompts from extra paths."""
        server = create_server(
            extra_paths=[temp_prompts_dir],
            include_bundled=False,
        )

        prompt_names = list(server._prompt_manager._prompts.keys())

        assert "test-prompt" in prompt_names

    @pytest.mark.asyncio
    async def test_prompt_returns_body_as_message(self, temp_prompts_dir: Path):
        """Calling a registered prompt returns the body as a PromptMessage."""
        server = create_server(
            extra_paths=[temp_prompts_dir],
            include_bundled=False,
        )

        # Get the prompt handler
        prompt_handler = server._prompt_manager._prompts["test-prompt"]

        # Call the prompt (no arguments in v1)
        messages = await prompt_handler.fn()

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert "Use the test-skill skill exactly as written." in messages[0].content.text
