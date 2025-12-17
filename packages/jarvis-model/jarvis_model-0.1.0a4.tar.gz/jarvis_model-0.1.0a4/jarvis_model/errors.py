from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .version import SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class Error:
    code: str
    message: str
    details: Optional[dict[str, Any]] = None
    retryable: bool = False
    cause: Optional["Error"] = None
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema_version": self.schema_version,
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.details is not None:
            data["details"] = self.details
        if self.cause is not None:
            data["cause"] = self.cause.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Error":
        cause = data.get("cause")
        return cls(
            schema_version=str(data.get("schema_version") or SCHEMA_VERSION),
            code=str(data.get("code") or ""),
            message=str(data.get("message") or ""),
            details=data.get("details") if isinstance(data.get("details"), dict) else None,
            retryable=bool(data.get("retryable") or False),
            cause=cls.from_dict(cause) if isinstance(cause, dict) else None,
        )

