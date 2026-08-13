"""Runtime configuration with explicit repository boundaries."""

from __future__ import annotations

import os
from pathlib import Path

from ai_governance_control_plane.service import GovernanceDecisionService


def build_service() -> GovernanceDecisionService:
    workspace = Path(os.getenv("AI_GOVERNANCE_WORKSPACE", Path.cwd().parent))
    framework = Path(os.getenv("AI_GOVERNANCE_FRAMEWORK", workspace / "ai-governance-control-framework/data/controls.yaml"))
    plane = Path(os.getenv("AI_GOVERNANCE_CONTROL_PLANE", workspace / "ai-governance-control-plane"))
    return GovernanceDecisionService.from_paths(
        framework,
        plane / "data/framework-source.yaml",
        plane / "data/risk-model.yaml",
        plane / "data/control-applicability-rules.yaml",
    )
