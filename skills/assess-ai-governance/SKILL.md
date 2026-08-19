---
name: assess-ai-governance
description: Assess and compare AI use cases with the AI Governance Assistant MCP tools. Use when a user asks to identify missing assessment facts, assign or explain an AI risk tier, identify applicable controls, explain a control or its evidence and framework mappings, or compare AI design options.
---

# Assess AI Governance

Use the connected AI Governance Assistant tools as the only authority for assessment results, controls, evidence expectations, applicability, and framework mappings. Do not reproduce or infer governance logic in conversation.

## Assess a use case

1. Call `get_assessment_requirements` before guided intake. Treat its current fields, allowed values, and questions as canonical.
2. Separate the intake into user-provided facts, proposed inferences with a stated basis, and unresolved questions.
3. Call `validate_assessment_input` with explicit facts and proposed inferences. Never treat an inference as confirmed unless the user explicitly confirms it.
4. If validation returns `needs_information`, ask only the unresolved questions required by the tool. Do not assess yet.
5. When validation returns `ready_for_assessment`, call `assess_ai_system` with the returned assessment object.
6. Present the deterministic tier, risk drivers, applicable controls, unresolved limitations, and framework provenance. State that the result requires human review.

Never ask the user for `assessment_id`; the server manages it. Never override a tool result or fill a missing field from general knowledge.

## Retrieve and explain controls

- Call `get_applicable_controls` when the user wants the authoritative control set without a full narrative assessment.
- Call `explain_control` for a named control. Report only fields returned by the tool, including evidence expectations, applicability metadata, and framework mappings.
- Preserve mapping type and source provenance exactly. Do not imply that a guideline mapping is a requirement.
- If a control ID or requested detail is not returned, say it is unavailable. Never invent a control, mapping, evidence expectation, or rationale.

## Compare designs

Validate each option independently. Call `compare_ai_design_options` only after both options are complete. Explain tier changes and added or removed controls from the returned comparison. Do not claim that the comparison covers cost, performance, architecture quality, or legal compliance unless the tool explicitly returns those dimensions.

## Output structure

Keep facts, assumptions, and open questions visibly distinct. For completed assessments, use:

1. Assessment result
2. Why this tier
3. Applicable controls
4. Facts and confirmed inferences
5. Unresolved questions or limitations
6. Framework provenance and human-review notice

For realistic invocation and safety checks, read [evaluation scenarios](references/evaluation-scenarios.md). For installation and surface-specific limits, read [setup](references/setup.md).
