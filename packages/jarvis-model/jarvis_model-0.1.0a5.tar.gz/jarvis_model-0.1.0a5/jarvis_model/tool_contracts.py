from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .errors import Error
from .version import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class ToolSummary:
    name: str
    description: str
    version: Optional[str] = None
    tags: Optional[list[str]] = None
    schema_version: str = SCHEMA_VERSION

    def to_planner_dict(self) -> dict[str, Any]:
        # Planner view is intentionally minimal (keeps prompts small).
        return {"name": self.name, "description": self.description}


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    version: str = "0.1.0"
    returns: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None
    source: Optional[dict[str, Any]] = None
    schema_version: str = SCHEMA_VERSION

    @property
    def parameters_json_schema(self) -> dict[str, Any]:
        return self.parameters

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": self.parameters,
        }
        if self.returns is not None:
            data["returns"] = self.returns
        if self.tags is not None:
            data["tags"] = self.tags
        if self.source is not None:
            data["source"] = self.source
        return data


@dataclass(frozen=True, slots=True)
class ToolCall:
    tool_name: str
    arguments: dict[str, Any]
    correlation_id: str
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "correlation_id": self.correlation_id,
        }


@dataclass(frozen=True, slots=True)
class ToolInvocationRequest:
    args: dict[str, Any]
    context: Optional[dict[str, Any]] = None
    trace: Optional[dict[str, Any]] = None
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolInvocationRequest":
        args = data.get("args")
        if not isinstance(args, dict):
            raise ValueError("ToolInvocationRequest.args must be an object")
        context = data.get("context")
        trace = data.get("trace")
        return cls(
            schema_version=str(data.get("schema_version") or SCHEMA_VERSION),
            args=args,
            context=context if isinstance(context, dict) else None,
            trace=trace if isinstance(trace, dict) else None,
        )


@dataclass(frozen=True, slots=True)
class ToolResult:
    ok: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[Error] = None
    metrics: Optional[dict[str, Any]] = None
    summary: Optional[str] = None
    schema_version: str = SCHEMA_VERSION

    @property
    def data(self) -> Optional[dict[str, Any]]:
        return self.result

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "ok": self.ok,
        }
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error.to_dict()
        if self.metrics is not None:
            data["metrics"] = self.metrics
        if self.summary is not None:
            data["summary"] = self.summary
        return data

