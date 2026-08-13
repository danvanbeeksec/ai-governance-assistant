import pytest

from ai_governance_assistant.config import build_service


def test_default_configuration_uses_packaged_resources(monkeypatch):
    for name in (
        "AI_GOVERNANCE_WORKSPACE",
        "AI_GOVERNANCE_FRAMEWORK",
        "AI_GOVERNANCE_CONTROL_PLANE",
    ):
        monkeypatch.delenv(name, raising=False)

    service = build_service()
    assert service.framework.source.status == "loaded"
    assert service.framework.source.library_version == "1.1.0"


def test_partial_path_override_fails_closed(monkeypatch):
    monkeypatch.delenv("AI_GOVERNANCE_WORKSPACE", raising=False)
    monkeypatch.setenv("AI_GOVERNANCE_FRAMEWORK", "/tmp/controls.yaml")
    monkeypatch.delenv("AI_GOVERNANCE_CONTROL_PLANE", raising=False)
    with pytest.raises(ValueError, match="both AI_GOVERNANCE_FRAMEWORK"):
        build_service()
