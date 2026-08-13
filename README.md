# AI Governance Assistant

Private MCP interface for the AI Governance Control Plane. This repository contains interface and configuration code only. It does not own controls, risk scoring, applicability rules, or governance decisions.

## Tools

- `get_assessment_requirements`: return canonical intake fields, allowed values, and questions.
- `validate_assessment_input`: validate partial facts and proposed inferences without assigning risk.
- `assess_ai_system`: run a validated assessment and return the risk decision plus control recommendations.
- `get_applicable_controls`: return the deterministic recommendation set for an assessment.
- `explain_control`: retrieve one authoritative control, including applicability metadata.
- `compare_ai_design_options`: assess two complete design options and report tier and applicable-control differences.

Assessment execution tools accept the Control Plane's canonical structured assessment contract. Guided intake can identify missing or invalid facts before execution. Natural-language extraction remains a client responsibility, and proposed inferences require a stated basis plus explicit confirmation before the Control Plane will use them.

## Release compatibility

| Assistant | Control Plane | Control Framework |
| --- | --- | --- |
| 0.2.0 | 0.4.0 | 1.1.0 |

The Assistant pins the reviewed Control Plane source commit, which in turn pins the reviewed Framework source commit. This table identifies the human-readable release versions represented by that dependency chain.

## Local development

Install this package in a virtual environment, then run `ai-governance-assistant`. The default stdio transport is suitable for local MCP clients. Normal operation uses the Framework and Control Plane policy resources supplied by the pinned installed packages, so sibling repositories are not required.

For reviewed local development overrides, set `AI_GOVERNANCE_WORKSPACE` to a parent containing sibling repositories. Alternatively, set both `AI_GOVERNANCE_FRAMEWORK` and `AI_GOVERNANCE_CONTROL_PLANE`. Partial overrides fail closed.

Run tests with `python -m pytest`.

The test suite launches the installed stdio server and exercises all six tools through an MCP client session. Public-safe synthetic fixtures cover guided intake, explicit inference confirmation, four AI design contexts, deterministic results, framework provenance, control explanation, and design comparison. GitHub Actions runs the same acceptance journey.

## Scope

This foundation does not provide approvals, evidence management, inventory expansion, authentication, hosted transport, legal conclusions, or natural-language inference. Tool outputs require human review and preserve the framework provenance emitted by the Control Plane.
