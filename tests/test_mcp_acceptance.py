"""End-to-end acceptance tests for the installed MCP stdio boundary."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


FIXTURES = Path(__file__).parent / "fixtures" / "acceptance_scenarios.json"
EXPECTED_TOOLS = {
    "assess_ai_system",
    "compare_ai_design_options",
    "explain_control",
    "get_applicable_controls",
    "get_assessment_requirements",
    "validate_assessment_input",
}


def _read_result(result: Any) -> dict[str, Any]:
    assert not result.isError
    assert len(result.content) == 1
    return json.loads(result.content[0].text)


async def _call(
    session: ClientSession, name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    return _read_result(await session.call_tool(name, arguments))


async def _run_acceptance_journey() -> None:
    scenarios = json.loads(FIXTURES.read_text())
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ai_governance_assistant.server"],
    )

    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listed = await session.list_tools()
            assert {tool.name for tool in listed.tools} == EXPECTED_TOOLS

            requirements = await _call(session, "get_assessment_requirements", {})
            required_fields = [
                field["field"] for field in requirements["fields"] if field["required"]
            ]
            assert required_fields[:3] == [
                "assessment_id",
                "system_name",
                "business_purpose",
            ]

            partial_facts = {
                "assessment_id": "ACC-PARTIAL",
                "system_name": "Synthetic Incomplete Assistant",
            }
            first_partial = await _call(
                session, "validate_assessment_input", {"facts": partial_facts}
            )
            second_partial = await _call(
                session, "validate_assessment_input", {"facts": partial_facts}
            )
            assert first_partial == second_partial
            assert first_partial["status"] == "needs_information"
            assert first_partial["assessment"] is None
            assert "business_purpose" in [
                issue["field"] for issue in first_partial["issues"]
            ]

            proposed_inference = {
                "field": "information_sensitivity",
                "value": "public",
                "basis": "The synthetic description states that only public data is used.",
                "confirmed": False,
            }
            unconfirmed = await _call(
                session,
                "validate_assessment_input",
                {
                    "facts": partial_facts,
                    "proposed_inferences": [proposed_inference],
                },
            )
            assert any(
                issue["issue"] == "unconfirmed_inference"
                and issue["field"] == "information_sensitivity"
                for issue in unconfirmed["issues"]
            )

            proposed_inference["confirmed"] = True
            confirmed = await _call(
                session,
                "validate_assessment_input",
                {
                    "facts": partial_facts,
                    "proposed_inferences": [proposed_inference],
                },
            )
            assert confirmed["confirmed_inferences"]["information_sensitivity"] == (
                "public"
            )
            assert not any(
                issue["field"] == "information_sensitivity"
                for issue in confirmed["issues"]
            )
            assert confirmed["assessment"] is None

            expected = {
                "internal_assistant": ("tier_3", []),
                "vendor_platform": ("tier_3", []),
                "customer_system": ("tier_1", ["ER-003", "ER-004"]),
                "autonomous_agent": ("tier_1", ["ER-005"]),
            }
            assessed: dict[str, dict[str, Any]] = {}
            for name, assessment in scenarios.items():
                ready = await _call(
                    session, "validate_assessment_input", {"facts": assessment}
                )
                assert ready["status"] == "ready_for_assessment"

                result = await _call(
                    session, "assess_ai_system", {"assessment": ready["assessment"]}
                )
                assessed[name] = result
                expected_tier, expected_rules = expected[name]
                decision = result["decision"]
                assert decision["status"] == "evaluated"
                assert decision["final_tier"] == expected_tier
                assert [rule["rule_id"] for rule in decision["applied_rules"]] == expected_rules
                assert decision["framework_source"]["repository"] == (
                    "danvanbeeksec/ai-governance-control-framework"
                )
                assert decision["framework_source"]["library_version"] == "1.1.0"
                assert decision["framework_source"]["status"] == "loaded"

            repeated = await _call(
                session,
                "assess_ai_system",
                {"assessment": scenarios["internal_assistant"]},
            )
            assert repeated == assessed["internal_assistant"]

            controls = await _call(
                session,
                "get_applicable_controls",
                {"assessment": scenarios["internal_assistant"]},
            )
            assert controls == assessed["internal_assistant"]["recommendations"]
            control_ids = {
                item["control"]["control_id"]
                for item in controls["applicable_system_controls"]
            }
            assert {"AI-GOV-003", "AI-SEC-002", "AI-DAT-001"} <= control_ids

            explained = await _call(
                session, "explain_control", {"control_id": "AI-GOV-001"}
            )
            assert explained["control_id"] == "AI-GOV-001"
            assert explained["applicability_metadata"] is not None

            identical = await _call(
                session,
                "compare_ai_design_options",
                {
                    "option_a": scenarios["internal_assistant"],
                    "option_b": scenarios["internal_assistant"],
                },
            )
            assert identical["tier_changed"] is False
            assert identical["controls_added"] == []
            assert identical["controls_removed"] == []

            comparison = await _call(
                session,
                "compare_ai_design_options",
                {
                    "option_a": scenarios["internal_assistant"],
                    "option_b": scenarios["autonomous_agent"],
                },
            )
            assert comparison["tier_changed"] is True
            assert comparison["option_a"]["decision"]["final_tier"] == "tier_3"
            assert comparison["option_b"]["decision"]["final_tier"] == "tier_1"
            assert comparison["controls_added"] == sorted(comparison["controls_added"])
            assert comparison["controls_removed"] == sorted(
                comparison["controls_removed"]
            )
            assert "AI-AGT-001" in comparison["controls_added"]


def test_mcp_acceptance_journey() -> None:
    asyncio.run(_run_acceptance_journey())
