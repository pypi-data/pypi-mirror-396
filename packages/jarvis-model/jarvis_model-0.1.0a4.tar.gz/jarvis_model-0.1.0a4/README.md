# JARVIS Runtime Model

This repo will contain the shared **data model and schemas** used by the ARP ecosystem:

- Agent Runtime Instances
- Tool Registry
- Clients/SDKs

Current phase: MVP with basic standard library tools only.

## Design docs

- `docs/intro.md`
- `docs/design/overview.md`

## What’s implemented

- `jarvis_model/`: dependency-free Python package with:
  - core types (`FlowRun`, `FlowStep`, `ToolDefinition`, `ToolInvocationRequest`, `ToolResult`, `Error`)
  - a small JSON Schema validator for tool arg validation
  - JSON Schema exports in `jarvis_model/schemas.py`

## Install

Pre-release:

```bash
pip install --pre jarvis-model
```

## Run tests

From `Repos/Jarvis/Model`:

```bash
python3 -m unittest discover -v
```

Or `pytest`:

```bash
pytest -q
```

## Install (dev)

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## MVP capabilities + known gaps

Capabilities:

- Shared, versioned types for flows/steps, tool definitions, invocations, and results.
- JSON Schema exports and a lightweight tool-args validator (stdlib-only).

Known gaps:

- Not a full ARP wire-protocol spec yet (transport/network protocol is explicitly out of scope for the MVP).
- Compatibility/versioning policy beyond `schema_version` is still minimal.
