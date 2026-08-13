# AI Governance Assistant

Private MCP interface for the AI Governance Control Plane. This repository contains interface and configuration code only. It does not own controls, risk scoring, applicability rules, or governance decisions.

## Tools

- `assess_ai_system`: run a validated assessment and return the risk decision plus control recommendations.
- `get_applicable_controls`: return the deterministic recommendation set for an assessment.
- `explain_control`: retrieve one authoritative control, including applicability metadata.
- `compare_ai_design_options`: assess two complete design options and report tier and applicable-control differences.

All assessment tools accept the Control Plane's canonical structured assessment contract. Natural-language fact extraction is intentionally deferred because guessed inputs would weaken determinism.

## Local development

Keep sibling checkouts of all three repositories in one workspace. Install this package in a virtual environment, then run `ai-governance-assistant`. The default stdio transport is suitable for local MCP clients.

Set `AI_GOVERNANCE_WORKSPACE` when the repositories do not share a parent directory. `AI_GOVERNANCE_FRAMEWORK` and `AI_GOVERNANCE_CONTROL_PLANE` can override the individual locations.

Run tests with `python -m pytest`.

## Scope

This foundation does not provide approvals, evidence management, inventory expansion, authentication, hosted transport, legal conclusions, or natural-language inference. Tool outputs require human review and preserve the framework provenance emitted by the Control Plane.
