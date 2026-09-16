# Microsoft 365 Copilot options

This repository supports two distinct Microsoft 365 Copilot patterns.

## Self-contained Copilot Studio solution kit

Use [`../m365-copilot/README.md`](../m365-copilot/README.md) when the assessment must run inside Microsoft Copilot Studio without an external MCP server, Azure runtime, custom connector, inventory, or assessment database.

The kit contains generated Power Fx formulas, an embedded control reference, agent instructions, a structured Adaptive Card, acceptance scenarios, and a tenant build and export runbook. Its final Power Platform solution ZIP must be assembled in a Microsoft tenant because Microsoft assigns environment-specific component identities.

This is the recommended distribution for a public, bring-your-own-tenant release.

## Hosted MCP connection

Microsoft 365 Copilot can use the Assistant through an agent created in Copilot Studio. The Assistant exposes MCP Streamable HTTP at `/mcp`; the existing stdio command remains the local Codex path.

## Before deployment

1. Build and publish this repository's container image to a registry available to Azure Container Apps.
2. Generate a long random API key and store it as an Azure Container Apps secret.
3. Deploy the image with external HTTPS ingress targeting port 8000.
4. Set the container command to `ai-governance-assistant-http`.
5. Confirm `https://<your-host>/healthz` returns `{"status":"ok"}`.
6. Test `https://<your-host>/mcp` with MCP Inspector using the `x-api-key` header.

[`../deploy/azure-container-app.yaml`](../deploy/azure-container-app.yaml) is a parameterized starting point. Replace all angle-bracket placeholders before applying it. Azure provides TLS at the ingress boundary. Keep the key in a secret reference rather than source control.

## Add the MCP server in Copilot Studio

1. Create or open an agent and enable generative orchestration.
2. Open **Tools**, select **Add a tool**, then choose **New tool** and **Model Context Protocol**.
3. Enter `https://<your-host>/mcp` as the server URL.
4. Select API-key authentication and configure the key as the `x-api-key` header.
5. Add the connection and confirm all six tools appear.
6. Add agent instructions that preserve the server's intake safeguards. Do not infer missing facts, confirm uncertain interpretations, validate before assessment, report Framework provenance, and require human review.
7. Publish only after completing the synthetic evaluation in `docs/conversational-evaluation.md`.

Microsoft's current Copilot Studio MCP wizard supports Streamable transport. If your tenant UI differs, use Microsoft's current Copilot Studio MCP documentation and verify that the connector sends the configured header.

## Expected behavior

The model conducts the conversation and converts explicit user statements into the structured tool contract. The Assistant does not perform language-model inference. The Control Plane remains authoritative for completeness, risk, applicability, and comparison. The Framework remains authoritative for controls.

The Assistant creates an `ASM-...` assessment correlation ID when the client does not supply one. Users should not be asked to invent it. This release does not save an inventory record or guarantee that the generated ID persists across separate conversations.

## Production limitations

The example uses one shared API key. That is suitable for controlled interoperability testing, not a complete enterprise identity model. Before broad use, decide on user identity, tenant isolation, authorization, rate limiting, secret rotation, audit logging, privacy, retention, support, and incident response. Keep all demonstrations fictional or synthetic until those decisions are implemented and reviewed.
