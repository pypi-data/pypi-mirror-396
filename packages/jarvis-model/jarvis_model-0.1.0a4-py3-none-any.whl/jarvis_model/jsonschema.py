from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Mapping, MutableSequence, Sequence


@dataclass(frozen=True, slots=True)
class SchemaViolation:
    path: str
    message: str
    expected: Any | None = None
    actual: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"path": self.path, "message": self.message}
        if self.expected is not None:
            data["expected"] = self.expected
        if self.actual is not None:
            data["actual"] = self.actual
        return data


class JsonSchemaValidationError(ValueError):
    def __init__(self, issues: Sequence[SchemaViolation]):
        self.issues = list(issues)
        message = self.issues[0].message if self.issues else "JSON Schema validation failed"
        super().__init__(message)


def validate_json_schema(instance: Any, schema: Mapping[str, Any]) -> None:
    issues: list[SchemaViolation] = []
    _validate(instance=instance, schema=schema, path="", issues=issues)
    if issues:
        raise JsonSchemaValidationError(issues)


def _validate(*, instance: Any, schema: Mapping[str, Any], path: str, issues: MutableSequence[SchemaViolation]) -> None:
    # Composition keywords first.
    if "allOf" in schema and isinstance(schema["allOf"], list):
        for idx, subschema in enumerate(schema["allOf"]):
            if isinstance(subschema, Mapping):
                _validate(instance=instance, schema=subschema, path=path, issues=issues)
            else:
                issues.append(
                    SchemaViolation(
                        path=path,
                        message=f"allOf[{idx}] must be an object schema",
                        expected="object",
                        actual=type(subschema).__name__,
                    )
                )
        return

    if "anyOf" in schema and isinstance(schema["anyOf"], list):
        if any(_is_valid(instance, subschema) for subschema in schema["anyOf"] if isinstance(subschema, Mapping)):
            return
        issues.append(SchemaViolation(path=path, message="Value does not match anyOf schemas"))
        return

    if "oneOf" in schema and isinstance(schema["oneOf"], list):
        matches = sum(
            1 for subschema in schema["oneOf"] if isinstance(subschema, Mapping) and _is_valid(instance, subschema)
        )
        if matches == 1:
            return
        issues.append(SchemaViolation(path=path, message=f"Value matches {matches} oneOf schemas (expected 1)"))
        return

    # Enum/const.
    if "const" in schema:
        if instance != schema["const"]:
            issues.append(
                SchemaViolation(path=path, message="Value does not match const", expected=schema["const"], actual=instance)
            )
        return

    if "enum" in schema and isinstance(schema["enum"], list):
        if instance not in schema["enum"]:
            issues.append(
                SchemaViolation(path=path, message="Value is not in enum", expected=schema["enum"], actual=instance)
            )
        return

    # Type.
    schema_type = schema.get("type")
    if schema_type is None:
        # No type constraint; accept any.
        return

    allowed = schema_type if isinstance(schema_type, list) else [schema_type]
    if not _matches_any_type(instance, allowed):
        issues.append(
            SchemaViolation(
                path=path,
                message="Type mismatch",
                expected=allowed,
                actual=_instance_type_name(instance),
            )
        )
        return

    # Type-specific constraints.
    if "object" in allowed:
        if not isinstance(instance, dict):
            return
        _validate_object(instance=instance, schema=schema, path=path, issues=issues)
        return
    if "array" in allowed:
        if not isinstance(instance, (list, tuple)):
            return
        _validate_array(instance=instance, schema=schema, path=path, issues=issues)
        return
    if "string" in allowed:
        if not isinstance(instance, str):
            return
        _validate_string(instance=instance, schema=schema, path=path, issues=issues)
        return
    if "integer" in allowed or "number" in allowed:
        _validate_number(instance=instance, schema=schema, path=path, issues=issues)
        return
    if "boolean" in allowed or "null" in allowed:
        return


def _is_valid(instance: Any, schema: Mapping[str, Any]) -> bool:
    try:
        validate_json_schema(instance, schema)
    except JsonSchemaValidationError:
        return False
    return True


def _matches_any_type(instance: Any, allowed: Sequence[Any]) -> bool:
    for t in allowed:
        if _matches_type(instance, t):
            return True
    return False


def _matches_type(instance: Any, schema_type: Any) -> bool:
    if schema_type == "object":
        return isinstance(instance, dict)
    if schema_type == "array":
        return isinstance(instance, (list, tuple))
    if schema_type == "string":
        return isinstance(instance, str)
    if schema_type == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if schema_type == "number":
        return (isinstance(instance, (int, float)) and not isinstance(instance, bool)) and (
            not isinstance(instance, float) or math.isfinite(instance)
        )
    if schema_type == "boolean":
        return isinstance(instance, bool)
    if schema_type == "null":
        return instance is None
    return False


def _instance_type_name(instance: Any) -> str:
    if instance is None:
        return "null"
    if isinstance(instance, bool):
        return "boolean"
    if isinstance(instance, dict):
        return "object"
    if isinstance(instance, (list, tuple)):
        return "array"
    if isinstance(instance, str):
        return "string"
    if isinstance(instance, int):
        return "integer"
    if isinstance(instance, float):
        return "number"
    return type(instance).__name__


def _join(path: str, key: str) -> str:
    if not path:
        return f"/{key}"
    return f"{path}/{key}"


def _validate_object(*, instance: dict[str, Any], schema: Mapping[str, Any], path: str, issues: MutableSequence[SchemaViolation]) -> None:
    raw_properties = schema.get("properties")
    properties: Mapping[str, Any] = raw_properties if isinstance(raw_properties, Mapping) else {}

    raw_required = schema.get("required")
    required: Sequence[Any] = raw_required if isinstance(raw_required, list) else []

    for req in required:
        if not isinstance(req, str):
            continue
        if req not in instance:
            issues.append(SchemaViolation(path=_join(path, req), message="Missing required property"))

    additional: Any = schema.get("additionalProperties", True)
    for key, value in instance.items():
        if key in properties:
            prop_schema = properties.get(key)
            if isinstance(prop_schema, Mapping):
                _validate(instance=value, schema=prop_schema, path=_join(path, key), issues=issues)
        else:
            if additional is False:
                issues.append(SchemaViolation(path=_join(path, key), message="Additional properties are not allowed"))
            elif isinstance(additional, Mapping):
                _validate(instance=value, schema=additional, path=_join(path, key), issues=issues)


def _validate_array(*, instance: Sequence[Any], schema: Mapping[str, Any], path: str, issues: MutableSequence[SchemaViolation]) -> None:
    items = schema.get("items")
    if not isinstance(items, Mapping):
        return
    for idx, item in enumerate(instance):
        _validate(instance=item, schema=items, path=_join(path, str(idx)), issues=issues)


def _validate_string(*, instance: str, schema: Mapping[str, Any], path: str, issues: MutableSequence[SchemaViolation]) -> None:
    min_len = schema.get("minLength")
    if isinstance(min_len, int) and len(instance) < min_len:
        issues.append(SchemaViolation(path=path, message="String shorter than minLength", expected=min_len, actual=len(instance)))
    max_len = schema.get("maxLength")
    if isinstance(max_len, int) and len(instance) > max_len:
        issues.append(SchemaViolation(path=path, message="String longer than maxLength", expected=max_len, actual=len(instance)))

    pattern = schema.get("pattern")
    if isinstance(pattern, str) and pattern:
        try:
            if re.search(pattern, instance) is None:
                issues.append(SchemaViolation(path=path, message="String does not match pattern", expected=pattern))
        except re.error:
            issues.append(SchemaViolation(path=path, message="Invalid pattern in schema", expected=pattern))


def _validate_number(*, instance: Any, schema: Mapping[str, Any], path: str, issues: MutableSequence[SchemaViolation]) -> None:
    # For "integer" and "number" we already verified type compatibility.
    if isinstance(instance, bool):
        issues.append(SchemaViolation(path=path, message="Type mismatch", expected=schema.get("type"), actual="boolean"))
        return
    if not isinstance(instance, (int, float)):
        return
    if isinstance(instance, float) and not math.isfinite(instance):
        issues.append(SchemaViolation(path=path, message="Number must be finite", actual=instance))
        return

    minimum = schema.get("minimum")
    if isinstance(minimum, (int, float)) and instance < minimum:
        issues.append(SchemaViolation(path=path, message="Number is less than minimum", expected=minimum, actual=instance))

    maximum = schema.get("maximum")
    if isinstance(maximum, (int, float)) and instance > maximum:
        issues.append(SchemaViolation(path=path, message="Number is greater than maximum", expected=maximum, actual=instance))
