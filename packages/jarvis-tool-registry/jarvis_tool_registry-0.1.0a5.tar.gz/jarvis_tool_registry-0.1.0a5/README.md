# Tool Registry

This repo will contain the **Tool Registry** service: a standalone tool provider for ARP runtimes.

Current phase: MVP implementation (stdlib-only).

## Design docs

- `docs/intro.md`
- `docs/design/overview.md`

## Install

From PyPI (once published):

```bash
pipx install jarvis-tool-registry
```

Pre-release (e.g. `0.1.0a1`):

```bash
pipx install --pip-args="--pre" jarvis-tool-registry
```

Or in a virtualenv:

```bash
pip install jarvis-tool-registry
```

## Run locally

Create a virtualenv, install `jarvis-model`, then install and run the service:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e path/to/jarvis-model
pip install -e .

tool-registry
```

Env vars:

- `TOOL_REGISTRY_HOST` (default `127.0.0.1`)
- `TOOL_REGISTRY_PORT` (default `8000`)
- `TOOL_REGISTRY_DOMAINS` (default `core`)

Endpoints:

- `GET /v1/tools`
- `GET /v1/tools/{name}`
- `POST /v1/tools/{name}:invoke` (body: `{"args": {...}}`)

More docs:

- `docs/intro.md`
- `docs/adding_tools.md`

## Run tests

From the repo root:

```bash
python3 -m unittest discover -v
```

Or (if you have `pytest` installed):

```bash
pytest -q
```

## MVP capabilities + known gaps

Capabilities:

- Tool discovery (`GET /v1/tools`) and schema detail (`GET /v1/tools/{name}`).
- Validated invocation (`POST /v1/tools/{name}:invoke`) with normalized `ToolResult`/`Error`.
- Simple in-repo “domain modules” pattern for adding tools.

Known gaps:

- No auth, rate limiting, or multi-tenant policy layer yet.
- Stdlib HTTP server only (FastAPI/ASGI swap is a future improvement).
- No MCP aggregation implementation in this MVP.
