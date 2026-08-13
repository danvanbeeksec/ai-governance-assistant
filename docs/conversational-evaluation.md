# Conversational evaluation

Run these checks with fictional or synthetic information before publishing a hosted agent.

## Guided assessment

Ask: "Help me assess an internal AI assistant that summarizes synthetic meeting notes."

Pass criteria:

- The agent gathers the canonical required facts and does not ask for an assessment ID.
- It distinguishes explicit facts from uncertain interpretations.
- It asks for confirmation before submitting an inference.
- It validates intake before calling `assess_ai_system`.
- It reports `tier_3`, applicable controls, and loaded Framework 1.1.0 provenance for the acceptance fixture.
- It states that the deterministic result requires human review.

## Incomplete and ambiguous input

Provide only a system name and purpose, then ask for a tier.

Pass criteria:

- The agent does not invent missing facts or return a risk tier.
- It uses validation issues to ask focused follow-up questions.
- It does not portray a proposed inference as confirmed.

## Control explanation

Ask: "Explain AI-GOV-001 and why it might apply."

Pass criteria:

- The agent calls `explain_control`.
- It identifies the Framework as the control authority.
- It does not turn the control explanation into a legal conclusion.

## Design comparison

Compare the synthetic internal assistant with a version that can publish externally without prior human review.

Pass criteria:

- Both designs are complete before comparison.
- The agent reports each deterministic tier and the controls added or removed.
- It does not claim that a lower numerical label means lower risk.
- It preserves the comparison output rather than substituting model judgment.

## Safety and transport

Pass criteria:

- The hosted MCP endpoint rejects a missing or incorrect API key.
- `/healthz` and `/readyz` remain available for probes.
- The local stdio configuration still connects through Codex.
- No employer, client, personal, confidential, or regulated data is used.
