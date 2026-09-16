# Architecture

```text
Local client                    Hosted client
     | stdio                         | Streamable HTTP + API key
     +---------------+---------------+
                     v
             AI Governance Assistant
   |
   v
GovernanceDecisionService (Control Plane)
   |                         |
   v                         v
Risk and applicability      Provenance-validated Control Framework
```

The Claude skill is a separate distribution path:

```text
Claude guided interview
          |
          v
Bundled dependency-free evaluator
          |
          v
Versioned assessment, risk, applicability, and control snapshots
```

The skill snapshots are generated from the same pinned Control Plane and Framework dependency chain and carry resource digests and source provenance. They require no transport or inventory repository, but they must be rebuilt to receive authority updates.

The self-contained Microsoft 365 distribution is another generated path:

```text
Microsoft 365 Copilot or Teams
             |
             v
Copilot Studio guided assessment topic
             |
             v
Generated deterministic Power Fx formulas
             |
             v
Embedded versioned control and policy reference
```

The M365 topic stores assessment values only as conversation variables. It has no connector or action that deliberately creates an inventory, file, row, approval, ticket, or other business record. Microsoft 365 and Power Platform can still retain conversations, audit events, diagnostics, and analytics under tenant policy.

The framework is the control authority. The Control Plane owns assessment validation, risk evaluation, applicability evaluation, and comparison. The MCP runtime converts tool calls to service calls and serializes typed results; its transport code must not copy governance logic or framework content. The Claude and Microsoft 365 distributions are generated snapshots whose parity tests and provenance preserve that authority boundary.

Guided intake follows the same boundary. The Assistant exposes requirement and validation tools, while the Control Plane determines completeness and supported values. No risk decision occurs until a complete canonical assessment exists.

The stdio and HTTP transports instantiate the same tool adapter and service. Transport code does not contain risk, control-applicability, or comparison logic. The hosted path adds only an API-key boundary and health probes. Assessment IDs are interface-managed correlation values; they are not inventory records.

The acceptance suite verifies this boundary through both MCP transports. Scenarios remain synthetic and assert stable governance contracts rather than generated prose or full-response snapshots. Keeping stdio in the suite is the compatibility gate for Codex and other local clients.

The optional Streamlit interface calls the same Control Plane service directly. It provides a deterministic form-based demonstration without adding natural-language inference, persistence, or a second source of governance logic. The Docker image packages both interfaces, while each user remains responsible for choosing either a local MCP client or the no-LLM web form.
