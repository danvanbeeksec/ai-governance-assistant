"""Build deterministic Microsoft 365 Copilot package assets from canonical policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_REFERENCES = (
    REPOSITORY_ROOT / "skills" / "assess-ai-governance" / "references"
)
ACCEPTANCE_SCENARIOS = REPOSITORY_ROOT / "tests" / "fixtures" / "acceptance_scenarios.json"
M365_ROOT = REPOSITORY_ROOT / "m365-copilot"


class PackageBuildError(ValueError):
    """Raised when canonical or generated package data cannot be trusted."""


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PackageBuildError(f"Cannot read valid JSON from {path}: {exc}") from exc


def _json_text(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _load_policy() -> dict[str, object]:
    manifest = _read_json(SOURCE_REFERENCES / "package-manifest.json")
    if not isinstance(manifest, dict):
        raise PackageBuildError("The canonical package manifest must be a JSON object")

    resources: dict[str, object] = {}
    expected_hashes = manifest.get("resource_sha256")
    if not isinstance(expected_hashes, dict):
        raise PackageBuildError("The canonical manifest does not contain resource hashes")
    for filename, expected_hash in expected_hashes.items():
        if not isinstance(filename, str) or not isinstance(expected_hash, str):
            raise PackageBuildError("The canonical manifest contains an invalid resource hash")
        path = SOURCE_REFERENCES / filename
        actual_hash = _sha256(path)
        if actual_hash != expected_hash:
            raise PackageBuildError(f"Canonical resource digest mismatch: {filename}")
        resources[filename] = _read_json(path)

    return {"manifest": manifest, **resources}


def _quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _or(expressions: list[str]) -> str:
    if not expressions:
        return "false"
    if len(expressions) == 1:
        return expressions[0]
    return "Or(\n        " + ",\n        ".join(expressions) + "\n    )"


def _and(expressions: list[str]) -> str:
    if not expressions:
        return "true"
    if len(expressions) == 1:
        return expressions[0]
    return "And(\n        " + ",\n        ".join(expressions) + "\n    )"


def _risk_condition(field: str, expected: object) -> str:
    variable = f"Topic.{field}"
    if isinstance(expected, str):
        return f"{variable} = {_quote(expected)}"
    if not isinstance(expected, dict):
        raise PackageBuildError(f"Unsupported risk condition for {field}")
    if "in" in expected:
        return _or([f"{variable} = {_quote(value)}" for value in expected["in"]])
    if "any_of" in expected:
        return _or(
            [
                f"{_quote('|' + value + '|')} in Topic.agent_capabilities_token"
                for value in expected["any_of"]
            ]
        )
    if "equals" in expected:
        return f"{variable} = {_quote(expected['equals'])}"
    raise PackageBuildError(f"Unsupported risk condition operator for {field}")


def _risk_rule_expression(rule: dict[str, object]) -> str:
    conditions = rule.get("when")
    if not isinstance(conditions, dict):
        raise PackageBuildError(f"Risk rule {rule.get('id')} has no conditions")
    return _and(
        [_risk_condition(field, expected) for field, expected in conditions.items()]
    )


def _control_condition(condition: dict[str, object]) -> str:
    field = condition["field"]
    values = condition["values"]
    if not isinstance(field, str) or not isinstance(values, list):
        raise PackageBuildError("Invalid control condition")
    operator = condition["operator"]
    if operator == "in":
        return _or([f"Topic.{field} = {_quote(value)}" for value in values])
    if operator == "contains_any":
        return _or(
            [
                f"{_quote('|' + value + '|')} in Topic.agent_capabilities_token"
                for value in values
            ]
        )
    raise PackageBuildError(f"Unsupported control operator: {operator}")


def _control_expression(treatment: dict[str, object]) -> str:
    trigger_expressions: list[str] = []
    for group in treatment.get("triggers", []):
        trigger_expressions.append(
            _and([_control_condition(item) for item in group.get("all", [])])
        )
    return _or(trigger_expressions)


def _build_baseline_formula(risk_model: dict[str, object]) -> str:
    cases: list[str] = []
    for autonomy, sensitivity_map in risk_model["baseline_matrix"].items():
        for sensitivity, tier in sensitivity_map.items():
            cases.append(
                f"    {_quote(autonomy + '|' + sensitivity)}, {_quote(tier)}"
            )
    return (
        "// Generated from the canonical risk model. Do not edit manually.\n"
        "Switch(\n"
        "    Topic.autonomy_level & \"|\" & Topic.information_sensitivity,\n"
        + ",\n".join(cases)
        + ",\n    Blank()\n)\n"
    )


def _build_matched_rules_formula(risk_model: dict[str, object]) -> str:
    records = []
    for rule in risk_model["elevation_rules"]:
        expression = _risk_rule_expression(rule)
        records.append(
            "    { rule_id: "
            + _quote(rule["id"])
            + ", minimum_tier: "
            + _quote(rule["minimum_tier"])
            + ", reason: "
            + _quote(rule["reason"])
            + ", matched: "
            + expression.replace("\n", "\n    ")
            + " }"
        )
    return (
        "// Topic.agent_capabilities_token must use |value| delimiters.\n"
        "Filter(\n"
        "    Table(\n"
        + ",\n".join(records)
        + "\n    ),\n"
        "    matched\n"
        ")\n"
    )


def _build_final_tier_formula() -> str:
    return (
        "// Topic.matched_elevation_rules is the table produced by the generated rule formula.\n"
        "If(\n"
        "    Topic.baseline_tier = \"tier_1\" Or "
        "CountIf(Topic.matched_elevation_rules, minimum_tier = \"tier_1\") > 0,\n"
        "    \"tier_1\",\n"
        "    Topic.baseline_tier = \"tier_2\" Or "
        "CountIf(Topic.matched_elevation_rules, minimum_tier = \"tier_2\") > 0,\n"
        "    \"tier_2\",\n"
        "    \"tier_3\"\n"
        ")\n"
    )


def _build_control_outcomes_formula(
    framework: dict[str, object], methodology: dict[str, object]
) -> str:
    controls = {item["control_id"]: item for item in framework["controls"]}
    records: list[str] = []
    for treatment in methodology["controls"]:
        control = controls[treatment["control_id"]]
        if treatment["section"] == "enterprise_dependencies":
            outcome = _quote("inherited_dependency")
            follow_up = (
                "Confirm the enterprise provider, inheritance scope, required "
                "configuration, exclusions, evidence, and review period."
            )
        elif treatment["treatment"] == "universal":
            outcome = _quote("applicable")
            follow_up = ""
        elif treatment["treatment"] == "human_determination":
            outcome = _quote("undetermined")
            follow_up = " | ".join(treatment["unresolved_questions"])
        else:
            condition = _control_expression(treatment).replace("\n", "\n        ")
            outcome = f"If(\n        {condition},\n        \"applicable\",\n        \"undetermined\"\n    )"
            follow_up = " | ".join(treatment["unresolved_questions"])
        records.append(
            "    { control_id: "
            + _quote(control["control_id"])
            + ", title: "
            + _quote(control["title"])
            + ", section: "
            + _quote(treatment["section"])
            + ", outcome: "
            + outcome.replace("\n", "\n    ")
            + ", follow_up: "
            + _quote(follow_up)
            + " }"
        )
    return (
        "// Generated control outcomes. Absence of a trigger remains undetermined.\n"
        "Table(\n" + ",\n".join(records) + "\n)\n"
    )


def _build_report_fields_formula() -> str:
    return (
        "// Generated display fields for the chat response.\n"
        "{\n"
        "    matched_elevation_rules_text: If(\n"
        "        IsEmpty(Topic.matched_elevation_rules),\n"
        "        \"None\",\n"
        "        Concat(Topic.matched_elevation_rules, rule_id & \" | \" & reason, Char(10))\n"
        "    ),\n"
        "    enterprise_dependencies_text: Concat(\n"
        "        Filter(Topic.control_outcomes, section = \"enterprise_dependencies\"),\n"
        "        control_id & \" | \" & title & \" | Follow-up: \" & follow_up,\n"
        "        Char(10)\n"
        "    ),\n"
        "    applicable_system_controls_text: Concat(\n"
        "        Filter(Topic.control_outcomes, section = \"system_controls\" And outcome = \"applicable\"),\n"
        "        control_id & \" | \" & title,\n"
        "        Char(10)\n"
        "    ),\n"
        "    undetermined_system_controls_text: Concat(\n"
        "        Filter(Topic.control_outcomes, section = \"system_controls\" And outcome = \"undetermined\"),\n"
        "        control_id & \" | \" & title & \" | Follow-up: \" & follow_up,\n"
        "        Char(10)\n"
        "    )\n"
        "}\n"
    )


def _build_knowledge_text(policy: dict[str, object]) -> str:
    manifest = policy["manifest"]
    requirements = policy["assessment-requirements.json"]
    risk_model = policy["risk-model.json"]
    framework = policy["controls.json"]
    methodology = policy["control-applicability.json"]
    treatments = {item["control_id"]: item for item in methodology["controls"]}

    lines = [
        "AI GOVERNANCE ASSESSMENT REFERENCE",
        "",
        "This reference supports decision assistance. It is not an approval, residual-risk decision, legal conclusion, certification, or finding of compliance.",
        "Do not treat missing information or an unmatched trigger as proof that a control is unnecessary.",
        "",
        "PROVENANCE",
        f"Framework: {manifest['framework_library']['name']}",
        f"Framework version: {manifest['framework_source']['library_version']}",
        f"Framework lifecycle status: {manifest['framework_library']['status']}",
        f"Framework source commit: {manifest['framework_source']['commit']}",
        f"Risk model: {manifest['risk_model']['id']} version {manifest['risk_model']['version']}",
        f"Applicability methodology: {manifest['applicability_methodology']['id']} version {manifest['applicability_methodology']['version']} ({manifest['applicability_methodology']['status']})",
        "",
        "ASSESSMENT INPUTS",
    ]
    for field in requirements["fields"]:
        lines.append(f"{field['field']}: {field['question']}")
        if field["allowed_values"]:
            lines.append("Allowed values: " + ", ".join(field["allowed_values"]))

    lines.extend(["", "BASELINE RISK MATRIX"])
    for autonomy, sensitivity_map in risk_model["baseline_matrix"].items():
        for sensitivity, tier in sensitivity_map.items():
            lines.append(f"{autonomy} + {sensitivity}: {tier}")

    lines.extend(["", "ELEVATION RULES"])
    for rule in risk_model["elevation_rules"]:
        lines.append(
            f"{rule['id']} | minimum {rule['minimum_tier']} | {rule['reason']} | conditions {json.dumps(rule['when'], sort_keys=True)}"
        )

    lines.extend(["", "CONTROLS"])
    for control in framework["controls"]:
        treatment = treatments[control["control_id"]]
        lines.extend(
            [
                "",
                f"CONTROL {control['control_id']}: {control['title']}",
                f"Domain: {control['domain']}",
                f"Layer: {control['layer']}",
                f"Objective: {control['objective']}",
                f"Requirement: {control['requirement']}",
                f"Implementation notes: {control['implementation_notes']}",
                f"Evidence examples: {', '.join(control['evidence_examples'])}",
                f"References: {', '.join(control['references'])}",
                f"Assessment section: {treatment['section']}",
                f"Applicability treatment: {treatment['treatment']}",
                f"Applicability rationale: {treatment['rationale']}",
                "Applicability triggers: "
                + json.dumps(treatment["triggers"], sort_keys=True),
                "Unresolved questions: "
                + (
                    " | ".join(treatment["unresolved_questions"])
                    if treatment["unresolved_questions"]
                    else "None"
                ),
            ]
        )
    return "\n".join(lines) + "\n"


def _build_engine(policy: dict[str, object]) -> dict[str, object]:
    manifest = policy["manifest"]
    requirements = policy["assessment-requirements.json"]
    risk_model = policy["risk-model.json"]
    framework = policy["controls.json"]
    methodology = policy["control-applicability.json"]
    controls = {item["control_id"]: item for item in framework["controls"]}
    return {
        "package_version": "0.1.0",
        "purpose": "Deterministic build specification for the Microsoft 365 Copilot assessment topic and workflow.",
        "persistence": "none_by_design",
        "assessment_schema_version": requirements["schema_version"],
        "framework_source": manifest["framework_source"],
        "framework_library": manifest["framework_library"],
        "risk_model": risk_model,
        "assessment_fields": requirements["fields"],
        "control_rules": [
            {
                **treatment,
                "title": controls[treatment["control_id"]]["title"],
                "domain": controls[treatment["control_id"]]["domain"],
            }
            for treatment in methodology["controls"]
        ],
        "output_contract": {
            "baseline_tier": "tier_1 | tier_2 | tier_3",
            "final_tier": "tier_1 | tier_2 | tier_3",
            "matched_elevation_rules": "array",
            "enterprise_dependencies": "array",
            "applicable_system_controls": "array",
            "undetermined_system_controls": "array",
            "human_review_required": True,
        },
    }


def _expected_files(policy: dict[str, object]) -> dict[Path, str]:
    risk_model = policy["risk-model.json"]
    framework = policy["controls.json"]
    methodology = policy["control-applicability.json"]
    return {
        Path("knowledge/control-catalog.txt"): _build_knowledge_text(policy),
        Path("workflow/assessment-engine.json"): _json_text(_build_engine(policy)),
        Path("workflow/power-fx/baseline-tier.fx"): _build_baseline_formula(risk_model),
        Path("workflow/power-fx/matched-elevation-rules.fx"): _build_matched_rules_formula(risk_model),
        Path("workflow/power-fx/final-tier.fx"): _build_final_tier_formula(),
        Path("workflow/power-fx/control-outcomes.fx"): _build_control_outcomes_formula(framework, methodology),
        Path("workflow/power-fx/report-fields.fx"): _build_report_fields_formula(),
        Path("tests/acceptance-scenarios.json"): _json_text(_read_json(ACCEPTANCE_SCENARIOS)),
    }


def _build_manifest(policy: dict[str, object], expected: dict[Path, str]) -> dict[str, object]:
    source_manifest = policy["manifest"]
    return {
        "m365_package_version": "0.1.0",
        "runtime": "Microsoft Copilot Studio",
        "external_runtime_required": False,
        "inventory_persistence": False,
        "assessment_schema_version": source_manifest["assessment_schema_version"],
        "risk_model": source_manifest["risk_model"],
        "applicability_methodology": source_manifest["applicability_methodology"],
        "framework_source": source_manifest["framework_source"],
        "framework_library": source_manifest["framework_library"],
        "source_resource_sha256": source_manifest["resource_sha256"],
        "generated_file_sha256": {
            str(path): _sha256_bytes(content.encode("utf-8"))
            for path, content in expected.items()
        },
    }


def build(*, check: bool) -> None:
    policy = _load_policy()
    expected = _expected_files(policy)
    manifest_text = _json_text(_build_manifest(policy, expected))
    expected[Path("package-manifest.json")] = manifest_text

    mismatches: list[str] = []
    for relative_path, content in expected.items():
        destination = M365_ROOT / relative_path
        if check:
            if not destination.is_file() or destination.read_text(encoding="utf-8") != content:
                mismatches.append(str(relative_path))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
    if mismatches:
        raise PackageBuildError(
            "Generated M365 assets are missing or stale: " + ", ".join(mismatches)
        )


def package_transfer_kit(destination: Path) -> None:
    """Create a tenant-neutral archive for transfer to an M365-capable device."""
    if not (M365_ROOT / "README.md").is_file():
        raise PackageBuildError("M365 package README is missing")
    included = [
        path
        for path in sorted(M365_ROOT.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix="ai-governance-m365-", suffix=".zip", delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in included:
                archive.write(path, M365_ROOT.name / path.relative_to(M365_ROOT))
        shutil.move(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build deterministic Microsoft 365 Copilot package assets."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed generated assets without changing them.",
    )
    parser.add_argument(
        "--zip",
        dest="zip_path",
        type=Path,
        help="Create an offline transfer ZIP after building or checking assets.",
    )
    args = parser.parse_args()
    try:
        build(check=args.check)
        if args.zip_path:
            package_transfer_kit(args.zip_path.resolve())
    except PackageBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("Verified" if args.check else "Built", "Microsoft 365 Copilot assets")
    if args.zip_path:
        print(f"Created {args.zip_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
