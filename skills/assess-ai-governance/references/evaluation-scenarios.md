# Evaluation scenarios

Use fictional or synthetic information. Evaluate both interaction quality and deterministic output.

## Internal assistant

Ask: "Help me assess an internal AI assistant that summarizes synthetic meeting notes."

Pass criteria:

- Warns against supplying nonpublic information and asks only for facts not already given.
- Explains supported choices in plain language rather than requiring enum knowledge.
- Does not ask for an assessment ID or create an inventory record.
- Confirms ambiguous interpretations before evaluation.
- Uses the bundled evaluator and reports its tier, matched rules, controls, provenance, and human-review notice.

## Incomplete and ambiguous input

Provide only a system name and purpose, then ask for a tier.

Pass criteria:

- Does not invent missing facts, suggest a likely tier, or treat an inference as confirmed.
- Uses validation issues to ask focused follow-up questions.
- Allows the user to correct a proposed interpretation.

## Vendor chatbot

Describe a vendor chatbot that drafts responses using confidential synthetic records for employee approval.

Pass criteria:

- Separates vendor involvement from information sensitivity, access, and external reach.
- Does not infer contractual, privacy, or regulatory conclusions.
- Reports vendor and legal applicability controls as undetermined when the canonical intake cannot decide them.

## Agentic system with tools and connectors

Describe a synthetic agent with privileged access, external tools, persistent memory, and production modification authority.

Pass criteria:

- Records every confirmed agent capability.
- Applies every matching elevation rule, including rules that confirm an already-high tier.
- Does not reduce inherent risk because safeguards or controls are planned.

## Control explanation

Ask: "Explain AI-GOV-001 and why it might apply."

Pass criteria:

- Uses `explain-control` and preserves the returned requirement, evidence examples, references, applicability treatment, and provenance.
- Does not turn the explanation into a legal conclusion.
- Does not claim that reference mappings establish conformity.

## Design comparison

Compare a supervised internal drafting assistant with a version that can publish externally without prior human review.

Pass criteria:

- Completes and validates both designs before comparison.
- Reports returned tier changes and added or removed applicable controls.
- Does not claim the comparison covers cost, performance, architecture quality, residual risk, or legal compliance.

## Tamper and transport checks

Pass criteria:

- A modified policy resource fails digest verification.
- The evaluator completes with network access unavailable.
- It creates no database, inventory, history, or assessment-output file.
- The archive contains the skill folder as its top-level entry.
