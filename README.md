# AI Governance Assistant

Public MCP and local demonstration interface for the AI Governance Control Plane. This repository contains interface and configuration code only. It does not own controls, risk scoring, applicability rules, or governance decisions.

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
| 0.4.0 | 0.6.0 | 1.2.0 |
| 0.3.0 | 0.4.0 | 1.1.0 |
| 0.2.0 | 0.4.0 | 1.1.0 |

The Assistant pins the reviewed Control Plane source commit, which in turn pins the reviewed Framework source commit. This table identifies the human-readable release versions represented by that dependency chain.

## Choose an access option

### Local MCP with pipx

This is the recommended option for an MCP client that supports local stdio servers. It has no hosted service or per-assessment charge.

```bash
pipx install "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
ai-governance-assistant
```

Use [`examples/mcp-config.pipx.json`](examples/mcp-config.pipx.json) as a client configuration template. The client should launch the server; do not start it separately.

### Docker MCP server

```bash
docker build -t ai-governance-assistant:0.4.0 .
```

Use [`examples/mcp-config.docker.json`](examples/mcp-config.docker.json) to let an MCP client launch the container over stdio.

### Local web demonstration without an LLM

```bash
pipx install "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
pipx inject ai-governance-assistant "streamlit>=1.41,<2"
ai-governance-assistant-web
```

Or run the web demonstration from Docker:

```bash
docker run --rm -p 8501:8501 ai-governance-assistant:0.4.0 \
  ai-governance-assistant-web --server.address=0.0.0.0
```

Open `http://localhost:8501`. The form calls the same deterministic Control Plane service and does not require a model or API key.

See [`docs/installation.md`](docs/installation.md) for installation, client configuration, verification, and security guidance.

### Claude Agent Skill

The portable [`assess-ai-governance`](skills/assess-ai-governance/SKILL.md) Agent Skill guides Claude through fact collection, validation, assessment, control explanation, and design comparison using the MCP tools above. It contains no governance logic or copied controls. See [`docs/claude-skill.md`](docs/claude-skill.md) for Claude Code installation, Claude.ai packaging, and cross-surface limits.

### Hosted MCP for Microsoft 365 Copilot

The separate `ai-governance-assistant-http` command exposes the same tools at `/mcp` using MCP Streamable HTTP. It requires an `x-api-key` header and provides `/healthz` and `/readyz` probes. The local stdio command remains unchanged.

See [`docs/microsoft-365-copilot.md`](docs/microsoft-365-copilot.md) for deployment and Copilot Studio setup. The included Azure Container Apps example is a starting point, not a production authorization.

## Local development

Install this package in a virtual environment, then run `ai-governance-assistant`. The default stdio transport is suitable for local MCP clients. Normal operation uses the Framework and Control Plane policy resources supplied by the pinned installed packages, so sibling repositories are not required.

For reviewed local development overrides, set `AI_GOVERNANCE_WORKSPACE` to a parent containing sibling repositories. Alternatively, set both `AI_GOVERNANCE_FRAMEWORK` and `AI_GOVERNANCE_CONTROL_PLANE`. Partial overrides fail closed.

Run tests with `python -m pytest`.

The test suite launches both stdio and authenticated Streamable HTTP servers and exercises the tools through MCP client sessions. Public-safe synthetic fixtures cover guided intake, explicit inference confirmation, system-managed assessment IDs, four AI design contexts, deterministic results, framework provenance, control explanation, and design comparison. GitHub Actions runs the same acceptance journey and starts the HTTP container.

## Safety and scope

This foundation does not provide approvals, evidence management, inventory persistence, legal conclusions, or server-side natural-language inference. Hosted MCP supports shared API-key authentication as an initial interoperability control, not as a complete production identity design. Tool outputs require human review and preserve the framework provenance emitted by the Control Plane.

Use only fictional or synthetic information. See [`SECURITY.md`](SECURITY.md) for public-use boundaries and vulnerability reporting.
