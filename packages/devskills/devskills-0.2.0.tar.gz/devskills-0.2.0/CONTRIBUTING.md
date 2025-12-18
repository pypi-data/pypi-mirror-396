# Contributing

## Development Setup

```bash
# Clone and install
git clone https://github.com/kontext-e/devskills.git
cd devskills
uv sync

# Run locally
uv run devskills --skills-path ./test-skills

# Run tests
uv run pytest
```

## Project Structure

```
devskills/
├── devskills/
│   ├── cli.py              # CLI commands (init, init-skill)
│   ├── main.py             # MCP server (FastMCP)
│   ├── skills.py           # SkillManager for discovery
│   └── bundled_skills/     # Default skills shipped with package
├── docs/                   # Documentation
├── test-skills/            # Test skills for development
└── tests/                  # Test suite
```

## Making Changes

1. Create a branch for your changes
2. Make your changes
3. Run tests: `uv run pytest`
4. Submit a pull request
