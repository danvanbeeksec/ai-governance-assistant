"""Integrity and parity tests for the tenant-neutral M365 Copilot kit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest


ROOT = Path(__file__).parents[1]
M365 = ROOT / "m365-copilot"
ENGINE = json.loads((M365 / "workflow" / "assessment-engine.json").read_text())
SCENARIOS = json.loads((M365 / "tests" / "acceptance-scenarios.json").read_text())


def _condition_matches(facts: dict[str, object], condition: dict[str, object]) -> bool:
    actual = facts[condition["field"]]
    if condition["operator"] == "in":
        return actual in condition["values"]
    if condition["operator"] == "contains_any":
        return any(value in actual for value in condition["values"])
    raise AssertionError(f"Unsupported condition operator: {condition['operator']}")


def _risk_rule_matches(facts: dict[str, object], conditions: dict[str, object]) -> bool:
    for field, expected in conditions.items():
        actual = facts[field]
        if isinstance(expected, str) and actual != expected:
            return False
        if isinstance(expected, dict):
            if "in" in expected and actual not in expected["in"]:
                return False
            if "any_of" in expected and not any(
                value in actual for value in expected["any_of"]
            ):
                return False
            if "equals" in expected and actual != expected["equals"]:
                return False
    return True


def _evaluate(facts: dict[str, object]) -> dict[str, object]:
    model = ENGINE["risk_model"]
    baseline = model["baseline_matrix"][facts["autonomy_level"]][
        facts["information_sensitivity"]
    ]
    tier_order = model["model"]["tier_order"]
    final_tier = baseline
    matched_rules = []
    for rule in model["elevation_rules"]:
        if not _risk_rule_matches(facts, rule["when"]):
            continue
        matched_rules.append(rule["id"])
        if tier_order.index(rule["minimum_tier"]) < tier_order.index(final_tier):
            final_tier = rule["minimum_tier"]

    outcomes: dict[str, str] = {}
    for treatment in ENGINE["control_rules"]:
        if treatment["section"] == "enterprise_dependencies":
            outcome = "inherited_dependency"
        elif treatment["treatment"] == "universal":
            outcome = "applicable"
        elif treatment["treatment"] == "human_determination":
            outcome = "undetermined"
        else:
            matched = any(
                all(_condition_matches(facts, item) for item in group["all"])
                for group in treatment["triggers"]
            )
            outcome = "applicable" if matched else "undetermined"
        outcomes[treatment["control_id"]] = outcome
    return {
        "baseline_tier": baseline,
        "final_tier": final_tier,
        "matched_rules": matched_rules,
        "outcomes": outcomes,
    }


def test_generated_assets_are_current() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/build_m365_copilot_package.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_standalone_transfer_verifier_passes() -> None:
    completed = subprocess.run(
        [sys.executable, "verify_package.py"],
        cwd=M365,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Package verified" in completed.stdout


def test_manifest_and_generated_file_digests() -> None:
    manifest = json.loads((M365 / "package-manifest.json").read_text())
    assert manifest["external_runtime_required"] is False
    assert manifest["inventory_persistence"] is False
    assert manifest["framework_source"]["library_version"] == "1.2.0"
    assert manifest["framework_library"]["status"] == "published"
    assert manifest["applicability_methodology"]["status"] == "approved"
    for relative_path, expected in manifest["generated_file_sha256"].items():
        actual = hashlib.sha256((M365 / relative_path).read_bytes()).hexdigest()
        assert actual == expected


def test_adaptive_card_covers_required_fields_and_allowed_values() -> None:
    card = json.loads(
        (M365 / "agent" / "adaptive-cards" / "assessment-form.json").read_text()
    )
    inputs = {
        item["id"]: item
        for item in card["body"]
        if item["type"].startswith("Input.")
    }
    required = {item["field"]: item for item in ENGINE["assessment_fields"]}
    assert set(inputs) == set(required) | {"confirmed"}
    assert inputs["confirmed"]["isRequired"] is True
    for field, specification in required.items():
        if field == "agent_capabilities":
            assert inputs[field].get("isRequired", False) is False
        else:
            assert inputs[field]["isRequired"] is True
        if specification["allowed_values"]:
            assert {choice["value"] for choice in inputs[field]["choices"]} == set(
                specification["allowed_values"]
            )
    assert inputs["agent_capabilities"]["isMultiSelect"] is True


@pytest.mark.parametrize(
    ("scenario", "expected_tier", "expected_rules"),
    [
        ("internal_assistant", "tier_3", []),
        ("vendor_platform", "tier_3", []),
        ("customer_system", "tier_1", ["ER-003", "ER-004"]),
        ("autonomous_agent", "tier_1", ["ER-005"]),
    ],
)
def test_m365_engine_matches_canonical_acceptance_results(
    scenario: str, expected_tier: str, expected_rules: list[str]
) -> None:
    result = _evaluate(SCENARIOS[scenario])
    assert result["final_tier"] == expected_tier
    assert result["matched_rules"] == expected_rules
    if scenario == "autonomous_agent":
        assert result["outcomes"]["AI-AGT-004"] == "applicable"


def test_formulas_cover_every_rule_and_control() -> None:
    matched_formula = (
        M365 / "workflow" / "power-fx" / "matched-elevation-rules.fx"
    ).read_text()
    control_formula = (
        M365 / "workflow" / "power-fx" / "control-outcomes.fx"
    ).read_text()
    assert {rule["id"] for rule in ENGINE["risk_model"]["elevation_rules"]} == {
        rule_id
        for rule_id in (f"ER-{number:03d}" for number in range(1, 1000))
        if rule_id in matched_formula
    }
    assert len(ENGINE["control_rules"]) == 70
    for treatment in ENGINE["control_rules"]:
        assert control_formula.count(f'control_id: "{treatment["control_id"]}"') == 1


def test_agent_boundary_is_inventory_free_and_human_reviewed() -> None:
    instructions = (M365 / "agent" / "instructions.md").read_text().lower()
    assert "do not create or update an ai-system inventory" in instructions
    assert "do not assign a risk tier until" in instructions
    assert "qualified human review" in instructions
    assert "not an approval" in instructions
    assert "absence of a trigger does not establish non-applicability" in instructions


def test_transfer_archive_has_one_portable_root(tmp_path: Path) -> None:
    destination = tmp_path / "m365-kit.zip"
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_m365_copilot_package.py",
            "--check",
            "--zip",
            str(destination),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    with zipfile.ZipFile(destination) as archive:
        names = archive.namelist()
    assert names
    assert all(name.startswith("m365-copilot/") for name in names)
    assert "m365-copilot/README.md" in names
    assert "m365-copilot/tenant-build-runbook.md" in names
    assert "m365-copilot/knowledge/control-catalog.txt" in names
