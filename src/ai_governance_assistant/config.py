"""Runtime configuration with explicit repository boundaries."""

from __future__ import annotations

import os
from pathlib import Path

from ai_governance_control_plane.service import GovernanceDecisionService


def build_service() -> GovernanceDecisionService:
    workspace_value = os.getenv("AI_GOVERNANCE_WORKSPACE")
    framework_value = os.getenv("AI_GOVERNANCE_FRAMEWORK")
    plane_value = os.getenv("AI_GOVERNANCE_CONTROL_PLANE")
    if not any((workspace_value, framework_value, plane_value)):
        return GovernanceDecisionService.from_packaged_resources()

    workspace = Path(workspace_value).expanduser() if workspace_value else None
    framework = (
        Path(framework_value).expanduser()
        if framework_value
        else workspace / "ai-governance-control-framework/data/controls.yaml"
        if workspace
        else None
    )
    plane = (
        Path(plane_value).expanduser()
        if plane_value
        else workspace / "ai-governance-control-plane"
        if workspace
        else None
    )
    if framework is None or plane is None:
        raise ValueError(
            "Set AI_GOVERNANCE_WORKSPACE or both AI_GOVERNANCE_FRAMEWORK and "
            "AI_GOVERNANCE_CONTROL_PLANE for path-based overrides."
        )
    return GovernanceDecisionService.from_paths(
        framework,
        plane / "data/framework-source.yaml",
        plane / "data/risk-model.yaml",
        plane / "data/control-applicability-rules.yaml",
    )
