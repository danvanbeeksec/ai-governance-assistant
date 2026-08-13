from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_web_demo_loads_without_external_services():
    app_path = Path(__file__).parents[1] / "src/ai_governance_assistant/web.py"
    app = AppTest.from_file(str(app_path)).run(timeout=15)
    assert not app.exception
    assert not app.error
    assert app.title[0].value == "AI Governance Assistant"
    assert len(app.selectbox) == 8
    assert len(app.multiselect) == 1
