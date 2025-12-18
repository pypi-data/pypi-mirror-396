# Team Skills Repository Setup

This guide explains how to create a skills repository for your team.

## Overview

Teams can create their own skills repositories that work alongside the bundled default skills. Team members clone the repo, configure their agent, and immediately have access to both team skills and bundled defaults.

## Quick Start

### 1. Create Your Repository

Using the CLI:
```bash
uvx devskills init my-team-skills
cd my-team-skills
git init && git add . && git commit -m "Initial commit"
```

Or manually:
```bash
mkdir -p my-team-skills/skills
cd my-team-skills
git init
```

This creates:
```
my-team-skills/
├── skills/           # Your team's skills
├── .gitignore
└── README.md
```

### 2. Configure Your MCP Client

Each team member configures their MCP client to point to their local checkout:

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": ["devskills", "--skills-path", "/path/to/my-team-skills/skills"]
    }
  }
}
```

See [setup.md](setup.md) for agent-specific config file locations.

### 3. Create a README

```markdown
# My Team Skills

Custom devskills for [Team Name].

## Setup

1. Clone this repo
2. Your AI agent will automatically connect to devskills

## Creating Skills

Ask your agent:
\`\`\`
I want to create a new skill. Use devskills.
\`\`\`

## Available Skills

| Skill | Description |
|-------|-------------|
| (your skills here) | |
```

### 5. Commit and Share

```bash
git add .
git commit -m "Initial skills repository setup"
git push origin main
```

## Team Workflow

### Adding New Skills

1. Team member creates a skill using `skill-creator`
2. Commits to the repo
3. Creates a PR for review
4. After merge, all team members pull to get the new skill

### Using Skills

Team members:
1. Clone the team skills repo
2. Configure their MCP client to point to the local checkout
3. Open projects in their preferred agent (Claude Code, Cursor, Copilot)
4. Both team skills and bundled defaults are available

## Skill Priority

When skill names conflict, priority order is:

1. Team skills (`./skills/` directory)
2. Environment variable paths (`DEVSKILLS_SKILLS_PATH`)
3. Bundled defaults (always available)

This means teams can override bundled skills by creating a skill with the same name.

## Example: Code Review Skill

Create `skills/code-review/SKILL.md`:

```markdown
---
name: code-review
description: Review code following our team's standards. Use when asked to review PRs or code changes.
---

# Code Review

## Checklist

1. Check for security issues
2. Verify error handling
3. Review naming conventions
4. Check test coverage
5. Look for performance issues

## Our Standards

- All functions must have docstrings
- Maximum function length: 50 lines
- Prefer composition over inheritance
- ...
```

## Multiple Skill Sources

For larger organizations with shared company-wide skills:

```json
{
  "mcpServers": {
    "devskills": {
      "command": "uvx",
      "args": [
        "devskills",
        "--skills-path", "./skills",
        "--skills-path", "~/company-skills"
      ]
    }
  }
}
```

Priority: `./skills` > `~/company-skills` > bundled defaults

## Tips

- Keep skill descriptions clear - they're used for discovery
- Use `scripts/` for reusable automation
- Use `references/` for detailed documentation
- Test skills before sharing with the team
- Consider a PR review process for new skills
