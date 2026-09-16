#!/usr/bin/env python3
"""Dependency-free evaluator for the packaged AI governance skill."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import hmac
import json
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = SKILL_ROOT / "references"
MANIFEST_FILE = REFERENCES / "package-manifest.json"


class SkillAssessmentError(ValueError):
    """Raised when bundled policy data or assessment input is unsafe to use."""


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillAssessmentError(f"Cannot read valid JSON from {path.name}: {exc}") from exc


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_policy() -> dict[str, Any]:
    """Load bundled resources only after verifying their manifest digests."""
    manifest = _read_json(MANIFEST_FILE)
    resources: dict[str, Any] = {}
    for filename, expected_digest in manifest["resource_sha256"].items():
        path = REFERENCES / filename
        try:
            actual_digest = _sha256(path)
        except OSError as exc:
            raise SkillAssessmentError(f"Bundled resource is unavailable: {filename}") from exc
        if not hmac.compare_digest(actual_digest, expected_digest):
            raise SkillAssessmentError(f"Bundled resource digest mismatch: {filename}")
        resources[filename] = _read_json(path)

    framework = resources["controls.json"]
    methodology = resources["control-applicability.json"]
    source = manifest["framework_source"]
    if framework["library_version"] != source["library_version"]:
        raise SkillAssessmentError("Framework version does not match package provenance")
    if methodology["methodology"]["framework_library_version"] != framework["library_version"]:
        raise SkillAssessmentError("Applicability methodology does not match the framework")
    if methodology["methodology"]["status"] != "approved":
        raise SkillAssessmentError("Applicability methodology is not approved")

    controls = framework["controls"]
    control_ids = [control["control_id"] for control in controls]
    treatment_ids = [item["control_id"] for item in methodology["controls"]]
    if len(control_ids) != len(set(control_ids)):
        raise SkillAssessmentError("Framework contains duplicate control IDs")
    if sorted(control_ids) != sorted(treatment_ids):
        raise SkillAssessmentError("Applicability methodology does not cover the framework exactly")

    return {
        "manifest": manifest,
        "requirements": resources["assessment-requirements.json"],
        "risk_model": resources["risk-model.json"],
        "methodology": methodology,
        "framework": framework,
    }


def assessment_requirements(policy: dict[str, Any]) -> dict[str, Any]:
    requirements = deepcopy(policy["requirements"])
    requirements["privacy_notice"] = (
        "This packaged evaluator does not create an inventory record, write assessment "
        "data, or transmit it to an external service. The host running the skill controls "
        "conversation and code-execution retention."
    )
    requirements["human_review_notice"] = (
        "The result is decision support. A qualified human owns the final classification "
        "and control decisions."
    )
    return requirements


def _issue(
    field: str,
    issue: str,
    question: str,
    detail: str | None = None,
    allowed_values: list[str] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"field": field, "issue": issue, "question": question}
    if detail:
        result["detail"] = detail
    if allowed_values is not None:
        result["allowed_values"] = allowed_values
    return result


def validate_assessment(
    raw_facts: Any, policy: dict[str, Any], *, assign_id: bool = False
) -> dict[str, Any]:
    """Validate explicit, user-confirmed facts without inferring missing values."""
    if not isinstance(raw_facts, dict):
        return {
            "status": "needs_information",
            "supplied_facts": {},
            "issues": [
                _issue(
                    "assessment",
                    "invalid",
                    "Provide the assessment as a JSON object.",
                )
            ],
            "assessment": None,
        }

    facts = deepcopy(raw_facts)
    requirements = policy["requirements"]
    risk_model = policy["risk_model"]
    fields = {item["field"]: item for item in requirements["fields"]}
    supported = set(fields) | {"assessment_id", "schema_version"}
    issues: list[dict[str, Any]] = []

    for field in sorted(set(facts) - supported):
        issues.append(
            _issue(
                field,
                "invalid",
                "Remove the unsupported assessment field.",
                "Unknown assessment field.",
            )
        )

    for field, requirement in fields.items():
        if field not in facts or facts[field] is None or facts[field] == "":
            issues.append(
                _issue(
                    field,
                    "missing",
                    requirement["question"],
                    allowed_values=requirement.get("allowed_values") or None,
                )
            )
            continue

        value = facts[field]
        allowed = risk_model["enums"].get(field)
        if requirement.get("accepts_multiple"):
            if not isinstance(value, list):
                issues.append(
                    _issue(
                        field,
                        "invalid",
                        requirement["question"],
                        "Provide a JSON array, including an empty array when none apply.",
                        allowed,
                    )
                )
            elif len(value) != len(set(value)):
                issues.append(
                    _issue(
                        field,
                        "invalid",
                        requirement["question"],
                        "Values must not be duplicated.",
                        allowed,
                    )
                )
            elif allowed and any(item not in allowed for item in value):
                issues.append(
                    _issue(
                        field,
                        "invalid",
                        requirement["question"],
                        "One or more values are unsupported.",
                        allowed,
                    )
                )
        elif allowed and value not in allowed:
            issues.append(
                _issue(
                    field,
                    "invalid",
                    requirement["question"],
                    "Select one supported value.",
                    allowed,
                )
            )
        elif not allowed and (not isinstance(value, str) or not value.strip()):
            issues.append(
                _issue(
                    field,
                    "invalid",
                    requirement["question"],
                    "Provide a non-empty text value.",
                )
            )

    if "schema_version" in facts and facts["schema_version"] != requirements["schema_version"]:
        issues.append(
            _issue(
                "schema_version",
                "invalid",
                f"Use assessment schema version {requirements['schema_version']}.",
            )
        )
    if "assessment_id" in facts and (
        not isinstance(facts["assessment_id"], str) or not facts["assessment_id"].strip()
    ):
        issues.append(
            _issue(
                "assessment_id",
                "invalid",
                "Omit the assessment ID and allow the skill to generate one.",
            )
        )

    if issues:
        return {
            "status": "needs_information",
            "supplied_facts": facts,
            "issues": issues,
            "assessment": None,
        }

    assessment = {"schema_version": requirements["schema_version"], **facts}
    if assign_id and "assessment_id" not in assessment:
        assessment["assessment_id"] = f"ASM-{uuid4().hex[:12].upper()}"
    return {
        "status": "ready_for_assessment",
        "supplied_facts": facts,
        "issues": [],
        "assessment": assessment,
    }


def _conditions_match(facts: dict[str, Any], conditions: dict[str, Any]) -> bool:
    for field, expected in conditions.items():
        actual = facts.get(field)
        if isinstance(expected, dict):
            if "equals" in expected and actual != expected["equals"]:
                return False
            if "in" in expected and actual not in expected["in"]:
                return False
            if "any_of" in expected:
                actual_values = actual if isinstance(actual, list) else [actual]
                if not any(value in actual_values for value in expected["any_of"]):
                    return False
        elif actual != expected:
            return False
    return True


def evaluate_risk(assessment: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    model = policy["risk_model"]
    autonomy = assessment["autonomy_level"]
    sensitivity = assessment["information_sensitivity"]
    baseline = model["baseline_matrix"][autonomy][sensitivity]
    tier_order = model["model"]["tier_order"]
    final_tier = baseline
    applied_rules: list[dict[str, Any]] = []
    explanation = [
        f"The baseline is {baseline.replace('_', ' ').title()} because the system is "
        f"{autonomy.replace('_', ' ')} and uses {sensitivity.replace('_', ' ')} information."
    ]

    for rule in model["elevation_rules"]:
        if not _conditions_match(assessment, rule["when"]):
            continue
        prior = final_tier
        minimum = rule["minimum_tier"]
        final_tier = prior if tier_order.index(prior) <= tier_order.index(minimum) else minimum
        changed = prior != final_tier
        applied_rules.append(
            {
                "rule_id": rule["id"],
                "reason": rule["reason"],
                "prior_tier": prior,
                "resulting_tier": final_tier,
                "changed_tier": changed,
            }
        )
        if changed:
            explanation.append(
                f"{rule['id']} increased the classification from "
                f"{prior.replace('_', ' ').title()} to {final_tier.replace('_', ' ').title()}: "
                f"{rule['reason']}"
            )
        else:
            explanation.append(
                f"{rule['id']} matched but did not change the classification because it was "
                f"already at least {minimum.replace('_', ' ').title()}: {rule['reason']}"
            )

    explanation.append(
        f"The final inherent-risk classification is {final_tier.replace('_', ' ').title()}. "
        "Controls do not reduce this inherent-risk result."
    )
    return {
        "status": "evaluated",
        "assessment_id": assessment["assessment_id"],
        "assessment_schema_version": assessment["schema_version"],
        "model_id": model["model"]["id"],
        "model_version": str(model["model"]["version"]),
        "submitted_facts": deepcopy(assessment),
        "baseline_inputs": {
            "autonomy_level": autonomy,
            "information_sensitivity": sensitivity,
        },
        "baseline_tier": baseline,
        "final_tier": final_tier,
        "applied_rules": applied_rules,
        "explanation": explanation,
        "human_review_required": True,
        "framework_source": deepcopy(policy["manifest"]["framework_source"]),
    }


def _condition_match(facts: dict[str, Any], condition: dict[str, Any]) -> bool:
    actual = facts[condition["field"]]
    if condition["operator"] == "in":
        return actual in condition["values"]
    if condition["operator"] == "contains_any":
        return any(value in actual for value in condition["values"])
    raise SkillAssessmentError(f"Unsupported operator: {condition['operator']}")


def _matched_facts(facts: dict[str, Any], treatment: dict[str, Any]) -> list[dict[str, Any]]:
    matched: list[dict[str, Any]] = []
    for group_number, group in enumerate(treatment.get("triggers", []), start=1):
        if not all(_condition_match(facts, condition) for condition in group["all"]):
            continue
        for condition in group["all"]:
            matched.append(
                {
                    "field": condition["field"],
                    "operator": condition["operator"],
                    "submitted_value": deepcopy(facts[condition["field"]]),
                    "expected_values": deepcopy(condition["values"]),
                    "trigger_group": group_number,
                }
            )
    return matched


def recommend_controls(
    assessment: dict[str, Any], decision: dict[str, Any], policy: dict[str, Any]
) -> dict[str, Any]:
    controls = {
        control["control_id"]: control for control in policy["framework"]["controls"]
    }
    enterprise: list[dict[str, Any]] = []
    applicable: list[dict[str, Any]] = []
    undetermined: list[dict[str, Any]] = []

    for treatment in policy["methodology"]["controls"]:
        control = controls[treatment["control_id"]]
        if treatment["section"] == "enterprise_dependencies":
            outcome = "inherited_dependency"
            matched = []
            questions = [
                "Confirm the enterprise provider, inheritance scope, required configuration, "
                "exclusions, evidence, and review period."
            ]
        elif treatment["treatment"] == "universal":
            outcome = "applicable"
            matched = []
            questions = []
        elif treatment["treatment"] == "human_determination":
            outcome = "undetermined"
            matched = []
            questions = deepcopy(treatment["unresolved_questions"])
        else:
            matched = _matched_facts(assessment, treatment)
            outcome = "applicable" if matched else "undetermined"
            questions = [] if matched else deepcopy(treatment["unresolved_questions"])

        recommendation = {
            "control_id": control["control_id"],
            "title": control["title"],
            "domain": control["domain"],
            "section": treatment["section"],
            "treatment": treatment["treatment"],
            "outcome": outcome,
            "enterprise_dependency": treatment["enterprise_dependency"],
            "rationale": treatment["rationale"],
            "matched_facts": matched,
            "unresolved_questions": questions,
            "evidence_examples": deepcopy(control["evidence_examples"]),
            "human_confirmation_required": True,
        }
        if treatment["section"] == "enterprise_dependencies":
            enterprise.append(recommendation)
        elif outcome == "applicable":
            applicable.append(recommendation)
        else:
            undetermined.append(recommendation)

    methodology = policy["methodology"]
    return {
        "status": "recommendations_generated",
        "assessment_id": assessment["assessment_id"],
        "assessment_schema_version": assessment["schema_version"],
        "risk_model_id": decision["model_id"],
        "risk_model_version": decision["model_version"],
        "inherent_risk_tier": decision["final_tier"],
        "framework_source": deepcopy(policy["manifest"]["framework_source"]),
        "methodology_id": methodology["methodology"]["id"],
        "methodology_version": methodology["methodology"]["version"],
        "enterprise_dependencies": enterprise,
        "applicable_system_controls": applicable,
        "undetermined_system_controls": undetermined,
        "summary": {
            "total_controls": len(controls),
            "enterprise_dependencies": len(enterprise),
            "applicable_system_controls": len(applicable),
            "undetermined_system_controls": len(undetermined),
        },
        "human_confirmation_required": True,
    }


def evaluate_assessment(raw_facts: Any, policy: dict[str, Any]) -> dict[str, Any]:
    validation = validate_assessment(raw_facts, policy, assign_id=True)
    if validation["status"] != "ready_for_assessment":
        return validation
    assessment = validation["assessment"]
    decision = evaluate_risk(assessment, policy)
    recommendations = recommend_controls(assessment, decision, policy)
    return {
        "status": "assessment_complete",
        "assessment": assessment,
        "decision": decision,
        "recommendations": recommendations,
        "limitations": [
            "This is an inherent-risk classification, not an approval or residual-risk decision.",
            "Control recommendations require human confirmation, tailoring, ownership, and evidence review.",
            "The result does not establish legal compliance, certification, or standards conformity.",
        ],
    }


def explain_control(control_id: str, policy: dict[str, Any]) -> dict[str, Any]:
    for control in policy["framework"]["controls"]:
        if control["control_id"] == control_id:
            treatment = next(
                item
                for item in policy["methodology"]["controls"]
                if item["control_id"] == control_id
            )
            return {
                "status": "control_found",
                "control": deepcopy(control),
                "applicability_treatment": deepcopy(treatment),
                "framework_source": deepcopy(policy["manifest"]["framework_source"]),
            }
    return {
        "status": "control_not_found",
        "control_id": control_id,
        "framework_source": deepcopy(policy["manifest"]["framework_source"]),
    }


def compare_assessments(
    raw_a: Any, raw_b: Any, policy: dict[str, Any]
) -> dict[str, Any]:
    left = evaluate_assessment(raw_a, policy)
    right = evaluate_assessment(raw_b, policy)
    if left["status"] != "assessment_complete" or right["status"] != "assessment_complete":
        return {
            "status": "needs_information",
            "option_a": left,
            "option_b": right,
        }
    left_ids = {
        item["control_id"]
        for item in left["recommendations"]["applicable_system_controls"]
    }
    right_ids = {
        item["control_id"]
        for item in right["recommendations"]["applicable_system_controls"]
    }
    return {
        "status": "comparison_complete",
        "option_a": left,
        "option_b": right,
        "tier_changed": left["decision"]["final_tier"] != right["decision"]["final_tier"],
        "controls_added": sorted(right_ids - left_ids),
        "controls_removed": sorted(left_ids - right_ids),
    }


def _input_json(value: str) -> Any:
    if value == "-":
        try:
            return json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise SkillAssessmentError(f"Standard input is not valid JSON: {exc}") from exc
    return _read_json(Path(value))


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the packaged AI governance assessment without a network service."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("requirements", help="Return the assessment questions and allowed values.")
    validate_parser = subparsers.add_parser("validate", help="Validate assessment facts without assigning a tier.")
    validate_parser.add_argument("input", help="JSON file path or - for standard input.")
    evaluate_parser = subparsers.add_parser("evaluate", help="Evaluate one complete assessment.")
    evaluate_parser.add_argument("input", help="JSON file path or - for standard input.")
    explain_parser = subparsers.add_parser("explain-control", help="Return one authoritative control.")
    explain_parser.add_argument("control_id")
    compare_parser = subparsers.add_parser("compare", help="Compare two complete assessment designs.")
    compare_parser.add_argument(
        "input",
        help="JSON file path or - for an object containing option_a and option_b.",
    )
    args = parser.parse_args()

    try:
        policy = load_policy()
        if args.command == "requirements":
            result = assessment_requirements(policy)
        elif args.command == "validate":
            result = validate_assessment(_input_json(args.input), policy)
        elif args.command == "evaluate":
            result = evaluate_assessment(_input_json(args.input), policy)
        elif args.command == "explain-control":
            result = explain_control(args.control_id, policy)
        else:
            comparison = _input_json(args.input)
            if not isinstance(comparison, dict) or not {
                "option_a",
                "option_b",
            }.issubset(comparison):
                raise SkillAssessmentError(
                    "Comparison input must contain option_a and option_b objects"
                )
            result = compare_assessments(
                comparison["option_a"], comparison["option_b"], policy
            )
        _print(result)
        return 0
    except SkillAssessmentError as exc:
        _print({"status": "error", "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
