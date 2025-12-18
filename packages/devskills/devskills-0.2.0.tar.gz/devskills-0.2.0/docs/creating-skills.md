# Creating Skills

## Using the skill-creator Skill

The best way to create a new skill is to use the built-in `skill-creator` skill:

```
Create a new skill for [your use case]. Use devskills.
```

This will guide the AI agent through the skill creation process with best practices.

## Manual Creation

If you prefer to create skills manually:

1. Create a new folder in `skills/`:
   ```bash
   mkdir -p skills/my-skill/scripts skills/my-skill/references
   ```

2. Create `skills/my-skill/SKILL.md` with frontmatter and instructions:

   ```yaml
   ---
   name: my-skill
   description: Brief description shown in list_skills()
   ---

   ## Instructions

   Step-by-step instructions for the AI to follow.
   ```

3. Add scripts in `scripts/` and reference docs in `references/` as needed

## Skill Structure

```
skills/my-skill/
├── SKILL.md          # Required: instructions + frontmatter
├── scripts/          # Optional: executable scripts
└── references/       # Optional: reference documents
```

## SKILL.md Format

```yaml
---
name: code-review
description: Review code for security issues, performance, and style. Use when asked to review PRs or check code quality.
---

# Code Review

When reviewing code, check for:

1. **Security vulnerabilities** — SQL injection, XSS, command injection
2. **Performance issues** — N+1 queries, unnecessary loops, missing indexes
3. **Style consistency** — Follow project conventions in .editorconfig

For detailed security patterns, see [references/security-checklist.md](references/security-checklist.md).

To run automated checks: `scripts/lint-check.sh`
```

**Key points:**

- The `description` field is critical—agents use it to decide when to load the skill
- Write instructions as if explaining to a capable colleague who doesn't know your specific context
- Reference scripts and docs with relative paths; agents fetch them via `get_script()` and `get_reference()`

For comprehensive guidance on skill design, bundled resources, and best practices, use the `skill-creator` skill.
