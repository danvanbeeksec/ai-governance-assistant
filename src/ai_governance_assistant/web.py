"""Optional no-LLM Streamlit demonstration for the governance service."""

from __future__ import annotations

from typing import Any

from ai_governance_assistant.config import build_service


LABELS = {
    "assessment_id": "Assessment ID",
    "system_name": "System name",
    "business_purpose": "Business purpose",
    "accountable_owner": "Accountable owner",
    "autonomy_level": "Autonomy level",
    "information_sensitivity": "Information sensitivity",
    "human_review": "Human review",
    "action_authority": "Action authority",
    "system_access": "System access",
    "external_reach": "External reach",
    "reversibility": "Reversibility",
    "decision_impact": "Decision impact",
    "agent_capabilities": "Agent capabilities",
}


def _display(value: str) -> str:
    return value.replace("_", " ").capitalize()


def render() -> None:
    import streamlit as st

    st.set_page_config(page_title="AI Governance Assistant", page_icon="🛡️")
    st.title("AI Governance Assistant")
    st.caption(
        "A deterministic, local demonstration. Use only fictional or synthetic information."
    )

    try:
        service = build_service()
        requirements = service.get_assessment_requirements()
    except Exception as exc:  # pragma: no cover - visible operational failure
        st.error(f"The governance service could not be initialized: {exc}")
        return

    facts: dict[str, Any] = {}
    with st.form("assessment"):
        for requirement in requirements.fields:
            field = requirement.field
            label = LABELS.get(field, _display(field))
            if requirement.accepts_multiple:
                facts[field] = st.multiselect(
                    label,
                    requirement.allowed_values,
                    format_func=_display,
                    help=requirement.question,
                )
            elif requirement.allowed_values:
                facts[field] = st.selectbox(
                    label,
                    [""] + requirement.allowed_values,
                    format_func=lambda value: "Select one" if not value else _display(value),
                    help=requirement.question,
                )
            elif field == "business_purpose":
                facts[field] = st.text_area(label, help=requirement.question)
            else:
                default = "SYNTHETIC-001" if field == "assessment_id" else ""
                facts[field] = st.text_input(
                    label, value=default, help=requirement.question
                )
        submitted = st.form_submit_button("Assess design", type="primary")

    if not submitted:
        st.info("Complete the form to receive a risk tier and applicable controls.")
        return

    facts = {
        key: value
        for key, value in facts.items()
        if value not in (None, "")
    }
    validation = service.validate_assessment_input(facts)
    if validation.assessment is None:
        st.warning("More information is required before assessment.")
        for issue in validation.issues:
            detail = f" ({issue.detail})" if issue.detail else ""
            st.write(f"- **{LABELS.get(issue.field, issue.field)}:** {issue.question}{detail}")
        return

    result = service.assess_ai_system(validation.assessment)
    decision = result.decision
    col1, col2, col3 = st.columns(3)
    col1.metric("Final tier", decision.final_tier_label or decision.final_tier)
    col2.metric(
        "Applicable controls",
        result.recommendations.summary.applicable_system_controls,
    )
    col3.metric("Framework", decision.framework_source.library_version or "Unknown")

    st.subheader("Decision explanation")
    st.write(decision.executive_summary)
    for explanation in decision.explanation:
        st.write(f"- {explanation}")

    st.subheader("Applicable controls")
    rows = [
        {
            "Control": item.control.control_id,
            "Title": item.control.title,
            "Rationale": item.rationale,
        }
        for item in result.recommendations.applicable_system_controls
    ]
    st.dataframe(rows, width="stretch", hide_index=True)

    with st.expander("Framework provenance"):
        st.json(decision.framework_source.model_dump(mode="json"))
    with st.expander("Structured result"):
        st.json(result.model_dump(mode="json"))

    st.warning(
        "This demonstration supports governance analysis and human review. "
        "It is not legal advice or an authorization decision."
    )


render()
