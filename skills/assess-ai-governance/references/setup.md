# Setup and surface limits

This skill orchestrates the AI Governance Assistant MCP server. The skill contains no control framework or decision logic and is not useful for authoritative assessment unless the six MCP tools are available.

## Claude Code

Install the released MCP package:

```bash
pipx install "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
```

Add the local stdio server for the current project:

```bash
claude mcp add --transport stdio --scope local ai-governance-assistant -- ai-governance-assistant
```

Install the skill for one project by copying the `assess-ai-governance` folder to `.claude/skills/assess-ai-governance/`. For personal use across projects, copy it to `~/.claude/skills/assess-ai-governance/`.

Start Claude Code, run `/mcp` to confirm the server is connected, then ask: `Assess an internal AI assistant and tell me what facts you need.` Claude can auto-invoke the skill or the user can invoke `/assess-ai-governance` explicitly.

## Claude.ai

Package the folder from the repository's `skills` directory:

```bash
cd skills
zip -r ../assess-ai-governance.zip assess-ai-governance
```

The ZIP must contain the `assess-ai-governance/` folder as its top-level entry. In Claude.ai, open **Customize > Skills**, select **+**, **Create skill**, then **Upload a skill**, upload the ZIP, and enable it.

The skill upload does not install or host the MCP server. Claude.ai can use governance tools only through a public HTTPS remote MCP connector. Its documented custom-connector setup supports OAuth client credentials, but this repository's current hosted example uses a shared `x-api-key` header instead. Therefore the uploaded skill can be inspected and tested for triggering in Claude.ai, but it cannot perform authoritative assessments there with the current server authentication design.

Do not remove authentication to work around this limit. A future, separately scoped change can add an OAuth-compatible authorization layer. Localhost and local stdio servers are not reachable from Claude.ai.

## Boundary

Claude Code, Claude.ai, and Claude API skill installations are separate. Installing the skill on one surface does not sync it to another.
