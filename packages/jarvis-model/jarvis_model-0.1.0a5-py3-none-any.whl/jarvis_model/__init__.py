"""Shared, versioned data model for ARP components.

This package is intentionally dependency-free (stdlib only) so it can be used
across repos without pulling in a framework.
"""

from .errors import Error
from .flow import Flow, FlowRun, FlowStep, Step
from .jsonschema import JsonSchemaValidationError, SchemaViolation, validate_json_schema
from .tool_contracts import (
    ToolCall,
    ToolDefinition,
    ToolInvocationRequest,
    ToolResult,
    ToolSummary,
)
from .validation import ToolArgsValidationError, validate_tool_args
from .version import SCHEMA_VERSION

__all__ = [
    "Error",
    "Flow",
    "FlowRun",
    "FlowStep",
    "JsonSchemaValidationError",
    "SCHEMA_VERSION",
    "SchemaViolation",
    "Step",
    "ToolArgsValidationError",
    "ToolCall",
    "ToolDefinition",
    "ToolInvocationRequest",
    "ToolResult",
    "ToolSummary",
    "validate_json_schema",
    "validate_tool_args",
]

