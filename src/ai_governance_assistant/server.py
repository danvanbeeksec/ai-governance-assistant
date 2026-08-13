"""MCP stdio server exposing the reusable governance service."""

from mcp.server.fastmcp import FastMCP

from .config import build_service
from .tools import GovernanceTools


def create_server(tools: GovernanceTools | None = None) -> FastMCP:
    adapter = tools or GovernanceTools(build_service())
    server = FastMCP("AI Governance Assistant")
    server.tool()(adapter.get_assessment_requirements)
    server.tool()(adapter.validate_assessment_input)
    server.tool()(adapter.assess_ai_system)
    server.tool()(adapter.get_applicable_controls)
    server.tool()(adapter.explain_control)
    server.tool()(adapter.compare_ai_design_options)
    return server


def main() -> None:
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
