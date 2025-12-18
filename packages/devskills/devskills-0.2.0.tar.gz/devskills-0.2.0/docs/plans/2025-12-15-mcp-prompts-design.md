# MCP Prompts Feature Design

**Date:** 2025-12-15
**Status:** Draft

## Problem Statement

Currently, devskills exposes skills only as MCP tools (model-triggered). Users have requested the ability to explicitly invoke skills via user-triggered mechanisms like slash commands.

## Background

### MCP Tools vs MCP Prompts

| Aspect | MCP Tools (current) | MCP Prompts (proposed) |
|--------|---------------------|------------------------|
| Trigger | Model decides when to call | User explicitly invokes |
| Discovery | Agent reads descriptions, matches to task | User browses available prompts |
| Control | AI autonomous | User controlled |
| Use case | Agent "just knows" when to apply | User wants explicit control |

### Research Findings

1. **MCP Protocol** supports prompts natively with structured arguments
2. **Superpowers repo** separates skills (20) from commands (3) - not every skill needs a user-facing entry point
3. **Commands are thin wrappers** that point to skills: "Use the X skill exactly as written"
4. **Parameters can be omitted** - the LLM asks for context dynamically based on skill instructions

## Design Decision

**Approach:** Separate concepts (skills vs prompts) without explicit parameters

- **Skills** = source of truth, model-triggered (existing)
- **Prompts** = thin wrappers, user-triggered entry points (new)
- **No parameters in v1** - LLM gathers context dynamically based on skill instructions
- **Not every skill gets a prompt** - only user-facing workflows

This follows the superpowers pattern and keeps implementation simple.

## Directory Structure

```
devskills/
├── cli.py                  # Update init commands
├── main.py                 # Add prompt registration
├── skills.py               # Existing (unchanged)
├── prompts.py              # NEW: PromptManager
├── bundled_skills/         # Existing (unchanged)
│   ├── mcp-builder/
│   │   └── SKILL.md
│   └── skill-creator/
│       └── SKILL.md
└── bundled_prompts/        # NEW
    ├── mcp-builder.md
    └── skill-creator.md
```

### User's Skill Directory

After `devskills init`:

```
my-team-skills/
├── skills/                 # Model-triggered workflows
│   └── my-skill/
│       └── SKILL.md
└── prompts/                # User-triggered entry points (optional)
    └── my-skill.md
```

## Prompt File Format

`bundled_prompts/mcp-builder.md`:

```markdown
---
name: mcp-builder
description: Build a high-quality MCP server with guided workflow
---

Use the mcp-builder skill exactly as written.
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Prompt identifier (should match skill name if wrapping a skill) |
| `description` | Yes | Short description shown in prompt listings |
| `arguments` | No | Reserved for future use (v2) |

## Implementation

### New Module: `prompts.py`

```python
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
        """Discover all available prompts."""
        prompts: dict[str, Path] = {}

        for prompts_dir in reversed(self._prompt_paths):
            if not prompts_dir.exists():
                continue
            for item in prompts_dir.iterdir():
                if item.is_file() and item.suffix == ".md":
                    name = item.stem
                    prompts[name] = item

        return prompts

    def _parse_frontmatter(self, content: str) -> dict:
        """Parse YAML frontmatter from prompt file."""
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            return {}

    def _get_body(self, content: str) -> str:
        """Get content after frontmatter."""
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
```

### Updates to `main.py`

```python
from mcp.types import PromptMessage, TextContent

from .skills import SkillManager
from .prompts import PromptManager


def create_server(
    extra_paths: list[Path] | None = None,
    include_bundled: bool = True,
) -> FastMCP:

    mcp = FastMCP("devskills")
    skills = SkillManager(extra_paths=extra_paths, include_bundled=include_bundled)
    prompts = PromptManager(extra_paths=extra_paths, include_bundled=include_bundled)

    # === Existing tools (unchanged) ===
    # ... list_skills, get_skill, get_script, get_reference, get_skill_paths ...

    # === NEW: Register prompts ===
    for prompt_info in prompts.list_all():
        _register_prompt(mcp, prompts, prompt_info)

    return mcp


def _register_prompt(mcp: FastMCP, prompts: PromptManager, prompt_info: dict):
    """Register a single prompt with the MCP server."""
    prompt_name = prompt_info["name"]
    prompt_desc = prompt_info["description"]

    @mcp.prompt(name=prompt_name, description=prompt_desc)
    async def handler() -> list[PromptMessage]:
        body = prompts.get_body(prompt_name)
        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=body)
            )
        ]
```

### Updates to `cli.py`

Update `init` command to create `prompts/` directory:

```python
@cli.command()
@click.argument("path", type=click.Path())
def init(path: str):
    """Initialize a team skills repository."""
    repo_path = Path(path)

    # Create directory structure
    (repo_path / "skills").mkdir(parents=True, exist_ok=True)
    (repo_path / "prompts").mkdir(parents=True, exist_ok=True)  # NEW

    # ... rest of init logic ...
```

### Bundled Prompts

`devskills/bundled_prompts/mcp-builder.md`:

```markdown
---
name: mcp-builder
description: Build a high-quality MCP server with guided workflow
---

Use the mcp-builder skill exactly as written.
```

`devskills/bundled_prompts/skill-creator.md`:

```markdown
---
name: skill-creator
description: Create a new devskills skill with proper structure
---

Use the skill-creator skill exactly as written.
```

## User Flow

### Prompt-Triggered (new)

```
1. User invokes /mcp__devskills__mcp-builder (or equivalent in their client)
2. Prompt returns message: "Use the mcp-builder skill exactly as written."
3. Model reads message, recognizes it needs to fetch the skill
4. Model calls get_skill("mcp-builder") tool
5. Model receives SKILL.md content
6. Model follows skill instructions, calling get_reference() as needed
7. Model asks user for context (what service to integrate, etc.)
```

### Tool-Triggered (existing, unchanged)

```
1. User asks: "Help me build an MCP server for GitHub"
2. Model recognizes context, calls get_skill("mcp-builder")
3. Model receives SKILL.md content
4. Model follows skill instructions...
```

Both flows converge at step 4 - the skill instructions are the single source of truth.

## Future Enhancements (v2)

### Adding Parameters

If needed later, prompts can define arguments:

```markdown
---
name: mcp-builder
description: Build a high-quality MCP server with guided workflow
arguments:
  - name: language
    description: Target language (python or typescript)
    required: false
  - name: service
    description: The API or service to integrate
    required: false
---

Use the mcp-builder skill exactly as written.

{{#if language}}Target language: {{language}}{{/if}}
{{#if service}}Service to integrate: {{service}}{{/if}}
```

This would require:
1. Adding `arguments` to `list_all()` return value
2. Updating prompt registration to include argument schema
3. Adding `render()` method with template substitution

## Testing

1. **Unit tests** for `PromptManager`:
   - `test_discover_prompts` - finds .md files in prompt paths
   - `test_list_all` - returns name and description
   - `test_get_body` - returns content after frontmatter
   - `test_priority` - earlier paths override later paths

2. **Integration test**:
   - Start server with test prompts
   - Call `prompts/list` - verify prompts appear
   - Call `prompts/get` - verify body returned as message

## Migration

No migration needed - this is purely additive. Existing skills and tools continue to work unchanged.

## Open Questions

1. Should `init-skill` also create a matching prompt file? (Probably optional flag)
2. Should we add a `init-prompt` CLI command? (Probably not needed for v1)
