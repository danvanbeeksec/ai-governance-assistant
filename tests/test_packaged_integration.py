from ai_governance_assistant.config import build_service


def test_packaged_service_runs_assessment(monkeypatch):
    for name in (
        "AI_GOVERNANCE_WORKSPACE",
        "AI_GOVERNANCE_FRAMEWORK",
        "AI_GOVERNANCE_CONTROL_PLANE",
    ):
        monkeypatch.delenv(name, raising=False)

    assessment = {
        "assessment_id": "assistant-package-smoke",
        "system_name": "Synthetic Knowledge Assistant",
        "business_purpose": "Verify the installed MCP service boundary",
        "accountable_owner": "Synthetic Owner",
        "autonomy_level": "human_supervised",
        "information_sensitivity": "internal",
        "human_review": "prior_to_each_meaningful_action",
        "action_authority": "generate_only",
        "system_access": "none",
        "external_reach": "none",
        "reversibility": "easy",
        "decision_impact": "operational",
        "agent_capabilities": [],
    }
    result = build_service().assess_ai_system(assessment)
    assert result.decision.framework_source.library_version == "1.1.0"
    assert result.decision.framework_source.status == "loaded"
    assert result.recommendations.summary.total_controls == 70


def test_packaged_service_guides_incomplete_input(monkeypatch):
    for name in (
        "AI_GOVERNANCE_WORKSPACE",
        "AI_GOVERNANCE_FRAMEWORK",
        "AI_GOVERNANCE_CONTROL_PLANE",
    ):
        monkeypatch.delenv(name, raising=False)
    result = build_service().validate_assessment_input(
        {"assessment_id": "partial-001", "system_name": "Synthetic Assistant"}
    )
    assert result.status == "needs_information"
    assert any(issue.field == "business_purpose" for issue in result.issues)
    assert result.assessment is None
