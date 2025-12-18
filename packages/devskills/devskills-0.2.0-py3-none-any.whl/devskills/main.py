"""MCP server for devskills - exposes skills as tools and prompts."""

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from mcp.types import PromptMessage, TextContent
from pydantic import BaseModel, Field

from .skills import SkillManager
from .prompts import PromptManager


# Pydantic input models for validation
class GetSkillInput(BaseModel):
    """Input for getting a skill's full instructions."""

    name: str = Field(
        ...,
        description="Skill name from list_skills() (e.g., 'mcp-builder')",
        min_length=1,
    )


class GetScriptInput(BaseModel):
    """Input for getting a script from a skill."""

    skill: str = Field(
        ...,
        description="Skill name from list_skills()",
        min_length=1,
    )
    filename: str = Field(
        ...,
        description="Script filename as referenced in skill instructions",
        min_length=1,
    )


class GetReferenceInput(BaseModel):
    """Input for getting a reference doc from a skill."""

    skill: str = Field(
        ...,
        description="Skill name from list_skills()",
        min_length=1,
    )
    filename: str = Field(
        ...,
        description="Reference filename as referenced in skill instructions",
        min_length=1,
    )


# Global instances (set by create_server or run)
mcp: FastMCP | None = None
skills: SkillManager | None = None
prompts: PromptManager | None = None


def create_server(
    extra_paths: list[Path] | None = None,
    include_bundled: bool = True,
) -> FastMCP:
    """Create and configure the MCP server.

    Args:
        extra_paths: Additional skill directories to include.
        include_bundled: Whether to include bundled default skills and prompts.

    Returns:
        Configured FastMCP server instance.
    """
    global mcp, skills, prompts

    mcp = FastMCP("devskills")
    skills = SkillManager(extra_paths=extra_paths, include_bundled=include_bundled)
    prompts = PromptManager(extra_paths=extra_paths, include_bundled=include_bundled)

    # Register tools
    @mcp.tool(
        name="devskills_list_skills",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def list_skills() -> list[dict]:
        """List all available skills with name and description.

        Call this tool FIRST when the user mentions 'devskills' or asks about available skills.
        Returns an array of {name, description} for each skill.

        After getting the list, if a skill matches the user's task:
        1. Call get_skill(name) to fetch the full instructions
        2. Follow the instructions in the skill
        """
        return skills.list_all()

    @mcp.tool(
        name="devskills_get_skill",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_skill(params: GetSkillInput) -> str:
        """Get the full instructions (SKILL.md content) for a skill.

        You MUST call list_skills() first to discover valid skill names.
        Returns the complete skill instructions including:
        - When to use the skill
        - Step-by-step instructions to follow
        - References to scripts and reference docs

        After fetching a skill:
        - Follow the instructions in the returned content
        - If instructions reference scripts, fetch them with get_script()
        - If instructions reference docs, fetch them with get_reference()
        """
        return skills.get_content(params.name)

    @mcp.tool(
        name="devskills_get_script",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_script(params: GetScriptInput) -> str:
        """Get a script file from a skill's scripts/ folder.

        Only call this when a skill's instructions explicitly reference a script.
        The skill parameter must be a valid skill name from list_skills().
        The filename should match what's referenced in the skill instructions.

        Returns the raw script content. Execute it locally in your environment
        following the skill's instructions.
        """
        return skills.get_script(params.skill, params.filename)

    @mcp.tool(
        name="devskills_get_reference",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_reference(params: GetReferenceInput) -> str:
        """Get a reference document from a skill's references/ folder.

        Only call this when a skill's instructions explicitly reference a doc.
        The skill parameter must be a valid skill name from list_skills().
        The filename should match what's referenced in the skill instructions.

        Returns reference documentation to inform how you complete the task.
        Read and apply this reference when following the skill's instructions.
        """
        return skills.get_reference(params.skill, params.filename)

    @mcp.tool(
        name="devskills_get_skill_paths",
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def get_skill_paths() -> list[str]:
        """Get the configured skill directories where new skills can be created.

        Returns paths configured via --skills-path or DEVSKILLS_SKILLS_PATH.
        Does NOT include the bundled skills directory (which is read-only).

        Use this to determine where to create new skills when using the
        skill-creator skill.
        """
        return [str(p) for p in skills.get_writable_paths()]

    # Register prompts
    for prompt_info in prompts.list_all():
        _register_prompt(mcp, prompts, prompt_info)

    return mcp


def _register_prompt(mcp: FastMCP, prompt_manager: PromptManager, prompt_info: dict):
    """Register a single prompt with the MCP server.

    Args:
        mcp: FastMCP server instance.
        prompt_manager: PromptManager to retrieve prompt body.
        prompt_info: Dict with 'name' and 'description' keys.
    """
    prompt_name = prompt_info["name"]
    prompt_desc = prompt_info["description"]

    @mcp.prompt(name=prompt_name, description=prompt_desc)
    async def handler() -> list[PromptMessage]:
        body = prompt_manager.get_body(prompt_name)
        return [
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=body),
            )
        ]


def run():
    """Run the MCP server with stdio transport (backward compatibility)."""
    server = create_server()
    server.run(transport="stdio")
