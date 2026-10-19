from pathlib import Path
import json

from streamlit.testing.v1 import AppTest

from ai_governance_assistant.web_launcher import format_tier


def test_tier_uses_canonical_tier_name():
    assert format_tier("tier_3") == "Tier 3"


def test_web_demo_loads_without_external_services():
    app_path = Path(__file__).parents[1] / "src/ai_governance_assistant/web.py"
    app = AppTest.from_file(str(app_path)).run(timeout=15)
    assert not app.exception
    assert not app.error
    assert app.title[0].value == "AI Governance Assistant"
    assert len(app.selectbox) == 8
    assert len(app.multiselect) == 1


def test_complete_web_form_produces_reviewable_result():
    root = Path(__file__).parents[1]
    facts = json.loads((root / 'tests/fixtures/acceptance_scenarios.json').read_text())['internal_assistant']
    app = AppTest.from_file(str(root / 'src/ai_governance_assistant/web.py')).run(timeout=15)
    for widget in app.text_input:
        widget.set_value(facts[widget.label.lower().replace(' ', '_')])
    app.text_area[0].set_value(facts['business_purpose'])
    for widget in app.selectbox:
        widget.set_value(facts[widget.label.lower().replace(' ', '_')])
    app.multiselect[0].set_value(facts['agent_capabilities'])
    app.button[0].click().run(timeout=15)
    assert not app.exception
    assert next(item for item in app.metric if item.label == 'Final tier').value == 'Tier 3: Lower'
    assert 'Controls requiring an applicability decision' in [item.value for item in app.subheader]
    assert 'Enterprise inheritance questions' in [item.value for item in app.subheader]
