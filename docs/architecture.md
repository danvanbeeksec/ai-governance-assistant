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
