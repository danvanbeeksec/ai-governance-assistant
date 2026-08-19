# Claude Agent Skill

The repository includes `skills/assess-ai-governance`, a portable Agent Skill that orchestrates the existing MCP interface. The Control Framework remains the control authority, the Control Plane remains the risk and decision service, and this repository remains the integration layer.

## What the skill adds

The skill instructs Claude to:

- collect canonical facts before assessment;
- distinguish explicit facts, confirmed inferences, and unresolved questions;
- call the MCP tools instead of reproducing governance logic;
- explain deterministic tiers, drivers, controls, evidence expectations, and mappings;
- preserve framework provenance and mapping classifications;
- stop rather than invent an outcome when the tools are absent or input is incomplete.

Detailed evaluation prompts live in `skills/assess-ai-governance/references/evaluation-scenarios.md`. Surface-specific commands and packaging steps live in `skills/assess-ai-governance/references/setup.md`.

## Validate and package

Run the full suite:

```bash
python -m pytest
```

Run Anthropic-compatible metadata validation:

```bash
python /path/to/quick_validate.py skills/assess-ai-governance
```

Create the Claude.ai upload archive from the repository's `skills` directory:

```bash
cd skills
zip -r ../assess-ai-governance.zip assess-ai-governance
```

Inspect the archive before upload. Its top-level entry must be the `assess-ai-governance/` folder, which contains `SKILL.md` and `references/`.

## Important Claude.ai limit

Uploading the ZIP installs the instructions only. Claude.ai cannot launch the local stdio command. A working Claude.ai assessment also requires an OAuth-compatible public HTTPS MCP connector. The repository's current hosted example uses a shared `x-api-key`, which is not an authentication option in Anthropic's documented custom-connector setup. Do not expose the service without authentication. OAuth support is follow-up work outside this skill-only change.
