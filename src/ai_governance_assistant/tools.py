"""Thin, serializable tool facade. Governance logic stays in the Control Plane."""

from __future__ import annotations

from typing import Any
from collections.abc import Callable
from uuid import uuid4

from ai_governance_control_plane.service import GovernanceDecisionService


def generate_assessment_id() -> str:
    """Create a public-safe correlation ID without collecting user identifiers."""
    return f"ASM-{uuid4().hex[:12].upper()}"


class GovernanceTools:
    def __init__(
        self,
        service: GovernanceDecisionService,
        assessment_id_factory: Callable[[], str] = generate_assessment_id,
    ) -> None:
        self.service = service
        self.assessment_id_factory = assessment_id_factory

    def _managed_assessment(self, assessment: dict[str, Any]) -> dict[str, Any]:
        if assessment.get("assessment_id"):
            return assessment
        return {**assessment, "assessment_id": self.assessment_id_factory()}

    def get_assessment_requirements(self) -> dict[str, Any]:
        """Return canonical user fields, allowed values, questions, and managed fields."""
        return self.service.get_assessment_requirements().model_dump(mode="json")

    def validate_assessment_input(
        self,
        facts: dict[str, Any],
        proposed_inferences: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Validate explicit facts and confirmed inferences without assigning risk.

        Do not ask the user for assessment_id. The Assistant generates it as a managed
        correlation value. Unconfirmed proposed inferences remain excluded.
        """
        managed_facts = None
        if not facts.get("assessment_id"):
            managed_facts = {"assessment_id": self.assessment_id_factory()}
        return self.service.validate_assessment_input(
            facts,
            proposed_inferences,
            managed_facts=managed_facts,
        ).model_dump(mode="json")

    def assess_ai_system(self, assessment: dict[str, Any]) -> dict[str, Any]:
        """Assess one complete AI design and return its deterministic tier and controls."""
        return self.service.assess_ai_system(
            self._managed_assessment(assessment)
        ).model_dump(mode="json")

    def get_applicable_controls(self, assessment: dict[str, Any]) -> dict[str, Any]:
        """Return deterministic applicable controls for one complete AI design."""
        return self.service.get_applicable_controls(
            self._managed_assessment(assessment)
        ).model_dump(mode="json")

    def explain_control(self, control_id: str) -> dict[str, Any]:
        """Explain one authoritative control and its applicability metadata."""
        return self.service.explain_control(control_id).model_dump(mode="json")

    def compare_ai_design_options(self, option_a: dict[str, Any], option_b: dict[str, Any]) -> dict[str, Any]:
        """Compare deterministic tiers and control sets for two complete AI designs."""
        return self.service.compare_ai_design_options(
            self._managed_assessment(option_a),
            self._managed_assessment(option_b),
        ).model_dump(mode="json")
