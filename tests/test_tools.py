from ai_governance_assistant.tools import GovernanceTools
from ai_governance_assistant import __version__


class Serializable:
    def __init__(self, value):
        self.value = value

    def model_dump(self, mode):
        assert mode == "json"
        return self.value


class FakeService:
    def get_assessment_requirements(self):
        return Serializable({"fields": ["assessment_id"]})

    def validate_assessment_input(self, facts, proposed_inferences=None):
        return Serializable({"facts": facts, "proposed_inferences": proposed_inferences})

    def assess_ai_system(self, value):
        return Serializable({"operation": "assess", "input": value})

    def get_applicable_controls(self, value):
        return Serializable({"operation": "controls", "input": value})

    def explain_control(self, value):
        return Serializable({"control_id": value})

    def compare_ai_design_options(self, left, right):
        return Serializable({"left": left, "right": right})


def test_tools_delegate_without_implementing_governance_logic():
    assert __version__ == "0.3.0"
    tools = GovernanceTools(FakeService())
    assert tools.get_assessment_requirements()["fields"] == ["assessment_id"]
    assert tools.validate_assessment_input({"x": 1})["facts"] == {"x": 1}
    assert tools.assess_ai_system({"x": 1})["operation"] == "assess"
    assert tools.get_applicable_controls({"x": 1})["operation"] == "controls"
    assert tools.explain_control("AI-GOV-001") == {"control_id": "AI-GOV-001"}
    assert tools.compare_ai_design_options({"a": 1}, {"b": 2})["right"] == {"b": 2}
