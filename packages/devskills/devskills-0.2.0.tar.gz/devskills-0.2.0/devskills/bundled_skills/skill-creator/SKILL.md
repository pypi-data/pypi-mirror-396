---
name: skill-creator
description: Guide for creating effective skills for AI coding agents. Use when creating a new skill or updating an existing skill that extends agent capabilities with specialized knowledge, workflows, or tool integrations.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend AI agent capabilities by providing specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific domains or tasks—they transform a general-purpose agent into a specialized agent equipped with procedural knowledge.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts and references for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a shared resource. Skills share it with system prompts, conversation history, and user requests.

**Default assumption: AI agents are already very capable.** Only add context the agent doesn't already have. Challenge each piece of information: "Does the agent really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    └── references/       - Documentation loaded into context as needed
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These determine when the skill gets used, so be clear and comprehensive.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers.

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context

##### References (`references/`)

Documentation and reference material loaded as needed into context.

- **When to include**: For documentation the agent should reference while working
- **Examples**: `references/schema.md` for database schemas, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies
- **Benefits**: Keeps SKILL.md lean, loaded only when needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md

#### What to Not Include

A skill should only contain essential files. Do NOT create:

- README.md
- INSTALLATION_GUIDE.md
- CHANGELOG.md
- etc.

The skill should only contain information needed for an AI agent to do the job at hand.

### Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed (unlimited)

Keep SKILL.md body under 500 lines. Split content into separate files when approaching this limit.

**Key principle:** When a skill supports multiple variations, keep only the core workflow in SKILL.md. Move variant-specific details into reference files.

**Pattern: Domain-specific organization**

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, the agent only reads aws.md.

## Skill Creation Process

1. Understand the skill with concrete examples
2. Plan reusable contents (scripts, references)
3. Create the skill directory
4. Write SKILL.md and implement resources
5. Create a prompt (optional)
6. Test and iterate

### Step 1: Understanding the Skill

To create an effective skill, understand concrete examples of how it will be used.

For example, when building an image-editor skill:
- "What functionality should the image-editor skill support?"
- "Can you give examples of how this skill would be used?"
- "What would a user say that should trigger this skill?"

### Step 2: Planning Contents

Analyze each example by:
1. Considering how to execute on the example from scratch
2. Identifying what scripts and references would help when executing repeatedly

Example: For a `pdf-editor` skill handling "Help me rotate this PDF":
- Rotating a PDF requires re-writing code each time
- A `scripts/rotate_pdf.py` script would be helpful

Example: For a `big-query` skill handling "How many users logged in today?":
- Querying requires re-discovering table schemas each time
- A `references/schema.md` file would be helpful

### Step 3: Create the Skill Directory

Create the skill directory structure:

```bash
mkdir -p skills/my-skill/scripts skills/my-skill/references
```

Or use the init script:

```bash
python scripts/init_skill.py my-skill --path skills/
```

### Step 4: Write SKILL.md

#### Frontmatter

Write YAML frontmatter with `name` and `description`:

- `name`: The skill name
- `description`: Primary triggering mechanism. Include:
  - What the skill does
  - Specific triggers/contexts for when to use it
  - All "when to use" information (the body is only loaded after triggering)

Example description:
```yaml
description: Comprehensive document creation, editing, and analysis. Use when working with .docx files for creating, modifying, or editing documents.
```

#### Body

Write instructions for using the skill and its bundled resources. Use imperative form.

### Step 5: Create a Prompt (Optional)

Ask the user: **"Should this skill also be available as a user-triggered prompt?"**

Prompts are user-triggered entry points (slash commands) that explicitly invoke a skill. Not every skill needs a prompt—only user-facing workflows benefit from one.

If yes, create a prompt file in the `prompts/` directory (sibling to `skills/`):

```
my-team-skills/
├── skills/
│   └── my-skill/
│       └── SKILL.md
└── prompts/
    └── my-skill.md    ← Create this file
```

Prompt file format:

```markdown
---
name: my-skill
description: [Short description for prompt listings]
---

I need help with [task]. Use devskills to get the my-skill skill and follow its instructions exactly.
```

The prompt body should:
- Describe the user's intent in first person
- Mention "use devskills" so the agent knows to use devskills tools
- Reference the skill name to fetch

### Step 6: Test and Iterate

1. Use the skill on real tasks
2. Notice struggles or inefficiencies
3. Update SKILL.md or bundled resources
4. Test again
