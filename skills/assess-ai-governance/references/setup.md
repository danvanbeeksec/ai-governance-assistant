# Setup and version boundaries

This skill contains a dependency-free evaluator plus versioned snapshots of the canonical assessment contract, risk model, control-applicability methodology, and control framework. It does not require an MCP server, network connector, database, or inventory.

## Claude.ai

Upload `assess-ai-governance.zip` through **Customize > Skills > + > Create skill > Upload a skill**, then enable it. Code execution must be enabled. The archive must contain the `assess-ai-governance/` folder as its top-level entry.

## Claude Code

Copy the `assess-ai-governance` folder to `.claude/skills/assess-ai-governance/` for one project or `~/.claude/skills/assess-ai-governance/` for personal use across projects. No MCP configuration is required.

## Rebuild

From the repository root, run:

```bash
python scripts/build_claude_skill.py --zip dist/assess-ai-governance.zip
```

The build reads the Assistant's pinned Control Plane dependency, exports its validated policy resources, writes resource digests and provenance to `references/package-manifest.json`, and creates the upload archive. Run the test suite before distributing a rebuilt package.

Treat a rebuilt ZIP as a new point-in-time release. Rebuild whenever the assessment schema, risk model, applicability methodology, or control framework changes. Do not edit exported JSON by hand.

## Data handling

The evaluator reads JSON from standard input and writes JSON to standard output. It does not make network requests or write assessment data. Claude and the code-execution host may retain conversation or execution data according to their own settings and terms. Use only generalized or synthetic information unless the deployment has been separately approved for the intended data.

## Boundary

Claude Code, Claude.ai, and Claude API skill installations are separate. Installing the skill on one surface does not sync it to another. The package does not establish approval, legal compliance, certification, evidence sufficiency, or residual risk.
