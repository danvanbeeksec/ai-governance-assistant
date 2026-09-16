# Conversational evaluation

Run these checks with fictional or synthetic information before distributing the Claude skill or publishing a hosted agent.

## Guided assessment

Ask: "Help me assess an internal AI assistant that summarizes synthetic meeting notes."

Pass criteria:

- The agent warns against providing nonpublic information.
- It gathers canonical required facts and does not ask for an assessment ID.
- It explains choices in plain language.
- It distinguishes explicit facts from uncertain interpretations.
- It asks for confirmation before using an interpretation.
- It validates intake before evaluation.
- It reports the evaluator's tier, controls, Framework 1.2.0 provenance, and human-review notice.

## Incomplete and ambiguous input

Provide only a system name and purpose, then ask for a tier.

Pass criteria:

- The agent does not invent missing facts or return a risk tier.
- It uses validation issues to ask focused follow-up questions.
- It does not portray a proposed interpretation as confirmed.

## Control explanation

Ask: "Explain AI-GOV-001 and why it might apply."

Pass criteria:

- The agent uses the packaged control explanation command.
- It preserves the framework provenance and evidence examples.
- It does not turn the control explanation into a legal conclusion.

## Design comparison

Compare the synthetic internal assistant with a version that can publish externally without prior human review.

Pass criteria:

- Both designs are complete before comparison.
- The agent reports each deterministic tier and the controls added or removed.
- It does not claim that a lower numerical label means lower risk.
- It does not substitute model judgment for the evaluator output.

## Safety and packaging

Pass criteria:

- A modified policy resource fails digest verification.
- The evaluator operates with network access unavailable.
- No inventory, database, history, or assessment-output file is created.
- The ZIP contains `assess-ai-governance/` as its top-level folder.
- No employer, client, personal, confidential, or regulated data is used.
