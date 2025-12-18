# DevSkills

[![PyPI](https://img.shields.io/pypi/v/devskills)](https://pypi.org/project/devskills/)

An MCP server that brings [Anthropic's Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) to any MCP-compatible coding agent.

**What this enables:** Your team creates a shared repository of skills — a skill that reviews PRs with your team's checklist, a skill that scaffolds services following your architecture patterns, a skill that debugs test failures with your stack's quirks in mind — and every team member's AI agent can use them automatically.

- [What are Skills?](#what-are-skills)
- [The Problem](#the-problem)
- [How DevSkills Works](#how-devskills-works)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Creating Skills](#creating-skills)
- [Documentation](#documentation)


## What are Skills?

Skills are Anthropic's concept for giving AI agents specialized knowledge. Instead of repeating context every conversation, you package instructions, scripts, and references into a folder that agents load on-demand.

Think of skills like onboarding docs for a new hire: "Here's how we do deployments. Here's our code review checklist. Here's the security patterns we follow." Except the new hire is an AI agent.

The key design principle is **progressive disclosure** — agents see only skill names and descriptions upfront, then load full instructions only when relevant. This means you can have dozens of skills without bloating context.

## The Problem

Native Skills support exists only in Claude Code, where skills live in `~/.claude/skills/` or `.claude/skills/`.

Teams using Cursor, GitHub Copilot, or other AI coding tools can't use Skills and can't share a common skill repository across different tools and maybe even agents running on the server side.

## How DevSkills Works

DevSkills runs as an MCP server that exposes your skills to any MCP-compatible agent:

```
┌─────────────────────────────────────────┐
│     devskills (MCP Server)              │
│  ├── bundled_skills/  (defaults)        │
│  ├── bundled_prompts/ (defaults)        │
│  └── your skills/prompts via --skills-path
└─────────────────────────────────────────┘
          │                    │
          │ MCP Tools          │ MCP Prompts
          │ (model-triggered)  │ (user-triggered)
          ▼                    ▼
┌─────────────────────────────────────────┐
│     AI Coding Agents                    │
│  Claude Code, Cursor, GitHub Copilot    │
└─────────────────────────────────────────┘
```

**Two ways to invoke skills:**

| Mechanism | Trigger | How it works |
|-----------|---------|--------------|
| **MCP Tools** | Model decides | Agent calls `list_skills()` → picks relevant skill → loads instructions |
| **MCP Prompts** | User invokes | User triggers `/mcp-builder` → agent receives prompt → follows skill |

**Tool-triggered flow (automatic):**

1. **Discovery** — Agent calls `list_skills()`, sees names and descriptions
2. **Selection** — Agent decides which skill matches the user's request
3. **Loading** — Agent calls `get_skill(name)` to load full instructions
4. **Execution** — Agent follows the instructions, optionally fetching scripts or references

**Prompt-triggered flow (explicit):**

1. **User invokes** — User triggers a prompt (e.g., `/skill-creator` in Claude Code)
2. **Agent receives** — Prompt tells agent to use devskills and which skill to load
3. **Loading** — Agent calls `get_skill(name)` as directed
4. **Execution** — Agent follows the instructions

Both flows converge at the same skill instructions—prompts just provide an explicit entry point.

**Team workflow:**

1. Team creates a skills repository (via `devskills init`)
2. Each developer clones the repo and configures their MCP client to point to it
3. Same skills, any agent

## Quick Start

### 1. Create a Skills Repository

```bash
uvx devskills init my-team-skills
cd my-team-skills
git init && git add . && git commit -m "Initial commit"
```

### 2. Configure Your MCP Client

See [Setup Guide](docs/setup.md) for agent-specific configuration (Claude Code, Cursor, GitHub Copilot).

## Usage

**Option 1: Let the agent decide (tools)**

Ask your agent naturally, mentioning "use devskills":

```
Review this PR. Use devskills.
```

```
Set up a new API endpoint for user management. Use devskills.
```

The agent will call `list_skills()` to discover available skills, pick the relevant one, and follow its instructions.

**Option 2: Explicitly invoke a skill (prompts)**

Use slash commands to trigger specific skills directly:

```
/skill-creator
```

```
/mcp-builder
```

The prompt tells the agent exactly which skill to use—no discovery step needed.

## Creating Skills

The recommended way to create a skill is using the built-in `skill-creator`:

```
I want to create a new skill for code review. Use devskills.
```

This guides you through creating a skill with the correct structure.

See [Creating Skills](docs/creating-skills.md) for the full guide, including skill structure and SKILL.md format.

## Documentation

- [Setup Guide](docs/setup.md) — Agent-specific MCP configuration
- [Creating Skills](docs/creating-skills.md) — Skill structure and format
- [Reference](docs/reference.md) — CLI, MCP tools, bundled skills
- [Contributing](CONTRIBUTING.md) — Development setup

**Anthropic Resources:**
- [Agent Skills Blog Post](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
