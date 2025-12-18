"""Skill discovery and management for devskills MCP server."""

import os
import re
import warnings
from pathlib import Path

import yaml


class SkillManager:
    """Manages skill discovery and content retrieval.

    Skills are directories containing a SKILL.md file with YAML frontmatter.
    Optional scripts/ and references/ subdirectories contain supporting files.

    Skill paths are configured via (in priority order):
    1. extra_paths parameter (from CLI --skills-path)
    2. DEVSKILLS_SKILLS_PATH env var (colon-separated paths)
    3. DEVSKILLS_LOCAL_SKILLS env var (deprecated, for backward compat)
    4. Bundled skills in the package (lowest priority, always included)

    Skills from higher priority sources override those with matching names.
    """

    def __init__(
        self,
        extra_paths: list[Path] | None = None,
        include_bundled: bool = True,
    ) -> None:
        """Initialize SkillManager with skill paths.

        Args:
            extra_paths: Additional skill directories (highest priority).
            include_bundled: Whether to include bundled default skills.
        """
        self._skill_paths: list[Path] = []
        self._writable_paths: list[Path] = []  # User-provided paths for skill creation

        # 1. Extra paths from CLI (highest priority)
        if extra_paths:
            for path in extra_paths:
                expanded = Path(path).expanduser().resolve()
                if expanded.exists():
                    self._skill_paths.append(expanded)
                    self._writable_paths.append(expanded)

        # 2. DEVSKILLS_SKILLS_PATH env var (colon-separated)
        env_paths = os.environ.get("DEVSKILLS_SKILLS_PATH", "")
        for path_str in env_paths.split(":"):
            if path_str.strip():
                path = Path(path_str.strip()).expanduser().resolve()
                if path.exists() and path not in self._skill_paths:
                    self._skill_paths.append(path)
                    self._writable_paths.append(path)

        # 3. Backward compat: DEVSKILLS_LOCAL_SKILLS (deprecated)
        local_skills_env = os.environ.get("DEVSKILLS_LOCAL_SKILLS")
        if local_skills_env:
            warnings.warn(
                "DEVSKILLS_LOCAL_SKILLS is deprecated. "
                "Use DEVSKILLS_SKILLS_PATH or --skills-path instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            local_path = Path(local_skills_env).expanduser().resolve()
            if local_path.exists() and local_path not in self._skill_paths:
                self._skill_paths.append(local_path)
                self._writable_paths.append(local_path)

        # 4. Bundled skills (lowest priority, always available)
        if include_bundled:
            bundled = Path(__file__).parent / "bundled_skills"
            if bundled.exists():
                self._skill_paths.append(bundled)

    def get_writable_paths(self) -> list[Path]:
        """Return paths where new skills can be created.

        Returns only user-provided paths, not bundled skills directory.
        """
        return self._writable_paths.copy()

    def _discover_skills(self) -> dict[str, Path]:
        """Discover all available skills, with earlier paths taking priority.

        Returns:
            Dict mapping skill name to its directory path.
        """
        skills: dict[str, Path] = {}

        # Process in reverse order so earlier paths (higher priority) override
        for skills_dir in reversed(self._skill_paths):
            if not skills_dir.exists():
                continue
            for item in skills_dir.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    skill_file = item / "SKILL.md"
                    if skill_file.exists():
                        skills[item.name] = item

        return skills

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from SKILL.md content.

        Args:
            content: Full content of SKILL.md file.

        Returns:
            Dict with parsed frontmatter (name, description, etc.)
        """
        # Match frontmatter between --- markers
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}

        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def list_all(self) -> list[dict]:
        """Return list of all available skills with name and description.

        Returns:
            List of dicts with 'name' and 'description' keys.
        """
        skills = self._discover_skills()
        result = []

        for name, path in sorted(skills.items()):
            skill_file = path / "SKILL.md"
            try:
                content = skill_file.read_text()
                frontmatter = self._parse_frontmatter(content)
                result.append({
                    "name": frontmatter.get("name", name),
                    "description": frontmatter.get("description", "No description available"),
                })
            except OSError:
                result.append({
                    "name": name,
                    "description": "Unable to read skill description",
                })

        return result

    def get_content(self, name: str) -> str:
        """Return full SKILL.md content for a skill.

        Args:
            name: Skill name to retrieve.

        Returns:
            Full content of SKILL.md file.

        Raises:
            ValueError: If skill not found.
        """
        skills = self._discover_skills()

        if name not in skills:
            available = ", ".join(sorted(skills.keys()))
            raise ValueError(
                f"Skill '{name}' not found. Available skills: {available}"
            )

        skill_file = skills[name] / "SKILL.md"
        try:
            return skill_file.read_text()
        except OSError as e:
            raise ValueError(f"Error reading skill '{name}': {e}")

    def get_script(self, skill: str, filename: str) -> str:
        """Return content of a script file from a skill's scripts/ folder.

        Args:
            skill: Skill name.
            filename: Script filename (e.g., 'hello.py').

        Returns:
            Raw script content.

        Raises:
            ValueError: If skill or script not found.
        """
        skills = self._discover_skills()

        if skill not in skills:
            available = ", ".join(sorted(skills.keys()))
            raise ValueError(
                f"Skill '{skill}' not found. Available skills: {available}"
            )

        script_path = skills[skill] / "scripts" / filename

        if not script_path.exists():
            scripts_dir = skills[skill] / "scripts"
            if scripts_dir.exists():
                available_scripts = [f.name for f in scripts_dir.iterdir() if f.is_file()]
                if available_scripts:
                    raise ValueError(
                        f"Script '{filename}' not found in skill '{skill}'. "
                        f"Available scripts: {', '.join(available_scripts)}"
                    )
            raise ValueError(
                f"Script '{filename}' not found in skill '{skill}'. "
                f"No scripts directory exists for this skill."
            )

        try:
            return script_path.read_text()
        except OSError as e:
            raise ValueError(f"Error reading script '{filename}' from skill '{skill}': {e}")

    def get_reference(self, skill: str, filename: str) -> str:
        """Return content of a reference document from a skill's references/ folder.

        Args:
            skill: Skill name.
            filename: Reference filename (e.g., 'notes.md').

        Returns:
            Reference document content.

        Raises:
            ValueError: If skill or reference file not found.
        """
        skills = self._discover_skills()

        if skill not in skills:
            available = ", ".join(sorted(skills.keys()))
            raise ValueError(
                f"Skill '{skill}' not found. Available skills: {available}"
            )

        ref_path = skills[skill] / "references" / filename

        if not ref_path.exists():
            refs_dir = skills[skill] / "references"
            if refs_dir.exists():
                available_refs = [f.name for f in refs_dir.iterdir() if f.is_file()]
                if available_refs:
                    raise ValueError(
                        f"Reference '{filename}' not found in skill '{skill}'. "
                        f"Available references: {', '.join(available_refs)}"
                    )
            raise ValueError(
                f"Reference '{filename}' not found in skill '{skill}'. "
                f"No references directory exists for this skill."
            )

        try:
            return ref_path.read_text()
        except OSError as e:
            raise ValueError(f"Error reading reference '{filename}' from skill '{skill}': {e}")
