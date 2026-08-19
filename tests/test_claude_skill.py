"""Static validation for the portable Anthropic Agent Skill."""

from pathlib import Path
import re

import yaml


SKILL = Path(__file__).parents[1] / "skills" / "assess-ai-governance"


def _frontmatter() -> dict[str, str]:
    text = (SKILL / "SKILL.md").read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None
    return yaml.safe_load(match.group(1))


def test_skill_uses_anthropic_structure_and_metadata_rules() -> None:
    metadata = _frontmatter()
    assert set(metadata) == {"name", "description"}
    assert metadata["name"] == SKILL.name
    assert re.fullmatch(r"[a-z0-9-]{1,64}", metadata["name"])
    assert "anthropic" not in metadata["name"]
    assert "claude" not in metadata["name"]
    assert 1 <= len(metadata["description"]) <= 1024


def test_skill_delegates_every_governance_operation_to_mcp() -> None:
    text = (SKILL / "SKILL.md").read_text()
    expected_tools = {
        "get_assessment_requirements",
        "validate_assessment_input",
        "assess_ai_system",
        "get_applicable_controls",
        "explain_control",
        "compare_ai_design_options",
    }
    assert all(f"`{tool}`" in text for tool in expected_tools)
    assert "Never invent a control" in text
    assert "framework provenance" in text.lower()


def test_skill_references_exist_and_examples_cover_required_scenarios() -> None:
    skill_text = (SKILL / "SKILL.md").read_text()
    for relative_path in re.findall(r"\]\((references/[^)]+)\)", skill_text):
        assert (SKILL / relative_path).is_file()

    scenarios = (SKILL / "references" / "evaluation-scenarios.md").read_text()
    assert "Internal Copilot-style assistant" in scenarios
    assert "Vendor chatbot" in scenarios
    assert "Agentic system with tools and connectors" in scenarios


def test_skill_contains_no_governance_outcomes() -> None:
    text = "\n".join(path.read_text() for path in SKILL.rglob("*.md"))
    assert not re.search(r"expected tier\s*:\s*tier_[123]", text, flags=re.IGNORECASE)
    assert "expected controls:" not in text.lower()
