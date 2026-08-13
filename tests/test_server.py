import asyncio

from ai_governance_assistant.server import SERVER_INSTRUCTIONS, create_server
from test_tools import FakeService
from ai_governance_assistant.tools import GovernanceTools


def test_server_registers_expected_tools():
    server = create_server(GovernanceTools(FakeService()))
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {
        "get_assessment_requirements",
        "validate_assessment_input",
        "assess_ai_system",
        "get_applicable_controls",
        "explain_control",
        "compare_ai_design_options",
    }
    assert server.instructions == SERVER_INSTRUCTIONS
    for tool in asyncio.run(server.list_tools()):
        assert tool.annotations.readOnlyHint is True
        assert tool.annotations.destructiveHint is False
        assert tool.annotations.idempotentHint is True
        assert tool.annotations.openWorldHint is False
