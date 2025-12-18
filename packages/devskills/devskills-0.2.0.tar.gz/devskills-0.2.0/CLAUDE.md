# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

DevSkills is an MCP (Model Context Protocol) server that exposes reusable "skills" as tools for AI coding agents. It works with Claude Code, GitHub Copilot, Cursor, and other MCP-compatible tools.

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server locally
uv run devskills --skills-path ./test-skills

# Run CLI commands
uv run devskills --help
uv run devskills init /tmp/test-repo
uv run devskills init-skill my-skill --path ./skills

# Test skill discovery
uv run python -c "
from devskills.skills import SkillManager
from pathlib import Path
sm = SkillManager(extra_paths=[Path('./test-skills')])
print([s['name'] for s in sm.list_all()])
"
```

## Architecture

### Core Components

- **`devskills/cli.py`** - Click-based CLI with three modes:
  - Default (no subcommand): runs MCP server
  - `init`: creates team skills repository with MCP configs
  - `init-skill`: creates skill from template

- **`devskills/main.py`** - MCP server using FastMCP. Registers 5 tools:
  - `list_skills()`, `get_skill()`, `get_script()`, `get_reference()`, `get_skill_paths()`
  - Uses `create_server(extra_paths, include_bundled)` factory pattern

- **`devskills/skills.py`** - `SkillManager` class handles skill discovery:
  - Scans directories for `SKILL.md` files with YAML frontmatter
  - Priority order: CLI paths > env var paths > bundled skills
  - Tracks writable paths separately from bundled (read-only)

- **`devskills/bundled_skills/`** - Default skills shipped with the package

### Skill Structure

```
skill-name/
├── SKILL.md           # Required: YAML frontmatter + instructions
├── scripts/           # Optional: executable scripts
└── references/        # Optional: reference documentation
```

SKILL.md frontmatter:
```yaml
---
name: skill-name
description: When to use this skill and what it does
---
```

### Key Design Decisions

- Skills are discovered by scanning directories for `SKILL.md` files (no manifest)
- Earlier paths in the list override later paths when skill names conflict
- Bundled skills are always lowest priority so users can override them
- `get_writable_paths()` excludes bundled directory (it's read-only in installed package)
