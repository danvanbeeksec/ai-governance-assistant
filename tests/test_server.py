import asyncio

from ai_governance_assistant.server import create_server
from test_tools import FakeService
from ai_governance_assistant.tools import GovernanceTools


def test_server_registers_expected_tools():
    server = create_server(GovernanceTools(FakeService()))
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {
        "assess_ai_system",
        "get_applicable_controls",
        "explain_control",
        "compare_ai_design_options",
    }
