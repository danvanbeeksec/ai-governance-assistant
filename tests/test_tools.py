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
        return Serializable({"fields": ["system_name"], "managed_fields": ["assessment_id"]})

    def validate_assessment_input(
        self, facts, proposed_inferences=None, managed_facts=None
    ):
        return Serializable(
            {
                "facts": facts,
                "proposed_inferences": proposed_inferences,
                "managed_facts": managed_facts,
            }
        )

    def assess_ai_system(self, value):
        return Serializable({"operation": "assess", "input": value})

    def get_applicable_controls(self, value):
        return Serializable({"operation": "controls", "input": value})

    def explain_control(self, value):
        return Serializable({"control_id": value})

    def compare_ai_design_options(self, left, right):
        return Serializable({"left": left, "right": right})


def test_tools_delegate_without_implementing_governance_logic():
    assert __version__ == "0.5.0"
    tools = GovernanceTools(FakeService(), assessment_id_factory=lambda: "ASM-TEST")
    assert tools.get_assessment_requirements()["fields"] == ["system_name"]
    assert tools.validate_assessment_input({"x": 1})["facts"] == {"x": 1}
    assert tools.validate_assessment_input({"x": 1})["managed_facts"] == {
        "assessment_id": "ASM-TEST"
    }
    assert tools.assess_ai_system({"x": 1})["input"]["assessment_id"] == "ASM-TEST"
    assert tools.get_applicable_controls({"x": 1})["input"]["assessment_id"] == "ASM-TEST"
    assert tools.explain_control("AI-GOV-001") == {"control_id": "AI-GOV-001"}
    comparison = tools.compare_ai_design_options({"a": 1}, {"b": 2})
    assert comparison["left"]["assessment_id"] == "ASM-TEST"
    assert comparison["right"]["assessment_id"] == "ASM-TEST"


def test_caller_supplied_assessment_id_is_preserved_for_compatibility():
    tools = GovernanceTools(FakeService(), assessment_id_factory=lambda: "ASM-NEW")
    result = tools.assess_ai_system({"assessment_id": "EXISTING"})
    assert result["input"]["assessment_id"] == "EXISTING"
