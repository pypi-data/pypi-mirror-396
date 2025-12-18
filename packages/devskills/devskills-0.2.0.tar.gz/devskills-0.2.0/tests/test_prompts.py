"""Tests for PromptManager - prompt discovery and content retrieval."""

import pytest
from pathlib import Path

from devskills.prompts import PromptManager


@pytest.fixture
def temp_prompts_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure with test prompts."""
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()

    # Create a valid prompt file
    (prompts_dir / "test-prompt.md").write_text(
        """---
name: test-prompt
description: A test prompt for unit testing
---

Use the test-skill skill exactly as written.
"""
    )

    # Create another prompt file
    (prompts_dir / "another-prompt.md").write_text(
        """---
name: another-prompt
description: Another test prompt
---

Follow the another-skill instructions.
"""
    )

    return tmp_path


@pytest.fixture
def temp_prompts_with_override(tmp_path: Path) -> tuple[Path, Path]:
    """Create two directories where the first overrides the second."""
    # Higher priority path
    high_priority = tmp_path / "high"
    high_priority.mkdir()
    high_prompts = high_priority / "prompts"
    high_prompts.mkdir()

    (high_prompts / "shared-prompt.md").write_text(
        """---
name: shared-prompt
description: High priority version
---

This is the high priority version.
"""
    )

    # Lower priority path
    low_priority = tmp_path / "low"
    low_priority.mkdir()
    low_prompts = low_priority / "prompts"
    low_prompts.mkdir()

    (low_prompts / "shared-prompt.md").write_text(
        """---
name: shared-prompt
description: Low priority version
---

This is the low priority version.
"""
    )

    (low_prompts / "only-in-low.md").write_text(
        """---
name: only-in-low
description: Only exists in low priority
---

Only in low.
"""
    )

    return high_priority, low_priority


class TestPromptDiscovery:
    """Tests for prompt discovery functionality."""

    def test_discovers_md_files_in_prompts_directory(self, temp_prompts_dir: Path):
        """PromptManager finds .md files in the prompts/ subdirectory."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)
        prompts = manager.list_all()

        names = [p["name"] for p in prompts]
        assert "test-prompt" in names
        assert "another-prompt" in names

    def test_ignores_non_md_files(self, tmp_path: Path):
        """PromptManager only discovers .md files."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "valid.md").write_text(
            """---
name: valid
description: Valid prompt
---

Content here.
"""
        )
        (prompts_dir / "invalid.txt").write_text("Not a prompt")
        (prompts_dir / "also-invalid.yaml").write_text("name: nope")

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        assert len(prompts) == 1
        assert prompts[0]["name"] == "valid"

    def test_handles_missing_prompts_directory(self, tmp_path: Path):
        """PromptManager handles paths that don't have a prompts/ subdirectory."""
        # tmp_path exists but has no prompts/ subdirectory
        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        assert prompts == []


class TestListAll:
    """Tests for list_all() method."""

    def test_returns_name_and_description_from_frontmatter(self, temp_prompts_dir: Path):
        """list_all() returns name and description parsed from YAML frontmatter."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)
        prompts = manager.list_all()

        test_prompt = next(p for p in prompts if p["name"] == "test-prompt")
        assert test_prompt["description"] == "A test prompt for unit testing"

    def test_uses_filename_as_fallback_name(self, tmp_path: Path):
        """list_all() uses filename stem when frontmatter has no name."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "no-name-field.md").write_text(
            """---
description: Has description but no name field
---

Content.
"""
        )

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        assert len(prompts) == 1
        assert prompts[0]["name"] == "no-name-field"
        assert prompts[0]["description"] == "Has description but no name field"

    def test_handles_empty_description(self, tmp_path: Path):
        """list_all() handles prompts without description."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "minimal.md").write_text(
            """---
name: minimal
---

Just content.
"""
        )

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        assert len(prompts) == 1
        assert prompts[0]["name"] == "minimal"
        assert prompts[0]["description"] == ""


class TestGetBody:
    """Tests for get_body() method."""

    def test_returns_content_after_frontmatter(self, temp_prompts_dir: Path):
        """get_body() returns only the content after the YAML frontmatter."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)
        body = manager.get_body("test-prompt")

        assert body == "Use the test-skill skill exactly as written."

    def test_raises_for_unknown_prompt(self, temp_prompts_dir: Path):
        """get_body() raises ValueError for non-existent prompts."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)

        with pytest.raises(ValueError, match="Prompt 'nonexistent' not found"):
            manager.get_body("nonexistent")

    def test_error_message_lists_available_prompts(self, temp_prompts_dir: Path):
        """get_body() error message includes available prompt names."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)

        with pytest.raises(ValueError) as exc_info:
            manager.get_body("nonexistent")

        assert "test-prompt" in str(exc_info.value)
        assert "another-prompt" in str(exc_info.value)

    def test_handles_no_frontmatter(self, tmp_path: Path):
        """get_body() handles files without frontmatter."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "no-frontmatter.md").write_text("Just plain content.")

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        body = manager.get_body("no-frontmatter")

        assert body == "Just plain content."


class TestPathPriority:
    """Tests for path priority (earlier paths override later paths)."""

    def test_earlier_paths_override_later_paths(
        self, temp_prompts_with_override: tuple[Path, Path]
    ):
        """Prompts in earlier paths override those with same name in later paths."""
        high_priority, low_priority = temp_prompts_with_override

        # High priority path is first in the list
        manager = PromptManager(
            extra_paths=[high_priority, low_priority], include_bundled=False
        )

        body = manager.get_body("shared-prompt")
        assert "high priority" in body

        prompts = manager.list_all()
        shared = next(p for p in prompts if p["name"] == "shared-prompt")
        assert shared["description"] == "High priority version"

    def test_prompts_from_all_paths_are_included(
        self, temp_prompts_with_override: tuple[Path, Path]
    ):
        """Prompts unique to lower priority paths are still included."""
        high_priority, low_priority = temp_prompts_with_override

        manager = PromptManager(
            extra_paths=[high_priority, low_priority], include_bundled=False
        )
        prompts = manager.list_all()

        names = [p["name"] for p in prompts]
        assert "shared-prompt" in names
        assert "only-in-low" in names


class TestBundledPrompts:
    """Tests for bundled prompts functionality."""

    def test_includes_bundled_when_flag_true(self):
        """PromptManager includes bundled prompts when include_bundled=True."""
        manager = PromptManager(include_bundled=True)
        prompts = manager.list_all()

        # Should find bundled prompts (once we create them)
        names = [p["name"] for p in prompts]
        assert "mcp-builder" in names
        assert "skill-creator" in names

    def test_excludes_bundled_when_flag_false(self, temp_prompts_dir: Path):
        """PromptManager excludes bundled prompts when include_bundled=False."""
        manager = PromptManager(extra_paths=[temp_prompts_dir], include_bundled=False)
        prompts = manager.list_all()

        names = [p["name"] for p in prompts]
        # Should only have our test prompts, not bundled ones
        assert "mcp-builder" not in names
        assert "skill-creator" not in names


class TestFrontmatterParsing:
    """Tests for YAML frontmatter parsing edge cases."""

    def test_handles_invalid_yaml(self, tmp_path: Path):
        """PromptManager handles malformed YAML gracefully."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "bad-yaml.md").write_text(
            """---
name: [unclosed bracket
description: broken
---

Content anyway.
"""
        )

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        # Should still discover the file, using filename as fallback
        assert len(prompts) == 1
        assert prompts[0]["name"] == "bad-yaml"

    def test_handles_empty_frontmatter(self, tmp_path: Path):
        """PromptManager handles empty frontmatter block."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        (prompts_dir / "empty-fm.md").write_text(
            """---
---

Content after empty frontmatter.
"""
        )

        manager = PromptManager(extra_paths=[tmp_path], include_bundled=False)
        prompts = manager.list_all()

        assert len(prompts) == 1
        assert prompts[0]["name"] == "empty-fm"
        assert prompts[0]["description"] == ""
