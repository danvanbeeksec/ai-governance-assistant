# Installation and local use

The Assistant supports three local access paths and one separately hosted MCP path. Local paths run the deterministic governance service on the user's machine and require no OpenAI API key.

## Requirements

- Python 3.10 or later for the pipx option
- Docker Desktop or another compatible Docker runtime for the container option
- An MCP client with local stdio support for conversational use
- Fictional or synthetic assessment information only

## Option 1: pipx and local MCP

Install the released package and its Git-pinned dependencies in an isolated environment:

```bash
pipx install "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
```

Confirm the command is available without starting the stdio server:

```bash
command -v ai-governance-assistant
```

The server uses stdio for MCP protocol messages, so an MCP client must launch it. Start with `examples/mcp-config.pipx.json` and adapt the configuration location to the client. If the client cannot find the command, replace it with the absolute path reported by:

```bash
which ai-governance-assistant
```

Do not type into the server process or send blank lines to it. Stdio accepts JSON-RPC messages only.

## Option 2: Docker and local MCP

Build the image:

```bash
docker build -t ai-governance-assistant:0.4.0 .
```

Start with `examples/mcp-config.docker.json`. The `-i` argument is required because MCP communicates through the container's standard input and output. Do not add `-t`, because terminal formatting can corrupt the protocol stream.

## Option 3: deterministic web form

Install the Assistant and optional web dependency:

```bash
pipx install "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
pipx inject ai-governance-assistant "streamlit>=1.41,<2"
ai-governance-assistant-web
```

Open `http://localhost:8501`, complete the synthetic assessment, and select **Assess design**. The result includes the risk tier, deterministic explanation, applicable controls, and Framework provenance.

The web demonstration has no authentication. Keep it bound to the local machine. Do not expose it to a public network without a separate production security design.

## Option 4: authenticated Streamable HTTP

For local transport testing only:

```bash
export AI_GOVERNANCE_API_KEY="replace-with-a-long-random-test-value"
ai-governance-assistant-http
```

The MCP endpoint is `http://localhost:8000/mcp`. Clients must send the API key in the `x-api-key` header. Health and readiness probes are available at `/healthz` and `/readyz`. Do not expose a workstation listener to the internet.

The equivalent container command is:

```bash
docker run --rm -p 8000:8000 \
  -e AI_GOVERNANCE_API_KEY="replace-with-a-long-random-test-value" \
  ai-governance-assistant:0.4.0 ai-governance-assistant-http
```

See `docs/microsoft-365-copilot.md` for the hosted path.

## Verification checklist

For MCP installations:

1. Confirm all six tools are discovered.
2. Call `get_assessment_requirements`.
3. Validate an incomplete assessment and confirm no risk tier is returned.
4. Assess a complete synthetic design.
5. Confirm Framework version 1.1.0 and status `loaded`.
6. Compare identical designs and confirm there is no artificial difference.

For the web form:

1. Confirm the page loads without an API key.
2. Submit an incomplete form and confirm it asks for missing information.
3. Submit a complete synthetic form and confirm a risk tier and controls appear.
4. Expand Framework provenance and confirm version 1.1.0.

## Upgrade and removal

Upgrade a pipx installation to a new tag:

```bash
pipx reinstall "git+https://github.com/danvanbeeksec/ai-governance-assistant.git@v0.4.0"
```

Remove it with:

```bash
pipx uninstall ai-governance-assistant
```

Remove the local Docker image with:

```bash
docker image rm ai-governance-assistant:0.4.0
```
