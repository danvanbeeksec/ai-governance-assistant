"""Thin, serializable tool facade. Governance logic stays in the Control Plane."""

from __future__ import annotations

from typing import Any

from ai_governance_control_plane.service import GovernanceDecisionService


class GovernanceTools:
    def __init__(self, service: GovernanceDecisionService) -> None:
        self.service = service

    def get_assessment_requirements(self) -> dict[str, Any]:
        """Return the canonical fields, allowed values, and intake questions."""
        return self.service.get_assessment_requirements().model_dump(mode="json")

    def validate_assessment_input(
        self,
        facts: dict[str, Any],
        proposed_inferences: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Validate partial facts without inferring values or assigning risk."""
        return self.service.validate_assessment_input(
            facts, proposed_inferences
        ).model_dump(mode="json")

    def assess_ai_system(self, assessment: dict[str, Any]) -> dict[str, Any]:
        return self.service.assess_ai_system(assessment).model_dump(mode="json")

    def get_applicable_controls(self, assessment: dict[str, Any]) -> dict[str, Any]:
        return self.service.get_applicable_controls(assessment).model_dump(mode="json")

    def explain_control(self, control_id: str) -> dict[str, Any]:
        return self.service.explain_control(control_id).model_dump(mode="json")

    def compare_ai_design_options(self, option_a: dict[str, Any], option_b: dict[str, Any]) -> dict[str, Any]:
        return self.service.compare_ai_design_options(option_a, option_b).model_dump(mode="json")
