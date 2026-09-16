# Claude Agent Skill

The repository includes `skills/assess-ai-governance`, a portable Agent Skill that conducts a guided AI governance interview and runs a bundled deterministic evaluator. It does not require the MCP server, a remote connector, an AI-system inventory, or a database.

## What the skill contains

- `SKILL.md`: interview, confirmation, safety, evaluation, and reporting instructions.
- `scripts/assess.py`: a dependency-free evaluator for validation, inherent-risk classification, control applicability, control explanation, and design comparison.
- `references/assessment-requirements.json`: canonical questions and supported values.
- `references/risk-model.json`: baseline matrix and elevation rules.
- `references/control-applicability.json`: approved applicability methodology.
- `references/controls.json`: the pinned control-framework snapshot.
- `references/package-manifest.json`: source provenance and resource digests.
- `references/intake-guide.md`: plain-language interpretation guidance.

The risk and control resources are exported from the Assistant's pinned Control Plane dependency. They are point-in-time release artifacts, not a new governance authority. The package preserves the framework library's lifecycle status as well as its version, source commit, and digest. The build fails closed at runtime if a resource digest is changed without rebuilding the manifest.

## Interaction model

Claude collects explicit facts, proposes interpretations when needed, and waits for confirmation before using them. The evaluator rejects incomplete or unsupported input instead of inferring it. Completed results preserve the baseline tier, every matched elevation rule, the final inherent-risk tier, control categories, open applicability questions, model versions, and framework provenance.

The evaluator creates an ephemeral assessment ID but no inventory record. It reads assessment JSON from standard input, writes result JSON to standard output, makes no network calls, and writes no assessment data.

## Validate and package

Run the full suite:

```bash
python -m pytest
```

Run Anthropic-compatible metadata validation:

```bash
python /path/to/quick_validate.py skills/assess-ai-governance
```

Refresh the exported resources and create the upload archive:

```bash
python scripts/build_claude_skill.py --zip dist/assess-ai-governance.zip
```

Inspect the archive before upload. Its top-level entry must be the `assess-ai-governance/` folder containing `SKILL.md`, `scripts/`, and `references/`.

## Claude.ai

Enable code execution, then open **Customize > Skills**, select **+**, **Create skill**, and **Upload a skill**. Upload `assess-ai-governance.zip` and enable it. No custom connector is required.

## Claude Code

Copy the skill folder to `.claude/skills/assess-ai-governance/` for a project or `~/.claude/skills/assess-ai-governance/` for personal use. No MCP configuration is required for the packaged assessment.

## Release boundary

Rebuild and retest the ZIP whenever the assessment contract, risk model, applicability methodology, or control framework changes. The skill package is not automatically updated when a source repository changes.

Do not submit personal, confidential, employer, client, regulated, security-sensitive, or other nonpublic information unless the intended Claude deployment and its retention settings have been separately approved. The result is decision support and does not establish approval, residual risk, legal compliance, certification, or evidence sufficiency.
