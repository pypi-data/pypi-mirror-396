"""Tests for CLI commands."""

import pytest
from pathlib import Path
from click.testing import CliRunner

from devskills.cli import main


@pytest.fixture
def runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestInitCommand:
    """Tests for the init command."""

    def test_init_creates_prompts_directory(self, runner: CliRunner, tmp_path: Path):
        """init command creates prompts/ directory in addition to skills/."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["init", "my-team-skills"])

            assert result.exit_code == 0, result.output
            assert (Path("my-team-skills") / "prompts").is_dir()
            assert (Path("my-team-skills") / "skills").is_dir()

    def test_init_creates_prompts_gitkeep(self, runner: CliRunner, tmp_path: Path):
        """init command creates .gitkeep in prompts/ directory."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["init", "my-team-skills"])

            assert result.exit_code == 0, result.output
            gitkeep = Path("my-team-skills") / "prompts" / ".gitkeep"
            assert gitkeep.exists()

    def test_init_outputs_prompts_directory_creation(
        self, runner: CliRunner, tmp_path: Path
    ):
        """init command outputs that prompts/ was created."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ["init", "my-team-skills"])

            assert result.exit_code == 0
            assert "prompts/" in result.output

    def test_init_in_existing_directory_creates_prompts(
        self, runner: CliRunner, tmp_path: Path
    ):
        """init in existing directory still creates prompts/ if missing."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("existing").mkdir()
            result = runner.invoke(main, ["init", "existing"])

            assert result.exit_code == 0, result.output
            assert (Path("existing") / "prompts").is_dir()
