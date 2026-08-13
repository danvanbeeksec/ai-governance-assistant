"""MCP stdio server exposing the reusable governance service."""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .config import build_service
from .tools import GovernanceTools


SERVER_INSTRUCTIONS = (
    "Use only fictional or synthetic information. Call get_assessment_requirements "
    "before guided intake. Treat only explicit user statements as facts. Submit "
    "uncertain interpretations as proposed inferences and do not use them until the "
    "user explicitly confirms them. Call validate_assessment_input before assessment. "
    "Never assess incomplete input or override deterministic results. Report Framework "
    "provenance and require human review."
)

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def create_server(
    tools: GovernanceTools | None = None,
    **server_options: object,
) -> FastMCP:
    adapter = tools or GovernanceTools(build_service())
    server = FastMCP(
        "AI Governance Assistant",
        instructions=SERVER_INSTRUCTIONS,
        **server_options,
    )
    for tool in (
        adapter.get_assessment_requirements,
        adapter.validate_assessment_input,
        adapter.assess_ai_system,
        adapter.get_applicable_controls,
        adapter.explain_control,
        adapter.compare_ai_design_options,
    ):
        server.tool(annotations=READ_ONLY_ANNOTATIONS)(tool)
    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
