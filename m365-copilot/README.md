# AI Governance Assessment for Microsoft 365 Copilot

This directory is a tenant-neutral build and transfer kit for a self-contained Microsoft Copilot Studio agent. The agent interviews a user, calculates inherent AI risk, and returns applicable, inherited, and undetermined governance controls in chat.

The runtime design uses Microsoft Copilot Studio only. It does not require the repository's MCP server, an Azure service, a custom connector, an AI-system inventory, or a database. Assessment answers are not deliberately written to Dataverse, SharePoint, OneDrive, or another business record. Microsoft 365 and Power Platform audit, diagnostic, and conversation-retention behavior still follows the installing tenant's configuration.

## What is included

- `agent/instructions.md`: agent behavior and safety instructions
- `agent/conversation-starters.json`: suggested prompts
- `agent/adaptive-cards/assessment-form.json`: optional structured chat form
- `agent/report-template.md`: chat response layout
- `knowledge/control-catalog.txt`: generated embedded knowledge file
- `workflow/assessment-engine.json`: generated decision-table specification
- `workflow/power-fx/`: generated deterministic formulas
- `tenant-build-runbook.md`: exact Copilot Studio assembly and export procedure
- `validation-checklist.md`: release and tenant acceptance checks
- `package-manifest.json`: authority versions and integrity hashes
- `verify_package.py`: dependency-free verification on the M365-capable device

## Important package boundary

This is not a Power Platform solution export. Microsoft creates environment-specific component identities when an agent, topic, and solution are created in a tenant. A valid managed or unmanaged solution ZIP must therefore be assembled and exported from the target Microsoft environment.

The kit removes policy-design work from that tenant step. The maker transfers the supplied files, follows the build runbook, runs the supplied scenarios, and exports the completed solution.

## Build and verify locally

From the repository root:

```bash
python scripts/build_m365_copilot_package.py --check
python scripts/build_m365_copilot_package.py --zip dist/ai-governance-m365-transfer-kit.zip
```

Generated assets are derived from the same integrity-checked Framework 1.2.0 snapshot used by the Claude skill. Do not manually edit generated knowledge, engine, formula, or manifest files.

After extracting the transfer archive on another device, verify it with:

```bash
python verify_package.py
```

## Installation sequence

1. Transfer this directory or the generated ZIP to the M365-capable device.
2. Follow `tenant-build-runbook.md` to assemble the agent in an unmanaged Power Platform solution.
3. Complete every item in `validation-checklist.md` using synthetic data.
4. Export an unmanaged solution for source preservation and a managed solution for repeatable installation.
5. Import the managed solution into the intended environment, reconfigure Microsoft authentication, publish it, and request organizational catalog approval.

## Scope

The result is decision support. It is not an approval, residual-risk decision, legal conclusion, certification, or finding of compliance. A qualified person must confirm classification, control applicability, ownership, tailoring, and evidence expectations.
