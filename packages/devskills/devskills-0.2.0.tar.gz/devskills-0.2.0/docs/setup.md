# Setup Guide

This guide covers how to configure devskills with different AI coding agents.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) - Fast Python package manager (for `uvx` command)

## Create a Skills Repository

Initialize a team skills repository:

```bash
uvx devskills init my-team-skills
```

Then configure your MCP client to point to it (see agent-specific instructions below).

> **Important:** Always include `--skills-path ./path/to/skills` to use your custom skills. Without it, only bundled skills are available.

## Claude Code

Add to your project's `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": ["devskills", "--skills-path", "./skills"]
    }
  }
}
```

### Global Setup (CLI)

```bash
claude mcp add devskills -- uvx devskills --skills-path ./skills
```

### Verify Installation

```bash
claude mcp list
```

You should see `devskills` in the list.

### Usage

Ask Claude to use skills explicitly:

```
Review this code. Use devskills.
```

Or add to your project's `CLAUDE.md` for automatic activation:

```markdown
Before implementation tasks, call list_skills() from the devskills MCP server.
If a relevant skill exists, fetch it with get_skill(name) and follow its instructions.
```

### Troubleshooting

Check server status in Claude Code:
```
/mcp
```

## GitHub Copilot (VS Code)

### Prerequisites

- VS Code 1.102 or later
- GitHub Copilot extension with MCP support

### Configuration

Create or edit `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "devskills": {
      "type": "stdio",
      "command": "uvx",
      "args": ["devskills", "--skills-path", "./skills"]
    }
  }
}
```

### Verify Installation

1. Open VS Code Command Palette (Cmd/Ctrl + Shift + P)
2. Run "GitHub Copilot: Show MCP Servers"
3. Verify `devskills` is listed and connected

### Usage

In Copilot Chat, reference skills:

```
@workspace Use devskills to review this code
```

## Cursor

Create or edit `.cursor/mcp.json` in your home directory (global) or project root (project-specific):

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": ["devskills", "--skills-path", "./skills"]
    }
  }
}
```

### Verify Installation

1. Open Cursor Settings (Cmd/Ctrl + Shift + P -> "Cursor Settings")
2. Navigate to MCP section
3. Verify `devskills` appears and shows as connected

### Usage

In Cursor's agent mode, ask it to use skills:

```
List available skills from devskills and use code-review for this PR.
```

## Multiple Skill Sources

You can combine multiple skill directories:

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": [
        "devskills",
        "--skills-path", "./skills",
        "--skills-path", "~/shared-company-skills"
      ]
    }
  }
}
```

Skills from earlier paths take priority when names conflict.

## Environment Variables

As an alternative to CLI arguments, you can use environment variables:

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": ["devskills"],
      "env": {
        "DEVSKILLS_SKILLS_PATH": "./skills:~/shared-skills"
      }
    }
  }
}
```
