from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .version import SCHEMA_VERSION


def _schema_id(name: str) -> str:
    return f"https://agentruntimeprotocol.org/schemas/{SCHEMA_VERSION}/{name}.schema.json"


ERROR_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("error"),
    "title": "Error",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "code", "message", "retryable"],
    "properties": {
        "schema_version": {"type": "string"},
        "code": {"type": "string"},
        "message": {"type": "string"},
        "details": {"type": "object"},
        "retryable": {"type": "boolean"},
        "cause": {"$ref": "#"},
    },
}

TOOL_SUMMARY_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("tool_summary"),
    "title": "ToolSummary",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "name", "description"],
    "properties": {
        "schema_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}

TOOL_DEFINITION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("tool_definition"),
    "title": "ToolDefinition",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "name", "description", "version", "parameters"],
    "properties": {
        "schema_version": {"type": "string"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "parameters": {"type": "object"},
        "returns": {"type": "object"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "source": {"type": "object"},
    },
}

TOOL_INVOCATION_REQUEST_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("tool_invocation_request"),
    "title": "ToolInvocationRequest",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "args"],
    "properties": {
        "schema_version": {"type": "string"},
        "args": {"type": "object"},
        "context": {"type": "object"},
        "trace": {"type": "object"},
    },
}

TOOL_RESULT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("tool_result"),
    "title": "ToolResult",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "ok"],
    "properties": {
        "schema_version": {"type": "string"},
        "ok": {"type": "boolean"},
        "result": {"type": "object"},
        "error": ERROR_SCHEMA,
        "metrics": {"type": "object"},
        "summary": {"type": "string"},
    },
}

FLOW_STEP_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("flow_step"),
    "title": "FlowStep",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "step_id", "type", "status", "created_at", "payload"],
    "properties": {
        "schema_version": {"type": "string"},
        "step_id": {"type": "string"},
        "type": {"type": "string"},
        "status": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "payload": {"type": "object"},
        "result": {"type": "object"},
        "error": ERROR_SCHEMA,
    },
}

FLOW_RUN_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": _schema_id("flow_run"),
    "title": "FlowRun",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "flow_id", "created_at", "input", "status"],
    "properties": {
        "schema_version": {"type": "string"},
        "flow_id": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time"},
        "input": {},
        "status": {"type": "string"},
        "steps": {"type": "array", "items": FLOW_STEP_SCHEMA},
        "metadata": {"type": "object"},
    },
}


SCHEMAS: dict[str, dict[str, Any]] = {
    "Error": ERROR_SCHEMA,
    "ToolSummary": TOOL_SUMMARY_SCHEMA,
    "ToolDefinition": TOOL_DEFINITION_SCHEMA,
    "ToolInvocationRequest": TOOL_INVOCATION_REQUEST_SCHEMA,
    "ToolResult": TOOL_RESULT_SCHEMA,
    "FlowStep": FLOW_STEP_SCHEMA,
    "FlowRun": FLOW_RUN_SCHEMA,
}


def get_schema(name: str) -> dict[str, Any]:
    if name not in SCHEMAS:
        raise KeyError(f"Unknown schema: {name}")
    return SCHEMAS[name]


def write_schema_bundle(out_dir: str | Path) -> None:
    """Write all schemas to disk as `*.schema.json` (useful for service boundaries)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, schema in SCHEMAS.items():
        path = out / f"{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")

