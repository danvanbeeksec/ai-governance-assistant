"""Validation and parity tests for the self-contained Claude Agent Skill."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from ai_governance_assistant.config import build_service
import pytest
import yaml


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "assess-ai-governance"
SCRIPT = SKILL / "scripts" / "assess.py"
SCENARIOS = json.loads(
    (ROOT / "tests" / "fixtures" / "acceptance_scenarios.json").read_text()
)


def _frontmatter() -> dict[str, str]:
    text = (SKILL / "SKILL.md").read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1))


def _run(*arguments: str, payload: object | None = None, script: Path = SCRIPT):
    completed = subprocess.run(
        [sys.executable, str(script), *arguments],
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        check=False,
        cwd=script.parents[1],
    )
    return completed, json.loads(completed.stdout)


def test_skill_uses_anthropic_structure_and_metadata_rules() -> None:
    metadata = _frontmatter()
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == SKILL.name
    assert re.fullmatch(r"[a-z0-9-]{1,64}", metadata["name"])
    assert "anthropic" not in metadata["name"]
    assert "claude" not in metadata["name"]
    assert 1 <= len(metadata["description"]) <= 1024


def test_skill_is_self_contained_and_has_no_inventory_workflow() -> None:
    text = (SKILL / "SKILL.md").read_text().lower()
    assert "scripts/assess.py" in text
    assert "do not call an mcp server" in text
    assert "do not create or update an ai-system inventory" in text
    assert "do not ask for an assessment id" in text
    for legacy_tool in (
        "get_assessment_requirements",
        "validate_assessment_input",
        "assess_ai_system",
        "get_applicable_controls",
        "compare_ai_design_options",
    ):
        assert legacy_tool not in text


def test_skill_references_exist_and_scenarios_cover_required_contexts() -> None:
    skill_text = (SKILL / "SKILL.md").read_text()
    for relative_path in re.findall(r"\]\((references/[^)]+)\)", skill_text):
        assert (SKILL / relative_path).is_file()

    scenarios = (SKILL / "references" / "evaluation-scenarios.md").read_text()
    assert "Internal assistant" in scenarios
    assert "Vendor chatbot" in scenarios
    assert "Agentic system with tools and connectors" in scenarios


def test_manifest_verifies_every_exported_policy_resource() -> None:
    references = SKILL / "references"
    manifest = json.loads((references / "package-manifest.json").read_text())
    assert manifest["framework_source"]["library_version"] == "1.2.0"
    assert manifest["framework_source"]["status"] == "loaded"
    assert manifest["framework_library"]["status"] == "draft"
    assert manifest["applicability_methodology"]["status"] == "approved"
    for filename, expected in manifest["resource_sha256"].items():
        actual = hashlib.sha256((references / filename).read_bytes()).hexdigest()
        assert actual == expected


def test_requirements_are_question_driven_and_inventory_free() -> None:
    completed, result = _run("requirements")
    assert completed.returncode == 0
    assert result["schema_version"] == "0.1.0"
    fields = {item["field"] for item in result["fields"]}
    assert "assessment_id" not in fields
    assert "system_name" in fields
    assert "agent_capabilities" in fields
    assert "inventory" in result["privacy_notice"]


def test_incomplete_input_returns_questions_without_a_tier() -> None:
    completed, result = _run(
        "evaluate",
        "-",
        payload={
            "system_name": "Synthetic Assistant",
            "business_purpose": "Summarize synthetic notes.",
        },
    )
    assert completed.returncode == 0
    assert result["status"] == "needs_information"
    assert result["assessment"] is None
    assert any(issue["field"] == "autonomy_level" for issue in result["issues"])
    assert "final_tier" not in result


@pytest.mark.parametrize(
    ("scenario", "expected_tier", "expected_rules"),
    [
        ("internal_assistant", "tier_3", []),
        ("vendor_platform", "tier_3", []),
        ("customer_system", "tier_1", ["ER-003", "ER-004"]),
        ("autonomous_agent", "tier_1", ["ER-005"]),
    ],
)
def test_packaged_evaluator_matches_canonical_service(
    scenario: str, expected_tier: str, expected_rules: list[str]
) -> None:
    assessment = SCENARIOS[scenario]
    completed, packaged = _run("evaluate", "-", payload=assessment)
    assert completed.returncode == 0
    assert packaged["status"] == "assessment_complete"

    canonical = build_service().assess_ai_system(assessment).model_dump(mode="json")
    assert packaged["decision"]["final_tier"] == expected_tier
    assert packaged["decision"]["final_tier"] == canonical["decision"]["final_tier"]
    packaged_rules = [item["rule_id"] for item in packaged["decision"]["applied_rules"]]
    canonical_rules = [item["rule_id"] for item in canonical["decision"]["applied_rules"]]
    assert packaged_rules == expected_rules
    assert packaged_rules == canonical_rules

    packaged_controls = {
        item["control_id"]
        for item in packaged["recommendations"]["applicable_system_controls"]
    }
    canonical_controls = {
        item["control"]["control_id"]
        for item in canonical["recommendations"]["applicable_system_controls"]
    }
    assert packaged_controls == canonical_controls
    assert packaged["recommendations"]["summary"] == canonical["recommendations"]["summary"]
    assert packaged["decision"]["framework_source"] == canonical["decision"]["framework_source"]


def test_control_explanation_and_design_comparison() -> None:
    completed, control = _run("explain-control", "AI-GOV-001")
    assert completed.returncode == 0
    assert control["status"] == "control_found"
    assert control["control"]["control_id"] == "AI-GOV-001"
    assert control["control"]["evidence_examples"]

    completed, comparison = _run(
        "compare",
        "-",
        payload={
            "option_a": SCENARIOS["internal_assistant"],
            "option_b": SCENARIOS["autonomous_agent"],
        },
    )
    assert completed.returncode == 0
    assert comparison["status"] == "comparison_complete"
    assert comparison["tier_changed"] is True
    assert comparison["option_a"]["decision"]["final_tier"] == "tier_3"
    assert comparison["option_b"]["decision"]["final_tier"] == "tier_1"
    assert "AI-AGT-004" in comparison["controls_added"]


def test_resource_tampering_fails_closed(tmp_path: Path) -> None:
    copied_skill = tmp_path / SKILL.name
    shutil.copytree(SKILL, copied_skill)
    risk_model = copied_skill / "references" / "risk-model.json"
    risk_model.write_text(risk_model.read_text() + "\n")
    completed, result = _run(
        "requirements", script=copied_skill / "scripts" / "assess.py"
    )
    assert completed.returncode == 2
    assert result["status"] == "error"
    assert "digest mismatch" in result["error"]
