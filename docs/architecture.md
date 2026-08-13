# Architecture

```text
MCP client
   |
   v
AI Governance Assistant
   |
   v
GovernanceDecisionService (Control Plane)
   |                         |
   v                         v
Risk and applicability      Provenance-validated Control Framework
```

The framework is the control authority. The Control Plane owns assessment validation, risk evaluation, applicability evaluation, and comparison. The Assistant converts MCP tool calls to service calls and serializes typed results. It must not copy governance logic or framework content.

Guided intake follows the same boundary. The Assistant exposes requirement and validation tools, while the Control Plane determines completeness and supported values. No risk decision occurs until a complete canonical assessment exists.

The acceptance suite verifies this boundary through the MCP stdio protocol. Scenarios remain synthetic and assert stable governance contracts rather than generated prose or full-response snapshots.
