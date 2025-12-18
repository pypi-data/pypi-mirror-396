# Reference

## CLI

```bash
# Run MCP server (default)
uvx devskills
uvx devskills --skills-path ./skills
uvx devskills --skills-path ./skills --no-bundled

# Initialize a team skills repository
uvx devskills init my-team-skills
uvx devskills init ./path -n "My Team"

# Create a new skill from template
uvx devskills init-skill code-review
uvx devskills init-skill deployment --path ./skills

# Show version
uvx devskills --version
```

## MCP Tools

The server exposes five tools that agents call automatically:

| Tool | Purpose |
|------|---------|
| `list_skills()` | Returns all skill names and descriptions. Agents call this to discover what's available. |
| `get_skill(name)` | Returns the full SKILL.md content. Called when an agent decides a skill is relevant. |
| `get_script(skill, filename)` | Returns a script from the skill's `scripts/` folder. For deterministic operations. |
| `get_reference(skill, filename)` | Returns a reference doc from `references/`. For additional context. |
| `get_skill_paths()` | Returns configured skill directories. Used when creating new skills. |

You don't call these directly—your AI agent uses them automatically based on context.

## MCP Prompts

Prompts are user-triggered entry points to skills. Unlike tools (which the model decides when to call), prompts let users explicitly invoke a skill via slash commands.

**Bundled Prompts:**

| Prompt | Description |
|--------|-------------|
| `mcp-builder` | Build a high-quality MCP server with guided workflow |
| `skill-creator` | Create a new devskills skill with proper structure |

**Creating Custom Prompts:**

Prompts are markdown files in the `prompts/` directory (created by `devskills init`):

```
my-team-skills/
├── skills/
│   └── code-review/
│       └── SKILL.md
└── prompts/
    └── code-review.md    ← User-triggered entry point
```

Prompt file format:

```markdown
---
name: code-review
description: Review code with team checklist
---

I need help reviewing code. Use devskills to get the code-review skill and follow its instructions exactly.
```

The prompt body should:
- Describe the user's intent in first person
- Mention "use devskills" so the agent uses devskills tools
- Reference the skill name to fetch

## Bundled Skills

| Skill | Description |
|-------|-------------|
| `skill-creator` | Guides you through creating new skills |
| `mcp-builder` | Best practices for building MCP servers |
