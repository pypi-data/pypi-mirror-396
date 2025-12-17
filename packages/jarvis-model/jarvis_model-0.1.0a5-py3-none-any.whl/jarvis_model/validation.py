from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .errors import Error
from .jsonschema import JsonSchemaValidationError, SchemaViolation, validate_json_schema


@dataclass(frozen=True, slots=True)
class ToolArgsValidationError(ValueError):
    error: Error
    issues: Sequence[SchemaViolation]

    def __str__(self) -> str:  # pragma: no cover
        return self.error.message


def validate_tool_args(parameters_schema: Mapping[str, Any], args: Any) -> None:
    try:
        validate_json_schema(args, parameters_schema)
    except JsonSchemaValidationError as exc:
        issues = exc.issues
        error = Error(
            code="tool.invalid_args",
            message="Tool arguments failed JSON Schema validation",
            details={"issues": [i.to_dict() for i in issues]},
            retryable=False,
        )
        raise ToolArgsValidationError(error=error, issues=issues) from exc

