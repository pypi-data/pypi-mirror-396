from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from .errors import Error
from .version import SCHEMA_VERSION


def _utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class FlowStep:
    step_id: str
    type: str  # plan | tool | chat
    status: str  # pending | in_progress | completed | failed
    created_at: str
    payload: dict[str, Any]
    result: Optional[dict[str, Any]] = None
    error: Optional[Error] = None
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def new(cls, *, step_id: str, type: str, payload: dict[str, Any], status: str = "pending") -> "FlowStep":
        return cls(step_id=step_id, type=type, status=status, created_at=_utc_iso(datetime.now(timezone.utc)), payload=payload)


@dataclass(frozen=True, slots=True)
class FlowRun:
    flow_id: str
    created_at: str
    input: Any
    status: str = "running"  # running | completed | failed
    steps: Optional[list[FlowStep]] = None
    metadata: Optional[dict[str, Any]] = None
    schema_version: str = SCHEMA_VERSION

    @classmethod
    def new(cls, *, flow_id: str, input: Any, status: str = "running") -> "FlowRun":
        return cls(flow_id=flow_id, created_at=_utc_iso(datetime.now(timezone.utc)), input=input, status=status)


# Compatibility aliases with the ExecutionPlan naming.
Flow = FlowRun
Step = FlowStep

