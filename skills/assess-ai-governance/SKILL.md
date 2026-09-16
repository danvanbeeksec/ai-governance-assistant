---
name: assess-ai-governance
description: Conduct a structured AI governance risk assessment by interviewing the user, validating the answers, and applying the bundled deterministic risk and control-applicability models. Use when a user asks to assess or classify an AI use case, identify governance controls, explain a control, compare AI designs, or determine what governance questions must be answered. The skill operates without an external MCP service or AI-system inventory.
---

# Assess AI Governance

Conduct assessments with the bundled, versioned evaluator. Do not substitute model judgment for its risk tier or control-applicability results.

## Safety boundary

- Tell the user not to provide personal, confidential, employer, client, regulated, security-sensitive, or other nonpublic information. Use generalized or synthetic descriptions.
- Explain that the assessment is decision support, not an approval, residual-risk decision, legal conclusion, certification, or finding of compliance.
- Do not create or update an AI-system inventory, assessment history, database, or durable record.
- Do not ask for an assessment ID. The evaluator creates an ephemeral correlation value.
- Do not call an MCP server, remote API, or external service.

## Guided assessment

1. Read [the intake guide](references/intake-guide.md) before interviewing the user.
2. Run `python scripts/assess.py requirements` from this skill directory to load the canonical questions and allowed values.
3. Extract facts the user has already supplied. Keep explicit facts, proposed interpretations, and unresolved questions visibly separate.
4. Ask only unresolved questions. Use concise batches when several fields remain, but ask individually when a prior answer changes the meaning of the next question.
5. When translating a natural-language answer into an allowed value, state the proposed value and basis. Do not use it until the user confirms it.
6. Pass only explicit facts and confirmed interpretations as JSON through standard input to `python scripts/assess.py validate -`.
7. If validation returns `needs_information`, ask the reported questions. Do not assign or suggest a tier.
8. When validation returns `ready_for_assessment`, pass the same confirmed facts to `python scripts/assess.py evaluate -`.

Treat the evaluator output as authoritative for the baseline tier, final tier, matched elevation rules, and control categories. Never lower the tier because controls exist or appear strong.

## Present a completed assessment

Summarize rather than reproducing the complete JSON. Use this order:

1. Assessment result and human-review notice
2. Why this tier, including baseline inputs and every matched elevation rule
3. Applicable system controls
4. Enterprise dependencies requiring inheritance confirmation
5. Controls that remain undetermined and their follow-up questions
6. Facts and confirmed interpretations used
7. Limitations and framework provenance

Do not describe an undetermined control as unnecessary. Absence of a trigger does not establish non-applicability.

## Explain a control

Run `python scripts/assess.py explain-control CONTROL_ID`. Report only returned control content, applicability treatment, evidence examples, references, and provenance. If the control is not found, say so. Do not invent a control, mapping, requirement, or evidence expectation.

## Compare designs

Complete and validate each option independently. Pass an object containing `option_a` and `option_b` through standard input to `python scripts/assess.py compare -`. Explain returned tier changes and added or removed applicable controls. Do not claim that the comparison covers cost, performance, architecture quality, residual risk, or legal compliance.

For realistic invocation and safety checks, read [evaluation scenarios](references/evaluation-scenarios.md). For installation, rebuilding, and version boundaries, read [setup](references/setup.md).
