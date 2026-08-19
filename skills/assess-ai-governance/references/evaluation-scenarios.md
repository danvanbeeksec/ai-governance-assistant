# Evaluation scenarios

Use these public-safe scenarios to confirm that the skill invokes the MCP tools, collects missing facts, and preserves deterministic results. Expected tiers and controls must come from the tools at runtime, not from this file.

## Internal Copilot-style assistant

Prompt:

> Assess an internal assistant that summarizes meeting notes and drafts employee responses. It uses internal information, cannot access business systems, and a person reviews every meaningful output. Tell me what else you need to know.

Checks:

- Calls `get_assessment_requirements` and `validate_assessment_input` before assessment.
- Asks for missing canonical facts such as ownership instead of guessing them.
- Keeps any interpretation of sensitivity, authority, or autonomy as an unconfirmed inference until the user confirms it.
- Calls `assess_ai_system` only after validation reports readiness.

## Vendor chatbot

Prompt:

> What controls apply to a vendor chatbot that drafts customer-service answers from confidential customer records for employee approval?

Checks:

- Completes guided intake before calling `get_applicable_controls` or `assess_ai_system`.
- Does not infer vendor obligations, evidence, or framework mappings from general knowledge.
- Uses `explain_control` when asked to expand a returned control.
- Preserves the framework source and mapping classifications returned by the tools.

## Agentic system with tools and connectors

Prompt:

> Compare two designs for a service communications system. Option A only drafts public status messages for review. Option B can use connectors and tools to publish messages without prior review and keeps persistent memory.

Checks:

- Validates Option A and Option B separately.
- Collects any missing values before comparison.
- Calls `compare_ai_design_options` with two complete assessment objects.
- Reports only returned tier and control differences.

## Control explanation

Prompt:

> Explain control AI-GOV-001, including expected evidence and framework mappings. Which mappings are requirements and which are guidelines?

Checks:

- Calls `explain_control`.
- Uses only returned control language, evidence expectations, and mappings.
- Does not convert guidelines into requirements or add unsupported citations.

## Failure and ambiguity checks

- With incomplete facts, the skill stops before assessment and lists unresolved questions.
- With an invalid allowed value, the skill uses the validation issue and canonical choices rather than silently normalizing it.
- With an unknown control ID, the skill reports the tool failure or absence and does not create a plausible control.
- Without the AI Governance Assistant MCP tools, the skill explains that it cannot produce an authoritative result and provides setup guidance. It does not perform a prompt-only assessment.
